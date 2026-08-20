from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models import Base

"""A small but interconnected B2B SaaS dataset that powers the database-chat
demo: HR (departments/employees), sales (customers/contracts), finance
(invoices/payments), and support (tickets) all reference each other, so
questions naturally span multiple tables. Kept separate from the app's own
tables and prefixed `demo_` so the NL-to-SQL feature has an obvious,
whitelisted schema to query without touching application data.
"""


class Department(Base):
    __tablename__ = "demo_departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    budget: Mapped[float] = mapped_column(Float)

    employees: Mapped[list["Employee"]] = relationship(back_populates="department")


class Employee(Base):
    __tablename__ = "demo_employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(120))
    department_id: Mapped[int] = mapped_column(ForeignKey("demo_departments.id"))
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("demo_employees.id"), nullable=True)
    salary: Mapped[float] = mapped_column(Float)
    hire_date: Mapped[date] = mapped_column(Date)

    department: Mapped[Department] = relationship(back_populates="employees")


class Customer(Base):
    __tablename__ = "demo_customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    industry: Mapped[str] = mapped_column(String(80))
    region: Mapped[str] = mapped_column(String(80))
    segment: Mapped[str] = mapped_column(String(40))
    signup_date: Mapped[date] = mapped_column(Date)


class Product(Base):
    __tablename__ = "demo_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(80))
    unit_price: Mapped[float] = mapped_column(Float)


class Contract(Base):
    __tablename__ = "demo_contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("demo_customers.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("demo_products.id"))
    owner_employee_id: Mapped[int] = mapped_column(ForeignKey("demo_employees.id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    contract_value: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20))


class Invoice(Base):
    __tablename__ = "demo_invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("demo_contracts.id"))
    issue_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20))


class Payment(Base):
    __tablename__ = "demo_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("demo_invoices.id"))
    payment_date: Mapped[date] = mapped_column(Date)
    amount: Mapped[float] = mapped_column(Float)
    method: Mapped[str] = mapped_column(String(40))


class SupportTicket(Base):
    __tablename__ = "demo_support_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("demo_customers.id"))
    assigned_employee_id: Mapped[int] = mapped_column(ForeignKey("demo_employees.id"))
    subject: Mapped[str] = mapped_column(String(200))
    priority: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    opened_date: Mapped[date] = mapped_column(Date)
    closed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
