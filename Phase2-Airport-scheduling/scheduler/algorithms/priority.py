from datetime import timedelta

from scheduler.algorithms.common import (
    get_processing_time,
    get_requested_time
)


def priority_scheduling(flights):
    """Run non-preemptive priority scheduling."""
    remaining = [
        {
            "flight": flight,
            "requested_time": get_requested_time(flight),
            "processing_time": get_processing_time(flight)
        }
        for flight in flights
    ]
    results = []
    current_time = min(
        (item["requested_time"] for item in remaining),
        default=None
    )

    while remaining:
        available = [
            item for item in remaining
            if item["requested_time"] <= current_time
        ]
        if not available:
            current_time = min(
                item["requested_time"] for item in remaining
            )
            continue

        selected = min(
            available,
            key=lambda item: (
                item["flight"].get("situation_priority", 6),
                item["flight"].get("priority", 999),
                item["requested_time"],
                item["flight"]["flight_id"]
            )
        )
        remaining.remove(selected)

        flight = selected["flight"]
        requested_time = selected["requested_time"]
        processing_time = selected["processing_time"]
        start_time = max(current_time, requested_time)
        end_time = start_time + timedelta(minutes=processing_time)
        waiting_time = (start_time - requested_time).total_seconds() / 60
        turnaround_time = (end_time - requested_time).total_seconds() / 60

        results.append({
            **flight,
            "flight_id": flight["flight_id"],
            "flight_number": flight["flight_number"],
            "requested_time": requested_time,
            "processing_time": processing_time,
            "start_time": start_time,
            "end_time": end_time,
            "completion_time": end_time,
            "queue_position": len(results) + 1,
            "waiting_time_minutes": round(waiting_time, 2),
            "turnaround_time_minutes": round(turnaround_time, 2),
            "response_time_minutes": round(waiting_time, 2)
        })
        current_time = end_time

    return results
