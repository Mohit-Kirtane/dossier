from sqlalchemy.orm import Session

from app.db.auth_models import ActivityLog


def log_activity(
    db: Session, user_id: str, event_type: str, workflow: str | None = None, detail: str | None = None
) -> None:
    db.add(ActivityLog(user_id=user_id, event_type=event_type, workflow=workflow, detail=detail))
    db.commit()
