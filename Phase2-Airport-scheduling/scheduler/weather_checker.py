# scheduler/weather_checker.py

from database import get_db_connection


def get_latest_weather(airport_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        query = """
            SELECT
                weather_id,
                airport_id,
                weather_condition,
                visibility_km,
                wind_speed_kmh,
                wind_direction,
                temperature_c,
                severity,
                recorded_at

            FROM weather_logs

            WHERE airport_id = %s

            ORDER BY recorded_at DESC

            LIMIT 1
        """

        cursor.execute(
            query,
            (airport_id,)
        )

        return cursor.fetchone()

    finally:

        cursor.close()
        connection.close()


def check_weather(airport_id):

    weather = get_latest_weather(
        airport_id
    )

    if not weather:

        return {
            "safe": True,
            "reason": "No weather data available"
        }

    severity = weather["severity"]

    if severity == "HIGH":

        return {
            "safe": False,
            "reason": "Severe weather conditions",
            "weather": weather
        }

    return {
        "safe": True,
        "reason": "Weather conditions acceptable",
        "weather": weather
    }