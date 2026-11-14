import unittest
from datetime import datetime, timedelta

from scheduler.algorithm_selector import run_algorithm
from scheduler.metrics import calculate_metrics


class SchedulingAlgorithmTests(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2026, 11, 13, 10, 0)
        self.flights = [
            {
                "flight_id": 101,
                "flight_number": "PBL101",
                "airport_id": 25,
                "aircraft_id": 201,
                "operation_type": "ARRIVAL",
                "arrival_time": self.start.isoformat(),
                "departure_time": None,
                "processing_time_minutes": 5,
                "priority": 2,
                "situation_priority": 6,
                "current_situation": "NORMAL"
            },
            {
                "flight_id": 102,
                "flight_number": "PBL102",
                "airport_id": 25,
                "aircraft_id": 202,
                "operation_type": "ARRIVAL",
                "arrival_time": (self.start + timedelta(minutes=2)),
                "departure_time": None,
                "processing_time_minutes": 2,
                "priority": 1,
                "situation_priority": 2,
                "current_situation": "EMERGENCY"
            }
        ]

    def test_all_algorithms_return_normalized_times(self):
        algorithms = (
            "FCFS", "SJF", "SRTF", "PRIORITY",
            "ROUND_ROBIN", "HRRN", "MLQ", "MLFQ"
        )

        for algorithm in algorithms:
            with self.subTest(algorithm=algorithm):
                results = run_algorithm(
                    algorithm,
                    self.flights,
                    time_quantum=2
                )
                self.assertEqual(len(results), len(self.flights))
                for result in results:
                    self.assertIsNotNone(result["flight_id"])
                    self.assertIsNotNone(result["flight_number"])
                    self.assertIsInstance(result["start_time"], datetime)
                    self.assertIsInstance(result["end_time"], datetime)
                    self.assertGreater(
                        result["end_time"],
                        result["start_time"]
                    )
                    self.assertGreater(result["processing_time"], 0)

    def test_priority_scheduling_calculates_execution_times(self):
        same_request_time = [
            dict(flight, arrival_time=self.start)
            for flight in self.flights
        ]
        results = run_algorithm("PRIORITY", same_request_time)
        emergency = next(
            result for result in results if result["flight_id"] == 102
        )
        self.assertEqual(emergency["start_time"], self.start)
        self.assertEqual(emergency["end_time"], self.start + timedelta(minutes=2))

    def test_preemptive_algorithms_keep_execution_slices(self):
        preemptive_flights = [
            dict(flight, processing_time_minutes=20)
            if flight["flight_id"] == 101 else flight
            for flight in self.flights
        ]
        for algorithm in ("SRTF", "ROUND_ROBIN", "MLFQ"):
            with self.subTest(algorithm=algorithm):
                results = run_algorithm(
                    algorithm,
                    preemptive_flights,
                    time_quantum=2
                )
                self.assertTrue(
                    any(len(result.get("execution_slices", [])) > 1
                        for result in results)
                )
                intervals = sorted(
                    (
                        segment["start_time"],
                        segment["end_time"]
                    )
                    for result in results
                    for segment in result["execution_slices"]
                )
                for previous, current in zip(intervals, intervals[1:]):
                    self.assertLessEqual(previous[1], current[0])

    def test_metrics_use_normalized_processing_time(self):
        results = run_algorithm("FCFS", self.flights)
        metrics = calculate_metrics(results)
        self.assertEqual(metrics["total_processing_time"], 7)
        self.assertEqual(metrics["total_execution_time"], 7)
        self.assertEqual(metrics["throughput"], 0.2857)
        self.assertEqual(metrics["runway_utilization"], 100)

    def test_invalid_request_time_reports_flight_and_field(self):
        invalid = [dict(self.flights[0], arrival_time="not-a-time")]
        with self.assertRaisesRegex(ValueError, "arrival_time.*PBL101"):
            run_algorithm("FCFS", invalid)


if __name__ == "__main__":
    unittest.main()
