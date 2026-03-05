"""
test_id_generator.py
Unit tests for IDGenerator in id_generator.py
"""

import unittest
from datetime import date, timedelta

from id_generator import IDGenerator, id_gen


# ─────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────
def make_gen() -> IDGenerator:
    """Return a fresh IDGenerator for each test."""
    return IDGenerator()


# ═════════════════════════════════════════════
# FORMAT TESTS
# ═════════════════════════════════════════════
class TestBookingID(unittest.TestCase):

    def setUp(self):
        self.gen = make_gen()

    def test_format_with_given_date(self):
        future_date = date.today() + timedelta(days=1)
        result = self.gen.booking_id(future_date)
        expected = f"B-{future_date.strftime('%Y%m%d')}-001"
        self.assertEqual(result, expected)

    def test_format_defaults_to_today(self):
        today_str = date.today().strftime("%Y%m%d")
        result = self.gen.booking_id()
        self.assertTrue(result.startswith(f"B-{today_str}-"))

    def test_counter_increments(self):
        d = date.today()
        first  = self.gen.booking_id(d)
        second = self.gen.booking_id(d)
        third  = self.gen.booking_id(d)
        self.assertTrue(first.endswith("-001"))
        self.assertTrue(second.endswith("-002"))
        self.assertTrue(third.endswith("-003"))

    def test_max_allowed_date(self):
        max_date = date.today() + timedelta(days=30)
        result = self.gen.booking_id(max_date)
        self.assertIn(max_date.strftime("%Y%m%d"), result)

    def test_past_date_raises(self):
        with self.assertRaises(ValueError):
            self.gen.booking_id(date.today() - timedelta(days=1))

    def test_over_30_days_raises(self):
        with self.assertRaises(ValueError):
            self.gen.booking_id(date.today() + timedelta(days=31))

    def test_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.gen.booking_id("2025-06-01")

    def test_wrong_type_int_raises(self):
        with self.assertRaises(TypeError):
            self.gen.booking_id(20250601)


class TestTicketID(unittest.TestCase):

    def setUp(self):
        self.gen = make_gen()

    def test_format(self):
        self.assertEqual(self.gen.ticket_id(), "T-001")

    def test_counter_increments(self):
        self.assertEqual(self.gen.ticket_id(), "T-001")
        self.assertEqual(self.gen.ticket_id(), "T-002")
        self.assertEqual(self.gen.ticket_id(), "T-003")

    def test_zero_padding(self):
        for _ in range(41):
            self.gen.ticket_id()
        self.assertEqual(self.gen.ticket_id(), "T-042")


class TestTripID(unittest.TestCase):

    def setUp(self):
        self.gen = make_gen()

    def test_format(self):
        self.assertEqual(self.gen.trip_id(), "TR-001")

    def test_counter_increments(self):
        self.assertEqual(self.gen.trip_id(), "TR-001")
        self.assertEqual(self.gen.trip_id(), "TR-002")

    def test_zero_padding(self):
        for _ in range(6):
            self.gen.trip_id()
        self.assertEqual(self.gen.trip_id(), "TR-007")


class TestMemberID(unittest.TestCase):

    def setUp(self):
        self.gen = make_gen()

    def test_format(self):
        self.assertEqual(self.gen.member_id(), "M-001")

    def test_counter_increments(self):
        self.assertEqual(self.gen.member_id(), "M-001")
        self.assertEqual(self.gen.member_id(), "M-002")

    def test_zero_padding(self):
        for _ in range(14):
            self.gen.member_id()
        self.assertEqual(self.gen.member_id(), "M-015")


class TestStaffID(unittest.TestCase):

    def setUp(self):
        self.gen = make_gen()

    def test_format(self):
        self.assertEqual(self.gen.staff_id(), "S-001")

    def test_counter_increments(self):
        self.assertEqual(self.gen.staff_id(), "S-001")
        self.assertEqual(self.gen.staff_id(), "S-002")

    def test_zero_padding(self):
        for _ in range(2):
            self.gen.staff_id()
        self.assertEqual(self.gen.staff_id(), "S-003")


class TestZoneID(unittest.TestCase):

    def setUp(self):
        self.gen = make_gen()

    def test_format(self):
        self.assertEqual(self.gen.zone_id(), "Z-01")

    def test_counter_increments(self):
        self.assertEqual(self.gen.zone_id(), "Z-01")
        self.assertEqual(self.gen.zone_id(), "Z-02")

    def test_two_digit_padding(self):
        for _ in range(9):
            self.gen.zone_id()
        self.assertEqual(self.gen.zone_id(), "Z-10")


class TestCageID(unittest.TestCase):

    def setUp(self):
        self.gen = make_gen()

    def test_format(self):
        self.assertEqual(self.gen.cage_id(), "C-001")

    def test_counter_increments(self):
        self.assertEqual(self.gen.cage_id(), "C-001")
        self.assertEqual(self.gen.cage_id(), "C-002")

    def test_zero_padding(self):
        for _ in range(11):
            self.gen.cage_id()
        self.assertEqual(self.gen.cage_id(), "C-012")


# ═════════════════════════════════════════════
# COUNTER INDEPENDENCE TESTS
# ═════════════════════════════════════════════
class TestCounterIndependence(unittest.TestCase):

    def setUp(self):
        self.gen = make_gen()

    def test_counters_are_independent(self):
        """Each entity type has its own counter."""
        self.gen.ticket_id()
        self.gen.ticket_id()
        self.gen.trip_id()
        # ticket counter = 2, trip counter = 1
        self.assertEqual(self.gen.ticket_id(), "T-003")
        self.assertEqual(self.gen.trip_id(), "TR-002")

    def test_different_instances_are_independent(self):
        gen1 = IDGenerator()
        gen2 = IDGenerator()
        gen1.ticket_id()
        gen1.ticket_id()
        # gen2 starts from 1 regardless of gen1
        self.assertEqual(gen2.ticket_id(), "T-001")


# ═════════════════════════════════════════════
# RESET TESTS
# ═════════════════════════════════════════════
class TestReset(unittest.TestCase):

    def setUp(self):
        self.gen = make_gen()

    def test_reset_single_entity(self):
        self.gen.ticket_id()
        self.gen.ticket_id()
        self.gen.reset("ticket")
        self.assertEqual(self.gen.ticket_id(), "T-001")

    def test_reset_single_does_not_affect_others(self):
        self.gen.ticket_id()
        self.gen.trip_id()
        self.gen.reset("ticket")
        # trip counter still at 1
        self.assertEqual(self.gen.trip_id(), "TR-002")

    def test_reset_all(self):
        self.gen.ticket_id()
        self.gen.trip_id()
        self.gen.member_id()
        self.gen.reset()
        self.assertEqual(self.gen.ticket_id(),  "T-001")
        self.assertEqual(self.gen.trip_id(),    "TR-001")
        self.assertEqual(self.gen.member_id(),  "M-001")

    def test_reset_unknown_entity_raises(self):
        with self.assertRaises(ValueError):
            self.gen.reset("vehicle")

    def test_reset_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.gen.reset(123)

    def test_reset_empty_string_raises(self):
        with self.assertRaises(TypeError):
            self.gen.reset("")

    def test_reset_none_resets_all(self):
        self.gen.ticket_id()
        self.gen.reset(None)
        self.assertEqual(self.gen.current("ticket"), 0)


# ═════════════════════════════════════════════
# CURRENT TESTS
# ═════════════════════════════════════════════
class TestCurrent(unittest.TestCase):

    def setUp(self):
        self.gen = make_gen()

    def test_current_starts_at_zero(self):
        self.assertEqual(self.gen.current("ticket"), 0)

    def test_current_after_generate(self):
        self.gen.ticket_id()
        self.gen.ticket_id()
        self.assertEqual(self.gen.current("ticket"), 2)

    def test_current_does_not_increment(self):
        self.gen.ticket_id()
        self.gen.current("ticket")
        self.gen.current("ticket")
        self.assertEqual(self.gen.current("ticket"), 1)

    def test_current_unknown_entity_raises(self):
        with self.assertRaises(ValueError):
            self.gen.current("round")

    def test_current_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.gen.current(None)

    def test_current_empty_string_raises(self):
        with self.assertRaises(TypeError):
            self.gen.current("   ")


# ═════════════════════════════════════════════
# SINGLETON TESTS
# ═════════════════════════════════════════════
class TestSingleton(unittest.TestCase):

    def setUp(self):
        id_gen.reset()

    def test_singleton_shared_across_imports(self):
        from id_generator import id_gen as id_gen2
        id_gen.ticket_id()
        # Same instance — counter should be 1
        self.assertEqual(id_gen2.current("ticket"), 1)

    def test_singleton_is_idgenerator_instance(self):
        self.assertIsInstance(id_gen, IDGenerator)


# ─────────────────────────────────────────────
if __name__ == "__main__":
    unittest.main(verbosity=2)