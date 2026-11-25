import unittest

from locker import Hold, LockerBank


class LockerTests(unittest.TestCase):
    def test_request_is_idempotent_and_uses_lowest_available_locker(self):
        bank = LockerBank(2)
        self.assertEqual(bank.request("Kay"), Hold("Kay", 1, 10))
        bank.advance(3)
        self.assertEqual(bank.request("Kay"), Hold("Kay", 1, 10))
        self.assertEqual(bank.request("Lee"), Hold("Lee", 2, 13))

    def test_hold_expires_at_deadline(self):
        bank = LockerBank(1)
        hold = bank.request("Lee")
        bank.advance(9)
        self.assertEqual(bank.lookup("Lee"), hold)
        bank.advance(10)
        self.assertIsNone(bank.lookup("Lee"))

    def test_time_jump_processes_successive_promotions(self):
        bank = LockerBank(1)
        for customer in ("Lee", "Bo", "Kay", "Jo"):
            bank.request(customer)
        bank.advance(23)
        self.assertEqual(bank.lookup("Kay"), Hold("Kay", 1, 30))
        self.assertIsNone(bank.lookup("Jo"))

    def test_waitlist_cancellation_and_duplicate_requests(self):
        bank = LockerBank(1)
        for customer in ("Lee", "Bo", "Bo", "Kay", "Jo"):
            bank.request(customer)
        bank.cancel("Kay")
        bank.advance(2)
        bank.cancel("Lee")
        self.assertEqual(bank.lookup("Bo"), Hold("Bo", 1, 12))
        bank.advance(12)
        self.assertEqual(bank.lookup("Jo"), Hold("Jo", 1, 22))

    def test_clock_cannot_rewind(self):
        bank = LockerBank(1)
        bank.advance(7)
        with self.assertRaises(ValueError):
            bank.advance(6)

    def test_evening_shift_replay(self):
        bank = LockerBank(2)
        bank.request("Mira")
        bank.advance(1)
        bank.request("Sol")
        bank.request("Alex")
        bank.advance(3)
        bank.cancel("Mira")
        bank.request("Mira")
        bank.request("Dev")
        bank.advance(4)
        bank.cancel("Sol")
        bank.advance(11)
        self.assertIsNone(bank.lookup("Dev"), "Dev received an early pickup notice")
