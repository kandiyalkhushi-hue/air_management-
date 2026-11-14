
# scheduler/algorithms/round_robin.py

from collections import deque
from datetime import datetime, timedelta


def get_requested_time(flight):
    """
    Get the time at which the flight enters the ready queue.
    """

    operation = str(
        flight.get("operation_type") or ""
    ).strip().upper()

    requested_time = (
        flight.get("arrival_time")
        if operation == "ARRIVAL"
        else flight.get("departure_time")
    )

    if requested_time is None:
        raise ValueError(
            f"Missing requested time for flight "
            f"{flight.get('flight_id')}"
        )

    if isinstance(requested_time, str):
        try:
            requested_time = datetime.fromisoformat(
                requested_time.strip().replace("Z", "+00:00")
            )
        except ValueError as error:
            raise ValueError(
                f"Invalid requested time for flight "
                f"{flight.get('flight_id')}: {requested_time}"
            ) from error

    if not isinstance(requested_time, datetime):
        raise ValueError(
            f"Unsupported requested time for flight "
            f"{flight.get('flight_id')}"
        )

    if requested_time.tzinfo is not None:
        requested_time = requested_time.astimezone().replace(
            tzinfo=None
        )

    return requested_time


def get_processing_time(flight):
    """
    Get positive processing time in minutes.
    Default = 10 minutes.
    """

    processing_time = flight.get(
        "processing_time_minutes"
    )

    if processing_time is None:
        processing_time = 10

    try:
        processing_time = float(processing_time)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Invalid processing time for flight "
            f"{flight.get('flight_id')}"
        ) from error

    if processing_time <= 0:
        raise ValueError(
            f"Processing time must be greater than zero for flight "
            f"{flight.get('flight_id')}"
        )

    return processing_time


def round_robin_scheduling(flights, time_quantum=3):
    """
    Round Robin scheduling simulation.

    Every execution slice is stored in execution_slices.

    Each slice contains:
        - turn_number
        - start_time
        - end_time
        - duration_minutes
        - remaining_time_minutes
        - completed

    Existing scheduling metrics are also returned.
    """

    if not flights:
        return []

    try:
        time_quantum = float(time_quantum)
    except (TypeError, ValueError) as error:
        raise ValueError(
            "Time quantum must be a positive number"
        ) from error

    if time_quantum <= 0:
        raise ValueError(
            "Time quantum must be greater than zero"
        )

    # -------------------------------------------------
    # 1. Prepare flight data
    # -------------------------------------------------

    flight_data = []

    for flight in flights:
        requested_time = get_requested_time(flight)
        processing_time = get_processing_time(flight)

        flight_data.append({
            "flight": flight,
            "requested_time": requested_time,
            "processing_time": processing_time,
            "remaining_time": processing_time,
            "first_start_time": None,
            "completion_time": None,
            "preemptions": 0,
            "execution_slices": [],
            "turn_number": 0
        })

    flight_data.sort(
        key=lambda item: (
            item["requested_time"],
            str(item["flight"].get("flight_id", ""))
        )
    )

    # -------------------------------------------------
    # 2. Initialize ready queue
    # -------------------------------------------------

    ready_queue = deque()

    current_time = flight_data[0]["requested_time"]

    next_index = 0
    completed = []

    while (
        next_index < len(flight_data)
        and flight_data[next_index]["requested_time"] <= current_time
    ):
        ready_queue.append(flight_data[next_index])
        next_index += 1

    # -------------------------------------------------
    # 3. Run Round Robin simulation
    # -------------------------------------------------

    while ready_queue or next_index < len(flight_data):

        # If no flight is ready, jump to the next request time.
        if not ready_queue:
            current_time = max(
                current_time,
                flight_data[next_index]["requested_time"]
            )

            while (
                next_index < len(flight_data)
                and flight_data[next_index]["requested_time"] <= current_time
            ):
                ready_queue.append(flight_data[next_index])
                next_index += 1

        current_flight = ready_queue.popleft()

        if current_flight["first_start_time"] is None:
            current_flight["first_start_time"] = current_time

        execution_start = current_time

        execution_time = min(
            time_quantum,
            current_flight["remaining_time"]
        )

        execution_end = execution_start + timedelta(
            minutes=execution_time
        )

        # Admit new flights arriving during this time slice.
        while (
            next_index < len(flight_data)
            and flight_data[next_index]["requested_time"] <= execution_end
        ):
            ready_queue.append(flight_data[next_index])
            next_index += 1

        # Execute the current flight for one quantum.
        current_flight["remaining_time"] = max(
            0.0,
            current_flight["remaining_time"] - execution_time
        )

        current_flight["turn_number"] += 1

        # Save this exact execution turn.
        current_flight["execution_slices"].append({
            "turn_number": current_flight["turn_number"],
            "start_time": execution_start,
            "end_time": execution_end,
            "duration_minutes": round(execution_time, 2),
            "remaining_time_minutes": round(
                current_flight["remaining_time"], 2
            ),
            "completed": current_flight["remaining_time"] <= 0
        })

        current_time = execution_end

        if current_flight["remaining_time"] <= 0:
            current_flight["completion_time"] = current_time
            completed.append(current_flight)
        else:
            current_flight["preemptions"] += 1
            ready_queue.append(current_flight)

    # -------------------------------------------------
    # 4. Build final flight results
    # -------------------------------------------------

    results = []

    # Preserve completion order for the final flight result list.
    for position, item in enumerate(completed, start=1):
        flight = item["flight"]

        requested_time = item["requested_time"]
        processing_time = item["processing_time"]
        start_time = item["first_start_time"]
        completion_time = item["completion_time"]

        turnaround_minutes = (
            completion_time - requested_time
        ).total_seconds() / 60

        waiting_minutes = (
            turnaround_minutes - processing_time
        )

        response_minutes = (
            start_time - requested_time
        ).total_seconds() / 60

        results.append({
            "flight_id": flight.get("flight_id"),
            "flight_number": flight.get("flight_number"),
            "airport_id": flight.get("airport_id"),
            "aircraft_id": flight.get("aircraft_id"),
            "operation_type": flight.get("operation_type"),

            "requested_time": requested_time,
            "processing_time": processing_time,

            "priority": flight.get("priority", 0),
            "situation": flight.get(
                "current_situation", "NORMAL"
            ),

            "queue_position": position,

            "start_time": start_time,
            "completion_time": completion_time,

            "waiting_time_minutes": round(
                waiting_minutes, 2
            ),
            "turnaround_time_minutes": round(
                turnaround_minutes, 2
            ),
            "response_time_minutes": round(
                response_minutes, 2
            ),

            "preemptions": item["preemptions"],

            # IMPORTANT: all execution turns are returned.
            "execution_slices": item["execution_slices"]
        })

    return results
