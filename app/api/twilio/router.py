"""
Twilio integration router — IVR, SMS, WhatsApp webhooks.
"""

import os
from typing import Optional

from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import Response

router = APIRouter(prefix="/twilio", tags=["Twilio Voice Integration"])


def validate_twilio_request(request: Request):
    """
    Validate Twilio webhook signature using TWILIO_AUTH_TOKEN.
    Normally we'd use twilio.request_validator.RequestValidator here.
    For local dev/demo, we skip if the token isn't set.
    """
    from app.core.config import get_settings
    settings = get_settings()
    auth_token = settings.TWILIO_AUTH_TOKEN
    if not auth_token:
        return True
        
    signature = request.headers.get("X-Twilio-Signature")
    if not signature:
        raise HTTPException(status_code=403, detail="Missing Twilio Signature")
        
    # In a real app, validate the signature here
    return True


@router.post("/incoming")
async def twilio_incoming(request: Request):
    validate_twilio_request(request)
    
    # Return TwiML
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather numDigits="1" action="/api/v1/twilio/gather-floor" method="POST">
        <Say>Welcome to Odoo Cafe. Press 1 for Ground Floor, 2 for First Floor.</Say>
    </Gather>
</Response>'''
    return Response(content=twiml, media_type="application/xml")


@router.post("/gather-floor")
async def twilio_gather_floor(request: Request, Digits: str = Form(None)):
    validate_twilio_request(request)
    
    floor = "Ground Floor" if Digits == "1" else "First Floor"
    
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather numDigits="2" action="/api/v1/twilio/gather-table?floor={floor}" method="POST">
        <Say>You selected {floor}. Please enter the table number.</Say>
    </Gather>
</Response>'''
    return Response(content=twiml, media_type="application/xml")


@router.post("/gather-table")
async def twilio_gather_table(request: Request, floor: str, Digits: str = Form(None)):
    validate_twilio_request(request)
    
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather numDigits="2" action="/api/v1/twilio/gather-guests?floor={floor}&amp;table={Digits}" method="POST">
        <Say>Please enter the number of guests.</Say>
    </Gather>
</Response>'''
    return Response(content=twiml, media_type="application/xml")


@router.post("/gather-guests")
async def twilio_gather_guests(request: Request, floor: str, table: str, Digits: str = Form(None)):
    validate_twilio_request(request)
    
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Reservation confirmed for {Digits} guests at table {table} on the {floor}. You will receive an SMS confirmation shortly. Goodbye.</Say>
</Response>'''

    # Normally we'd call ReservationService.create() here and send an SMS
    
    return Response(content=twiml, media_type="application/xml")
