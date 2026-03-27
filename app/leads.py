from app.database import SessionLocal
from app.models import Lead

def save_lead(data: dict):
    db = SessionLocal()
    try:
        lead = Lead(
            name=data.get("name"),
            phone=data.get("phone"),
            email=data.get("email"),
            concern=data.get("concern"),
            message=data.get("original_message")
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)

        return {
            "id": lead.id,
            "name": lead.name,
            "phone": lead.phone,
            "email": lead.email,
            "concern": lead.concern,
            "message": lead.message,
        }
    finally:
        db.close()

def get_all_leads():
    db = SessionLocal()
    try:
        leads = db.query(Lead).all()
        return [
            {
                "id": l.id,
                "name": l.name,
                "phone": l.phone,
                "email": l.email,
                "concern": l.concern,
                "message": l.message,
            }
            for l in leads
        ]
    finally:
        db.close()