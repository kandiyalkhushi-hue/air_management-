from flask import Blueprint, jsonify, request
from database import get_db_connection


atc_bp = Blueprint(
    "atc",
    __name__,
    url_prefix="/atc"
)


# GET ALL ATC CONTROLLERS
@atc_bp.route("/", methods=["GET"])
def get_atc_controllers():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            at.atc_id,
            at.airport_id,
            a.airport_name,
            a.airport_code,
            at.employee_code,
            at.controller_name,
            at.experience_years,
            at.shift,
            at.status,
            at.max_concurrent_flights,
            at.created_at
        FROM atc_controllers at
        JOIN airports a
            ON at.airport_id = a.airport_id
        ORDER BY at.atc_id
    """)

    controllers = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(controllers)


# GET SINGLE ATC CONTROLLER
@atc_bp.route("/<int:atc_id>", methods=["GET"])
def get_atc_controller(atc_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            at.atc_id,
            at.airport_id,
            a.airport_name,
            a.airport_code,
            at.employee_code,
            at.controller_name,
            at.experience_years,
            at.shift,
            at.status,
            at.max_concurrent_flights,
            at.created_at
        FROM atc_controllers at
        JOIN airports a
            ON at.airport_id = a.airport_id
        WHERE at.atc_id = %s
    """, (atc_id,))

    controller = cursor.fetchone()

    cursor.close()
    connection.close()

    if controller is None:
        return jsonify({
            "error": "ATC controller not found"
        }), 404

    return jsonify(controller)


# ADD ATC CONTROLLER
@atc_bp.route("/", methods=["POST"])
def add_atc_controller():

    data = request.get_json()

    required_fields = [
        "airport_id",
        "employee_code",
        "controller_name",
        "experience_years",
        "shift",
        "max_concurrent_flights"
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
        INSERT INTO atc_controllers
        (
            airport_id,
            employee_code,
            controller_name,
            experience_years,
            shift,
            status,
            max_concurrent_flights
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        data["airport_id"],
        data["employee_code"],
        data["controller_name"],
        data["experience_years"],
        data["shift"],
        data.get("status", "AVAILABLE"),
        data["max_concurrent_flights"]
    )

    cursor.execute(query, values)

    connection.commit()

    atc_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "ATC controller added successfully",
        "atc_id": atc_id
    }), 201


# UPDATE ATC CONTROLLER
@atc_bp.route("/<int:atc_id>", methods=["PUT"])
def update_atc_controller(atc_id):

    data = request.get_json()

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE atc_controllers
        SET
            airport_id = %s,
            employee_code = %s,
            controller_name = %s,
            experience_years = %s,
            shift = %s,
            status = %s,
            max_concurrent_flights = %s
        WHERE atc_id = %s
    """

    values = (
        data["airport_id"],
        data["employee_code"],
        data["controller_name"],
        data["experience_years"],
        data["shift"],
        data.get("status", "AVAILABLE"),
        data["max_concurrent_flights"],
        atc_id
    )

    cursor.execute(query, values)

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "ATC controller not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "ATC controller updated successfully"
    })


# DELETE ATC CONTROLLER
@atc_bp.route("/<int:atc_id>", methods=["DELETE"])
def delete_atc_controller(atc_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM atc_controllers
        WHERE atc_id = %s
    """, (atc_id,))

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "ATC controller not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "ATC controller deleted successfully"
    })