from flask import Blueprint, jsonify, request
from database import get_db_connection


runway_bp = Blueprint(
    "runway",
    __name__,
    url_prefix="/runways"
)


# GET ALL RUNWAYS
@runway_bp.route("/", methods=["GET"])
def get_runways():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            r.runway_id,
            r.airport_id,
            a.airport_name,
            a.airport_code,
            r.runway_code,
            r.length_meters,
            r.width_meters,
            r.runway_type,
            r.allowed_operation,
            r.ils_available,
            r.night_operation,
            r.status,
            r.created_at
        FROM runways r
        JOIN airports a
            ON r.airport_id = a.airport_id
        ORDER BY r.runway_id
    """)

    runways = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(runways)


# GET SINGLE RUNWAY
@runway_bp.route("/<int:runway_id>", methods=["GET"])
def get_runway(runway_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            r.runway_id,
            r.airport_id,
            a.airport_name,
            a.airport_code,
            r.runway_code,
            r.length_meters,
            r.width_meters,
            r.runway_type,
            r.allowed_operation,
            r.ils_available,
            r.night_operation,
            r.status,
            r.created_at
        FROM runways r
        JOIN airports a
            ON r.airport_id = a.airport_id
        WHERE r.runway_id = %s
    """, (runway_id,))

    runway = cursor.fetchone()

    cursor.close()
    connection.close()

    if runway is None:
        return jsonify({
            "error": "Runway not found"
        }), 404

    return jsonify(runway)


# ADD RUNWAY
@runway_bp.route("/", methods=["POST"])
def add_runway():

    data = request.get_json()

    required_fields = [
        "airport_id",
        "runway_code",
        "length_meters",
        "width_meters",
        "runway_type",
        "allowed_operation"
    ]

    for field in required_fields:

        if field not in data:
            return jsonify({
                "error": f"{field} is required"
            }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check airport
    cursor.execute("""
        SELECT airport_id
        FROM airports
        WHERE airport_id = %s
    """, (data["airport_id"],))

    airport = cursor.fetchone()

    if airport is None:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Airport not found"
        }), 404

    query = """
        INSERT INTO runways
        (
            airport_id,
            runway_code,
            length_meters,
            width_meters,
            runway_type,
            allowed_operation,
            ils_available,
            night_operation,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        data["airport_id"],
        data["runway_code"],
        data["length_meters"],
        data["width_meters"],
        data["runway_type"],
        data["allowed_operation"],
        data.get("ils_available", False),
        data.get("night_operation", False),
        data.get("status", "AVAILABLE")
    )

    cursor.execute(query, values)

    connection.commit()

    runway_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Runway added successfully",
        "runway_id": runway_id
    }), 201


# UPDATE RUNWAY
@runway_bp.route("/<int:runway_id>", methods=["PUT"])
def update_runway(runway_id):

    data = request.get_json()

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE runways
        SET
            airport_id = %s,
            runway_code = %s,
            length_meters = %s,
            width_meters = %s,
            runway_type = %s,
            allowed_operation = %s,
            ils_available = %s,
            night_operation = %s,
            status = %s
        WHERE runway_id = %s
    """

    values = (
        data["airport_id"],
        data["runway_code"],
        data["length_meters"],
        data["width_meters"],
        data["runway_type"],
        data["allowed_operation"],
        data.get("ils_available", False),
        data.get("night_operation", False),
        data.get("status", "AVAILABLE"),
        runway_id
    )

    cursor.execute(query, values)

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Runway not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Runway updated successfully"
    })


# DELETE RUNWAY
@runway_bp.route("/<int:runway_id>", methods=["DELETE"])
def delete_runway(runway_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM runways
        WHERE runway_id = %s
    """, (runway_id,))

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Runway not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Runway deleted successfully"
    })