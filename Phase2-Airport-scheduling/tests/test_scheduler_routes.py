import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from flask import Flask
from routes.scheduler_routes import scheduler_bp
from scheduler import runway_allocator


class SchedulerRouteTests(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2026, 11, 13, 10, 0)
        self.flight = {
            "flight_id": 25,
            "flight_number": "PBL102",
            "airport_id": 25,
            "aircraft_id": 12,
            "operation_type": "ARRIVAL",
            "arrival_time": self.start,
            "departure_time": None,
            "processing_time_minutes": 10,
            "priority": 1,
            "situation_priority": 2,
            "current_situation": "EMERGENCY",
            "required_runway_type": "MEDIUM",
            "status": "WAITING"
        }
        app = Flask(__name__)
        app.register_blueprint(scheduler_bp)
        self.client = app.test_client()

    def test_preview_uses_algorithm_order_without_allocating(self):
        with patch(
            "routes.scheduler_routes.get_waiting_flights",
            return_value=[self.flight]
        ), patch("routes.scheduler_routes.create_scheduler_run") as create_run, \
             patch("routes.scheduler_routes.save_schedule") as save, \
             patch("routes.scheduler_routes.update_flight_status") as update:
            response = self.client.post(
                "/scheduler/preview/25",
                json={"algorithm": "PRIORITY"}
            )

        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["queue"][0]["flight_number"], "PBL102")
        self.assertEqual(payload["queue"][0]["queue_position"], 1)
        create_run.assert_not_called()
        save.assert_not_called()
        update.assert_not_called()

    def test_preview_all_returns_gantt_segments_for_each_algorithm(self):
        long_flight = dict(
            self.flight,
            flight_id=25,
            processing_time_minutes=20
        )
        short_flight = dict(
            self.flight,
            flight_id=26,
            flight_number="PBL103",
            arrival_time=self.start + timedelta(minutes=2),
            processing_time_minutes=2
        )

        with patch(
            "routes.scheduler_routes.get_waiting_flights",
            return_value=[long_flight, short_flight]
        ) as get_flights, patch(
            "routes.scheduler_routes.create_scheduler_run"
        ) as create_run, \
             patch("routes.scheduler_routes.save_schedule") as save, \
             patch("routes.scheduler_routes.update_flight_status") as update:
            response = self.client.post(
                "/scheduler/preview/all/25",
                json={"time_quantum": 3}
            )

        payload = response.get_json()
        self.assertEqual(response.status_code, 200, payload)
        get_flights.assert_called_once_with(25, include_scheduled=True)
        self.assertEqual(payload["flight_count"], 2)
        self.assertEqual(
            payload["input_flights"],
            [
                {"flight_id": 25, "flight_number": "PBL102"},
                {"flight_id": 26, "flight_number": "PBL103"}
            ]
        )
        self.assertEqual(
            [chart["algorithm"] for chart in payload["charts"]],
            [
                "FCFS", "SJF", "SRTF", "PRIORITY",
                "ROUND_ROBIN", "HRRN", "MLQ", "MLFQ"
            ]
        )
        self.assertTrue(all(chart["segments"] for chart in payload["charts"]))
        self.assertTrue(all("metrics" in chart for chart in payload["charts"]))
        srtf_chart = next(
            chart for chart in payload["charts"]
            if chart["algorithm"] == "SRTF"
        )
        self.assertGreater(len(srtf_chart["segments"]), 2)
        create_run.assert_not_called()
        save.assert_not_called()
        update.assert_not_called()

    def test_invalid_flight_time_returns_specific_reason(self):
        invalid_flight = dict(self.flight, arrival_time="invalid timestamp")
        with patch(
            "routes.scheduler_routes.get_waiting_flights",
            return_value=[invalid_flight]
        ):
            response = self.client.post(
                "/scheduler/run/25",
                json={"algorithm": "FCFS"}
            )

        payload = response.get_json()
        self.assertEqual(response.status_code, 422)
        self.assertIn("Invalid arrival_time", payload["failed"][0]["reason"])
        self.assertIn("PBL102", payload["failed"][0]["reason"])

    def test_priority_run_persists_valid_algorithm_times(self):
        runway = {
            "runway_id": 1,
            "runway_code": "RWY-A",
            "runway_type": "HEAVY"
        }
        atc = {
            "atc_id": 2,
            "employee_code": "ATC-2",
            "controller_name": "Controller"
        }

        def save_schedule(**kwargs):
            return {
                "schedule_id": 99,
                "scheduled_start": kwargs["scheduled_start"],
                "scheduled_end": kwargs["scheduled_end"],
                "waiting_time_minutes": kwargs["waiting_time_minutes"],
                "turnaround_time_minutes": kwargs["turnaround_time_minutes"],
                "response_time_minutes": kwargs["response_time_minutes"]
            }

        with patch(
            "routes.scheduler_routes.get_waiting_flights",
            return_value=[self.flight]
        ), patch(
            "routes.scheduler_routes.check_weather",
            return_value={"safe": True}
        ), patch(
            "routes.scheduler_routes.select_best_runway",
            return_value=runway
        ), patch(
            "routes.scheduler_routes.select_atc",
            return_value=atc
        ), patch(
            "routes.scheduler_routes.create_scheduler_run",
            return_value=7
        ), patch(
            "routes.scheduler_routes.save_schedule",
            side_effect=save_schedule
        ) as save, patch(
            "routes.scheduler_routes.update_flight_status"
        ), patch(
            "routes.scheduler_routes.update_flight_situation"
        ), patch(
            "routes.scheduler_routes.update_scheduler_run_metrics"
        ), patch(
            "routes.scheduler_routes.complete_scheduler_run"
        ):
            response = self.client.post(
                "/scheduler/run/25",
                json={"algorithm": "PRIORITY"}
            )

        payload = response.get_json()
        self.assertEqual(response.status_code, 200, payload)
        self.assertEqual(payload["scheduled_flights"], 1)
        self.assertEqual(payload["failed_flights"], 0)
        self.assertEqual(
            payload["scheduled"][0]["scheduled_start"],
            self.start.isoformat()
        )
        self.assertEqual(
            payload["scheduled"][0]["scheduled_end"],
            (self.start + timedelta(minutes=10)).isoformat()
        )
        save.assert_called_once()

    def test_srtf_persists_non_overlapping_execution_segments(self):
        second_flight = dict(
            self.flight,
            flight_id=26,
            flight_number="PBL103",
            arrival_time=self.start + timedelta(minutes=2),
            processing_time_minutes=2,
            current_situation="NORMAL",
            situation_priority=6,
            priority=2
        )
        runway = {
            "runway_id": 1,
            "runway_code": "RWY-A",
            "runway_type": "HEAVY"
        }
        atc = {
            "atc_id": 2,
            "employee_code": "ATC-2",
            "controller_name": "Controller"
        }
        saved_intervals = []

        def save_schedule(**kwargs):
            saved_intervals.append((
                kwargs["scheduled_start"],
                kwargs["scheduled_end"]
            ))
            return {
                "schedule_id": len(saved_intervals),
                "scheduled_start": kwargs["scheduled_start"],
                "scheduled_end": kwargs["scheduled_end"]
            }

        with patch(
            "routes.scheduler_routes.get_waiting_flights",
            return_value=[self.flight, second_flight]
        ), patch(
            "routes.scheduler_routes.check_weather",
            return_value={"safe": True}
        ), patch(
            "routes.scheduler_routes.select_best_runway",
            return_value=runway
        ), patch(
            "routes.scheduler_routes.select_atc",
            return_value=atc
        ), patch(
            "routes.scheduler_routes.create_scheduler_run",
            return_value=7
        ), patch(
            "routes.scheduler_routes.save_schedule",
            side_effect=save_schedule
        ), patch(
            "routes.scheduler_routes.update_flight_status"
        ), patch(
            "routes.scheduler_routes.update_flight_situation"
        ), patch(
            "routes.scheduler_routes.update_scheduler_run_metrics"
        ), patch(
            "routes.scheduler_routes.complete_scheduler_run"
        ):
            response = self.client.post(
                "/scheduler/run/25",
                json={"algorithm": "SRTF"}
            )

        payload = response.get_json()
        self.assertEqual(response.status_code, 200, payload)
        self.assertEqual(len(payload["execution_timeline"]), 3)
        self.assertEqual(len(saved_intervals), 3)
        ordered_intervals = sorted(saved_intervals)
        for previous, current in zip(
            ordered_intervals,
            ordered_intervals[1:]
        ):
            self.assertLessEqual(previous[1], current[0])

    def test_runway_allocator_rejects_reserved_overlaps(self):
        runway = {"runway_id": 1}
        segment_start = self.start + timedelta(minutes=5)
        segment_end = self.start + timedelta(minutes=10)
        reservation = {
            "runway_id": 1,
            "scheduled_start": self.start,
            "scheduled_end": self.start + timedelta(minutes=6)
        }

        with patch.object(
            runway_allocator,
            "get_available_runways",
            return_value=[runway]
        ), patch.object(
            runway_allocator,
            "is_runway_free",
            return_value=True
        ):
            selected = runway_allocator.select_best_runway(
                airport_id=25,
                operation_type="ARRIVAL",
                aircraft_type="MEDIUM",
                scheduled_start=segment_start,
                scheduled_end=segment_end,
                reserved_intervals=[reservation]
            )

        self.assertIsNone(selected)


if __name__ == "__main__":
    unittest.main()
