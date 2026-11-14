# scheduler/scheduler.py

from datetime import timedelta

from database import get_db_connection

from scheduler.priority_manager import (
    get_priority
)

from scheduler.runway_allocator import (
    select_best_runway
)

from scheduler.atc_allocator import (
    select_atc
)

from scheduler.weather_checker import (
    check_weather
)

from scheduler.schedule_manager import (
    create_scheduler_run,
    save_schedule,
    complete_scheduler_run
)


# =========================================================
# GET WAITING FLIGHTS
# =========================================================

def get_waiting_flights(airport_id=None, include_scheduled=False):
    """
    Fetch all flights which are waiting for scheduling.

    Optional airport_id can be used to fetch flights
    belonging to a particular airport.

    include_scheduled is intended for read-only algorithm comparisons.

    The flight's current situation is also converted
    into a scheduling priority.
    """

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        statuses = ["WAITING", "EMERGENCY"]
        if include_scheduled:
            statuses.extend(["SCHEDULED", "IN_PROGRESS"])

        status_placeholders = ", ".join(["%s"] * len(statuses))

        query = """
            SELECT

                f.flight_id,
                f.flight_number,

                f.airport_id,
                f.airline_id,
                f.aircraft_id,

                f.terminal_id,
                f.gate_id,

                f.operation_type,

                f.arrival_time,
                f.departure_time,

                f.processing_time_minutes,

                f.priority,
                f.current_situation,

                f.fuel_percentage,
                f.passenger_count,

                f.is_emergency,
                f.emergency_reason,

                f.status,

                a.aircraft_category,
                a.required_runway_type

            FROM flights f

            JOIN aircraft a
                ON f.aircraft_id = a.aircraft_id

            WHERE f.status IN ({})
        """.format(status_placeholders)

        parameters = list(statuses)

        # -------------------------------------------------
        # Airport filter
        # -------------------------------------------------

        if airport_id is not None:

            query += """
                AND f.airport_id = %s
            """

            parameters.append(
                airport_id
            )

        # -------------------------------------------------
        # Sort by requested time
        # -------------------------------------------------

        query += """

            ORDER BY

                CASE

                    WHEN f.operation_type = 'ARRIVAL'
                    THEN f.arrival_time

                    ELSE f.departure_time

                END ASC,

                f.flight_id ASC
        """

        cursor.execute(
            query,
            tuple(parameters)
        )

        flights = cursor.fetchall()

        # -------------------------------------------------
        # Add situation priority
        # -------------------------------------------------

        for flight in flights:

            situation = (
                flight["current_situation"]
                or "NORMAL"
            )

            flight["situation_priority"] = (
                get_priority(situation)
            )

        return flights

    finally:

        cursor.close()
        connection.close()


# =========================================================
# GET SINGLE FLIGHT
# =========================================================

def get_flight(flight_id):
    """
    Fetch one flight with aircraft information.
    """

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        query = """
            SELECT

                f.flight_id,
                f.flight_number,

                f.airport_id,
                f.airline_id,
                f.aircraft_id,

                f.terminal_id,
                f.gate_id,

                f.operation_type,

                f.arrival_time,
                f.departure_time,

                f.processing_time_minutes,

                f.priority,
                f.current_situation,

                f.fuel_percentage,
                f.passenger_count,

                f.is_emergency,
                f.emergency_reason,

                f.status,

                a.aircraft_category,
                a.required_runway_type

            FROM flights f

            JOIN aircraft a
                ON f.aircraft_id = a.aircraft_id

            WHERE f.flight_id = %s
        """

        cursor.execute(
            query,
            (flight_id,)
        )

        flight = cursor.fetchone()

        # -------------------------------------------------
        # Add situation priority
        # -------------------------------------------------

        if flight:

            situation = (
                flight["current_situation"]
                or "NORMAL"
            )

            flight["situation_priority"] = (
                get_priority(situation)
            )

        return flight

    finally:

        cursor.close()
        connection.close()


# =========================================================
# GET FLIGHT REQUESTED TIME
# =========================================================

def get_requested_time(flight):
    """
    Determine when the flight wants to be processed.

    ARRIVAL   -> arrival_time
    DEPARTURE -> departure_time
    """

    if flight["operation_type"] == "ARRIVAL":

        return flight["arrival_time"]

    return flight["departure_time"]


# =========================================================
# CALCULATE SCHEDULE END TIME
# =========================================================

def calculate_end_time(
    start_time,
    processing_time
):
    """
    Calculate when runway processing will finish.
    """

    if processing_time is None:

        processing_time = 10

    return (
        start_time
        + timedelta(
            minutes=processing_time
        )
    )


# =========================================================
# SCHEDULE SINGLE FLIGHT
# =========================================================

def schedule_flight(
    flight_id,
    situation=None
):
    """
    Schedule one flight.

    Flow:

    Flight
       ↓
    Situation
       ↓
    Priority
       ↓
    Requested Time
       ↓
    Weather Check
       ↓
    Runway Check
       ↓
    Runway Conflict Check
       ↓
    ATC Check
       ↓
    Save Schedule
       ↓
    Complete Scheduler Run
    """

    # =====================================================
    # 1. GET FLIGHT
    # =====================================================

    flight = get_flight(
        flight_id
    )

    if not flight:

        return {
            "success": False,
            "message": "Flight not found"
        }


    # =====================================================
    # 2. DETERMINE SITUATION
    # =====================================================

    if situation:

        situation = situation.upper().strip()

    else:

        situation = (
            flight["current_situation"]
            or "NORMAL"
        )


    # =====================================================
    # 3. VALIDATE SITUATION
    # =====================================================

    try:

        situation_priority = get_priority(
            situation
        )

    except ValueError as error:

        return {
            "success": False,
            "message": str(error)
        }


    # =====================================================
    # 4. GET REQUESTED TIME
    # =====================================================

    scheduled_start = get_requested_time(
        flight
    )

    if scheduled_start is None:

        return {
            "success": False,
            "message": (
                "Flight does not have a valid "
                "arrival/departure time"
            )
        }


    # =====================================================
    # 5. CALCULATE END TIME
    # =====================================================

    processing_time = (
        flight["processing_time_minutes"]
    )

    if processing_time is None:

        processing_time = 10

    scheduled_end = calculate_end_time(
        scheduled_start,
        processing_time
    )


    # =====================================================
    # 6. WEATHER CHECK
    # =====================================================

    weather_result = check_weather(
        flight["airport_id"]
    )

    if not weather_result["safe"]:

        return {

            "success": False,

            "message": (
                weather_result["reason"]
            ),

            "flight": {

                "flight_id": (
                    flight["flight_id"]
                ),

                "flight_number": (
                    flight["flight_number"]
                )
            },

            "situation": situation,

            "weather": (
                weather_result.get(
                    "weather"
                )
            )
        }


    # =====================================================
    # 7. CREATE SCHEDULER RUN
    # =====================================================

    run_id = create_scheduler_run(
        "PRIORITY",
        1
    )


    # =====================================================
    # 8. FIND SUITABLE RUNWAY
    # =====================================================

    runway = select_best_runway(

        airport_id=(
            flight["airport_id"]
        ),

        operation_type=(
            flight["operation_type"]
        ),

        aircraft_type=(
            flight["required_runway_type"]
        ),

        scheduled_start=(
            scheduled_start
        ),

        scheduled_end=(
            scheduled_end
        ),

        flight_id=flight_id
    )


    # =====================================================
    # 9. RUNWAY NOT AVAILABLE
    # =====================================================

    if not runway:

        return {

            "success": False,

            "message": (
                "No suitable runway available "
                "for this time"
            ),

            "run_id": run_id,

            "flight": {

                "flight_id": (
                    flight["flight_id"]
                ),

                "flight_number": (
                    flight["flight_number"]
                ),

                "operation_type": (
                    flight["operation_type"]
                )
            },

            "situation": situation,

            "priority": situation_priority
        }


    # =====================================================
    # 10. FIND ATC
    # =====================================================

    atc = select_atc(
        flight["airport_id"]
    )


    # =====================================================
    # 11. ATC NOT AVAILABLE
    # =====================================================

    if not atc:

        return {

            "success": False,

            "message": (
                "No ATC controller available"
            ),

            "run_id": run_id,

            "flight": {

                "flight_id": (
                    flight["flight_id"]
                ),

                "flight_number": (
                    flight["flight_number"]
                )
            },

            "situation": situation,

            "priority": situation_priority
        }


    # =====================================================
    # 12. SAVE SCHEDULE
    # =====================================================

    saved_schedule = save_schedule(

        run_id=run_id,

        flight=flight,

        runway=runway,

        atc=atc,

        situation=situation,

        scheduled_start=scheduled_start
    )


    # =====================================================
    # 13. COMPLETE RUN
    # =====================================================

    complete_scheduler_run(
        run_id,
        1
    )


    # =====================================================
    # 14. RETURN RESULT
    # =====================================================

    return {

        "success": True,

        "message": (
            "Flight successfully scheduled"
        ),

        "run_id": run_id,

        "schedule_id": (
            saved_schedule[
                "schedule_id"
            ]
        ),

        "flight": {

            "flight_id": (
                flight["flight_id"]
            ),

            "flight_number": (
                flight["flight_number"]
            ),

            "operation_type": (
                flight["operation_type"]
            ),

            "aircraft_type": (
                flight["aircraft_category"]
            )
        },

        "situation": situation,

        "priority": situation_priority,

        "runway": {

            "runway_id": (
                runway["runway_id"]
            ),

            "runway_code": (
                runway["runway_code"]
            ),

            "runway_type": (
                runway["runway_type"]
            )
        },

        "atc": {

            "atc_id": (
                atc["atc_id"]
            ),

            "employee_code": (
                atc["employee_code"]
            ),

            "controller_name": (
                atc["controller_name"]
            )
        },

        "weather": (
            weather_result.get(
                "weather"
            )
        ),

        "schedule": {

            "start": (
                saved_schedule[
                    "scheduled_start"
                ]
            ),

            "end": (
                saved_schedule[
                    "scheduled_end"
                ]
            ),

            "waiting_time_minutes": (
                saved_schedule[
                    "waiting_time_minutes"
                ]
            ),

            "turnaround_time_minutes": (
                saved_schedule[
                    "turnaround_time_minutes"
                ]
            ),

            "response_time_minutes": (
                saved_schedule[
                    "response_time_minutes"
                ]
            )
        }
    }