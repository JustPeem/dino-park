# 🦕 Dino Park Management System

ระบบจัดการสวนไดโนเสาร์ครบวงจร พัฒนาด้วย Python

---

## 👥 Team Members & Responsibilities

| คนที่ | ชื่อ | รับผิดชอบ |
|-------|------|-----------|
| 1 | TBD | **Models** – User, Member, Staff, Coupon, Ticket |
| 2 | TBD | **Models** – Park, Zone, Cage, Dino, Food, Vehicle, Driver |
| 3 | TBD | **Models + Services** – Booking, Trip, Round, Payment + BookingService, PaymentService |
| 4 | TBD | **Controllers + Reports + Utils** – CLI controllers, Report generation, Validators |

---

## 📁 Project Structure

```
dino_park/
├── models/                  # Data classes & business logic
│   ├── __init__.py
│   ├── users.py             # [Person 1] User (abstract), Member, GuestUser
│   ├── staff.py             # [Person 1] Staff (abstract), Manager, Ranger, TicketStaff, Driver
│   ├── coupon.py            # [Person 1] Coupon
│   ├── ticket.py            # [Person 1] Ticket
│   ├── park.py              # [Person 2] Park
│   ├── zone.py              # [Person 2] Zone
│   ├── cage.py              # [Person 2] Cage
│   ├── dino.py              # [Person 2] Dino
│   ├── food.py              # [Person 2] Food
│   ├── vehicle.py           # [Person 2] Vehicle
│   ├── driver.py            # [Person 2] Driver
│   ├── booking.py           # [Person 3] Booking
│   ├── trip.py              # [Person 3] Trip
│   ├── round.py             # [Person 3] Round
│   └── payment.py           # [Person 3] Payment, PaymentMethod (interface), CashPayment, QRPayment
│
├── services/                # Business logic / Use-case layer
│   ├── __init__.py
│   ├── booking_service.py   # [Person 3] Visitor booking, cancel, refund flow
│   ├── payment_service.py   # [Person 3] Payment processing, coupon validation
│   ├── checkin_service.py   # [Person 4] TicketStaff check-in flow
│   ├── trip_service.py      # [Person 4] Manager create trip flow
│   └── food_service.py      # [Person 4] Ranger food refill & notification flow
│
├── controllers/             # Entry points (CLI / future API)
│   ├── __init__.py
│   ├── visitor_controller.py   # [Person 4] Booking, payment, cancel use-cases
│   ├── staff_controller.py     # [Person 4] Check-in, coupon, food use-cases
│   └── manager_controller.py   # [Person 4] Trip creation, approve refill use-cases
│
├── reports/                 # Report generation
│   ├── __init__.py
│   ├── daily_report.py      # [Person 4] Daily visitor count report
│   └── food_report.py       # [Person 4] Food stock / refill history report
│
├── utils/                   # Shared helpers
│   ├── __init__.py
│   ├── validators.py        # [Person 4] Input validation (date, phone, seats, etc.)
│   ├── id_generator.py      # [Person 1] Centralized ID generation (B-001, T-001, etc.)
│   └── exceptions.py        # [Person 4] Custom exceptions for the system
│
├── tests/                   # Unit tests (mirror structure of models/services)
│   ├── __init__.py
│   ├── test_models/
│   │   ├── test_booking.py
│   │   ├── test_payment.py
│   │   ├── test_member.py
│   │   └── test_trip.py
│   ├── test_services/
│   │   ├── test_booking_service.py
│   │   └── test_payment_service.py
│   └── test_controllers/
│       └── test_visitor_controller.py
│
├── data/                    # Sample seed data (JSON)
│   ├── sample_members.json
│   ├── sample_zones.json
│   └── sample_dinos.json
│
├── docs/                    # Design documents
│   ├── class_diagram.md
│   ├── use_case_diagram.md
│   └── sequence_diagrams.md
│
├── main.py                  # Entry point
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🌐 FastAPI – REST Endpoints

| Method | Endpoint | UC | Description |
|--------|----------|----|-------------|
| GET | `/bookings/availability` | UC7 | Check available seats |
| POST | `/bookings/` | UC1+UC2 | Create booking + payment |
| GET | `/bookings/{id}` | – | Get booking detail |
| DELETE | `/bookings/{id}` | UC3 | Cancel & refund |
| POST | `/staff/checkin` | UC4 | Ticket check-in |
| POST | `/staff/coupon` | UC8 | Add coupon to member |
| POST | `/trips/` | UC5 | Manager create trip |
| POST | `/food/refill-request` | UC6 | Ranger refill request |
| POST | `/food/approve-refill` | UC6 | Manager approve refill |
| GET | `/reports/daily` | – | Daily visitor report |
| GET | `/reports/food` | – | Food stock report |
| GET | `/reports/zones` | – | Zone availability |

```bash
# Start API server
uvicorn api.app:app --reload

# Interactive Swagger UI → http://localhost:8000/docs
# ReDoc             → http://localhost:8000/redoc
```

---

## 🤖 MCP Service (Model Context Protocol)

MCP exposes all 8 use cases as **AI-callable tools** for Claude Desktop, Cursor, or any MCP client.

### MCP Tools
| Tool | UC | Description |
|------|----|-------------|
| `check_seat_availability` | UC7 | Check seats |
| `create_booking` | UC1+UC2 | Full booking flow |
| `cancel_booking` | UC3 | Cancel + refund |
| `check_in_ticket` | UC4 | Check-in visitor |
| `create_trip` | UC5 | Manager creates trip |
| `request_food_refill` | UC6 | Ranger requests refill |
| `approve_food_refill` | UC6 | Manager approves refill |
| `add_coupon_to_member` | UC8 | Issue coupon |

### MCP Resources
| URI | Description |
|-----|-------------|
| `report://daily` | Today's visitor & revenue report |
| `report://food` | Food stock status |
| `park://zones` | Zone availability listing |

### Run MCP server (stdio – for Claude Desktop)
```bash
python mcp_service/dino_park_mcp.py
```

### Claude Desktop config (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "dino-park": {
      "command": "python",
      "args": ["mcp_service/dino_park_mcp.py"],
      "cwd": "/your/path/to/dino_park"
    }
  }
}
```

---

## 🚀 Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/JustPeem/dino-park.git
cd dino-park

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run demo (CLI)
python main.py

# 5. Run FastAPI server
uvicorn api.app:app --reload
# → Swagger UI: http://localhost:8000/docs

# 6. Run MCP server (stdio for Claude Desktop)
python mcp_service/dino_park_mcp.py

# 7. Run all tests
pytest tests/ -v

# 8. Run only API tests
pytest tests/test_api/ -v

# 9. Run with coverage
pytest tests/ --cov=. --cov-report=term-missing
```

---

## 🌿 Git Branching Strategy

```
main          ← production-ready, protected
dev           ← integration branch (PR target)
├── feat/person1-models-users
├── feat/person2-models-park
├── feat/person3-booking-payment
└── feat/person4-controllers-reports
```

**Rules:**
- ❌ ห้าม push ตรงเข้า `main` หรือ `dev`
- ✅ ทุก feature ต้องเปิด Pull Request → รอ review 1 คนก่อน merge
- ✅ Commit message format: `feat:`, `fix:`, `test:`, `docs:`

---

## 🎯 Use Cases Covered

| # | Use Case | Actor | Service |
|---|----------|-------|---------|
| 1 | Visitor Booking | Visitor / Member | `BookingService` |
| 2 | Payment (Cash/QR), Member Discount, Coupon | Visitor / Member | `PaymentService` |
| 3 | Cancel Booking & Refund | Visitor / Member | `BookingService` |
| 4 | Ticket Check-in | TicketStaff | `CheckInService` |
| 5 | Create Trip | Manager | `TripService` |
| 6 | Food Refill Request | Ranger | `FoodService` |
| 7 | Check Seat Availability | Member | `BookingService` |
| 8 | Add Coupon to Member | TicketStaff | `PaymentService` |

---

## 💰 Pricing & Discount Rules

| ประเภท | ราคา |
|--------|------|
| ผู้ใหญ่ (Adult) | 500 บาท |
| เด็ก (Child, ≤12 ปี) | 300 บาท |
| ผู้สูงอายุ (Senior, ≥60 ปี) | 250 บาท |
| Feeding Ticket (เสริม) | 150 บาท |

| ส่วนลด | เงื่อนไข |
|--------|---------|
| Member Discount | 10% ทุกการจอง |
| Coupon | ตามมูลค่าคูปอง (หมดอายุตาม `expiryDate`) |
| Group Discount | จอง ≥ 10 ที่นั่ง ลด 5% |

---

## ⚙️ Business Rules

**Time Constraints:**
- จองล่วงหน้าได้สูงสุด **30 วัน**
- ยกเลิกได้ก่อนวันเข้าชม **24 ชั่วโมง** (refund 100%)
- ยกเลิกก่อนน้อยกว่า 24 ชั่วโมง → refund 50%

**Quantity Constraints:**
- จองได้สูงสุด **10 ที่นั่ง** ต่อ 1 การจอง
- รอบละไม่เกินความจุของ Vehicle (`totalSeats`)

---

## 🆔 Entity ID Format

| Entity | Format | Example |
|--------|--------|---------|
| Booking | `B-YYYYMMDD-XXX` | `B-20250601-001` |
| Ticket | `T-XXX` | `T-042` |
| Trip | `TR-XXX` | `TR-007` |
| Member | `M-XXX` | `M-015` |
| Staff | `S-XXX` | `S-003` |
| Zone | `Z-XX` | `Z-01` |
| Cage | `C-XXX` | `C-012` |

---