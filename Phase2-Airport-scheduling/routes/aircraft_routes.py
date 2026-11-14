from flask import Blueprint, jsonify, request
from database import get_db_connection


aircraft_bp = Blueprint(
    "aircraft",
    __name__,
    url_prefix="/aircraft"
)


# GET ALL AIRCRAFT
@aircraft_bp.route("/", methods=["GET"])
def get_aircraft():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.aircraft_id,
            a.airline_id,
            al.airline_name,
            al.airline_code,
            a.registration_number,
            a.model,
            a.aircraft_category,
            a.passenger_capacity,
            a.max_takeoff_weight,
            a.required_runway_type,
            a.status,
            a.created_at
        FROM aircraft a
        JOIN airlines al
            ON a.airline_id = al.airline_id
        ORDER BY a.aircraft_id
    """)

    aircraft = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(aircraft)


# GET SINGLE AIRCRAFT
@aircraft_bp.route("/<int:aircraft_id>", methods=["GET"])
def get_single_aircraft(aircraft_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.aircraft_id,
            a.airline_id,
            al.airline_name,
            al.airline_code,
            a.registration_number,
            a.model,
            a.aircraft_category,
            a.passenger_capacity,
            a.max_takeoff_weight,
            a.required_runway_type,
            a.status,
            a.created_at
        FROM aircraft a
        JOIN airlines al
            ON a.airline_id = al.airline_id
        WHERE a.aircraft_id = %s
    """, (aircraft_id,))

    aircraft = cursor.fetchone()

    cursor.close()
    connection.close()

    if aircraft is None:
        return jsonify({
            "error": "Aircraft not found"
        }), 404

    return jsonify(aircraft)


# ADD AIRCRAFT
@aircraft_bp.route("/", methods=["POST"])
def add_aircraft():

    data = request.get_json()

    required_fields = [
        "airline_id",
        "registration_number",
        "model",
        "aircraft_category",
        "passenger_capacity",
        "max_takeoff_weight",
        "required_runway_type"
    ]

    for field in required_fields:

        if field not in data:
            return jsonify({
                "error": f"{field} is required"
            }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check whether airline exists
    cursor.execute("""
        SELECT airline_id
        FROM airlines
        WHERE airline_id = %s
    """, (data["airline_id"],))

    airline = cursor.fetchone()

    if airline is None:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Airline not found"
        }), 404

    query = """
        INSERT INTO aircraft
        (
            airline_id,
            registration_number,
            model,
            aircraft_category,
            passenger_capacity,
            max_takeoff_weight,
            required_runway_type,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        data["airline_id"],
        data["registration_number"],
        data["model"],
        data["aircraft_category"],
        data["passenger_capacity"],
        data["max_takeoff_weight"],
        data["required_runway_type"],
        data.get("status", "AVAILABLE")
    )

    cursor.execute(query, values)

    connection.commit()

    aircraft_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Aircraft added successfully",
        "aircraft_id": aircraft_id
    }), 201


# UPDATE AIRCRAFT
@aircraft_bp.route("/<int:aircraft_id>", methods=["PUT"])
def update_aircraft(aircraft_id):

    data = request.get_json()

    required_fields = [
        "airline_id",
        "registration_number",
        "model",
        "aircraft_category",
        "passenger_capacity",
        "max_takeoff_weight",
        "required_runway_type"
    ]

    for field in required_fields:

        if field not in data:
            return jsonify({
                "error": f"{field} is required"
            }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check airline
    cursor.execute("""
        SELECT airline_id
        FROM airlines
        WHERE airline_id = %s
    """, (data["airline_id"],))

    airline = cursor.fetchone()

    if airline is None:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Airline not found"
        }), 404

    query = """
        UPDATE aircraft
        SET
            airline_id = %s,
            registration_number = %s,
            model = %s,
            aircraft_category = %s,
            passenger_capacity = %s,
            max_takeoff_weight = %s,
            required_runway_type = %s,
            status = %s
        WHERE aircraft_id = %s
    """

    values = (
        data["airline_id"],
        data["registration_number"],
        data["model"],
        data["aircraft_category"],
        data["passenger_capacity"],
        data["max_takeoff_weight"],
        data["required_runway_type"],
        data.get("status", "AVAILABLE"),
        aircraft_id
    )

    cursor.execute(query, values)

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Aircraft not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Aircraft updated successfully"
    })


# DELETE AIRCRAFT
@aircraft_bp.route("/<int:aircraft_id>", methods=["DELETE"])
def delete_aircraft(aircraft_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM aircraft
        WHERE aircraft_id = %s
    """, (aircraft_id,))

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Aircraft not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Aircraft deleted successfully"
    })