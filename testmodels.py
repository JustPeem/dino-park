"""
test_models.py
Unit tests for Person 1 models:
  - Coupon
  - Ticket
  - User / Member / GuestUser
  - Staff / Manager / Ranger / TicketStaff / Driver
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from coupon import Coupon
from ticket import Ticket, TICKET_PRICES
from users import Member, GuestUser
from staff import Manager, Ranger, TicketStaff, Driver


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def future(days=30) -> datetime:
    return datetime.now() + timedelta(days=days)


def make_coupon(code="SAVE50", amount=50.0, days=30) -> Coupon:
    return Coupon(code, amount, future(days))


def make_member(name="Alice", phone="0812345678") -> Member:
    return Member(name, phone)


def make_round_mock():
    return MagicMock()  # Round is Person 2's responsibility


# ═════════════════════════════════════════════
# COUPON TESTS
# ═════════════════════════════════════════════
class TestCouponInit(unittest.TestCase):

    def test_valid_creation(self):
        c = make_coupon()
        self.assertEqual(c.coupon_code, "SAVE50")
        self.assertEqual(c.discount_amount, 50.0)
        self.assertFalse(c.is_used)

    def test_empty_code_raises(self):
        with self.assertRaises(ValueError):
            Coupon("", 50.0, future())

    def test_whitespace_code_raises(self):
        with self.assertRaises(ValueError):
            Coupon("   ", 50.0, future())

    def test_negative_discount_raises(self):
        with self.assertRaises(ValueError):
            Coupon("CODE", -10.0, future())

    def test_zero_discount_raises(self):
        with self.assertRaises(ValueError):
            Coupon("CODE", 0, future())

    def test_past_expiry_raises(self):
        with self.assertRaises(ValueError):
            Coupon("CODE", 50.0, datetime.now() - timedelta(days=1))

    def test_invalid_expiry_type_raises(self):
        with self.assertRaises(TypeError):
            Coupon("CODE", 50.0, "2099-01-01")


class TestCouponCreate(unittest.TestCase):

    def test_create_with_expiry(self):
        exp = future(10)
        c = Coupon.create("VIP10", 100.0, exp)
        self.assertEqual(c.coupon_code, "VIP10")
        self.assertEqual(c.discount_amount, 100.0)

    def test_create_without_expiry_defaults_30_days(self):
        c = Coupon.create("AUTO", 20.0)
        expected = datetime.now() + timedelta(days=30)
        diff = abs((c.expiry_date - expected).total_seconds())
        self.assertLess(diff, 5)  # within 5 seconds


class TestCouponBehavior(unittest.TestCase):

    def test_is_valid_when_unused_and_not_expired(self):
        c = make_coupon()
        self.assertTrue(c.is_valid())

    def test_is_invalid_after_mark_used(self):
        c = make_coupon()
        c.mark_used()
        self.assertFalse(c.is_valid())
        self.assertTrue(c.is_used)

    def test_is_invalid_when_expired(self):
        # Create with very short expiry — use internal trick via create
        exp = datetime.now() + timedelta(seconds=1)
        c = Coupon("EXP", 50.0, exp)
        import time; time.sleep(1.1)
        self.assertFalse(c.is_valid())

    def test_mark_used_twice_stays_used(self):
        c = make_coupon()
        c.mark_used()
        c.mark_used()
        self.assertTrue(c.is_used)

    def test_repr(self):
        c = make_coupon("CODE", 50.0)
        self.assertIn("CODE", repr(c))
        self.assertIn("50.0", repr(c))


# ═════════════════════════════════════════════
# TICKET TESTS
# ═════════════════════════════════════════════
class TestTicketInit(unittest.TestCase):

    def test_valid_adult_ticket(self):
        t = Ticket("T-001", make_round_mock(), 1, "adult")
        self.assertEqual(t.ticket_id, "T-001")
        self.assertEqual(t.price, 500.0)
        self.assertEqual(t.type, "adult")
        self.assertEqual(t.seat_number, 1)
        self.assertFalse(t.is_used)

    def test_all_ticket_types_price(self):
        for ttype, expected_price in TICKET_PRICES.items():
            t = Ticket("T-001", make_round_mock(), 1, ttype)
            self.assertEqual(t.price, expected_price)

    def test_invalid_ticket_id_format_raises(self):
        with self.assertRaises(ValueError):
            Ticket("TK001", make_round_mock(), 1)

    def test_ticket_id_too_short_raises(self):
        with self.assertRaises(ValueError):
            Ticket("T-01", make_round_mock(), 1)

    def test_invalid_ticket_type_raises(self):
        with self.assertRaises(ValueError):
            Ticket("T-001", make_round_mock(), 1, "vip")

    def test_zero_seat_number_raises(self):
        with self.assertRaises(ValueError):
            Ticket("T-001", make_round_mock(), 0)

    def test_negative_seat_number_raises(self):
        with self.assertRaises(ValueError):
            Ticket("T-001", make_round_mock(), -1)

    def test_none_round_raises(self):
        with self.assertRaises(ValueError):
            Ticket("T-001", None, 1)


class TestTicketCreate(unittest.TestCase):

    def test_create_factory(self):
        t = Ticket.create("T-042", make_round_mock(), 5, "child")
        self.assertEqual(t.ticket_id, "T-042")
        self.assertEqual(t.price, 300.0)


class TestTicketBehavior(unittest.TestCase):

    def setUp(self):
        self.ticket = Ticket("T-001", make_round_mock(), 1, "adult")

    def test_initial_is_not_used(self):
        self.assertFalse(self.ticket.is_used)
        self.assertFalse(self.ticket.check_is_used())

    def test_set_used_true(self):
        self.ticket.set_used(True)
        self.assertTrue(self.ticket.is_used)
        self.assertTrue(self.ticket.check_is_used())

    def test_set_used_false(self):
        self.ticket.set_used(True)
        self.ticket.set_used(False)
        self.assertFalse(self.ticket.is_used)

    def test_set_used_invalid_type_raises(self):
        with self.assertRaises(TypeError):
            self.ticket.set_used("yes")

    def test_get_price_static(self):
        self.assertEqual(Ticket.get_price("senior"), 250.0)
        self.assertEqual(Ticket.get_price("feeding"), 150.0)

    def test_get_price_invalid_raises(self):
        with self.assertRaises(ValueError):
            Ticket.get_price("premium")

    def test_repr(self):
        self.assertIn("T-001", repr(self.ticket))
        self.assertIn("adult", repr(self.ticket))


# ═════════════════════════════════════════════
# USERS TESTS
# ═════════════════════════════════════════════
class TestUserInit(unittest.TestCase):

    def test_member_valid(self):
        m = Member("Alice", "0812345678")
        self.assertEqual(m.name, "Alice")
        self.assertEqual(m.phone_number, "0812345678")
        self.assertEqual(m.user_type, "member")

    def test_guest_valid(self):
        g = GuestUser("Bob", "0899999999")
        self.assertEqual(g.user_type, "guest")

    def test_empty_name_raises(self):
        with self.assertRaises(ValueError):
            Member("", "0812345678")

    def test_whitespace_name_raises(self):
        with self.assertRaises(ValueError):
            Member("   ", "0812345678")

    def test_invalid_phone_too_short_raises(self):
        with self.assertRaises(ValueError):
            Member("Alice", "081234")

    def test_invalid_phone_letters_raises(self):
        with self.assertRaises(ValueError):
            Member("Alice", "081234567X")

    def test_invalid_phone_11_digits_raises(self):
        with self.assertRaises(ValueError):
            Member("Alice", "08123456789")

    def test_name_stripped(self):
        m = Member("  Alice  ", "0812345678")
        self.assertEqual(m.name, "Alice")


class TestMemberCoupon(unittest.TestCase):

    def setUp(self):
        self.member = make_member()
        self.coupon = make_coupon("SAVE50", 50.0)

    def test_add_coupon(self):
        self.member.add_coupon(self.coupon)
        self.assertEqual(len(self.member.coupons), 1)

    def test_add_invalid_coupon_type_raises(self):
        with self.assertRaises(TypeError):
            self.member.add_coupon("not-a-coupon")

    def test_get_valid_coupons(self):
        self.member.add_coupon(self.coupon)
        valid = self.member.get_valid_coupons()
        self.assertEqual(len(valid), 1)

    def test_get_valid_coupons_excludes_used(self):
        self.member.add_coupon(self.coupon)
        self.coupon.mark_used()
        self.assertEqual(len(self.member.get_valid_coupons()), 0)

    def test_use_coupon_success_returns_discount_amount(self):
        self.member.add_coupon(self.coupon)
        discount = self.member.use_coupon("SAVE50", 500.0)
        self.assertEqual(discount, 50.0)
        self.assertTrue(self.coupon.is_used)

    def test_use_coupon_not_found_returns_zero(self):
        discount = self.member.use_coupon("NOCODE", 500.0)
        self.assertEqual(discount, 0.0)

    def test_use_coupon_already_used_returns_zero(self):
        self.member.add_coupon(self.coupon)
        self.coupon.mark_used()
        discount = self.member.use_coupon("SAVE50", 500.0)
        self.assertEqual(discount, 0.0)

    def test_use_coupon_marks_coupon_used(self):
        self.member.add_coupon(self.coupon)
        self.member.use_coupon("SAVE50", 500.0)
        self.assertTrue(self.coupon.is_used)

    def test_use_coupon_cannot_use_twice(self):
        self.member.add_coupon(self.coupon)
        self.member.use_coupon("SAVE50", 500.0)
        second = self.member.use_coupon("SAVE50", 500.0)
        self.assertEqual(second, 0.0)

    def test_use_coupon_empty_code_raises(self):
        with self.assertRaises(ValueError):
            self.member.use_coupon("", 500.0)

    def test_use_coupon_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.member.use_coupon("SAVE50", -100.0)


class TestMemberCalculateDiscount(unittest.TestCase):

    def setUp(self):
        self.member = make_member()

    def test_member_discount_only(self):
        # 1000 * 0.90 = 900
        result = self.member.calculate_discount(1000.0, seats=1)
        self.assertAlmostEqual(result, 900.0)

    def test_group_discount(self):
        # 1000 * 0.90 * 0.95 = 855
        result = self.member.calculate_discount(1000.0, seats=10)
        self.assertAlmostEqual(result, 855.0)

    def test_group_discount_not_applied_below_10(self):
        result = self.member.calculate_discount(1000.0, seats=9)
        self.assertAlmostEqual(result, 900.0)

    def test_coupon_discount_passed_directly(self):
        # discount passed in directly from use_coupon()
        # 1000 * 0.90 - 50 = 850
        result = self.member.calculate_discount(1000.0, seats=1, discount=50.0)
        self.assertAlmostEqual(result, 850.0)

    def test_all_discounts_combined(self):
        # 1000 * 0.90 * 0.95 - 50 = 805
        result = self.member.calculate_discount(1000.0, seats=10, discount=50.0)
        self.assertAlmostEqual(result, 805.0)

    def test_full_flow_use_coupon_then_calculate(self):
        """Simulate sequence diagram: use_coupon() → discount → calculate_discount(discount)"""
        coupon = make_coupon("C50", 50.0)
        self.member.add_coupon(coupon)
        discount = self.member.use_coupon("C50", 1000.0)       # step 1
        result = self.member.calculate_discount(1000.0, seats=1, discount=discount)  # step 2
        self.assertAlmostEqual(result, 850.0)
        self.assertTrue(coupon.is_used)

    def test_result_not_negative(self):
        result = self.member.calculate_discount(100.0, discount=9999.0)
        self.assertEqual(result, 0.0)

    def test_negative_base_price_raises(self):
        with self.assertRaises(ValueError):
            self.member.calculate_discount(-100.0)

    def test_zero_seats_raises(self):
        with self.assertRaises(ValueError):
            self.member.calculate_discount(1000.0, seats=0)

    def test_negative_discount_raises(self):
        with self.assertRaises(ValueError):
            self.member.calculate_discount(1000.0, discount=-50.0)


# ═════════════════════════════════════════════
# STAFF TESTS
# ═════════════════════════════════════════════
class TestStaffInit(unittest.TestCase):

    def test_manager_valid(self):
        m = Manager(1, "John")
        self.assertEqual(m.staff_id, 1)
        self.assertEqual(m.name, "John")

    def test_negative_staff_id_raises(self):
        with self.assertRaises(ValueError):
            Manager(-1, "John")

    def test_empty_name_raises(self):
        with self.assertRaises(ValueError):
            Manager(1, "")

    def test_whitespace_name_raises(self):
        with self.assertRaises(ValueError):
            Manager(1, "   ")

    def test_name_stripped(self):
        m = Manager(1, "  John  ")
        self.assertEqual(m.name, "John")

    def test_login(self):
        m = Manager(1, "John")
        self.assertTrue(m.login())


class TestManager(unittest.TestCase):

    def setUp(self):
        self.manager = Manager(1, "Boss")

    def test_approve_refill(self):
        self.assertTrue(self.manager.approve_refill(1))

    def test_approve_refill_invalid_zone_raises(self):
        with self.assertRaises(ValueError):
            self.manager.approve_refill(-1)

    def test_notify_refill_completed(self):
        self.assertTrue(self.manager.notify_refill_completed(1))

    def test_receive_food_low_notification(self):
        # Should not raise
        self.manager.receive_food_low_notification(1, "meat")

    def test_receive_food_low_empty_food_type_raises(self):
        with self.assertRaises(ValueError):
            self.manager.receive_food_low_notification(1, "")

    def test_request_create_trip_valid(self):
        zone = MagicMock(); zone.zone_id = 1
        vehicle = MagicMock(); vehicle.vehicle_id = 10
        driver = Driver(2, "Dave", 999)
        tomorrow = datetime.now() + timedelta(days=1)
        start = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        # Should not raise
        self.manager.request_create_trip(zone, vehicle, driver, start, end)

    def test_request_create_trip_in_past_raises(self):
        zone = MagicMock(); zone.zone_id = 1
        vehicle = MagicMock(); vehicle.vehicle_id = 10
        driver = Driver(2, "Dave", 999)
        past = datetime(2020, 1, 1, 9, 0)
        end = past + timedelta(hours=1)
        with self.assertRaises(ValueError):
            self.manager.request_create_trip(zone, vehicle, driver, past, end)

    def test_request_create_trip_wrong_duration_raises(self):
        zone = MagicMock(); zone.zone_id = 1
        vehicle = MagicMock(); vehicle.vehicle_id = 10
        driver = Driver(2, "Dave", 999)
        tomorrow = datetime.now() + timedelta(days=1)
        start = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=2)
        with self.assertRaises(ValueError):
            self.manager.request_create_trip(zone, vehicle, driver, start, end)

    def test_request_create_trip_outside_slot_raises(self):
        zone = MagicMock(); zone.zone_id = 1
        vehicle = MagicMock(); vehicle.vehicle_id = 10
        driver = Driver(2, "Dave", 999)
        tomorrow = datetime.now() + timedelta(days=1)
        start = tomorrow.replace(hour=8, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        with self.assertRaises(ValueError):
            self.manager.request_create_trip(zone, vehicle, driver, start, end)

    def test_request_create_trip_none_zone_raises(self):
        vehicle = MagicMock(); vehicle.vehicle_id = 10
        driver = Driver(2, "Dave", 999)
        tomorrow = datetime.now() + timedelta(days=1)
        start = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        with self.assertRaises(ValueError):
            self.manager.request_create_trip(None, vehicle, driver, start, end)


class TestRanger(unittest.TestCase):

    def setUp(self):
        self.ranger = Ranger(2, "Rex")

    def test_assign_zone(self):
        zone = MagicMock(); zone.zone_id = 1
        self.ranger.assign_zone(zone)
        self.assertIn(zone, self.ranger.zones)

    def test_assign_zone_not_duplicated(self):
        zone = MagicMock(); zone.zone_id = 1
        self.ranger.assign_zone(zone)
        self.ranger.assign_zone(zone)
        self.assertEqual(len(self.ranger.zones), 1)

    def test_assign_zone_none_raises(self):
        with self.assertRaises(ValueError):
            self.ranger.assign_zone(None)

    def test_request_refill_valid(self):
        self.ranger.request_refill(1)  # Should not raise

    def test_request_refill_negative_raises(self):
        with self.assertRaises(ValueError):
            self.ranger.request_refill(-1)

    def test_add_dino_lunch_valid(self):
        self.ranger.add_dino_lunch(1)  # Should not raise

    def test_add_dino_lunch_negative_raises(self):
        with self.assertRaises(ValueError):
            self.ranger.add_dino_lunch(-5)

    def test_request_food_refill_delegates_to_park(self):
        park = MagicMock()
        park.request_food_refill.return_value = True
        result = self.ranger.request_food_refill(1, park)
        park.request_food_refill.assert_called_once_with(1)
        self.assertTrue(result)

    def test_request_food_refill_none_park_raises(self):
        with self.assertRaises(ValueError):
            self.ranger.request_food_refill(1, None)


class TestTicketStaff(unittest.TestCase):

    def setUp(self):
        self.staff = TicketStaff(3, "Tina")

    def test_check_in_delegates_to_park(self):
        park = MagicMock()
        park.check_in.return_value = True
        result = self.staff.check_in("T-001", park)
        park.check_in.assert_called_once_with("T-001")
        self.assertTrue(result)

    def test_check_in_empty_ticket_id_raises(self):
        park = MagicMock()
        with self.assertRaises(ValueError):
            self.staff.check_in("", park)

    def test_check_in_none_park_raises(self):
        with self.assertRaises(ValueError):
            self.staff.check_in("T-001", None)

    def test_add_food_coupon_delegates_to_park(self):
        park = MagicMock()
        park.issue_food_coupon.return_value = "Coupon issued successfully"
        result = self.staff.add_food_coupon("M-001", park)
        park.issue_food_coupon.assert_called_once_with("M-001")
        self.assertEqual(result, "Coupon issued successfully")

    def test_add_food_coupon_empty_member_id_raises(self):
        park = MagicMock()
        with self.assertRaises(ValueError):
            self.staff.add_food_coupon("", park)

    def test_add_food_coupon_none_park_raises(self):
        with self.assertRaises(ValueError):
            self.staff.add_food_coupon("M-001", None)


class TestDriver(unittest.TestCase):

    def setUp(self):
        self.driver = Driver(4, "Dave", 12345)

    def test_valid_creation(self):
        self.assertEqual(self.driver.license_id, 12345)
        self.assertEqual(self.driver.trips, [])

    def test_negative_license_raises(self):
        with self.assertRaises(ValueError):
            Driver(4, "Dave", -1)

    def test_is_available_no_trips(self):
        start = datetime(2030, 1, 1, 9, 0)
        end = datetime(2030, 1, 1, 10, 0)
        self.assertTrue(self.driver.is_available(start, end))

    def test_is_available_with_conflict(self):
        trip = MagicMock()
        trip.start_time = datetime(2030, 1, 1, 9, 0)
        trip.end_time = datetime(2030, 1, 1, 10, 0)
        self.driver.add_trip(trip)

        # Overlapping time
        start = datetime(2030, 1, 1, 9, 30)
        end = datetime(2030, 1, 1, 10, 30)
        self.assertFalse(self.driver.is_available(start, end))

    def test_is_available_adjacent_no_conflict(self):
        trip = MagicMock()
        trip.start_time = datetime(2030, 1, 1, 9, 0)
        trip.end_time = datetime(2030, 1, 1, 10, 0)
        self.driver.add_trip(trip)

        # Starts exactly when previous ends — no overlap
        start = datetime(2030, 1, 1, 10, 0)
        end = datetime(2030, 1, 1, 11, 0)
        self.assertTrue(self.driver.is_available(start, end))

    def test_is_available_invalid_type_raises(self):
        with self.assertRaises(TypeError):
            self.driver.is_available("2030-01-01", "2030-01-02")

    def test_is_available_start_after_end_raises(self):
        with self.assertRaises(ValueError):
            self.driver.is_available(
                datetime(2030, 1, 1, 11, 0),
                datetime(2030, 1, 1, 9, 0),
            )

    def test_add_trip(self):
        trip = MagicMock()
        trip.trip_id = "TR-001"
        self.driver.add_trip(trip)
        self.assertIn(trip, self.driver.trips)

    def test_add_trip_not_duplicated(self):
        trip = MagicMock()
        trip.trip_id = "TR-001"
        self.driver.add_trip(trip)
        self.driver.add_trip(trip)
        self.assertEqual(len(self.driver.trips), 1)

    def test_add_trip_none_raises(self):
        with self.assertRaises(ValueError):
            self.driver.add_trip(None)


# ─────────────────────────────────────────────
if __name__ == "__main__":
    unittest.main(verbosity=2)