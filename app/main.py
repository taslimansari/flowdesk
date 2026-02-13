from datetime import date
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models, schemas, automation

Base.metadata.create_all(bind=engine)
app = FastAPI(title="FlowDesk Unified Ops MVP")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    today = date.today()
    todays_bookings = db.query(models.Booking).filter(func.date(models.Booking.starts_at) == today).count()
    upcoming = db.query(models.Booking).filter(models.Booking.status == "upcoming").count()
    completed = db.query(models.Booking).filter(models.Booking.status == "completed").count()
    no_show = db.query(models.Booking).filter(models.Booking.status == "no-show").count()
    new_inquiries = db.query(models.Contact).count()
    ongoing = db.query(models.Conversation).count()
    unanswered = db.query(models.Conversation).join(models.Message, isouter=True).filter(models.Message.id.is_(None)).count()
    pending_forms = db.query(models.Booking).filter(models.Booking.forms_status == "pending").count()
    overdue_forms = db.query(models.Booking).filter(models.Booking.forms_status == "overdue").count()
    completed_forms = db.query(models.Booking).filter(models.Booking.forms_status == "completed").count()
    low_stock = db.query(models.InventoryItem).filter(models.InventoryItem.quantity <= models.InventoryItem.low_threshold).all()
    alerts = db.query(models.Alert).order_by(models.Alert.created_at.desc()).limit(8).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "kpis": {
            "todays_bookings": todays_bookings,
            "upcoming": upcoming,
            "completed": completed,
            "no_show": no_show,
            "new_inquiries": new_inquiries,
            "ongoing": ongoing,
            "unanswered": unanswered,
            "pending_forms": pending_forms,
            "overdue_forms": overdue_forms,
            "completed_forms": completed_forms,
            "low_stock_count": len(low_stock),
        },
        "low_stock": low_stock,
        "alerts": alerts,
    })


@app.post("/onboarding/workspace")
def create_workspace(payload: schemas.WorkspaceCreate, db: Session = Depends(get_db)):
    ws = models.Workspace(**payload.model_dump())
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return ws


@app.post("/onboarding/channels/{workspace_id}")
def setup_channels(workspace_id: int, payload: schemas.ChannelSetup, db: Session = Depends(get_db)):
    ws = db.get(models.Workspace, workspace_id)
    if not ws:
        raise HTTPException(404, "workspace not found")
    ws.email_connected = payload.email_connected
    ws.sms_connected = payload.sms_connected
    if not (ws.email_connected or ws.sms_connected):
        raise HTTPException(400, "At least one channel is mandatory")
    db.commit()
    return {"inbox_active": True}


@app.post("/contact-form/submit")
def submit_contact(payload: schemas.ContactFormSubmission, db: Session = Depends(get_db)):
    contact = models.Contact(**payload.model_dump())
    db.add(contact)
    db.flush()
    convo = models.Conversation(contact_id=contact.id)
    db.add(convo)
    db.flush()
    automation.send_welcome(db, convo)
    db.commit()
    return {"contact_id": contact.id, "conversation_id": convo.id}


@app.post("/booking-types")
def create_booking_type(payload: schemas.BookingTypeCreate, db: Session = Depends(get_db)):
    bt = models.BookingType(**payload.model_dump())
    db.add(bt)
    db.commit()
    db.refresh(bt)
    return bt


@app.post("/bookings")
def create_booking(payload: schemas.BookingCreate, db: Session = Depends(get_db)):
    booking = models.Booking(**payload.model_dump())
    db.add(booking)
    db.flush()
    convo = db.query(models.Conversation).filter(models.Conversation.contact_id == booking.contact_id).first()
    if convo:
        automation.booking_confirmation(db, convo.id)
    db.commit()
    return booking


@app.post("/inventory")
def create_inventory(payload: schemas.InventoryCreate, db: Session = Depends(get_db)):
    item = models.InventoryItem(**payload.model_dump())
    db.add(item)
    if item.quantity <= item.low_threshold:
        automation.low_inventory_alert(db, item.name)
    db.commit()
    return item


@app.post("/inbox/{conversation_id}/reply")
def staff_reply(conversation_id: int, payload: schemas.StaffReply, db: Session = Depends(get_db)):
    convo = db.get(models.Conversation, conversation_id)
    if not convo:
        raise HTTPException(404, "conversation not found")
    convo.automation_paused = True
    db.add(models.Message(
        conversation_id=conversation_id,
        direction="outbound",
        channel=payload.channel,
        body=payload.body,
    ))
    db.commit()
    return {"automation_paused": True}


@app.post("/onboarding/activate/{workspace_id}")
def activate_workspace(workspace_id: int, db: Session = Depends(get_db)):
    ws = db.get(models.Workspace, workspace_id)
    if not ws:
        raise HTTPException(404, "workspace not found")
    has_channel = ws.email_connected or ws.sms_connected
    has_booking_type = db.query(models.BookingType).count() > 0
    has_availability = db.query(models.BookingType).filter(models.BookingType.availability != "").count() > 0
    if not (has_channel and has_booking_type and has_availability):
        raise HTTPException(400, "Activation checks failed")
    ws.active = True
    db.commit()
    return {"workspace_active": True}
