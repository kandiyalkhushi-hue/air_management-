# scheduler/atc_allocator.py

from database import get_db_connection


def get_available_atc(
    airport_id,
    scheduled_start=None,
    scheduled_end=None
):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        query = """
            SELECT
                atc_id,
                airport_id,
                employee_code,
                controller_name,
                experience_years,
                shift,
                status,
                max_concurrent_flights

            FROM atc_controllers

            WHERE airport_id = %s

            AND status = 'AVAILABLE'

            ORDER BY
                experience_years DESC,
                max_concurrent_flights DESC
        """

        cursor.execute(
            query,
            (airport_id,)
        )

        controllers = cursor.fetchall()

        if scheduled_start is None or scheduled_end is None:
            return controllers

        available_controllers = []
        for controller in controllers:
            cursor.execute(
                """
                SELECT COUNT(*) AS concurrent_count
                FROM schedules
                WHERE atc_id = %s
                  AND status IN ('SCHEDULED', 'IN_PROGRESS')
                  AND scheduled_start < %s
                  AND scheduled_end > %s
                """,
                (
                    controller["atc_id"],
                    scheduled_end,
                    scheduled_start
                )
            )
            concurrent_count = cursor.fetchone()["concurrent_count"]
            maximum = controller.get("max_concurrent_flights") or 1
            if concurrent_count < maximum:
                available_controllers.append(controller)

        return available_controllers

    finally:

        cursor.close()
        connection.close()


def select_atc(
    airport_id,
    scheduled_start=None,
    scheduled_end=None
):

    controllers = get_available_atc(
        airport_id,
        scheduled_start,
        scheduled_end
    )

    if not controllers:
        return None

    return controllers[0]