import random
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.demo_models import (
    Contract,
    Customer,
    Department,
    Employee,
    Invoice,
    Payment,
    SupportTicket,
)
from app.db.demo_models import Product as DemoProduct

# Fixed "today" for the demo dataset, so invoice/ticket status (paid, overdue,
# open) is deterministic and doesn't drift as real time passes.
TODAY = date(2026, 6, 15)

DEPARTMENTS = [
    Department(id=1, name="Engineering", budget=2_400_000),
    Department(id=2, name="Sales", budget=1_100_000),
    Department(id=3, name="Marketing", budget=650_000),
    Department(id=4, name="Customer Success", budget=480_000),
]

# (id, name, title, department_id, manager_id, salary, hire_date)
_EMPLOYEE_ROWS = [
    (1, "Ava Chen", "Engineering Manager", 1, None, 168000, date(2019, 3, 4)),
    (2, "Ravi Patel", "Senior Backend Engineer", 1, 1, 152000, date(2020, 7, 12)),
    (3, "Sofia Marin", "Backend Engineer", 1, 1, 128000, date(2022, 1, 17)),
    (4, "Liam O'Brien", "Frontend Engineer", 1, 1, 124000, date(2021, 9, 1)),
    (5, "Priya Nair", "Data Engineer", 1, 1, 139000, date(2021, 4, 19)),
    (6, "Diego Alvarez", "VP of Sales", 2, None, 190000, date(2018, 6, 11)),
    (7, "Emma Johansson", "Account Executive", 2, 6, 98000, date(2022, 2, 28)),
    (8, "Noah Kim", "Account Executive", 2, 6, 101000, date(2021, 11, 3)),
    (9, "Grace Adeyemi", "Sales Development Rep", 2, 6, 68000, date(2023, 5, 22)),
    (10, "Mateus Silva", "Marketing Director", 3, None, 155000, date(2019, 10, 7)),
    (11, "Hana Suzuki", "Content Marketing Lead", 3, 10, 104000, date(2022, 8, 15)),
    (12, "Oliver Bennett", "Growth Marketer", 3, 10, 92000, date(2023, 1, 9)),
    (13, "Wei Zhang", "Customer Success Lead", 4, None, 112000, date(2020, 12, 1)),
    (14, "Fatima Haidari", "Customer Success Manager", 4, 13, 89000, date(2022, 6, 6)),
    (15, "Lucas Ferreira", "Support Engineer", 4, 13, 84000, date(2023, 3, 20)),
]

EMPLOYEES = [
    Employee(
        id=row[0], name=row[1], title=row[2], department_id=row[3],
        manager_id=row[4], salary=row[5], hire_date=row[6],
    )
    for row in _EMPLOYEE_ROWS
]

_SALES_REP_IDS = [6, 7, 8, 9]
_SUPPORT_REP_IDS = [13, 14, 15]

PRODUCTS = [
    DemoProduct(id=1, name="Copilot Starter", category="Subscription", unit_price=49.0),
    DemoProduct(id=2, name="Copilot Pro", category="Subscription", unit_price=149.0),
    DemoProduct(id=3, name="Copilot Enterprise", category="Subscription", unit_price=499.0),
    DemoProduct(id=4, name="Onboarding Package", category="Services", unit_price=2500.0),
    DemoProduct(id=5, name="Custom Integration", category="Services", unit_price=6000.0),
]
_SUBSCRIPTION_PRODUCT_IDS = [1, 2, 3]
_SERVICE_PRODUCT_IDS = [4, 5]

_CUSTOMER_NAMES = [
    "Northwind Traders", "Globex Corp", "Initech", "Umbrella Health", "Soylent Foods",
    "Hooli", "Stark Industries", "Wayne Enterprises", "Wonka Industries", "Acme Corp",
    "Cyberdyne Systems", "Aperture Labs", "Massive Dynamic", "Pied Piper", "Gringotts Bank",
    "Oscorp", "Tyrell Corporation", "Vandelay Industries", "Prestige Worldwide", "Dunder Mifflin",
    "Sirius Cybernetics", "Weyland-Yutani", "Buy n Large", "Oceanic Airlines", "Duff Brewing",
    "Monsters Inc", "Rekall Inc", "Nakatomi Trading", "Genco Pura Olive Oil", "Los Pollos Hermanos",
]
_INDUSTRIES = [
    "Retail", "Healthcare", "Finance", "Manufacturing", "Logistics",
    "Media", "Energy", "Education", "Hospitality", "Technology",
]
_REGIONS = ["North America", "Europe", "APAC", "LATAM"]
_SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]
_PAYMENT_METHODS = ["Credit Card", "ACH Transfer", "Wire Transfer"]
_TICKET_SUBJECTS = [
    "Login/SSO issue", "Billing question", "Feature request: bulk export",
    "API rate limit clarification", "Data import failed", "Slow response times",
    "Requesting additional seats", "Integration setup help", "Permissions/RBAC question",
    "Renewal timeline question",
]


def _build_customers(rng: random.Random) -> list[Customer]:
    customers = []
    for i, name in enumerate(_CUSTOMER_NAMES, start=1):
        signup = TODAY - relativedelta(months=rng.randint(3, 42))
        customers.append(
            Customer(
                id=i,
                name=name,
                industry=rng.choice(_INDUSTRIES),
                region=rng.choice(_REGIONS),
                segment=rng.choice(_SEGMENTS),
                signup_date=signup,
            )
        )
    return customers


def _contract_value(product: DemoProduct, months: int) -> float:
    if product.id in _SERVICE_PRODUCT_IDS:
        return product.unit_price
    return round(product.unit_price * months, 2)


def _build_contracts_and_invoices(
    rng: random.Random, customers: list[Customer]
) -> tuple[list[Contract], list[Invoice], list[Payment]]:
    contracts, invoices, payments = [], [], []
    contract_id = invoice_id = payment_id = 1

    for customer in customers:
        for _ in range(rng.randint(1, 3)):
            product = PRODUCTS[rng.randrange(len(PRODUCTS))]
            is_subscription = product.id in _SUBSCRIPTION_PRODUCT_IDS
            term_months = rng.choice([12, 24]) if is_subscription else 0
            start = customer.signup_date + timedelta(days=rng.randint(0, 60))
            end = start + relativedelta(months=term_months) if is_subscription else start
            value = _contract_value(product, term_months if is_subscription else 1)

            if end < TODAY:
                status = "Cancelled" if rng.random() < 0.12 else "Expired"
            else:
                status = "Active"

            contracts.append(
                Contract(
                    id=contract_id,
                    customer_id=customer.id,
                    product_id=product.id,
                    owner_employee_id=rng.choice(_SALES_REP_IDS),
                    start_date=start,
                    end_date=end,
                    contract_value=value,
                    status=status,
                )
            )

            billing_dates = (
                _quarterly_billing_dates(start, min(end, TODAY) if status != "Cancelled" else start)
                if is_subscription
                else [start]
            )
            per_invoice_amount = round(value / len(billing_dates), 2) if billing_dates else value

            for issue_date in billing_dates:
                due = issue_date + timedelta(days=30)
                invoice_status = "Pending" if due > TODAY else "Paid"
                if invoice_status == "Paid" and rng.random() < 0.15:
                    invoice_status = "Overdue"

                invoices.append(
                    Invoice(
                        id=invoice_id,
                        contract_id=contract_id,
                        issue_date=issue_date,
                        due_date=due,
                        amount=per_invoice_amount,
                        status=invoice_status,
                    )
                )

                if invoice_status == "Paid":
                    payments.append(
                        Payment(
                            id=payment_id,
                            invoice_id=invoice_id,
                            payment_date=issue_date + timedelta(days=rng.randint(1, 25)),
                            amount=per_invoice_amount,
                            method=rng.choice(_PAYMENT_METHODS),
                        )
                    )
                    payment_id += 1
                elif invoice_status == "Overdue" and rng.random() < 0.3:
                    partial = round(per_invoice_amount * rng.uniform(0.3, 0.7), 2)
                    payments.append(
                        Payment(
                            id=payment_id,
                            invoice_id=invoice_id,
                            payment_date=due - timedelta(days=rng.randint(1, 10)),
                            amount=partial,
                            method=rng.choice(_PAYMENT_METHODS),
                        )
                    )
                    payment_id += 1

                invoice_id += 1

            contract_id += 1

    return contracts, invoices, payments


def _quarterly_billing_dates(start: date, through: date) -> list[date]:
    dates = []
    current = start
    while current <= through:
        dates.append(current)
        current = current + relativedelta(months=3)
    return dates or [start]


def _build_support_tickets(rng: random.Random, customers: list[Customer]) -> list[SupportTicket]:
    tickets = []
    ticket_id = 1
    for customer in customers:
        for _ in range(rng.randint(1, 5)):
            opened = customer.signup_date + timedelta(days=rng.randint(1, 700))
            if opened > TODAY:
                continue
            priority = rng.choices(
                ["Low", "Medium", "High", "Urgent"], weights=[0.35, 0.35, 0.2, 0.1]
            )[0]
            resolution_days = {"Low": 7, "Medium": 4, "High": 2, "Urgent": 1}[priority]
            will_close = rng.random() < 0.8
            closed = opened + timedelta(days=rng.randint(1, resolution_days * 3)) if will_close else None
            if closed and closed > TODAY:
                closed = None

            tickets.append(
                SupportTicket(
                    id=ticket_id,
                    customer_id=customer.id,
                    assigned_employee_id=rng.choice(_SUPPORT_REP_IDS),
                    subject=rng.choice(_TICKET_SUBJECTS),
                    priority=priority,
                    status="Closed" if closed else "Open",
                    opened_date=opened,
                    closed_date=closed,
                )
            )
            ticket_id += 1
    return tickets


def seed_demo_data(session: Session) -> None:
    if session.scalar(select(Department.id).limit(1)) is not None:
        return

    rng = random.Random(42)
    customers = _build_customers(rng)
    contracts, invoices, payments = _build_contracts_and_invoices(rng, customers)
    tickets = _build_support_tickets(rng, customers)

    session.add_all(DEPARTMENTS)
    session.add_all(EMPLOYEES)
    session.add_all(PRODUCTS)
    session.add_all(customers)
    session.add_all(contracts)
    session.add_all(invoices)
    session.add_all(payments)
    session.add_all(tickets)
    session.commit()
