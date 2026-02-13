from datetime import datetime
from pydantic import BaseModel, EmailStr


class WorkspaceCreate(BaseModel):
    name: str
    address: str
    timezone: str
    contact_email: EmailStr


class ChannelSetup(BaseModel):
    email_connected: bool = False
    sms_connected: bool = False


class ContactFormSubmission(BaseModel):
    name: str
    email_or_phone: str
    message: str | None = None


class BookingTypeCreate(BaseModel):
    name: str
    duration_min: int
    availability: str
    location: str


class BookingCreate(BaseModel):
    contact_id: int
    booking_type_id: int
    starts_at: datetime


class InventoryCreate(BaseModel):
    name: str
    quantity: int
    low_threshold: int


class StaffReply(BaseModel):
    body: str
    channel: str = "email"
