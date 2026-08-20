from app.db.models import Base

ALLOWED_TABLES = (
    "demo_departments",
    "demo_employees",
    "demo_customers",
    "demo_products",
    "demo_contracts",
    "demo_invoices",
    "demo_payments",
    "demo_support_tickets",
)


def _table_columns(table_name: str) -> list[tuple[str, str]]:
    table = Base.metadata.tables[table_name]
    return [(col.name, str(col.type)) for col in table.columns]


def get_schema_summary() -> list[dict]:
    return [
        {"table": name, "columns": [{"name": n, "type": t} for n, t in _table_columns(name)]}
        for name in ALLOWED_TABLES
    ]


def get_schema_description() -> str:
    lines = []
    for name in ALLOWED_TABLES:
        columns = ", ".join(f"{col} {dtype}" for col, dtype in _table_columns(name))
        lines.append(f"{name}({columns})")
    lines.append(
        "Relationships: demo_employees.department_id -> demo_departments.id; "
        "demo_employees.manager_id -> demo_employees.id (nullable, self-reference); "
        "demo_contracts.customer_id -> demo_customers.id; "
        "demo_contracts.product_id -> demo_products.id; "
        "demo_contracts.owner_employee_id -> demo_employees.id; "
        "demo_invoices.contract_id -> demo_contracts.id; "
        "demo_payments.invoice_id -> demo_invoices.id; "
        "demo_support_tickets.customer_id -> demo_customers.id; "
        "demo_support_tickets.assigned_employee_id -> demo_employees.id."
    )
    return "\n".join(lines)
