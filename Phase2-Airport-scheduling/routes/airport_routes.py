from flask import Blueprint, jsonify, request
from database import get_db_connection


airport_bp = Blueprint("airport", __name__, url_prefix="/airports")


# GET ALL AIRPORTS
@airport_bp.route("/", methods=["GET"])
def get_airports():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM airports ORDER BY airport_id")

    airports = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(airports)


# GET SINGLE AIRPORT
@airport_bp.route("/<int:airport_id>", methods=["GET"])
def get_airport(airport_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM airports WHERE airport_id = %s",
        (airport_id,)
    )

    airport = cursor.fetchone()

    cursor.close()
    connection.close()

    if airport is None:
        return jsonify({"error": "Airport not found"}), 404

    return jsonify(airport)


# ADD AIRPORT
@airport_bp.route("/", methods=["POST"])
def add_airport():

    data = request.get_json()

    required_fields = [
        "airport_code",
        "airport_name",
        "city",
        "country"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"{field} is required"
            }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO airports
        (
            airport_code,
            airport_name,
            city,
            country,
            timezone,
            max_aircraft_capacity,
            operating_hours,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        data["airport_code"],
        data["airport_name"],
        data["city"],
        data["country"],
        data.get("timezone", "IST"),
        data.get("max_aircraft_capacity", 0),
        data.get("operating_hours", "24x7"),
        data.get("status", "ACTIVE")
    )

    cursor.execute(query, values)

    connection.commit()

    airport_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Airport added successfully",
        "airport_id": airport_id
    }), 201


# UPDATE AIRPORT
@airport_bp.route("/<int:airport_id>", methods=["PUT"])
def update_airport(airport_id):

    data = request.get_json()

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE airports
        SET
            airport_code = %s,
            airport_name = %s,
            city = %s,
            country = %s,
            timezone = %s,
            max_aircraft_capacity = %s,
            operating_hours = %s,
            status = %s
        WHERE airport_id = %s
    """

    values = (
        data["airport_code"],
        data["airport_name"],
        data["city"],
        data["country"],
        data.get("timezone", "IST"),
        data.get("max_aircraft_capacity", 0),
        data.get("operating_hours", "24x7"),
        data.get("status", "ACTIVE"),
        airport_id
    )

    cursor.execute(query, values)

    connection.commit()

    if cursor.rowcount == 0:
        cursor.close()
        connection.close()

        return jsonify({
            "error": "Airport not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Airport updated successfully"
    })


# DELETE AIRPORT
@airport_bp.route("/<int:airport_id>", methods=["DELETE"])
def delete_airport(airport_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM airports WHERE airport_id = %s",
        (airport_id,)
    )

    connection.commit()

    if cursor.rowcount == 0:
        cursor.close()
        connection.close()

        return jsonify({
            "error": "Airport not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Airport deleted successfully"
    })