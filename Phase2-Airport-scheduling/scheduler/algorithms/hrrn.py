# scheduler/algorithms/hrrn.py

from datetime import timedelta


def get_requested_time(flight):
    """
    Get the time at which the flight
    enters the scheduling queue.

    ARRIVAL   -> arrival_time
    DEPARTURE -> departure_time
    """

    if flight["operation_type"] == "ARRIVAL":
        return flight["arrival_time"]

    return flight["departure_time"]


def get_processing_time(flight):
    """
    Get processing time of a flight.

    Default = 10 minutes.
    """

    processing_time = flight.get(
        "processing_time_minutes"
    )

    if processing_time is None:
        processing_time = 10

    return processing_time


def calculate_response_ratio(
    waiting_time,
    processing_time
):
    """
    HRRN Formula:

    Response Ratio =
        (Waiting Time + Processing Time)
        / Processing Time

    Equivalent:

        1 + Waiting Time / Processing Time
    """

    if processing_time <= 0:
        return float("inf")

    return (
        waiting_time
        + processing_time
    ) / processing_time


def hrrn_scheduling(flights):
    """
    Highest Response Ratio Next Scheduling.

    HRRN is a NON-PREEMPTIVE scheduling algorithm.

    At every scheduling decision, the flight with
    the highest response ratio is selected.

    Formula:

        Response Ratio =
        (Waiting Time + Processing Time)
        / Processing Time

    Metrics:
        - queue_position
        - start_time
        - completion_time
        - waiting_time
        - turnaround_time
        - response_time
        - response_ratio
    """

    if not flights:
        return []

    # -------------------------------------------------
    # Prepare flights
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
            "processing_time": processing_time
        })

    # -------------------------------------------------
    # Scheduler clock starts at earliest flight
    # -------------------------------------------------

    current_time = min(
        item["requested_time"]
        for item in remaining_flights
    )

    ready_queue = []

    results = []

    # -------------------------------------------------
    # Main HRRN loop
    # -------------------------------------------------

    while remaining_flights:

        # ---------------------------------------------
        # Find flights that have arrived
        # ---------------------------------------------

        ready_queue = [
            item
            for item in remaining_flights
            if item["requested_time"]
            <= current_time
        ]

        # ---------------------------------------------
        # If no flight is available,
        # move time to next arrival
        # ---------------------------------------------

        if not ready_queue:

            current_time = min(
                item["requested_time"]
                for item in remaining_flights
            )

            continue

        # ---------------------------------------------
        # Calculate response ratio
        # ---------------------------------------------

        for item in ready_queue:

            waiting_time = (
                current_time
                - item["requested_time"]
            )

            waiting_time_minutes = (
                waiting_time.total_seconds()
                / 60
            )

            item["waiting_time_minutes"] = (
                waiting_time_minutes
            )

            item["response_ratio"] = (
                calculate_response_ratio(
                    waiting_time_minutes,
                    item["processing_time"]
                )
            )

        # ---------------------------------------------
        # Select highest response ratio
        #
        # Tie-breakers:
        # 1. Earlier requested time
        # 2. Smaller flight ID
        # ---------------------------------------------

        selected = max(
            ready_queue,
            key=lambda item: (
                item["response_ratio"],
                -item["requested_time"].timestamp(),
                -item["flight"]["flight_id"]
            )
        )

        # ---------------------------------------------
        # Remove selected flight
        # ---------------------------------------------

        remaining_flights.remove(
            selected
        )

        flight = selected["flight"]

        requested_time = (
            selected["requested_time"]
        )

        processing_time = (
            selected["processing_time"]
        )

        # ---------------------------------------------
        # Start time
        # ---------------------------------------------

        start_time = max(
            current_time,
            requested_time
        )

        # ---------------------------------------------
        # Waiting time
        # ---------------------------------------------

        waiting_time = (
            start_time
            - requested_time
        )

        waiting_time_minutes = (
            waiting_time.total_seconds()
            / 60
        )

        # ---------------------------------------------
        # Response ratio
        # ---------------------------------------------

        response_ratio = (
            calculate_response_ratio(
                waiting_time_minutes,
                processing_time
            )
        )

        # ---------------------------------------------
        # Completion time
        # ---------------------------------------------

        completion_time = (
            start_time
            + timedelta(
                minutes=processing_time
            )
        )

        # ---------------------------------------------
        # Turnaround time
        # ---------------------------------------------

        turnaround_time = (
            completion_time
            - requested_time
        )

        turnaround_time_minutes = (
            turnaround_time.total_seconds()
            / 60
        )

        # ---------------------------------------------
        # Response time
        #
        # HRRN is non-preemptive,
        # so response time = waiting time.
        # ---------------------------------------------

        response_time_minutes = (
            waiting_time_minutes
        )

        # ---------------------------------------------
        # Save result
        # ---------------------------------------------

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
                len(results) + 1,

            "start_time":
                start_time,

            "completion_time":
                completion_time,

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

            "response_ratio":
                round(
                    response_ratio,
                    2
                )
        })

        # ---------------------------------------------
        # Move scheduler clock
        # ---------------------------------------------

        current_time = completion_time

    return results