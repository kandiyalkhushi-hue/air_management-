import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from scheduler.schedule_manager import is_runway_free


class RunwayConflictTests(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2026, 11, 16, 6, 0)
        self.end = self.start + timedelta(minutes=8)
        self.cursor = Mock()
        self.cursor.fetchone.return_value = (0,)
        self.connection = Mock()
        self.connection.cursor.return_value = self.cursor

    def test_terminal_own_schedule_is_excluded_but_others_and_active_runs_block(self):
        with patch(
            "scheduler.schedule_manager.get_db_connection",
            return_value=self.connection
        ):
            self.assertTrue(is_runway_free(
                7,
                self.start,
                self.end,
                flight_id=22
            ))

        query, parameters = self.cursor.execute.call_args.args
        self.assertIn("LEFT JOIN scheduler_runs", query)
        self.assertIn("s.flight_id <> %s", query)
        self.assertIn("s.status = 'IN_PROGRESS'", query)
        self.assertIn("sr.status NOT IN ('COMPLETED', 'FAILED')", query)
        self.assertEqual(parameters, (7, self.end, self.start, 22))
        self.cursor.close.assert_called_once()
        self.connection.close.assert_called_once()

    def test_calls_without_flight_id_keep_all_overlaps_as_blockers(self):
        with patch(
            "scheduler.schedule_manager.get_db_connection",
            return_value=self.connection
        ):
            self.assertTrue(is_runway_free(7, self.start, self.end))

        query, parameters = self.cursor.execute.call_args.args
        self.assertNotIn("s.flight_id <>", query)
        self.assertEqual(parameters, (7, self.end, self.start))


if __name__ == "__main__":
    unittest.main()
