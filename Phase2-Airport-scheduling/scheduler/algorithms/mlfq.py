# scheduler/algorithms/mlfq.py

from collections import deque
from datetime import timedelta


# -------------------------------------------------
# MLFQ configuration
# -------------------------------------------------

QUEUE_0_QUANTUM = 2
QUEUE_1_QUANTUM = 4
QUEUE_2_QUANTUM = 8


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


def get_initial_queue(flight):
    """
    Determine the initial MLFQ queue.

    Special situations start with higher priority.

    Queue 0 -> Emergency / Medical
    Queue 1 -> Low Fuel / Weather / VIP
    Queue 2 -> Normal
    """

    situation = (
        flight.get(
            "current_situation",
            "NORMAL"
        )
        or "NORMAL"
    ).upper()

    if situation in (
        "EMERGENCY",
        "MEDICAL"
    ):
        return 0

    if situation in (
        "LOW_FUEL",
        "WEATHER",
        "VIP"
    ):
        return 1

    return 2


def mlfq_scheduling(flights):
    """
    Multilevel Feedback Queue Scheduling.

    Queues:

        Queue 0 -> Highest priority
        Queue 1 -> Medium priority
        Queue 2 -> Lowest priority

    Time Quantums:

        Queue 0 -> 2 minutes
        Queue 1 -> 4 minutes
        Queue 2 -> 8 minutes

    Rules:

        1. New flights enter according to situation.
        2. Higher queue always gets preference.
        3. A flight gets the quantum of its queue.
        4. If it does not finish within the quantum,
           it is moved to the next lower queue.
        5. Completed flights leave the system.
        6. Queue movement demonstrates feedback.
        7. Response time is measured from first execution.
    """

    if not flights:
        return []

    # -------------------------------------------------
    # Prepare flight information
    # -------------------------------------------------

    flight_data = []

    for flight in flights:

        requested_time = get_requested_time(
            flight
        )

        processing_time = get_processing_time(
            flight
        )

        initial_queue = get_initial_queue(
            flight
        )

        flight_data.append({

            "flight": flight,

            "requested_time":
                requested_time,

            "processing_time":
                processing_time,

            "remaining_time":
                processing_time,

            "current_queue":
                initial_queue,

            "first_start_time":
                None,

            "completion_time":
                None,

            "preemptions":
                0,

            "queue_movements":
                0,

            "execution_slices":
                [],

            "turn_number":
                0
        })

    # -------------------------------------------------
    # Sort according to arrival/request time
    # -------------------------------------------------

    flight_data.sort(
        key=lambda item: (
            item["requested_time"],
            item["flight"]["flight_id"]
        )
    )

    # -------------------------------------------------
    # Create three feedback queues
    # -------------------------------------------------

    queues = {
        0: deque(),
        1: deque(),
        2: deque()
    }

    current_time = flight_data[0][
        "requested_time"
    ]

    next_index = 0
    completed = []

    # -------------------------------------------------
    # Add flights that have already arrived
    # -------------------------------------------------

    while (
        next_index < len(flight_data)
        and flight_data[next_index][
            "requested_time"
        ] <= current_time
    ):

        item = flight_data[next_index]

        queues[
            item["current_queue"]
        ].append(item)

        next_index += 1

    # -------------------------------------------------
    # Main MLFQ loop
    # -------------------------------------------------

    while len(completed) < len(
        flight_data
    ):

        # ---------------------------------------------
        # Add newly arrived flights
        # ---------------------------------------------

        while (
            next_index < len(flight_data)
            and flight_data[next_index][
                "requested_time"
            ] <= current_time
        ):

            item = flight_data[next_index]

            queues[
                item["current_queue"]
            ].append(item)

            next_index += 1

        # ---------------------------------------------
        # Find highest non-empty queue
        # ---------------------------------------------

        selected = None

        for queue_level in range(3):

            if queues[queue_level]:

                selected = queues[
                    queue_level
                ].popleft()

                break

        # ---------------------------------------------
        # If no flight is available,
        # jump to next arrival
        # ---------------------------------------------

        if selected is None:

            if next_index < len(flight_data):

                current_time = max(
                    current_time,
                    flight_data[next_index][
                        "requested_time"
                    ]
                )

                continue

            break

        # ---------------------------------------------
        # First response/start time
        # ---------------------------------------------

        if (
            selected["first_start_time"]
            is None
        ):

            selected[
                "first_start_time"
            ] = current_time

        # ---------------------------------------------
        # Quantum based on queue
        # ---------------------------------------------

        queue_level = selected[
            "current_queue"
        ]

        if queue_level == 0:

            quantum = QUEUE_0_QUANTUM

        elif queue_level == 1:

            quantum = QUEUE_1_QUANTUM

        else:

            quantum = QUEUE_2_QUANTUM

        # ---------------------------------------------
        # Determine execution time
        # ---------------------------------------------

        execution_time = min(
            quantum,
            selected["remaining_time"]
        )

        execution_end = (
            current_time
            + timedelta(
                minutes=execution_time
            )
        )

        selected["turn_number"] += 1
        selected["execution_slices"].append({
            "turn_number": selected["turn_number"],
            "start_time": current_time,
            "end_time": execution_end,
            "duration_minutes": round(execution_time, 2),
            "remaining_time_minutes": round(
                selected["remaining_time"] - execution_time, 2
            ),
            "completed": selected["remaining_time"] <= execution_time
        })

        # ---------------------------------------------
        # Execute flight
        # ---------------------------------------------

        selected["remaining_time"] -= (
            execution_time
        )

        current_time = execution_end

        # ---------------------------------------------
        # Add newly arrived flights
        # ---------------------------------------------

        while (
            next_index < len(flight_data)
            and flight_data[next_index][
                "requested_time"
            ] <= current_time
        ):

            new_flight = flight_data[
                next_index
            ]

            queues[
                new_flight["current_queue"]
            ].append(new_flight)

            next_index += 1

        # ---------------------------------------------
        # Flight completed
        # ---------------------------------------------

        if selected["remaining_time"] <= 0:

            selected["remaining_time"] = 0

            selected[
                "completion_time"
            ] = current_time

            completed.append(
                selected
            )

        # ---------------------------------------------
        # Flight did not complete
        #
        # Feedback:
        # Move it to lower queue.
        # ---------------------------------------------

        else:

            selected["preemptions"] += 1

            old_queue = selected[
                "current_queue"
            ]

            if old_queue < 2:

                selected[
                    "current_queue"
                ] = old_queue + 1

                selected[
                    "queue_movements"
                ] += 1

            queues[
                selected["current_queue"]
            ].append(selected)

    # -------------------------------------------------
    # Build final results
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

        processing_time = (
            item["processing_time"]
        )

        start_time = (
            item["first_start_time"]
        )

        completion_time = (
            item["completion_time"]
        )

        # ---------------------------------------------
        # Turnaround Time
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
        # Waiting Time
        # ---------------------------------------------

        waiting_time_minutes = (
            turnaround_time_minutes
            - processing_time
        )

        # ---------------------------------------------
        # Response Time
        # ---------------------------------------------

        response_time = (
            start_time
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

            "initial_queue":
                get_initial_queue(
                    flight
                ),

            "final_queue":
                item["current_queue"],

            "queue_position":
                position,

            "start_time":
                start_time,

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
                item["preemptions"],

            "queue_movements":
                item["queue_movements"]
        })

    return results