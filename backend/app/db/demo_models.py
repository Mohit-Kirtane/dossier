from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models import Base

"""Synthetic HR/sales dataset that powers the database-chat demo.

Kept separate from the app's own tables (documents, chat sessions) and
prefixed `demo_` so the NL-to-SQL feature has an obvious, whitelisted
schema to query without touching application data.
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
    salary: Mapped[float] = mapped_column(Float)
    hire_date: Mapped[date] = mapped_column(Date)

    department: Mapped[Department] = relationship(back_populates="employees")


class Product(Base):
    __tablename__ = "demo_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(80))
    unit_price: Mapped[float] = mapped_column(Float)


class Order(Base):
    __tablename__ = "demo_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(120))
    product_id: Mapped[int] = mapped_column(ForeignKey("demo_products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    region: Mapped[str] = mapped_column(String(80))
    order_date: Mapped[date] = mapped_column(Date)
