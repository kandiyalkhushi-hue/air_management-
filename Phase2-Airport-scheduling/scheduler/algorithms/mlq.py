# scheduler/algorithms/mlq.py

from datetime import timedelta


# -------------------------------------------------
# Queue levels
# -------------------------------------------------

QUEUE_PRIORITY = {
    "EMERGENCY": 1,
    "MEDICAL": 1,
    "LOW_FUEL": 2,
    "WEATHER": 3,
    "VIP": 4,
    "NORMAL": 5
}


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
    Get processing time.

    Default = 10 minutes.
    """

    processing_time = flight.get(
        "processing_time_minutes"
    )

    if processing_time is None:
        processing_time = 10

    return processing_time


def get_queue_level(flight):
    """
    Determine the fixed MLQ queue
    based on flight situation.
    """

    situation = (
        flight.get(
            "current_situation",
            "NORMAL"
        )
        or "NORMAL"
    ).upper()

    return QUEUE_PRIORITY.get(
        situation,
        5
    )


def mlq_scheduling(flights):
    """
    Multilevel Queue Scheduling.

    Queues:

        Queue 1 -> Emergency / Medical
        Queue 2 -> Low Fuel
        Queue 3 -> Weather
        Queue 4 -> VIP
        Queue 5 -> Normal

    Higher queue gets higher priority.

    Scheduling inside each queue:
        FCFS

    MLQ is NON-PREEMPTIVE in this implementation.

    Important:
        A flight remains in the queue assigned
        to it. It does not move between queues.

    Metrics:
        - queue_level
        - queue_position
        - start_time
        - completion_time
        - waiting_time
        - turnaround_time
        - response_time
    """

    if not flights:
        return []

    # -------------------------------------------------
    # Create five fixed queues
    # -------------------------------------------------

    queues = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: []
    }

    # -------------------------------------------------
    # Put each flight into its queue
    # -------------------------------------------------

    for flight in flights:

        requested_time = get_requested_time(
            flight
        )

        processing_time = get_processing_time(
            flight
        )

        queue_level = get_queue_level(
            flight
        )

        queues[queue_level].append({

            "flight": flight,

            "requested_time":
                requested_time,

            "processing_time":
                processing_time,

            "queue_level":
                queue_level
        })

    # -------------------------------------------------
    # FCFS inside each individual queue
    # -------------------------------------------------

    for queue_level in queues:

        queues[queue_level].sort(
            key=lambda item: (
                item["requested_time"],
                item["flight"]["flight_id"]
            )
        )

    # -------------------------------------------------
    # Scheduler starts at earliest request time
    # -------------------------------------------------

    all_items = []

    for queue in queues.values():
        all_items.extend(queue)

    if not all_items:
        return []

    current_time = min(
        item["requested_time"]
        for item in all_items
    )

    results = []

    # -------------------------------------------------
    # Process queues from highest priority
    # to lowest priority
    # -------------------------------------------------

    for queue_level in range(1, 6):

        queue = queues[queue_level]

        for item in queue:

            flight = item["flight"]

            requested_time = (
                item["requested_time"]
            )

            processing_time = (
                item["processing_time"]
            )

            # -----------------------------------------
            # If flight has not arrived yet,
            # scheduler waits for it.
            # -----------------------------------------

            if current_time < requested_time:

                current_time = requested_time

            # -----------------------------------------
            # Start time
            # -----------------------------------------

            start_time = current_time

            # -----------------------------------------
            # Waiting time
            # -----------------------------------------

            waiting_time = (
                start_time
                - requested_time
            )

            waiting_time_minutes = (
                waiting_time.total_seconds()
                / 60
            )

            # -----------------------------------------
            # Completion time
            # -----------------------------------------

            completion_time = (
                start_time
                + timedelta(
                    minutes=processing_time
                )
            )

            # -----------------------------------------
            # Turnaround time
            # -----------------------------------------

            turnaround_time = (
                completion_time
                - requested_time
            )

            turnaround_time_minutes = (
                turnaround_time.total_seconds()
                / 60
            )

            # -----------------------------------------
            # Response time
            #
            # Non-preemptive:
            # response = waiting
            # -----------------------------------------

            response_time_minutes = (
                waiting_time_minutes
            )

            # -----------------------------------------
            # Save result
            # -----------------------------------------

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

                "queue_level":
                    queue_level,

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
                    )
            })

            # -----------------------------------------
            # Move scheduler clock
            # -----------------------------------------

            current_time = completion_time

    return results