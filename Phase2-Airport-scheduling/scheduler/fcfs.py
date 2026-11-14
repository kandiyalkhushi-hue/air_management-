def fcfs_scheduling(flights):

    sorted_flights = sorted(
        flights,
        key=lambda flight: (
            flight["arrival_time"]
            if flight["operation_type"] == "ARRIVAL"
            else flight["departure_time"],
            flight["flight_id"]
        )
    )

    return sorted_flights