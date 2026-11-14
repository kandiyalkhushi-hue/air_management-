# scheduler/batch_scheduler.py

from database import get_db_connection

from scheduler.scheduler import (
    get_waiting_flights
)

from scheduler.priority_manager import (
    get_priority
)

from scheduler.runway_allocator import (
    select_best_runway
)

from scheduler.atc_allocator import (
    select_atc
)

from scheduler.weather_checker import (
    check_weather
)

from scheduler.schedule_manager import (
    create_scheduler_run,
    save_schedule,
    complete_scheduler_run
)


# =========================================================
# UPDATE FLIGHT STATUS
# =========================================================

def update_flight_status(
    flight_id,
    status
):
    """
    Update the status of a flight after scheduling.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        query = """
            UPDATE flights

            SET status = %s

            WHERE flight_id = %s
        """

        cursor.execute(
            query,
            (
                status,
                flight_id
            )
        )

        connection.commit()

    finally:

        cursor.close()
        connection.close()


# =========================================================
# SORT FLIGHTS BY PRIORITY
# =========================================================

def sort_by_priority(flights):
    """
    Priority scheduling.

    Lower number = higher priority.

    MEDICAL   -> 1
    EMERGENCY -> 2
    LOW_FUEL  -> 3
    WEATHER   -> 4
    VIP       -> 5
    NORMAL    -> 6

    If two flights have the same situation priority,
    normal flight priority is used.

    If that is also same, earlier requested time wins.
    """

    for flight in flights:

        situation = (
            flight.get(
                "current_situation"
            )
            or "NORMAL"
        )

        flight["situation_priority"] = (
            get_priority(situation)
        )

    def sort_key(flight):

        if flight["operation_type"] == "ARRIVAL":

            requested_time = (
                flight["arrival_time"]
            )

        else:

            requested_time = (
                flight["departure_time"]
            )

        return (

            flight["situation_priority"],

            flight.get(
                "priority",
                999
            ),

            requested_time,

            flight["flight_id"]
        )

    return sorted(
        flights,
        key=sort_key
    )


# =========================================================
# RUN PRIORITY SCHEDULER
# =========================================================

def run_priority_scheduler(
    airport_id
):
    """
    Process all waiting flights of one airport.

    Flow:

    Airport
       ↓
    Waiting Flights
       ↓
    Priority Queue
       ↓
    Weather
       ↓
    Runway
       ↓
    ATC
       ↓
    Save Schedule
       ↓
    Update Flight Status
       ↓
    Final Results
    """

    # =====================================================
    # 1. GET WAITING FLIGHTS
    # =====================================================

    flights = get_waiting_flights(
        airport_id
    )

    if not flights:

        return {
            "success": False,

            "message": (
                "No waiting flights found "
                "for this airport"
            ),

            "airport_id": airport_id,

            "total_flights": 0
        }


    # =====================================================
    # 2. CREATE PRIORITY QUEUE
    # =====================================================

    priority_queue = sort_by_priority(
        flights
    )


    # =====================================================
    # 3. CREATE ONE SCHEDULER RUN
    # =====================================================

    run_id = create_scheduler_run(
        "PRIORITY",
        len(priority_queue)
    )


    # =====================================================
    # 4. RESULT ARRAYS
    # =====================================================

    successful_flights = []

    failed_flights = []


    # =====================================================
    # 5. PROCESS EACH FLIGHT
    # =====================================================

    for queue_position, flight in enumerate(
        priority_queue,
        start=1
    ):

        flight_id = (
            flight["flight_id"]
        )

        flight_number = (
            flight["flight_number"]
        )

        situation = (
            flight.get(
                "current_situation"
            )
            or "NORMAL"
        )

        situation = situation.upper()


        # -------------------------------------------------
        # Determine requested time
        # -------------------------------------------------

        if flight["operation_type"] == "ARRIVAL":

            scheduled_start = (
                flight["arrival_time"]
            )

        else:

            scheduled_start = (
                flight["departure_time"]
            )


        if scheduled_start is None:

            failed_flights.append({

                "flight_id": flight_id,

                "flight_number": flight_number,

                "reason": (
                    "No arrival/departure time"
                )
            })

            continue


        # -------------------------------------------------
        # Processing time
        # -------------------------------------------------

        processing_time = (
            flight[
                "processing_time_minutes"
            ]
        )

        if processing_time is None:

            processing_time = 10


        # -------------------------------------------------
        # Calculate end time
        # -------------------------------------------------

        from datetime import timedelta

        scheduled_end = (
            scheduled_start
            + timedelta(
                minutes=processing_time
            )
        )


        # -------------------------------------------------
        # Situation priority
        # -------------------------------------------------

        try:

            situation_priority = (
                get_priority(
                    situation
                )
            )

        except ValueError as error:

            failed_flights.append({

                "flight_id": flight_id,

                "flight_number": flight_number,

                "reason": str(error)
            })

            continue


        # -------------------------------------------------
        # Weather check
        # -------------------------------------------------

        weather_result = check_weather(
            airport_id
        )

        if not weather_result["safe"]:

            failed_flights.append({

                "flight_id": flight_id,

                "flight_number": flight_number,

                "reason": (
                    weather_result[
                        "reason"
                    ]
                )
            })

            continue


        # -------------------------------------------------
        # Find runway
        # -------------------------------------------------

        runway = select_best_runway(

            airport_id=airport_id,

            operation_type=(
                flight["operation_type"]
            ),

            aircraft_type=(
                flight[
                    "required_runway_type"
                ]
            ),

            scheduled_start=(
                scheduled_start
            ),

            scheduled_end=(
                scheduled_end
            ),

            flight_id=flight_id
        )


        if not runway:

            failed_flights.append({

                "flight_id": flight_id,

                "flight_number": flight_number,

                "reason": (
                    "No suitable runway "
                    "available for requested time"
                )
            })

            continue


        # -------------------------------------------------
        # Find ATC
        # -------------------------------------------------

        atc = select_atc(
            airport_id
        )


        if not atc:

            failed_flights.append({

                "flight_id": flight_id,

                "flight_number": flight_number,

                "reason": (
                    "No ATC controller available"
                )
            })

            continue


        # -------------------------------------------------
        # Save schedule
        # -------------------------------------------------

        try:

            saved_schedule = save_schedule(

                run_id=run_id,

                flight=flight,

                runway=runway,

                atc=atc,

                situation=situation,

                scheduled_start=scheduled_start
            )

        except Exception as error:

            failed_flights.append({

                "flight_id": flight_id,

                "flight_number": flight_number,

                "reason": str(error)
            })

            continue


        # -------------------------------------------------
        # Update flight status
        # -------------------------------------------------

        update_flight_status(
            flight_id,
            "SCHEDULED"
        )


        # -------------------------------------------------
        # Add successful result
        # -------------------------------------------------

        successful_flights.append({

            "queue_position": (
                queue_position
            ),

            "flight_id": flight_id,

            "flight_number": flight_number,

            "operation_type": (
                flight["operation_type"]
            ),

            "situation": situation,

            "priority": (
                situation_priority
            ),

            "runway": {

                "runway_id": (
                    runway["runway_id"]
                ),

                "runway_code": (
                    runway["runway_code"]
                ),

                "runway_type": (
                    runway["runway_type"]
                )
            },

            "atc": {

                "atc_id": (
                    atc["atc_id"]
                ),

                "employee_code": (
                    atc["employee_code"]
                ),

                "controller_name": (
                    atc["controller_name"]
                )
            },

            "schedule_id": (
                saved_schedule[
                    "schedule_id"
                ]
            ),

            "scheduled_start": (
                saved_schedule[
                    "scheduled_start"
                ]
            ),

            "scheduled_end": (
                saved_schedule[
                    "scheduled_end"
                ]
            )
        })


    # =====================================================
    # 6. COMPLETE SCHEDULER RUN
    # =====================================================

    complete_scheduler_run(
        run_id,
        len(priority_queue)
    )


    # =====================================================
    # 7. FINAL RESPONSE
    # =====================================================

    return {

        "success": True,

        "message": (
            "Priority scheduling completed"
        ),

        "run_id": run_id,

        "algorithm": "PRIORITY",

        "airport_id": airport_id,

        "total_flights": len(
            priority_queue
        ),

        "scheduled_flights": len(
            successful_flights
        ),

        "failed_flights": len(
            failed_flights
        ),

        "queue": successful_flights,

        "failed": failed_flights
    }