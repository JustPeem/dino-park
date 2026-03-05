import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

# นำเข้าเฉพาะ 7 ไฟล์ที่กำหนดเท่านั้น
from zone import Zone
from cage import Cage
from dino import Dino
from driver import Driver
from food import Food
from park import Park
from vehicle import Vehicle

class TestParkSystem(unittest.TestCase):

    def setUp(self):
        """เตรียมข้อมูลพื้นฐานที่ต้องใช้ซ้ำๆ ในหลายการทดสอบ"""
        self.now = datetime.now()
        print("\n" + "="*70)
        print(f"[🚀 เริ่มเทสต์] : {self._testMethodName}")

    # ==========================================
    # 1. Food Refill Flow
    # ==========================================
    def test_food_refill_and_expiration(self):
        # 🟢 Test Case: test_food_refill_and_expiration
        # 📝 ทำอะไร: จำลองการสร้างกรง เติมอาหาร และลบอาหารหมดอายุ
        
        zone = Zone("Z-01", "Herbivore")
        cage = Cage("C-001")
        zone.add_cage(cage)

        # เพิ่มอาหาร 2 ชิ้น: หมดอายุอีก 3 วัน และ หมดอายุไปแล้ว 1 วัน
        cage.add_food("Meat", self.now + timedelta(days=3))
        expired_food = Food("Meat", self.now - timedelta(days=1))
        cage._Cage__foods.append(expired_food) 
        
        print("[EXPECTED OUTPUT] โซนต้องดึงกรง C-001 ได้ 1 กรง และอาหารหลังเคลียร์ของเสีย ต้องเหลือแค่ 1 ชิ้นที่ยังไม่หมดอายุ")
        
        cages_in_zone = zone.get_cages()
        self.assertEqual(len(cages_in_zone), 1)
        self.assertEqual(cages_in_zone[0].cage_id, "C-001")

        cage.remove_expired_food()
        remaining_foods = cage.get_foods()
        
        print(f"[ACTUAL OUTPUT]   ดึงกรงได้ {len(cages_in_zone)} กรง (ID: {cages_in_zone[0].cage_id}), อาหารเหลือ {len(remaining_foods)} ชิ้น (หมดอายุหรือไม่: {remaining_foods[0].is_expired()})")
        
        self.assertEqual(len(remaining_foods), 1)
        self.assertFalse(remaining_foods[0].is_expired())

    # ==========================================
    # 2. Vehicle & Driver Availability
    # ==========================================
    def test_vehicle_availability_with_mock_trip(self):
        # 🟢 Test Case: test_vehicle_availability_with_mock_trip
        # 📝 ทำอะไร: ทดสอบ is_available ของรถ 3 กรณี (เวลาชน, เวลาชนแต่คิวถูกยกเลิก, เวลาไม่ชน)
        
        vehicle = Vehicle("V-01", 20)
        
        # Mock 1: เวลา 10:00 - 12:00 (CONFIRMED)
        mock_round_1 = MagicMock()
        mock_round_1.start_time = self.now.replace(hour=10, minute=0)
        mock_round_1.end_time = self.now.replace(hour=12, minute=0)
        mock_trip_1 = MagicMock()
        mock_trip_1.status = "CONFIRMED"
        mock_trip_1.round = mock_round_1

        # Mock 2: เวลา 13:00 - 15:00 (CANCELLED)
        mock_round_2 = MagicMock()
        mock_round_2.start_time = self.now.replace(hour=13, minute=0)
        mock_round_2.end_time = self.now.replace(hour=15, minute=0)
        mock_trip_2 = MagicMock()
        mock_trip_2.status = "CANCELLED"
        mock_trip_2.round = mock_round_2

        vehicle.add_trip(mock_trip_1)
        vehicle.add_trip(mock_trip_2)

        print("[EXPECTED OUTPUT] เคส 1(เวลาทับ) = False | เคส 2(ทับคิวยกเลิก) = True | เคส 3(ว่าง) = True")

        # เคสที่ 1: เวลาทับซ้อนกับ Trip 1 (11:00 - 11:30)
        is_avail_1 = vehicle.is_available(self.now.replace(hour=11, minute=0), self.now.replace(hour=11, minute=30))
        
        # เคสที่ 2: เวลาทับซ้อนกับ Trip 2 ที่ยกเลิกแล้ว (14:00 - 14:30)
        is_avail_2 = vehicle.is_available(self.now.replace(hour=14, minute=0), self.now.replace(hour=14, minute=30))
        
        # เคสที่ 3: เวลาว่างสนิท (16:00 - 17:00)
        is_avail_3 = vehicle.is_available(self.now.replace(hour=16, minute=0), self.now.replace(hour=17, minute=0))

        print(f"[ACTUAL OUTPUT]   เคส 1 = {is_avail_1} | เคส 2 = {is_avail_2} | เคส 3 = {is_avail_3}")

        self.assertFalse(is_avail_1)
        self.assertTrue(is_avail_2)
        self.assertTrue(is_avail_3)

    def test_driver_availability(self):
        # 🟢 Test Case: test_driver_availability
        # 📝 ทำอะไร: ทดสอบความพร้อมของ Driver เมื่อมีคิวทับซ้อน
        
        driver = Driver("S-001", "John Doe", "D-1234")
        mock_round = MagicMock()
        mock_round.start_time = self.now.replace(hour=9, minute=0)
        mock_round.end_time = self.now.replace(hour=11, minute=0)
        mock_trip = MagicMock()
        mock_trip.status = "SCHEDULED"
        mock_trip.round = mock_round
        
        driver.add_trip(mock_trip)

        print("[EXPECTED OUTPUT] คนขับต้องไม่ว่าง (False) เพราะถูกจองคิว 09:00-11:00 ไว้แล้ว ขอจอง 10:00-12:00 จะต้องล้มเหลว")

        is_avail = driver.is_available(self.now.replace(hour=10, minute=0), self.now.replace(hour=12, minute=0))
        
        print(f"[ACTUAL OUTPUT]   สถานะคนขับ = {is_avail}")
        
        self.assertFalse(is_avail)

    # ==========================================
    # 3. Park Entity Management
    # ==========================================
    def test_park_entity_management(self):
        # 🟢 Test Case: test_park_entity_management
        # 📝 ทำอะไร: ทดสอบการ Add และ Get ข้อมูลในคลาส Park
        
        park = Park("Jurassic Wonderland")
        zone = Zone("Z-99", "Carnivore")
        vehicle = Vehicle("V-99", 15)

        park.add_zone(zone)
        park.add_vehicle(vehicle)

        print("[EXPECTED OUTPUT] ดึง Z-99 ต้องเจอและเป็น 'Carnivore' | ดึง V-99 ต้องเจอและจุ '15' ที่นั่ง | ดึง Z-00 ต้องได้ 'None'")

        fetched_zone = park.get_zone("Z-99")
        fetched_vehicle = park.get_vehicle("V-99")
        not_found_zone = park.get_zone("Z-00")

        z_type = fetched_zone.zone_type if fetched_zone else None
        v_seats = fetched_vehicle.total_seats if fetched_vehicle else None

        print(f"[ACTUAL OUTPUT]   ดึง Z-99 ได้ชนิด '{z_type}' | ดึง V-99 ได้ความจุ '{v_seats}' | ดึง Z-00 ได้ '{not_found_zone}'")

        self.assertIsNotNone(fetched_zone)
        self.assertEqual(fetched_zone.zone_type, "Carnivore")
        self.assertIsNotNone(fetched_vehicle)
        self.assertEqual(fetched_vehicle.total_seats, 15)
        self.assertIsNone(not_found_zone)

if __name__ == '__main__':
    unittest.main()