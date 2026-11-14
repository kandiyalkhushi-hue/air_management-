from datetime import date, datetime, timedelta
import math


def parse_datetime(value, flight, field_name):
    flight_label = (
        flight.get("flight_number")
        or flight.get("flight_id")
        or "unknown"
    )

    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, datetime.min.time())
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(
                value.strip().replace("Z", "+00:00")
            )
        except ValueError as error:
            raise ValueError(
                f"Invalid {field_name} for flight {flight_label}: {value!r}"
            ) from error
    else:
        raise ValueError(
            f"Missing or invalid {field_name} for flight {flight_label}"
        )

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone().replace(tzinfo=None)

    return parsed


def get_requested_time(flight):
    operation = str(
        flight.get("operation_type") or ""
    ).strip().upper()

    if operation == "ARRIVAL":
        field_name = "arrival_time"
    elif operation == "DEPARTURE":
        field_name = "departure_time"
    else:
        raise ValueError(
            f"Invalid operation_type for flight "
            f"{flight.get('flight_number') or flight.get('flight_id')}: "
            f"{operation or 'missing'}"
        )

    return parse_datetime(
        flight.get(field_name),
        flight,
        field_name
    )


def get_processing_time(flight):
    value = flight.get("processing_time_minutes")
    if value is None:
        value = 10

    try:
        processing_time = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Invalid processing time for flight "
            f"{flight.get('flight_number') or flight.get('flight_id')}: "
            f"{value!r}"
        ) from error

    if not math.isfinite(processing_time) or processing_time <= 0:
        raise ValueError(
            f"Processing time must be a positive finite number for flight "
            f"{flight.get('flight_number') or flight.get('flight_id')}"
        )

    return processing_time


def prepare_flight(flight):
    prepared = dict(flight)
    prepared["operation_type"] = str(
        prepared.get("operation_type") or ""
    ).strip().upper()
    requested_time = get_requested_time(prepared)
    requested_time_field = (
        "arrival_time"
        if prepared["operation_type"] == "ARRIVAL"
        else "departure_time"
    )
    prepared[requested_time_field] = requested_time
    prepared["processing_time_minutes"] = get_processing_time(prepared)
    return prepared


def normalize_results(results, flights):
    flights_by_id = {
        flight.get("flight_id"): flight
        for flight in flights
    }
    current_time = None

    for position, result in enumerate(results, start=1):
        flight = flights_by_id.get(result.get("flight_id"))
        if flight is None:
            raise ValueError(
                f"Algorithm returned unknown flight "
                f"{result.get('flight_id')!r}"
            )

        requested_time = get_requested_time(flight)
        processing_time = get_processing_time(flight)
        start_time = result.get("start_time")

        if start_time is None:
            start_time = max(
                requested_time,
                current_time or requested_time
            )
        else:
            start_time = parse_datetime(
                start_time,
                flight,
                "start_time"
            )

        if start_time < requested_time:
            raise ValueError(
                f"Scheduling start time precedes request time for flight "
                f"{flight.get('flight_number') or flight.get('flight_id')}"
            )

        end_time = result.get("end_time")
        if end_time is None:
            end_time = result.get("completion_time")
        if end_time is None:
            end_time = start_time + timedelta(minutes=processing_time)
        else:
            end_time = parse_datetime(end_time, flight, "end_time")

        if end_time <= start_time:
            raise ValueError(
                f"Scheduling end time must be after start time for flight "
                f"{flight.get('flight_number') or flight.get('flight_id')}"
            )

        result.update({
            "flight_id": flight.get("flight_id"),
            "flight_number": flight.get("flight_number"),
            "requested_time": requested_time,
            "start_time": start_time,
            "end_time": end_time,
            "completion_time": end_time,
            "processing_time": processing_time,
            "queue_position": result.get("queue_position", position)
        })

        slices = result.get("execution_slices")
        if slices:
            for execution_slice in slices:
                execution_slice["start_time"] = parse_datetime(
                    execution_slice.get("start_time"),
                    flight,
                    "execution slice start_time"
                )
                execution_slice["end_time"] = parse_datetime(
                    execution_slice.get("end_time"),
                    flight,
                    "execution slice end_time"
                )
                if execution_slice["end_time"] <= execution_slice["start_time"]:
                    raise ValueError(
                        f"Invalid execution slice for flight "
                        f"{flight.get('flight_number') or flight.get('flight_id')}"
                    )

        current_time = max(current_time or end_time, end_time)

    return results
