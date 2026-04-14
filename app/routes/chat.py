from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
import os
from app.knowledge import get_clinic_info, get_treatments
from app.leads import save_lead

router = APIRouter()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
BOOKING_LINK = "https://shmily.janeapp.com/"

class ChatRequest(BaseModel):
    message: str
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    concern: str | None = None

SYSTEM_PROMPT = f"""
You are an AI Front Desk Assistant for a medical aesthetics clinic.

You help clients understand treatments, answer common questions, and guide them toward booking a consultation.

Communication style:
- Friendly
- Professional
- Clear
- Concise
- 2-4 sentences when possible

Rules:
- Do not diagnose medical conditions
- Do not guarantee results
- Encourage consultation when medical judgment is needed

Booking behavior:
- If the user clearly wants to schedule, provide this booking link: {BOOKING_LINK}
- If the user sounds interested but not ready, invite them to leave their contact information for follow-up
"""

def detect_booking_intent(message: str) -> bool:
    booking_keywords = [
        "book", "booking", "schedule", "appointment", "availability", "consultation"
    ]
    text = message.lower()
    return any(word in text for word in booking_keywords)

def detect_lead_intent(message: str) -> bool:
    lead_keywords = [
        "thinking about it", "not ready", "maybe later", "can someone follow up",
        "need more info", "interested"
    ]
    text = message.lower()
    return any(phrase in text for phrase in lead_keywords)

@router.post("/")
def chat(request: ChatRequest):
    context = get_clinic_info() + get_treatments()

    if request.name and (request.phone or request.email):
        lead = save_lead({
            "name": request.name,
            "phone": request.phone,
            "email": request.email,
            "concern": request.concern,
            "original_message": request.message
        })
        return {
            "reply": f"Thanks, {lead['name']}! Our team will follow up with you soon.",
            "lead_saved": True,
            "lead_id": lead["id"]
        }

    if detect_booking_intent(request.message):
        return {
            "reply": f"Absolutely — you can book your consultation here: {BOOKING_LINK}"
        }

    if detect_lead_intent(request.message):
        return {
            "reply": "I’d be happy to help. You can leave your name and phone or email, and our team can follow up with you."
        }

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": context},
            {"role": "user", "content": request.message}
        ]
    )

    return {"reply": response.choices[0].message.content}