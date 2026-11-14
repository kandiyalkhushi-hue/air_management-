# scheduler/algorithms/fcfs.py


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


def fcfs_scheduling(flights):
    """
    First Come First Serve Scheduling.

    FCFS rule:
    The flight that arrives/requested scheduling first
    gets processed first.

    This function creates the OS ready queue and
    calculates basic scheduling metrics.

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


    # =====================================================
    # 1. SORT FLIGHTS BY ARRIVAL / REQUEST TIME
    # =====================================================

    sorted_flights = sorted(
        flights,
        key=lambda flight: (
            get_requested_time(flight),
            flight["flight_id"]
        )
    )


    # =====================================================
    # 2. CREATE READY QUEUE
    # =====================================================

    ready_queue = []

    for position, flight in enumerate(
        sorted_flights,
        start=1
    ):

        requested_time = get_requested_time(
            flight
        )

        processing_time = (
            flight.get(
                "processing_time_minutes"
            )
        )

        if processing_time is None:
            processing_time = 10


        ready_queue.append({

            "flight_id": (
                flight["flight_id"]
            ),

            "flight_number": (
                flight["flight_number"]
            ),

            "airport_id": (
                flight["airport_id"]
            ),

            "aircraft_id": (
                flight["aircraft_id"]
            ),

            "operation_type": (
                flight["operation_type"]
            ),

            "requested_time": (
                requested_time
            ),

            "processing_time": (
                processing_time
            ),

            "priority": (
                flight.get(
                    "priority",
                    0
                )
            ),

            "situation": (
                flight.get(
                    "current_situation",
                    "NORMAL"
                )
            ),

            "queue_position": position
        })


    # =====================================================
    # 3. CALCULATE SCHEDULING TIMES
    # =====================================================

    current_time = None


    for flight in ready_queue:

        requested_time = (
            flight["requested_time"]
        )

        processing_time = (
            flight["processing_time"]
        )


        # -------------------------------------------------
        # First flight
        # -------------------------------------------------

        if current_time is None:

            start_time = requested_time


        # -------------------------------------------------
        # If CPU/runway is free before next
        # flight arrives
        # -------------------------------------------------

        elif current_time < requested_time:

            start_time = requested_time


        # -------------------------------------------------
        # Otherwise flight waits
        # -------------------------------------------------

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
        #
        # Time spent waiting before execution
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
        #
        # Completion - Arrival/Request
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
        # First execution - Arrival/Request
        #
        # For non-preemptive FCFS:
        #
        # Response Time = Waiting Time
        # -------------------------------------------------

        response_time_minutes = (
            waiting_time_minutes
        )


        # -------------------------------------------------
        # Store calculated metrics
        # -------------------------------------------------

        flight["start_time"] = (
            start_time
        )

        flight["completion_time"] = (
            completion_time
        )

        flight["waiting_time_minutes"] = (
            round(
                waiting_time_minutes,
                2
            )
        )

        flight["turnaround_time_minutes"] = (
            round(
                turnaround_time_minutes,
                2
            )
        )

        flight["response_time_minutes"] = (
            round(
                response_time_minutes,
                2
            )
        )


        # -------------------------------------------------
        # Move current time forward
        # -------------------------------------------------

        current_time = completion_time


    return ready_queue