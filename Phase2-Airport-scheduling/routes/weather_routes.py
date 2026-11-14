from flask import Blueprint, jsonify, request
from database import get_db_connection


weather_bp = Blueprint(
    "weather",
    __name__,
    url_prefix="/weather"
)


# GET ALL WEATHER LOGS
@weather_bp.route("/", methods=["GET"])
def get_weather_logs():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            w.weather_id,
            w.airport_id,
            a.airport_name,
            a.airport_code,
            w.weather_condition,
            w.visibility_km,
            w.wind_speed_kmh,
            w.wind_direction,
            w.temperature_c,
            w.severity,
            w.recorded_at
        FROM weather_logs w
        JOIN airports a
            ON w.airport_id = a.airport_id
        ORDER BY w.recorded_at DESC
    """)

    weather_logs = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(weather_logs)


# GET SINGLE WEATHER LOG
@weather_bp.route("/<int:weather_id>", methods=["GET"])
def get_weather(weather_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            w.weather_id,
            w.airport_id,
            a.airport_name,
            a.airport_code,
            w.weather_condition,
            w.visibility_km,
            w.wind_speed_kmh,
            w.wind_direction,
            w.temperature_c,
            w.severity,
            w.recorded_at
        FROM weather_logs w
        JOIN airports a
            ON w.airport_id = a.airport_id
        WHERE w.weather_id = %s
    """, (weather_id,))

    weather = cursor.fetchone()

    cursor.close()
    connection.close()

    if weather is None:
        return jsonify({
            "error": "Weather record not found"
        }), 404

    return jsonify(weather)


# ADD WEATHER LOG
@weather_bp.route("/", methods=["POST"])
def add_weather():

    data = request.get_json()

    required_fields = [
        "airport_id",
        "weather_condition",
        "visibility_km",
        "wind_speed_kmh",
        "wind_direction",
        "temperature_c",
        "severity"
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
        INSERT INTO weather_logs
        (
            airport_id,
            weather_condition,
            visibility_km,
            wind_speed_kmh,
            wind_direction,
            temperature_c,
            severity
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        data["airport_id"],
        data["weather_condition"],
        data["visibility_km"],
        data["wind_speed_kmh"],
        data["wind_direction"],
        data["temperature_c"],
        data["severity"]
    )

    cursor.execute(query, values)

    connection.commit()

    weather_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Weather record added successfully",
        "weather_id": weather_id
    }), 201


# UPDATE WEATHER LOG
@weather_bp.route("/<int:weather_id>", methods=["PUT"])
def update_weather(weather_id):

    data = request.get_json()

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE weather_logs
        SET
            airport_id = %s,
            weather_condition = %s,
            visibility_km = %s,
            wind_speed_kmh = %s,
            wind_direction = %s,
            temperature_c = %s,
            severity = %s
        WHERE weather_id = %s
    """

    values = (
        data["airport_id"],
        data["weather_condition"],
        data["visibility_km"],
        data["wind_speed_kmh"],
        data["wind_direction"],
        data["temperature_c"],
        data["severity"],
        weather_id
    )

    cursor.execute(query, values)

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Weather record not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Weather record updated successfully"
    })


# DELETE WEATHER LOG
@weather_bp.route("/<int:weather_id>", methods=["DELETE"])
def delete_weather(weather_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM weather_logs
        WHERE weather_id = %s
    """, (weather_id,))

    connection.commit()

    if cursor.rowcount == 0:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Weather record not found"
        }), 404

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Weather record deleted successfully"
    })