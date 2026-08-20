from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.demo_models import Department, Employee, Order, Product

DEPARTMENTS = [
    Department(id=1, name="Engineering", budget=2_400_000),
    Department(id=2, name="Sales", budget=1_100_000),
    Department(id=3, name="Marketing", budget=650_000),
    Department(id=4, name="Customer Success", budget=480_000),
]

EMPLOYEES = [
    Employee(id=1, name="Ava Chen", title="Engineering Manager", department_id=1, salary=168000, hire_date=date(2019, 3, 4)),
    Employee(id=2, name="Ravi Patel", title="Senior Backend Engineer", department_id=1, salary=152000, hire_date=date(2020, 7, 12)),
    Employee(id=3, name="Sofia Marin", title="Backend Engineer", department_id=1, salary=128000, hire_date=date(2022, 1, 17)),
    Employee(id=4, name="Liam O'Brien", title="Frontend Engineer", department_id=1, salary=124000, hire_date=date(2021, 9, 1)),
    Employee(id=5, name="Priya Nair", title="Data Engineer", department_id=1, salary=139000, hire_date=date(2021, 4, 19)),
    Employee(id=6, name="Diego Alvarez", title="VP of Sales", department_id=2, salary=190000, hire_date=date(2018, 6, 11)),
    Employee(id=7, name="Emma Johansson", title="Account Executive", department_id=2, salary=98000, hire_date=date(2022, 2, 28)),
    Employee(id=8, name="Noah Kim", title="Account Executive", department_id=2, salary=101000, hire_date=date(2021, 11, 3)),
    Employee(id=9, name="Grace Adeyemi", title="Sales Development Rep", department_id=2, salary=68000, hire_date=date(2023, 5, 22)),
    Employee(id=10, name="Mateus Silva", title="Marketing Director", department_id=3, salary=155000, hire_date=date(2019, 10, 7)),
    Employee(id=11, name="Hana Suzuki", title="Content Marketing Lead", department_id=3, salary=104000, hire_date=date(2022, 8, 15)),
    Employee(id=12, name="Oliver Bennett", title="Growth Marketer", department_id=3, salary=92000, hire_date=date(2023, 1, 9)),
    Employee(id=13, name="Wei Zhang", title="Customer Success Lead", department_id=4, salary=112000, hire_date=date(2020, 12, 1)),
    Employee(id=14, name="Fatima Haidari", title="Customer Success Manager", department_id=4, salary=89000, hire_date=date(2022, 6, 6)),
    Employee(id=15, name="Lucas Ferreira", title="Support Engineer", department_id=4, salary=84000, hire_date=date(2023, 3, 20)),
]

PRODUCTS = [
    Product(id=1, name="Copilot Starter", category="Subscription", unit_price=49.0),
    Product(id=2, name="Copilot Pro", category="Subscription", unit_price=149.0),
    Product(id=3, name="Copilot Enterprise", category="Subscription", unit_price=499.0),
    Product(id=4, name="Onboarding Package", category="Services", unit_price=2500.0),
    Product(id=5, name="Custom Integration", category="Services", unit_price=6000.0),
]

_REGIONS = ["North America", "Europe", "APAC", "LATAM"]
_CUSTOMERS = [
    "Northwind Traders", "Globex Corp", "Initech", "Umbrella Health", "Soylent Foods",
    "Hooli", "Stark Industries", "Wayne Enterprises", "Wonka Industries", "Acme Corp",
    "Cyberdyne Systems", "Aperture Labs", "Massive Dynamic", "Pied Piper", "Gringotts Bank",
]


def _build_orders() -> list[Order]:
    orders = []
    order_id = 1
    for month in range(1, 13):
        for i in range(4):
            product_id = ((order_id + i) % 5) + 1
            customer = _CUSTOMERS[(order_id * 3 + i) % len(_CUSTOMERS)]
            region = _REGIONS[(order_id + i) % len(_REGIONS)]
            quantity = 1 + ((order_id * 7 + i * 3) % 12)
            orders.append(
                Order(
                    id=order_id,
                    customer_name=customer,
                    product_id=product_id,
                    quantity=quantity,
                    region=region,
                    order_date=date(2025, month, 1 + (i * 6) % 27),
                )
            )
            order_id += 1
    return orders


def seed_demo_data(session: Session) -> None:
    if session.scalar(select(Department.id).limit(1)) is not None:
        return

    session.add_all(DEPARTMENTS)
    session.add_all(EMPLOYEES)
    session.add_all(PRODUCTS)
    session.add_all(_build_orders())
    session.commit()
