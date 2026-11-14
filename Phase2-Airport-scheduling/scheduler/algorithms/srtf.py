# scheduler/algorithms/srtf.py

from datetime import timedelta


def get_requested_time(flight):
    """
    Get the time at which the flight
    enters the scheduling queue.
    """

    if flight["operation_type"] == "ARRIVAL":
        return flight["arrival_time"]

    return flight["departure_time"]


def get_processing_time(flight):
    """
    Get processing time of a flight.

    Default processing time = 10 minutes
    """

    processing_time = flight.get(
        "processing_time_minutes"
    )

    if processing_time is None:
        processing_time = 10

    return processing_time


def srtf_scheduling(flights):
    """
    Shortest Remaining Time First Scheduling.

    SRTF is the PREEMPTIVE version of SJF.

    Rule:
        The flight with the shortest remaining
        processing time gets CPU/scheduler time.

    If a new flight arrives with a shorter
    remaining time, the currently running flight
    is preempted.

    Metrics:
        - queue_position
        - start_time
        - completion_time
        - waiting_time
        - turnaround_time
        - response_time
        - preemptions
    """

    if not flights:
        return []

    # -------------------------------------------------
    # Prepare flight information
    # -------------------------------------------------

    remaining_flights = []

    for flight in flights:

        requested_time = get_requested_time(
            flight
        )

        processing_time = get_processing_time(
            flight
        )

        remaining_flights.append({
            "flight": flight,
            "requested_time": requested_time,
            "processing_time": processing_time,
            "remaining_time": processing_time,
            "first_start_time": None,
            "completion_time": None,
            "preemptions": 0,
            "execution_slices": []
        })

    # -------------------------------------------------
    # Start scheduler clock
    # -------------------------------------------------

    current_time = min(
        item["requested_time"]
        for item in remaining_flights
    )

    completed = []

    current_flight = None

    # -------------------------------------------------
    # SRTF simulation
    # -------------------------------------------------

    while len(completed) < len(
        remaining_flights
    ):

        available = []

        for item in remaining_flights:

            if (
                item["completion_time"] is None
                and item["requested_time"]
                <= current_time
                and item["remaining_time"] > 0
            ):
                available.append(item)

        # ---------------------------------------------
        # No flight available
        # ---------------------------------------------

        if not available:

            future_flights = [
                item
                for item in remaining_flights
                if (
                    item["completion_time"]
                    is None
                    and item["requested_time"]
                    > current_time
                )
            ]

            if not future_flights:
                break

            current_time = min(
                item["requested_time"]
                for item in future_flights
            )

            current_flight = None

            continue

        # ---------------------------------------------
        # Select shortest remaining time
        # ---------------------------------------------

        selected = min(
            available,
            key=lambda item: (
                item["remaining_time"],
                item["requested_time"],
                item["flight"]["flight_id"]
            )
        )

        # ---------------------------------------------
        # Detect preemption
        # ---------------------------------------------

        if (
            current_flight is not None
            and current_flight is not selected
        ):

            current_flight["preemptions"] += 1

        current_flight = selected

        # ---------------------------------------------
        # First response/start time
        # ---------------------------------------------

        if (
            selected["first_start_time"]
            is None
        ):
            selected["first_start_time"] = (
                current_time
            )

        # ---------------------------------------------
        # Determine next event
        #
        # Either:
        # 1. Current flight completes
        # 2. New shorter flight arrives
        # ---------------------------------------------

        completion_time = (
            current_time
            + timedelta(
                minutes=selected["remaining_time"]
            )
        )

        future_arrivals = [
            item
            for item in remaining_flights
            if (
                item["completion_time"]
                is None
                and item["requested_time"]
                > current_time
                and item["requested_time"]
                < completion_time
            )
        ]

        if future_arrivals:

            next_arrival = min(
                item["requested_time"]
                for item in future_arrivals
            )

            elapsed_minutes = (
                next_arrival
                - current_time
            ).total_seconds() / 60

            selected["execution_slices"].append({
                "turn_number": len(selected["execution_slices"]) + 1,
                "start_time": current_time,
                "end_time": next_arrival,
                "duration_minutes": round(elapsed_minutes, 2),
                "remaining_time_minutes": round(
                    selected["remaining_time"] - elapsed_minutes, 2
                ),
                "completed": False
            })

            selected["remaining_time"] -= (
                elapsed_minutes
            )

            current_time = next_arrival

            # Don't permanently switch here.
            # Next loop will select the shortest
            # remaining flight.

        else:

            # -----------------------------------------
            # Current flight completes
            # -----------------------------------------

            selected["execution_slices"].append({
                "turn_number": len(selected["execution_slices"]) + 1,
                "start_time": current_time,
                "end_time": completion_time,
                "duration_minutes": round(
                    selected["remaining_time"], 2
                ),
                "remaining_time_minutes": 0,
                "completed": True
            })

            current_time = completion_time

            selected["remaining_time"] = 0

            selected["completion_time"] = (
                current_time
            )

            completed.append(selected)

            current_flight = None

    # -------------------------------------------------
    # Build final result
    # -------------------------------------------------

    results = []

    for position, item in enumerate(
        completed,
        start=1
    ):

        flight = item["flight"]

        requested_time = (
            item["requested_time"]
        )

        first_start_time = (
            item["first_start_time"]
        )

        completion_time = (
            item["completion_time"]
        )

        # ---------------------------------------------
        # Waiting Time
        #
        # Turnaround - Burst Time
        # ---------------------------------------------

        processing_time = (
            item["processing_time"]
        )

        turnaround_time = (
            completion_time
            - requested_time
        )

        turnaround_time_minutes = (
            turnaround_time.total_seconds()
            / 60
        )

        waiting_time_minutes = (
            turnaround_time_minutes
            - processing_time
        )

        # ---------------------------------------------
        # Response Time
        #
        # First time CPU/scheduler gets the flight
        # ---------------------------------------------

        response_time = (
            first_start_time
            - requested_time
        )

        response_time_minutes = (
            response_time.total_seconds()
            / 60
        )

        results.append({

            "flight_id":
                flight["flight_id"],

            "flight_number":
                flight["flight_number"],

            "airport_id":
                flight["airport_id"],

            "aircraft_id":
                flight["aircraft_id"],

            "operation_type":
                flight["operation_type"],

            "requested_time":
                requested_time,

            "processing_time":
                processing_time,

            "priority":
                flight.get(
                    "priority",
                    0
                ),

            "situation":
                flight.get(
                    "current_situation",
                    "NORMAL"
                ),

            "queue_position":
                position,

            "start_time":
                first_start_time,

            "completion_time":
                completion_time,

            "execution_slices":
                item["execution_slices"],

            "waiting_time_minutes":
                round(
                    waiting_time_minutes,
                    2
                ),

            "turnaround_time_minutes":
                round(
                    turnaround_time_minutes,
                    2
                ),

            "response_time_minutes":
                round(
                    response_time_minutes,
                    2
                ),

            "preemptions":
                item["preemptions"]
        })

    return results