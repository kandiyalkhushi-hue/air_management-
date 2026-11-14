from flask import Blueprint, jsonify, request
from database import get_db_connection


airline_bp = Blueprint(
    "airline",
    __name__,
    url_prefix="/airlines"
)


# GET ALL AIRLINES
@airline_bp.route("/", methods=["GET"])
def get_airlines():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM airlines
        ORDER BY airline_id
    """)

    airlines = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(airlines)


# GET SINGLE AIRLINE
@airline_bp.route("/<int:airline_id>", methods=["GET"])
def get_airline(airline_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM airlines
        WHERE airline_id = %s
    """, (airline_id,))

    airline = cursor.fetchone()

    cursor.close()
    connection.close()

    if airline is None:
        return jsonify({
            "error": "Airline not found"
        }), 404

    return jsonify(airline)


# ADD AIRLINE
@airline_bp.route("/", methods=["POST"])
def add_airline():

    data = request.get_json()

    required_fields = [
        "airline_code",
        "airline_name",
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
        INSERT INTO airlines
        (
            airline_code,
            airline_name,
            country,
            status
        )
        VALUES (%s, %s, %s, %s)
    """

    values = (
        data["airline_code"],
        data["airline_name"],
        data["country"],
        data.get("status", "ACTIVE")
    )

    cursor.execute(query, values)

    connection.commit()

    airline_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Airline added successfully",
        "airline_id": airline_id
    }), 201


# UPDATE AIRLINE
@airline_bp.route("/<int:airline_id>", methods=["PUT"])
def update_airline(airline_id):

    data = request.get_json()

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE airlines
        SET
            airline_code = %s,
            airline_name = %s,
            country = %s,
            status = %s
        WHERE airline_id = %s
    """

    values = (
        data["airline_code"],
        data["airline_name"],
        data["country"],
        data.get("status", "ACTIVE"),
        airline_id
    )

    cursor.execute(query, values)

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Airline not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Airline updated successfully"
    })


# DELETE AIRLINE
@airline_bp.route("/<int:airline_id>", methods=["DELETE"])
def delete_airline(airline_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM airlines
        WHERE airline_id = %s
        """,
        (airline_id,)
    )

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Airline not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Airline deleted successfully"
    })