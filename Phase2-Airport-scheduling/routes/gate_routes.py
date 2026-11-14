from flask import Blueprint, jsonify, request
from database import get_db_connection


gate_bp = Blueprint(
    "gate",
    __name__,
    url_prefix="/gates"
)


# =========================================================
# GET ALL GATES
# =========================================================

@gate_bp.route("/", methods=["GET"])
def get_gates():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            g.gate_id,
            g.terminal_id,
            t.terminal_name,
            t.airport_id,
            a.airport_name,
            a.airport_code,
            g.gate_number,
            g.gate_type,
            g.status,
            g.created_at
        FROM gates g
        JOIN terminals t
            ON g.terminal_id = t.terminal_id
        JOIN airports a
            ON t.airport_id = a.airport_id
        ORDER BY g.gate_id
    """)

    gates = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(gates)


# =========================================================
# GET SINGLE GATE
# =========================================================

@gate_bp.route("/<int:gate_id>", methods=["GET"])
def get_gate(gate_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            g.gate_id,
            g.terminal_id,
            t.terminal_name,
            t.airport_id,
            a.airport_name,
            a.airport_code,
            g.gate_number,
            g.gate_type,
            g.status,
            g.created_at
        FROM gates g
        JOIN terminals t
            ON g.terminal_id = t.terminal_id
        JOIN airports a
            ON t.airport_id = a.airport_id
        WHERE g.gate_id = %s
    """, (gate_id,))

    gate = cursor.fetchone()

    cursor.close()
    connection.close()

    if gate is None:
        return jsonify({
            "error": "Gate not found"
        }), 404

    return jsonify(gate)


# =========================================================
# ADD GATE
# =========================================================

@gate_bp.route("/", methods=["POST"])
def add_gate():

    data = request.get_json()

    required_fields = [
        "terminal_id",
        "gate_number",
        "gate_type"
    ]

    for field in required_fields:

        if field not in data:
            return jsonify({
                "error": f"{field} is required"
            }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # -----------------------------------------------------
    # CHECK TERMINAL
    # -----------------------------------------------------

    cursor.execute("""
        SELECT terminal_id
        FROM terminals
        WHERE terminal_id = %s
    """, (data["terminal_id"],))

    terminal = cursor.fetchone()

    if terminal is None:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Terminal not found"
        }), 404


    # -----------------------------------------------------
    # INSERT GATE
    # -----------------------------------------------------

    query = """
        INSERT INTO gates
        (
            terminal_id,
            gate_number,
            gate_type,
            status
        )
        VALUES (%s, %s, %s, %s)
    """

    values = (
        data["terminal_id"],
        data["gate_number"],
        data["gate_type"],
        data.get("status", "AVAILABLE")
    )

    cursor.execute(query, values)

    connection.commit()

    gate_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Gate added successfully",
        "gate_id": gate_id
    }), 201


# =========================================================
# UPDATE GATE
# =========================================================

@gate_bp.route("/<int:gate_id>", methods=["PUT"])
def update_gate(gate_id):

    data = request.get_json()

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE gates
        SET
            terminal_id = %s,
            gate_number = %s,
            gate_type = %s,
            status = %s
        WHERE gate_id = %s
    """

    values = (
        data["terminal_id"],
        data["gate_number"],
        data["gate_type"],
        data.get("status", "AVAILABLE"),
        gate_id
    )

    cursor.execute(query, values)

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Gate not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Gate updated successfully"
    })


# =========================================================
# DELETE GATE
# =========================================================

@gate_bp.route("/<int:gate_id>", methods=["DELETE"])
def delete_gate(gate_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM gates
        WHERE gate_id = %s
    """, (gate_id,))

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Gate not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Gate deleted successfully"
    })