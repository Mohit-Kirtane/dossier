from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin, get_current_user
from app.db.auth_models import ActivityLog, User
from app.db.session import get_db
from app.schemas import ActivityLogOut

router = APIRouter(tags=["activity"])


@router.get("/activity/me", response_model=list[ActivityLogOut])
def my_activity(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    rows = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(200)
        .all()
    )
    return [_to_out(r, user) for r in rows]


@router.get("/admin/activity", response_model=list[ActivityLogOut])
def all_activity(_: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> list[dict]:
    rows = (
        db.query(ActivityLog)
        .join(User, ActivityLog.user_id == User.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(500)
        .all()
    )
    return [_to_out(r, r.user) for r in rows]


def _to_out(row: ActivityLog, user: User) -> dict:
    return {
        "id": row.id,
        "event_type": row.event_type,
        "workflow": row.workflow,
        "detail": row.detail,
        "created_at": row.created_at,
        "user_name": user.name,
        "user_email": user.email,
    }
