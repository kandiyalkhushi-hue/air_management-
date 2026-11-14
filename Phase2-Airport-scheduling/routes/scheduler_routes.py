
from flask import Blueprint, jsonify, request

from scheduler.scheduler import (
    get_waiting_flights,
    get_flight,
    schedule_flight
)
from scheduler.algorithm_selector import (
    run_algorithm,
    get_supported_algorithms,
    normalize_algorithm
)
from scheduler.metrics import calculate_metrics
from scheduler.algorithms.priority import priority_scheduling
from scheduler.algorithms.common import prepare_flight
from scheduler.batch_scheduler import run_priority_scheduler
from scheduler.runway_allocator import select_best_runway
from scheduler.atc_allocator import select_atc
from scheduler.weather_checker import check_weather
from scheduler.schedule_manager import (
    create_scheduler_run,
    save_schedule,
    update_flight_status,
    update_flight_situation,
    update_scheduler_run_metrics,
    complete_scheduler_run
)


scheduler_bp = Blueprint(
    "scheduler",
    __name__,
    url_prefix="/scheduler"
)


def prepare_flight_batch(flights):
    prepared = []
    failures = []

    for flight in flights:
        try:
            prepared.append(prepare_flight(flight))
        except ValueError as error:
            failures.append({
                "flight_id": flight.get("flight_id"),
                "flight_number": flight.get("flight_number"),
                "reason": str(error),
                "stage": "SCHEDULING"
            })

    return prepared, failures


# =========================================================
# GET WAITING FLIGHTS
# =========================================================

@scheduler_bp.route("/flights", methods=["GET"])
def waiting_flights():
    try:
        airport_id = request.args.get("airport_id", type=int)
        flights = get_waiting_flights(airport_id)

        return jsonify({
            "success": True,
            "total_flights": len(flights),
            "airport_id": airport_id,
            "flights": flights
        }), 200

    except Exception as error:
        return jsonify({
            "success": False,
            "message": "Unable to fetch waiting flights",
            "error": str(error)
        }), 500


# =========================================================
# GET SINGLE FLIGHT
# =========================================================

@scheduler_bp.route("/flight/<int:flight_id>", methods=["GET"])
def get_single_flight(flight_id):
    try:
        flight = get_flight(flight_id)

        if not flight:
            return jsonify({
                "success": False,
                "message": "Flight not found"
            }), 404

        return jsonify({
            "success": True,
            "flight": flight
        }), 200

    except Exception as error:
        return jsonify({
            "success": False,
            "message": "Unable to fetch flight",
            "error": str(error)
        }), 500


# =========================================================
# ASSIGN SINGLE FLIGHT
# =========================================================

@scheduler_bp.route("/assign/<int:flight_id>", methods=["POST"])
def assign_flight(flight_id):
    try:
        data = request.get_json(silent=True) or {}
        situation = data.get("situation")

        result = schedule_flight(
            flight_id=flight_id,
            situation=situation
        )

        if not result["success"]:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as error:
        return jsonify({
            "success": False,
            "message": "Unable to schedule flight",
            "error": str(error)
        }), 500


# =========================================================
# PRIORITY QUEUE
# =========================================================

@scheduler_bp.route("/priority-queue/<int:airport_id>", methods=["GET"])
def priority_queue(airport_id):
    try:
        flights = get_waiting_flights(airport_id)

        if not flights:
            return jsonify({
                "success": True,
                "algorithm": "PRIORITY",
                "airport_id": airport_id,
                "total_flights": 0,
                "queue": []
            }), 200

        scheduled_queue = priority_scheduling(flights)
        result = []

        for position, flight in enumerate(scheduled_queue, start=1):
            result.append({
                "queue_position": position,
                "flight_id": flight["flight_id"],
                "flight_number": flight["flight_number"],
                "operation_type": flight["operation_type"],
                "situation": flight["current_situation"],
                "situation_priority": flight["situation_priority"],
                "normal_priority": flight["priority"],
                "processing_time": flight["processing_time_minutes"],
                "fuel_percentage": flight["fuel_percentage"],
                "passenger_count": flight["passenger_count"],
                "status": flight["status"]
            })

        return jsonify({
            "success": True,
            "algorithm": "PRIORITY",
            "airport_id": airport_id,
            "total_flights": len(result),
            "queue": result
        }), 200

    except Exception as error:
        return jsonify({
            "success": False,
            "message": "Unable to generate priority queue",
            "error": str(error)
        }), 500


# =========================================================
# RUN PRIORITY SCHEDULER
# =========================================================

@scheduler_bp.route("/run-priority/<int:airport_id>", methods=["POST"])
def run_priority(airport_id):
    try:
        result = run_priority_scheduler(airport_id)

        if not result["success"]:
            return jsonify(result), 404

        return jsonify(result), 200

    except Exception as error:
        return jsonify({
            "success": False,
            "message": "Unable to run priority scheduler",
            "error": str(error)
        }), 500


# =========================================================
# GET SUPPORTED ALGORITHMS
# =========================================================

@scheduler_bp.route("/algorithms", methods=["GET"])
def supported_algorithms():
    try:
        algorithms = get_supported_algorithms()

        return jsonify({
            "success": True,
            "total_algorithms": len(algorithms),
            "algorithms": algorithms
        }), 200

    except Exception as error:
        return jsonify({
            "success": False,
            "message": "Unable to fetch algorithms",
            "error": str(error)
        }), 500


@scheduler_bp.route("/preview/<int:airport_id>", methods=["POST"])
def preview_scheduler(airport_id):
    try:
        data = request.get_json(silent=True) or {}
        try:
            algorithm = normalize_algorithm(data.get("algorithm"))
        except ValueError as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 400

        try:
            time_quantum = int(data.get(
                "time_quantum",
                data.get("quantum", 3)
            ))
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "time_quantum must be an integer"
            }), 400

        if time_quantum <= 0:
            return jsonify({
                "success": False,
                "message": "time_quantum must be greater than 0"
            }), 400

        waiting_flights = get_waiting_flights(airport_id)
        flights, invalid_flights = prepare_flight_batch(waiting_flights)
        results = run_algorithm(
            algorithm=algorithm,
            flights=flights,
            time_quantum=time_quantum
        )

        queue = [{
            "queue_position": result["queue_position"],
            "flight_id": result["flight_id"],
            "flight_number": result["flight_number"],
            "situation": (
                result.get("situation")
                or result.get("current_situation")
                or "NORMAL"
            ),
            "processing_time": result["processing_time"],
            "requested_time": result["requested_time"].isoformat()
        } for result in results]

        return jsonify({
            "success": True,
            "airport_id": airport_id,
            "algorithm": algorithm,
            "queue": queue,
            "invalid_flights": invalid_flights
        }), 200
    except Exception as error:
        return jsonify({
            "success": False,
            "message": "Unable to preview airport scheduling",
            "error": str(error)
        }), 500


@scheduler_bp.route("/preview/all/<int:airport_id>", methods=["POST"])
def preview_all_schedulers(airport_id):
    try:
        data = request.get_json(silent=True) or {}
        try:
            time_quantum = int(data.get(
                "time_quantum",
                data.get("quantum", 3)
            ))
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "time_quantum must be an integer"
            }), 400

        if time_quantum <= 0:
            return jsonify({
                "success": False,
                "message": "time_quantum must be greater than 0"
            }), 400

        waiting_flights = get_waiting_flights(
            airport_id,
            include_scheduled=True
        )
        flights, invalid_flights = prepare_flight_batch(waiting_flights)
        charts = []

        for algorithm in get_supported_algorithms():
            results = run_algorithm(
                algorithm=algorithm,
                flights=flights,
                time_quantum=time_quantum
            )
            segments = []

            for result in results:
                execution_slices = result.get("execution_slices") or [{
                    "start_time": result["start_time"],
                    "end_time": result["end_time"],
                    "duration_minutes": result["processing_time"],
                    "completed": True
                }]

                for index, execution_slice in enumerate(
                    execution_slices,
                    start=1
                ):
                    segments.append({
                        "flight_id": result["flight_id"],
                        "flight_number": result["flight_number"],
                        "queue_position": result["queue_position"],
                        "turn_number": execution_slice.get(
                            "turn_number",
                            index
                        ),
                        "start_time": execution_slice["start_time"].isoformat(),
                        "end_time": execution_slice["end_time"].isoformat(),
                        "duration_minutes": execution_slice.get(
                            "duration_minutes",
                            result["processing_time"]
                        ),
                        "completed": execution_slice.get("completed", True)
                    })

            segments.sort(
                key=lambda segment: (
                    segment["start_time"],
                    str(segment["flight_id"]),
                    segment["turn_number"]
                )
            )
            charts.append({
                "algorithm": algorithm,
                "segments": segments,
                "metrics": calculate_metrics(results)
            })

        return jsonify({
            "success": True,
            "airport_id": airport_id,
            "time_quantum": time_quantum,
            "flight_count": len(flights),
            "input_flights": [{
                "flight_id": flight.get("flight_id"),
                "flight_number": flight.get("flight_number")
            } for flight in flights],
            "charts": charts,
            "invalid_flights": invalid_flights
        }), 200
    except Exception as error:
        return jsonify({
            "success": False,
            "message": "Unable to preview all airport scheduling algorithms",
            "error": str(error)
        }), 500


# =========================================================
# UNIFIED SCHEDULER
# =========================================================

@scheduler_bp.route("/run/<int:airport_id>", methods=["POST"])
def run_unified_scheduler(airport_id):
    try:
        # -------------------------------------------------
        # 1. READ REQUEST BODY
        # -------------------------------------------------

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "message": "Request body is required"
            }), 400

        algorithm = data.get("algorithm")

        # -------------------------------------------------
        # 2. VALIDATE ALGORITHM
        # -------------------------------------------------

        try:
            algorithm = normalize_algorithm(algorithm)
        except ValueError as error:
            return jsonify({
                "success": False,
                "message": str(error)
            }), 400

        # -------------------------------------------------
        # 3. VALIDATE TIME QUANTUM
        # -------------------------------------------------

        time_quantum = data.get(
            "time_quantum",
            data.get("quantum", 3)
        )

        try:
            time_quantum = int(time_quantum)
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "time_quantum must be an integer"
            }), 400

        if time_quantum <= 0:
            return jsonify({
                "success": False,
                "message": "time_quantum must be greater than 0"
            }), 400

        # -------------------------------------------------
        # 4. GET WAITING FLIGHTS
        # -------------------------------------------------

        flights = get_waiting_flights(airport_id)

        if not flights:
            return jsonify({
                "success": False,
                "message": "No waiting flights found",
                "airport_id": airport_id,
                "algorithm": algorithm
            }), 404

        all_flights = flights
        flights, invalid_flights = prepare_flight_batch(all_flights)

        if not flights:
            return jsonify({
                "success": False,
                "message": "No flights have valid scheduling inputs",
                "airport_id": airport_id,
                "algorithm": algorithm,
                "failed": invalid_flights
            }), 422

        # -------------------------------------------------
        # 5. RUN SCHEDULING ALGORITHM
        # -------------------------------------------------

        results = run_algorithm(
            algorithm=algorithm,
            flights=flights,
            time_quantum=time_quantum
        )

        if not results:
            return jsonify({
                "success": False,
                "message": "Algorithm produced no scheduling results",
                "airport_id": airport_id,
                "algorithm": algorithm
            }), 400

        # -------------------------------------------------
        # 6. BUILD ROUND ROBIN EXECUTION TIMELINE
        # -------------------------------------------------

        execution_timeline = []

        for flight_result in results:
            execution_slices = flight_result.get("execution_slices") or [{
                "start_time": flight_result["start_time"],
                "end_time": flight_result["end_time"],
                "turn_number": 1,
                "duration_minutes": flight_result["processing_time"],
                "remaining_time_minutes": 0,
                "completed": True
            }]
            for execution_slice in execution_slices:
                start_time = execution_slice["start_time"]
                end_time = execution_slice["end_time"]

                execution_timeline.append({
                    "flight_id": flight_result.get("flight_id"),
                    "flight_number": flight_result.get("flight_number"),
                    "turn_number": execution_slice.get("turn_number"),
                    "_sort_start_time": start_time,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_minutes": execution_slice.get(
                        "duration_minutes"
                    ),
                    "remaining_time_minutes": execution_slice.get(
                        "remaining_time_minutes"
                    ),
                    "completed": execution_slice.get(
                        "completed", False
                    )
                })

        # Sort using actual datetime values before converting
        # them to strings for the JSON response.
        execution_timeline.sort(
            key=lambda turn: (
                turn["_sort_start_time"],
                str(turn["flight_id"])
            )
        )

        for global_turn, turn in enumerate(
            execution_timeline, start=1
        ):
            turn["global_turn"] = global_turn
            turn.pop("_sort_start_time", None)

        # -------------------------------------------------
        # 7. CALCULATE METRICS
        # -------------------------------------------------

        metrics = calculate_metrics(results)

        # -------------------------------------------------
        # 8. CREATE SCHEDULER RUN
        # -------------------------------------------------

        run_id = create_scheduler_run(
            algorithm=algorithm,
            total_flights=len(all_flights)
        )

        scheduled_flights = []
        failed_flights = list(invalid_flights)

        # -------------------------------------------------
        # 9. RESOURCE ALLOCATION
        # -------------------------------------------------

        flights_by_id = {
            flight["flight_id"]: flight
            for flight in flights
        }
        failed_ids = set()
        segment_requests = []

        for flight_result in results:
            flight_id = flight_result["flight_id"]
            flight = flights_by_id.get(flight_id)
            if not flight:
                failed_flights.append({
                    "flight_id": flight_id,
                    "reason": "Original flight data not found",
                    "stage": "SCHEDULING"
                })
                failed_ids.add(flight_id)
                continue

            weather_result = check_weather(airport_id)
            if not weather_result["safe"]:
                failed_flights.append({
                    "flight_id": flight_id,
                    "flight_number": flight.get("flight_number"),
                    "reason": weather_result["reason"],
                    "stage": "WEATHER",
                    "weather": weather_result.get("weather")
                })
                failed_ids.add(flight_id)
                continue

            slices = flight_result.get("execution_slices") or [{
                "start_time": flight_result["start_time"],
                "end_time": flight_result["end_time"],
                "duration_minutes": flight_result["processing_time"],
                "completed": True
            }]
            for slice_number, execution_slice in enumerate(slices, start=1):
                segment_requests.append({
                    "flight_result": flight_result,
                    "flight": flight,
                    "slice_number": slice_number,
                    "start_time": execution_slice["start_time"],
                    "end_time": execution_slice["end_time"],
                    "duration_minutes": execution_slice.get(
                        "duration_minutes"
                    )
                })

        segment_requests.sort(
            key=lambda segment: (
                segment["start_time"],
                str(segment["flight"]["flight_id"]),
                segment["slice_number"]
            )
        )
        reserved_intervals = []
        allocated_segments = []

        for segment in segment_requests:
            flight = segment["flight"]
            flight_id = flight["flight_id"]
            if flight_id in failed_ids:
                continue

            runway = select_best_runway(
                airport_id=airport_id,
                operation_type=flight["operation_type"],
                aircraft_type=flight["required_runway_type"],
                scheduled_start=segment["start_time"],
                scheduled_end=segment["end_time"],
                reserved_intervals=reserved_intervals,
                flight_id=flight_id
            )
            if not runway:
                failed_flights.append({
                    "flight_id": flight_id,
                    "flight_number": flight.get("flight_number"),
                    "reason": (
                        "No compatible runway available for "
                        f"{segment['start_time'].isoformat()} to "
                        f"{segment['end_time'].isoformat()}"
                    ),
                    "stage": "RUNWAY"
                })
                failed_ids.add(flight_id)
                reserved_intervals = [
                    reservation for reservation in reserved_intervals
                    if reservation["flight_id"] != flight_id
                ]
                continue

            atc = select_atc(
                airport_id,
                scheduled_start=segment["start_time"],
                scheduled_end=segment["end_time"]
            )
            if not atc:
                failed_flights.append({
                    "flight_id": flight_id,
                    "flight_number": flight.get("flight_number"),
                    "reason": (
                        "No ATC controller available for "
                        f"{segment['start_time'].isoformat()} to "
                        f"{segment['end_time'].isoformat()}"
                    ),
                    "stage": "ATC"
                })
                failed_ids.add(flight_id)
                reserved_intervals = [
                    reservation for reservation in reserved_intervals
                    if reservation["flight_id"] != flight_id
                ]
                continue

            reservation = {
                "flight_id": flight_id,
                "runway_id": runway["runway_id"],
                "scheduled_start": segment["start_time"],
                "scheduled_end": segment["end_time"]
            }
            reserved_intervals.append(reservation)
            allocated_segments.append({
                **segment,
                "runway": runway,
                "atc": atc
            })

        saved_segments_by_flight = {}
        for segment in allocated_segments:
            flight = segment["flight"]
            flight_id = flight["flight_id"]
            if flight_id in failed_ids:
                continue

            flight_result = segment["flight_result"]
            situation = (
                flight.get("current_situation") or "NORMAL"
            ).upper()
            saved_schedule = save_schedule(
                run_id=run_id,
                flight=flight,
                runway=segment["runway"],
                atc=segment["atc"],
                situation=situation,
                algorithm=algorithm,
                queue_position=flight_result["queue_position"],
                scheduled_start=segment["start_time"],
                scheduled_end=segment["end_time"],
                waiting_time_minutes=flight_result.get(
                    "waiting_time_minutes", 0
                ),
                turnaround_time_minutes=flight_result.get(
                    "turnaround_time_minutes", 0
                ),
                response_time_minutes=flight_result.get(
                    "response_time_minutes", 0
                )
            )
            saved_segments_by_flight.setdefault(flight_id, []).append({
                "slice_number": segment["slice_number"],
                "start_time": saved_schedule["scheduled_start"].isoformat(),
                "end_time": saved_schedule["scheduled_end"].isoformat(),
                "schedule_id": saved_schedule["schedule_id"],
                "runway": {
                    "runway_id": segment["runway"]["runway_id"],
                    "runway_code": segment["runway"]["runway_code"],
                    "runway_type": segment["runway"]["runway_type"]
                },
                "atc": {
                    "atc_id": segment["atc"]["atc_id"],
                    "employee_code": segment["atc"]["employee_code"],
                    "controller_name": segment["atc"]["controller_name"]
                }
            })

        for flight_result in results:
            flight_id = flight_result["flight_id"]
            if flight_id in failed_ids:
                continue

            flight = flights_by_id[flight_id]
            situation = (
                flight.get("current_situation") or "NORMAL"
            ).upper()
            segment_schedules = saved_segments_by_flight.get(flight_id, [])
            if not segment_schedules:
                failed_flights.append({
                    "flight_id": flight_id,
                    "flight_number": flight.get("flight_number"),
                    "reason": "No execution segments were allocated",
                    "stage": "SCHEDULING"
                })
                continue

            update_flight_situation(flight_id, situation)
            update_flight_status(flight_id, "SCHEDULED")

            first_segment = segment_schedules[0]
            scheduled_flights.append({
                "queue_position": flight_result["queue_position"],
                "flight_id": flight_id,
                "flight_number": flight.get("flight_number"),
                "operation_type": flight.get("operation_type"),
                "situation": situation,
                "algorithm": algorithm,
                "schedule_id": first_segment["schedule_id"],
                "runway": first_segment["runway"],
                "atc": first_segment["atc"],
                "scheduled_start": first_segment["start_time"],
                "scheduled_end": segment_schedules[-1]["end_time"],
                "execution_slices": segment_schedules,
                "waiting_time_minutes": flight_result.get(
                    "waiting_time_minutes", 0
                ),
                "turnaround_time_minutes": flight_result.get(
                    "turnaround_time_minutes", 0
                ),
                "response_time_minutes": flight_result.get(
                    "response_time_minutes", 0
                )
            })

        # -------------------------------------------------
        # 10. UPDATE RUN METRICS
        # -------------------------------------------------

        update_scheduler_run_metrics(
            run_id=run_id,
            average_waiting_time=metrics["average_waiting_time"],
            average_turnaround_time=metrics["average_turnaround_time"],
            average_response_time=metrics["average_response_time"],
            throughput=metrics["throughput"],
            runway_utilization=metrics["runway_utilization"]
        )

        # -------------------------------------------------
        # 11. DETERMINE RUN STATUS
        # -------------------------------------------------

        if failed_flights and not scheduled_flights:
            run_status = "FAILED"
        else:
            run_status = "COMPLETED"

        # -------------------------------------------------
        # 12. COMPLETE SCHEDULER RUN
        # -------------------------------------------------

        complete_scheduler_run(
            run_id=run_id,
            total_flights=len(all_flights),
            status=run_status
        )

        # -------------------------------------------------
        # 13. FINAL API RESPONSE
        # -------------------------------------------------

        return jsonify({
            "success": True,
            "message": "Airport scheduling completed",
            "run_id": run_id,
            "airport_id": airport_id,
            "algorithm": algorithm,
            "time_quantum": (
                time_quantum
                if algorithm == "ROUND_ROBIN"
                else None
            ),
            "total_flights": len(all_flights),
            "scheduled_flights": len(scheduled_flights),
            "failed_flights": len(failed_flights),
            "metrics": metrics,
            "scheduled": scheduled_flights,
            "failed": failed_flights,
            "execution_timeline": execution_timeline
        }), 200

    except Exception as error:
        return jsonify({
            "success": False,
            "message": "Unable to run airport scheduler",
            "error": str(error)
        }), 500
