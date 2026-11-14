from flask import Blueprint, jsonify, request
from database import get_db_connection


terminal_bp = Blueprint(
    "terminal",
    __name__,
    url_prefix="/terminals"
)


# GET ALL TERMINALS
@terminal_bp.route("/", methods=["GET"])
def get_terminals():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            t.terminal_id,
            t.airport_id,
            a.airport_name,
            a.airport_code,
            t.terminal_name,
            t.terminal_type,
            t.passenger_capacity,
            t.status,
            t.created_at
        FROM terminals t
        JOIN airports a
            ON t.airport_id = a.airport_id
        ORDER BY t.terminal_id
    """)

    terminals = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(terminals)


# GET SINGLE TERMINAL
@terminal_bp.route("/<int:terminal_id>", methods=["GET"])
def get_terminal(terminal_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            t.terminal_id,
            t.airport_id,
            a.airport_name,
            a.airport_code,
            t.terminal_name,
            t.terminal_type,
            t.passenger_capacity,
            t.status,
            t.created_at
        FROM terminals t
        JOIN airports a
            ON t.airport_id = a.airport_id
        WHERE t.terminal_id = %s
    """, (terminal_id,))

    terminal = cursor.fetchone()

    cursor.close()
    connection.close()

    if terminal is None:
        return jsonify({
            "error": "Terminal not found"
        }), 404

    return jsonify(terminal)


# ADD TERMINAL
@terminal_bp.route("/", methods=["POST"])
def add_terminal():

    data = request.get_json()

    required_fields = [
        "airport_id",
        "terminal_name",
        "terminal_type",
        "passenger_capacity"
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
        INSERT INTO terminals
        (
            airport_id,
            terminal_name,
            terminal_type,
            passenger_capacity,
            status
        )
        VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        data["airport_id"],
        data["terminal_name"],
        data["terminal_type"],
        data["passenger_capacity"],
        data.get("status", "OPERATIONAL")
    )

    cursor.execute(query, values)

    connection.commit()

    terminal_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Terminal added successfully",
        "terminal_id": terminal_id
    }), 201


# UPDATE TERMINAL
@terminal_bp.route("/<int:terminal_id>", methods=["PUT"])
def update_terminal(terminal_id):

    data = request.get_json()

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE terminals
        SET
            airport_id = %s,
            terminal_name = %s,
            terminal_type = %s,
            passenger_capacity = %s,
            status = %s
        WHERE terminal_id = %s
    """

    values = (
        data["airport_id"],
        data["terminal_name"],
        data["terminal_type"],
        data["passenger_capacity"],
        data.get("status", "OPERATIONAL"),
        terminal_id
    )

    cursor.execute(query, values)

    connection.commit()

    if cursor.rowcount == 0:
        cursor.close()
        connection.close()

        return jsonify({
            "error": "Terminal not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Terminal updated successfully"
    })


# DELETE TERMINAL
@terminal_bp.route("/<int:terminal_id>", methods=["DELETE"])
def delete_terminal(terminal_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM terminals
        WHERE terminal_id = %s
    """, (terminal_id,))

    connection.commit()

    if cursor.rowcount == 0:
        cursor.close()
        connection.close()

        return jsonify({
            "error": "Terminal not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Terminal deleted successfully"
    })