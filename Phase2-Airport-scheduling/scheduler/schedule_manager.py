# scheduler/schedule_manager.py

from database import get_db_connection


def create_scheduler_run(
    algorithm,
    total_flights=0
):
    """
    Create a new scheduler run.

    One scheduler run represents one execution
    of an OS scheduling algorithm.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        query = """
            INSERT INTO scheduler_runs
            (
                algorithm,
                status,
                total_flights
            )
            VALUES
            (
                %s,
                'RUNNING',
                %s
            )
        """

        cursor.execute(
            query,
            (
                algorithm,
                total_flights
            )
        )

        connection.commit()

        return cursor.lastrowid

    finally:

        cursor.close()
        connection.close()


def is_runway_free(
    runway_id,
    scheduled_start,
    scheduled_end,
    flight_id=None
):
    """
    Check whether a runway is free during
    the requested scheduling interval. A flight's own SCHEDULED records
    from terminal runs do not block rescheduling; active and other-flight
    records remain conflicts.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        query = """
            SELECT COUNT(*)
            FROM schedules s
            LEFT JOIN scheduler_runs sr
                ON sr.run_id = s.run_id
            WHERE s.runway_id = %s

            AND s.status IN (
                'SCHEDULED',
                'IN_PROGRESS'
            )

            AND s.scheduled_start < %s
            AND s.scheduled_end > %s
        """

        parameters = [
            runway_id,
            scheduled_end,
            scheduled_start
        ]

        if flight_id is not None:
            query += """
                AND (
                    s.flight_id <> %s
                    OR s.status = 'IN_PROGRESS'
                    OR sr.status NOT IN ('COMPLETED', 'FAILED')
                    OR sr.status IS NULL
                )
            """
            parameters.append(flight_id)

        cursor.execute(query, tuple(parameters))

        count = cursor.fetchone()[0]

        return count == 0

    finally:

        cursor.close()
        connection.close()


def save_schedule(
    run_id,
    flight,
    runway,
    atc,
    situation,
    algorithm,
    queue_position,
    scheduled_start,
    scheduled_end=None,
    waiting_time_minutes=0,
    turnaround_time_minutes=0,
    response_time_minutes=0
):
    """
    Save one scheduled flight into schedules table.

    This function is now generic and can be used
    by all scheduling algorithms.
    """

    from datetime import timedelta

    # ---------------------------------------------
    # Processing time
    # ---------------------------------------------

    processing_time = (
        flight.get(
            "processing_time_minutes"
        )
    )

    if processing_time is None:
        processing_time = 10

    # ---------------------------------------------
    # Calculate end time
    # ---------------------------------------------

    if scheduled_end is None:
        scheduled_end = scheduled_start + timedelta(
            minutes=processing_time
        )

    # ---------------------------------------------
    # Database connection
    # ---------------------------------------------

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        query = """
            INSERT INTO schedules
            (
                run_id,
                flight_id,
                runway_id,
                atc_id,
                algorithm,
                situation,
                queue_position,
                scheduled_start,
                scheduled_end,
                waiting_time_minutes,
                turnaround_time_minutes,
                response_time_minutes,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'SCHEDULED'
            )
        """

        cursor.execute(
            query,
            (
                run_id,

                flight["flight_id"],

                runway["runway_id"],

                atc["atc_id"],

                algorithm,

                situation,

                queue_position,

                scheduled_start,

                scheduled_end,

                waiting_time_minutes,

                turnaround_time_minutes,

                response_time_minutes
            )
        )

        schedule_id = (
            cursor.lastrowid
        )

        connection.commit()

        return {

            "schedule_id":
                schedule_id,

            "scheduled_start":
                scheduled_start,

            "scheduled_end":
                scheduled_end,

            "waiting_time_minutes":
                waiting_time_minutes,

            "turnaround_time_minutes":
                turnaround_time_minutes,

            "response_time_minutes":
                response_time_minutes
        }

    finally:

        cursor.close()
        connection.close()


def update_flight_status(
    flight_id,
    status
):
    """
    Update lifecycle status of a flight.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        query = """
            UPDATE flights
            SET status = %s
            WHERE flight_id = %s
        """

        cursor.execute(
            query,
            (
                status,
                flight_id
            )
        )

        connection.commit()

    finally:

        cursor.close()
        connection.close()


def update_flight_situation(
    flight_id,
    situation
):
    """
    Update the current situation of a flight.

    Examples:
        NORMAL
        EMERGENCY
        LOW_FUEL
        MEDICAL
        WEATHER
        VIP
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        query = """
            UPDATE flights
            SET current_situation = %s
            WHERE flight_id = %s
        """

        cursor.execute(
            query,
            (
                situation,
                flight_id
            )
        )

        connection.commit()

    finally:

        cursor.close()
        connection.close()


def update_scheduler_run_metrics(
    run_id,
    average_waiting_time,
    average_turnaround_time,
    average_response_time,
    throughput,
    runway_utilization
):
    """
    Save calculated scheduling metrics
    into scheduler_runs.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        query = """
            UPDATE scheduler_runs
            SET
                average_waiting_time = %s,
                average_turnaround_time = %s,
                average_response_time = %s,
                throughput = %s,
                runway_utilization = %s
            WHERE run_id = %s
        """

        cursor.execute(
            query,
            (
                average_waiting_time,
                average_turnaround_time,
                average_response_time,
                throughput,
                runway_utilization,
                run_id
            )
        )

        connection.commit()

    finally:

        cursor.close()
        connection.close()


def complete_scheduler_run(
    run_id,
    total_flights,
    status="COMPLETED"
):
    """
    Mark scheduler run as completed or failed.
    """

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        query = """
            UPDATE scheduler_runs
            SET
                status = %s,
                completed_at = NOW(),
                total_flights = %s
            WHERE run_id = %s
        """

        cursor.execute(
            query,
            (
                status,
                total_flights,
                run_id
            )
        )

        connection.commit()

    finally:

        cursor.close()
        connection.close()

        
def get_all_schedules():
    """
    Fetch saved schedules with flight, airport, runway,
    and ATC details for the schedules dashboard.
    """

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                s.schedule_id,
                s.run_id,
                s.flight_id,
                s.runway_id,
                s.atc_id,
                s.algorithm,
                s.situation,
                s.queue_position,
                s.scheduled_start,
                s.scheduled_end,
                s.waiting_time_minutes,
                s.turnaround_time_minutes,
                s.response_time_minutes,
                s.status,

                f.flight_number,
                f.operation_type,
                f.airport_id,
                f.status AS flight_status,

                a.airport_name,
                a.airport_code,

                r.runway_code,
                r.runway_type,

                c.employee_code,
                c.controller_name

            FROM schedules s

            LEFT JOIN flights f
                ON s.flight_id = f.flight_id

            LEFT JOIN airports a
                ON f.airport_id = a.airport_id

            LEFT JOIN runways r
                ON s.runway_id = r.runway_id

            LEFT JOIN atc_controllers c
    ON s.atc_id = c.atc_id

            ORDER BY s.scheduled_start ASC
        """

        cursor.execute(query)
        schedules = cursor.fetchall()

        for schedule in schedules:
            for key, value in schedule.items():
                if hasattr(value, "isoformat"):
                    schedule[key] = value.isoformat()

        return schedules

    finally:
        cursor.close()
        connection.close()
