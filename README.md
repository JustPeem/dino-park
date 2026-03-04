dino_park_system/
│
├── main.py                  # ไฟล์หลักสำหรับรันโปรแกรม (Entry Point)
├── README.md                # อธิบายโปรเจกต์ วิธีรัน และวิธี Setup
├── requirements.txt         # ระบุ Library ที่ต้องใช้ (ถ้ามี)
│
├── models/                  # (Layer 1: ข้อมูลและโครงสร้าง Class)
│   ├── __init__.py
│   ├── users.py             # Person (Abstract), User, Member, Staff, Manager, │   │                          Ranger, TicketStaff
│   ├── park.py              # Park, Zone, Cage, Dino
│   ├── operations.py        # Round, Trip, Vehicle, Driver
│   └── transactions.py      # Booking, Ticket, Coupon
│
├── services/                # (Layer 2: Business Logic และการทำงาน)
│   ├── __init__.py
│   ├── booking_service.py   # จัดการการจอง, ยกเลิก, คืนเงิน
│   ├── payment_service.py   # PaymentMethod, CashPayment, QRPayment,
│   └── park_service.py      # ManagerAssignรถ,Rangerเติมอาหาร,
│                              TicketStaff Check-in
│
├── utils/                   # (Layer 3: เครื่องมือช่วยเหลือต่างๆ)
│   ├── __init__.py
│   ├── exceptions.py        # Custom Exceptions (เช่น SeatFullError,        InvalidCouponError)
│   ├── validators.py        # ฟังก์ชันตรวจสอบข้อมูล (เช็ควันที่, เช็คเบอร์โทร)
│   └── notifications.py     # ระบบแจ้งเตือน (ส่ง SMS, Alert อาหารใกล้หมด)
│
└── tests/                   # (Layer 4: Unit Test สำหรับทดสอบระบบ)
    ├── __init__.py
    ├── test_booking.py      # Person 2 เขียนเทส
    ├── test_park.py         # Person 3 เขียนเทส
    └── test_payment.py      # Person 2 เขียนเทส