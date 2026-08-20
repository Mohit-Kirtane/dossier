from app.db.models import Base

ALLOWED_TABLES = ("demo_departments", "demo_employees", "demo_products", "demo_orders")


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
        "demo_orders.product_id -> demo_products.id."
    )
    return "\n".join(lines)
