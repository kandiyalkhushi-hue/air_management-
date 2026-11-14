# scheduler/algorithms/sjf.py

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


def sjf_scheduling(flights):
    """
    Shortest Job First Scheduling.

    SJF rule:
    Among the available flights, the flight with
    the shortest processing time is selected first.

    This is NON-PREEMPTIVE SJF.

    Once a flight starts processing, it continues
    until completion.

    Metrics:
        - queue_position
        - start_time
        - completion_time
        - waiting_time
        - turnaround_time
        - response_time
    """

    if not flights:
        return []

    # Copy flights so original data is not modified
    remaining_flights = list(flights)

    ready_queue = []

    current_time = None

    while remaining_flights:

        # -------------------------------------------------
        # Find flights that are available at current time
        # -------------------------------------------------

        if current_time is None:

            earliest_time = min(
                get_requested_time(flight)
                for flight in remaining_flights
            )

            current_time = earliest_time

        available_flights = []

        for flight in remaining_flights:

            requested_time = get_requested_time(
                flight
            )

            if requested_time <= current_time:
                available_flights.append(
                    flight
                )

        # -------------------------------------------------
        # If no flight is available yet,
        # jump current time to next flight
        # -------------------------------------------------

        if not available_flights:

            current_time = min(
                get_requested_time(flight)
                for flight in remaining_flights
            )

            continue

        # -------------------------------------------------
        # SJF selection
        #
        # Shortest processing time first.
        #
        # If processing time is same:
        # 1. Earlier requested time
        # 2. Smaller flight ID
        # -------------------------------------------------

        selected_flight = min(
            available_flights,
            key=lambda flight: (
                flight.get(
                    "processing_time_minutes"
                )
                if flight.get(
                    "processing_time_minutes"
                ) is not None
                else 10,

                get_requested_time(
                    flight
                ),

                flight["flight_id"]
            )
        )

        remaining_flights.remove(
            selected_flight
        )

        # -------------------------------------------------
        # Flight information
        # -------------------------------------------------

        requested_time = get_requested_time(
            selected_flight
        )

        processing_time = (
            selected_flight.get(
                "processing_time_minutes"
            )
        )

        if processing_time is None:
            processing_time = 10

        # -------------------------------------------------
        # Start time
        # -------------------------------------------------

        if current_time < requested_time:
            start_time = requested_time
        else:
            start_time = current_time

        # -------------------------------------------------
        # Completion time
        # -------------------------------------------------

        from datetime import timedelta

        completion_time = (
            start_time
            + timedelta(
                minutes=processing_time
            )
        )

        # -------------------------------------------------
        # Waiting Time
        # -------------------------------------------------

        waiting_time = (
            start_time
            - requested_time
        )

        waiting_time_minutes = (
            waiting_time.total_seconds()
            / 60
        )

        # -------------------------------------------------
        # Turnaround Time
        # -------------------------------------------------

        turnaround_time = (
            completion_time
            - requested_time
        )

        turnaround_time_minutes = (
            turnaround_time.total_seconds()
            / 60
        )

        # -------------------------------------------------
        # Response Time
        #
        # For non-preemptive SJF:
        #
        # Response Time = Waiting Time
        # -------------------------------------------------

        response_time_minutes = (
            waiting_time_minutes
        )

        # -------------------------------------------------
        # Add to ready queue
        # -------------------------------------------------

        ready_queue.append({

            "flight_id":
                selected_flight["flight_id"],

            "flight_number":
                selected_flight["flight_number"],

            "airport_id":
                selected_flight["airport_id"],

            "aircraft_id":
                selected_flight["aircraft_id"],

            "operation_type":
                selected_flight["operation_type"],

            "requested_time":
                requested_time,

            "processing_time":
                processing_time,

            "priority":
                selected_flight.get(
                    "priority",
                    0
                ),

            "situation":
                selected_flight.get(
                    "current_situation",
                    "NORMAL"
                ),

            "queue_position":
                len(ready_queue) + 1,

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
                )
        })

        # -------------------------------------------------
        # Move CPU/scheduler clock forward
        # -------------------------------------------------

        current_time = completion_time

    return ready_queue