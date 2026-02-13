from sqlalchemy.orm import Session
from .models import Alert, Conversation, Message


def send_welcome(db: Session, conversation: Conversation):
    if conversation.automation_paused:
        return
    db.add(Message(
        conversation_id=conversation.id,
        direction="outbound",
        channel="email",
        body="Welcome! Thanks for reaching out. Reply here or use our booking link.",
    ))


def booking_confirmation(db: Session, conversation_id: int):
    convo = db.get(Conversation, conversation_id)
    if not convo or convo.automation_paused:
        return
    db.add(Message(
        conversation_id=conversation_id,
        direction="outbound",
        channel="sms",
        body="Your booking is confirmed. We'll send reminders and required forms.",
    ))


def low_inventory_alert(db: Session, item_name: str):
    db.add(Alert(
        type="inventory_low",
        message=f"Inventory item '{item_name}' is below threshold",
        link="/inventory",
    ))
