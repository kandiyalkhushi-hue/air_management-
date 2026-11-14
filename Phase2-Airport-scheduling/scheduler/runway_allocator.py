
# scheduler/runway_allocator.py

from database import get_db_connection
from scheduler.schedule_manager import is_runway_free


# ---------------------------------------------------------
# Runway capacity levels
# ---------------------------------------------------------

RUNWAY_LEVEL = {
    "LIGHT": 1,
    "MEDIUM": 2,
    "HEAVY": 3
}


# ---------------------------------------------------------
# Check aircraft and runway compatibility
# ---------------------------------------------------------

def is_runway_compatible(aircraft_type, runway_type):

    if not aircraft_type or not runway_type:
        return False

    aircraft_type = str(aircraft_type).strip().upper()
    runway_type = str(runway_type).strip().upper()

    aircraft_level = RUNWAY_LEVEL.get(aircraft_type)
    runway_level = RUNWAY_LEVEL.get(runway_type)

    if aircraft_level is None or runway_level is None:
        print(
            f"[RUNWAY DEBUG] Invalid type: "
            f"Aircraft={aircraft_type}, Runway={runway_type}"
        )
        return False

    return runway_level >= aircraft_level


# ---------------------------------------------------------
# Get all suitable runways
# ---------------------------------------------------------

def get_available_runways(
    airport_id,
    operation_type,
    aircraft_type
):

    operation_map = {
        "ARRIVAL": "LANDING",
        "DEPARTURE": "TAKEOFF"
    }

    operation_type = (
        str(operation_type).strip().upper()
        if operation_type else ""
    )

    runway_operation = operation_map.get(operation_type)

    if not runway_operation:
        print("[RUNWAY DEBUG] Invalid operation:", operation_type)
        return []

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        query = """
            SELECT
                runway_id,
                airport_id,
                runway_code,
                length_meters,
                width_meters,
                runway_type,
                allowed_operation,
                ils_available,
                night_operation,
                status
            FROM runways
            WHERE airport_id = %s
              AND UPPER(status) = 'AVAILABLE'
              AND (
                  UPPER(allowed_operation) = %s
                  OR UPPER(allowed_operation) = 'BOTH'
              )
            ORDER BY length_meters DESC
        """

        cursor.execute(
            query,
            (airport_id, runway_operation)
        )

        runways = cursor.fetchall()

        compatible_runways = []

        for runway in runways:

            if is_runway_compatible(
                aircraft_type,
                runway["runway_type"]
            ):
                compatible_runways.append(runway)

        print("\n[RUNWAY DEBUG] Available compatible runways:")
        for runway in compatible_runways:
            print(
                runway["runway_id"],
                runway["runway_code"],
                runway["runway_type"],
                runway["allowed_operation"]
            )

        return compatible_runways

    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------
# Select best runway
# ---------------------------------------------------------

def select_best_runway(
    airport_id,
    operation_type,
    aircraft_type,
    scheduled_start,
    scheduled_end,
    reserved_intervals=None,
    flight_id=None
):

    print("\n========== RUNWAY ALLOCATION DEBUG ==========")
    print("Airport ID:", airport_id)
    print("Operation:", operation_type)
    print("Aircraft type received:", aircraft_type)
    print("Flight ID:", flight_id)
    print("Start:", scheduled_start)
    print("End:", scheduled_end)

    runways = get_available_runways(
        airport_id,
        operation_type,
        aircraft_type
    )

    if not runways:
        print("[RUNWAY DEBUG] No compatible runways found.")
        print("=============================================")
        return None

    for runway in runways:

        runway_id = runway["runway_id"]

        print("\nChecking runway:", runway_id)

        # Check existing database schedules
        try:
            runway_free = is_runway_free(
                runway_id,
                scheduled_start,
                scheduled_end,
                flight_id=flight_id
            )

        except TypeError as error:
            print("[RUNWAY DEBUG] is_runway_free argument error:", error)
            raise

        print("Database runway free:", runway_free)

        # Check reservations created during this scheduling run
        if runway_free and reserved_intervals:

            has_conflict = any(
                reservation["runway_id"] == runway_id
                and scheduled_start < reservation["scheduled_end"]
                and scheduled_end > reservation["scheduled_start"]
                for reservation in reserved_intervals
            )

            runway_free = not has_conflict

            print("Reserved interval conflict:", has_conflict)

        if runway_free:

            print("[RUNWAY DEBUG] Selected runway:", runway_id)
            print("=============================================")

            return runway

    print("[RUNWAY DEBUG] No runway free for this time slot.")
    print("=============================================")

    return None
