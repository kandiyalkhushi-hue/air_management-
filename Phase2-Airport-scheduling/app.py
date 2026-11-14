
# app.py

from flask import Flask, render_template, jsonify

# =========================================================
# API BLUEPRINTS
# =========================================================

from routes.airport_routes import airport_bp
from routes.airline_routes import airline_bp
from routes.aircraft_routes import aircraft_bp
from routes.terminal_routes import terminal_bp
from routes.runway_routes import runway_bp
from routes.atc_routes import atc_bp
from routes.weather_routes import weather_bp
from routes.flight_routes import flight_bp
from routes.gate_routes import gate_bp
from routes.scheduler_routes import scheduler_bp

# =========================================================
# SCHEDULE MANAGER
# =========================================================

from scheduler.schedule_manager import get_all_schedules


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)


# =========================================================
# REGISTER API BLUEPRINTS
# =========================================================

app.register_blueprint(airport_bp)
app.register_blueprint(airline_bp)
app.register_blueprint(aircraft_bp)
app.register_blueprint(terminal_bp)
app.register_blueprint(runway_bp)
app.register_blueprint(atc_bp)
app.register_blueprint(weather_bp)
app.register_blueprint(flight_bp)
app.register_blueprint(gate_bp)
app.register_blueprint(scheduler_bp)


# =========================================================
# SCHEDULES API
# =========================================================

@app.route("/api/schedules", methods=["GET"])
def api_schedules():
    try:
        schedules = get_all_schedules()

        return jsonify({
            "success": True,
            "total_schedules": len(schedules),
            "schedules": schedules
        }), 200

    except Exception as error:
        app.logger.exception(
            "Unable to fetch scheduled flights"
        )

        return jsonify({
            "success": False,
            "message": "Unable to fetch scheduled flights",
            "error": str(error),
            "schedules": []
        }), 500


# =========================================================
# FRONTEND PAGES
# =========================================================

@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# /airports is reserved for the Airport API.

@app.route("/manage-airports")
def airports_page():
    return render_template("airports.html")


@app.route("/manage-flights")
def flights_page():
    return render_template("flights.html")


@app.route("/scheduler")
def scheduler_page():
    return render_template("scheduler.html")


@app.route("/schedules")
def schedules_page():
    return render_template("schedules.html")


@app.route("/analytics")
def analytics_page():
    return render_template("analytics.html")


# =========================================================
# APPLICATION HEALTH CHECK
# =========================================================

@app.route("/health")
def health_check():
    return jsonify({
        "success": True,
        "message": (
            "Intelligent Airport Runway Scheduling System "
            "is running"
        )
    }), 200


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)
