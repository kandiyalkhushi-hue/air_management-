# scheduler/metrics.py

def calculate_average_waiting_time(results):
    """
    Calculate average waiting time.
    """

    if not results:
        return 0

    total = sum(
        flight.get(
            "waiting_time_minutes",
            0
        )
        for flight in results
    )

    return round(
        total / len(results),
        2
    )


def calculate_average_turnaround_time(results):
    """
    Calculate average turnaround time.
    """

    if not results:
        return 0

    total = sum(
        flight.get(
            "turnaround_time_minutes",
            0
        )
        for flight in results
    )

    return round(
        total / len(results),
        2
    )


def calculate_average_response_time(results):
    """
    Calculate average response time.
    """

    if not results:
        return 0

    total = sum(
        flight.get(
            "response_time_minutes",
            0
        )
        for flight in results
    )

    return round(
        total / len(results),
        2
    )


def calculate_total_processing_time(results):
    """
    Calculate total processing/burst time.
    """

    return round(
        sum(
            flight.get(
                "processing_time",
                0
            )
            for flight in results
        ),
        2
    )


def calculate_throughput(
    results,
    total_time_minutes
):
    """
    Throughput =
        Number of completed flights
        / total execution time

    Result:
        flights per minute
    """

    if not results:
        return 0

    if total_time_minutes <= 0:
        return 0

    throughput = (
        len(results)
        / total_time_minutes
    )

    return round(
        throughput,
        4
    )


def calculate_runway_utilization(
    processing_time_minutes,
    total_time_minutes
):
    """
    Runway Utilization:

        Processing Time
        ---------------- × 100
        Total Time

    Returns percentage.
    """

    if total_time_minutes <= 0:
        return 0

    utilization = (
        processing_time_minutes
        / total_time_minutes
    ) * 100

    return round(
        utilization,
        2
    )


def calculate_total_execution_time(
    results
):
    """
    Calculate total scheduling execution
    time from first start to last completion.
    """

    if not results:
        return 0

    start_times = [
        flight["start_time"]
        for flight in results
        if flight.get("start_time")
    ]

    completion_times = [
        flight["completion_time"]
        for flight in results
        if flight.get("completion_time")
    ]

    if not start_times or not completion_times:
        return 0

    start_time = min(start_times)
    completion_time = max(completion_times)

    duration = (
        completion_time
        - start_time
    )

    return round(
        duration.total_seconds() / 60,
        2
    )


def calculate_metrics(results):
    """
    Calculate all common scheduling metrics.

    Returns a standard dictionary that can be
    used by every scheduling algorithm.
    """

    if not results:

        return {
            "total_flights": 0,
            "average_waiting_time": 0,
            "average_turnaround_time": 0,
            "average_response_time": 0,
            "total_processing_time": 0,
            "total_execution_time": 0,
            "throughput": 0,
            "runway_utilization": 0
        }

    total_processing_time = (
        calculate_total_processing_time(
            results
        )
    )

    total_execution_time = (
        calculate_total_execution_time(
            results
        )
    )

    average_waiting_time = (
        calculate_average_waiting_time(
            results
        )
    )

    average_turnaround_time = (
        calculate_average_turnaround_time(
            results
        )
    )

    average_response_time = (
        calculate_average_response_time(
            results
        )
    )

    throughput = calculate_throughput(
        results,
        total_execution_time
    )

    runway_utilization = (
        calculate_runway_utilization(
            total_processing_time,
            total_execution_time
        )
    )

    return {

        "total_flights":
            len(results),

        "average_waiting_time":
            average_waiting_time,

        "average_turnaround_time":
            average_turnaround_time,

        "average_response_time":
            average_response_time,

        "total_processing_time":
            total_processing_time,

        "total_execution_time":
            total_execution_time,

        "throughput":
            throughput,

        "runway_utilization":
            runway_utilization
    }