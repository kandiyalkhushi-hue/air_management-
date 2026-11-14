# routes/flight_routes.py

from flask import Blueprint, jsonify, request

from database import get_db_connection


flight_bp = Blueprint(
    "flight",
    __name__,
    url_prefix="/flights"
)


# =========================================================
# GET ALL FLIGHTS
# =========================================================

@flight_bp.route("", methods=["GET"])
def get_flights():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        airport_id = request.args.get(
            "airport_id",
            type=int
        )

        query = """
            SELECT
                f.flight_id,
                f.flight_number,
                f.airline_id,
                al.airline_code,
                al.airline_name,

                f.aircraft_id,
                ac.registration_number,
                ac.model,
                ac.aircraft_category,
                ac.required_runway_type,

                f.airport_id,
                ap.airport_code,
                ap.airport_name,

                f.terminal_id,
                t.terminal_name,

                f.gate_id,
                g.gate_number,

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
                f.created_at

            FROM flights f

            JOIN airlines al
                ON f.airline_id = al.airline_id

            JOIN aircraft ac
                ON f.aircraft_id = ac.aircraft_id

            JOIN airports ap
                ON f.airport_id = ap.airport_id

            LEFT JOIN terminals t
                ON f.terminal_id = t.terminal_id

            LEFT JOIN gates g
                ON f.gate_id = g.gate_id
        """

        parameters = []

        if airport_id is not None:

            query += """
                WHERE f.airport_id = %s
            """

            parameters.append(
                airport_id
            )

        query += """
            ORDER BY f.flight_id DESC
        """

        cursor.execute(
            query,
            tuple(parameters)
        )

        flights = cursor.fetchall()

        return jsonify({

            "success": True,

            "total_flights":
                len(flights),

            "flights":
                flights

        }), 200

    except Exception as error:

        return jsonify({

            "success": False,

            "message":
                "Unable to fetch flights",

            "error":
                str(error)

        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# GET SINGLE FLIGHT
# =========================================================

@flight_bp.route(
    "/<int:flight_id>",
    methods=["GET"]
)
def get_single_flight(flight_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        query = """
            SELECT
                f.*,

                al.airline_code,
                al.airline_name,

                ac.registration_number,
                ac.model,
                ac.aircraft_category,
                ac.required_runway_type,

                ap.airport_code,
                ap.airport_name,

                t.terminal_name,

                g.gate_number

            FROM flights f

            JOIN airlines al
                ON f.airline_id = al.airline_id

            JOIN aircraft ac
                ON f.aircraft_id = ac.aircraft_id

            JOIN airports ap
                ON f.airport_id = ap.airport_id

            LEFT JOIN terminals t
                ON f.terminal_id = t.terminal_id

            LEFT JOIN gates g
                ON f.gate_id = g.gate_id

            WHERE f.flight_id = %s
        """

        cursor.execute(
            query,
            (flight_id,)
        )

        flight = cursor.fetchone()

        if not flight:

            return jsonify({

                "success": False,

                "message":
                    "Flight not found"

            }), 404

        return jsonify({

            "success": True,

            "flight":
                flight

        }), 200

    except Exception as error:

        return jsonify({

            "success": False,

            "message":
                "Unable to fetch flight",

            "error":
                str(error)

        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# CREATE FLIGHT
# =========================================================

@flight_bp.route(
    "",
    methods=["POST"]
)
def create_flight():

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({

            "success": False,

            "message":
                "Request body is required"

        }), 400

    required_fields = [

        "flight_number",
        "airline_id",
        "aircraft_id",
        "airport_id",
        "operation_type"

    ]

    missing_fields = [

        field
        for field in required_fields

        if data.get(field) is None
        or data.get(field) == ""

    ]

    if missing_fields:

        return jsonify({

            "success": False,

            "message":
                "Required fields are missing",

            "missing_fields":
                missing_fields

        }), 400


    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        query = """
            INSERT INTO flights
            (
                flight_number,
                airline_id,
                aircraft_id,
                airport_id,
                terminal_id,
                gate_id,

                operation_type,

                arrival_time,
                departure_time,

                processing_time_minutes,

                priority,

                current_situation,

                fuel_percentage,
                passenger_count,

                is_emergency,
                emergency_reason,

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

                %s,
                %s,

                %s,
                %s,

                %s
            )
        """

        values = (

            data.get(
                "flight_number"
            ),

            data.get(
                "airline_id"
            ),

            data.get(
                "aircraft_id"
            ),

            data.get(
                "airport_id"
            ),

            data.get(
                "terminal_id"
            ),

            data.get(
                "gate_id"
            ),

            data.get(
                "operation_type"
            ),

            data.get(
                "arrival_time"
            ),

            data.get(
                "departure_time"
            ),

            data.get(
                "processing_time_minutes",
                10
            ),

            data.get(
                "priority",
                5
            ),

            data.get(
                "current_situation",
                "NORMAL"
            ),

            data.get(
                "fuel_percentage"
            ),

            data.get(
                "passenger_count"
            ),

            data.get(
                "is_emergency",
                False
            ),

            data.get(
                "emergency_reason"
            ),

            data.get(
                "status",
                "WAITING"
            )

        )

        cursor.execute(
            query,
            values
        )

        flight_id = (
            cursor.lastrowid
        )

        connection.commit()

        return jsonify({

            "success": True,

            "message":
                "Flight created successfully",

            "flight_id":
                flight_id

        }), 201

    except Exception as error:

        connection.rollback()

        return jsonify({

            "success": False,

            "message":
                "Unable to create flight",

            "error":
                str(error)

        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# UPDATE FLIGHT
# =========================================================

@flight_bp.route(
    "/<int:flight_id>",
    methods=["PUT"]
)
def update_flight(flight_id):

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({

            "success": False,

            "message":
                "Request body is required"

        }), 400


    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        check_query = """
            SELECT flight_id
            FROM flights
            WHERE flight_id = %s
        """

        cursor.execute(
            check_query,
            (flight_id,)
        )

        if not cursor.fetchone():

            return jsonify({

                "success": False,

                "message":
                    "Flight not found"

            }), 404


        allowed_fields = [

            "flight_number",
            "airline_id",
            "aircraft_id",
            "airport_id",
            "terminal_id",
            "gate_id",
            "operation_type",
            "arrival_time",
            "departure_time",
            "processing_time_minutes",
            "priority",
            "current_situation",
            "fuel_percentage",
            "passenger_count",
            "is_emergency",
            "emergency_reason",
            "status"

        ]


        updates = []
        values = []

        for field in allowed_fields:

            if field in data:

                updates.append(
                    f"{field} = %s"
                )

                values.append(
                    data[field]
                )


        if not updates:

            return jsonify({

                "success": False,

                "message":
                    "No fields provided for update"

            }), 400


        values.append(
            flight_id
        )


        query = f"""
            UPDATE flights

            SET
                {", ".join(updates)}

            WHERE flight_id = %s
        """


        cursor.execute(
            query,
            tuple(values)
        )

        connection.commit()

        return jsonify({

            "success": True,

            "message":
                "Flight updated successfully",

            "flight_id":
                flight_id

        }), 200

    except Exception as error:

        connection.rollback()

        return jsonify({

            "success": False,

            "message":
                "Unable to update flight",

            "error":
                str(error)

        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# DELETE FLIGHT
# =========================================================

@flight_bp.route(
    "/<int:flight_id>",
    methods=["DELETE"]
)
def delete_flight(flight_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        query = """
            DELETE FROM flights
            WHERE flight_id = %s
        """

        cursor.execute(
            query,
            (flight_id,)
        )

        if cursor.rowcount == 0:

            return jsonify({

                "success": False,

                "message":
                    "Flight not found"

            }), 404

        connection.commit()

        return jsonify({

            "success": True,

            "message":
                "Flight deleted successfully",

            "flight_id":
                flight_id

        }), 200

    except Exception as error:

        connection.rollback()

        return jsonify({

            "success": False,

            "message":
                "Unable to delete flight",

            "error":
                str(error)

        }), 500

    finally:

        cursor.close()
        connection.close()