from backend.database import SessionLocal
import backend.models
from backend.models.user import User

db = SessionLocal()
u = db.query(User).first()
if u:
    u.last_savings_refill_month = None
    db.commit()
    print('Reset last_savings_refill_month for:', u.email)
