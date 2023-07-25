from http import HTTPStatus

from fastapi import Depends, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, FileResponse, Response

from lnbits.core.crud import update_payment_status
from lnbits.core.models import User
from lnbits.core.views.api import api_payment
from lnbits.decorators import check_user_exists

from . import devicetimer_ext, devicetimer_renderer, devicetimer_static_files
from .crud import get_device, get_payment, get_payment_allowed

from .models import PaymentAllowed

from loguru import logger
import pyqrcode
from io import BytesIO

import os
import httpx

templates = Jinja2Templates(directory="templates")


@devicetimer_ext.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return devicetimer_renderer().TemplateResponse(
        "devicetimer/index.html",
        {"request": request, "user": user.dict()},
    )


@devicetimer_ext.get("/device/{deviceid}/{switchid}")
async def devicetimer_device(request: Request, deviceid: str, switchid: str):
    """
    return the landing page for a device where the customer
    kan initiate the feeding or when it is a allowed, an LNURL payment
    """
    device = await get_device(deviceid)
    if not device:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Device does not exist"
        )

    switch = None
    for _switch in device.switches:
        if _switch.id == switchid:
            switch = _switch

    if not switch:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Switch does not exist"
        )

    result = await get_payment_allowed(device,switch)
    logger.info(f"PaymentAllowd == {result}")

    if result == PaymentAllowed.CLOSED:
        return devicetimer_renderer().TemplateResponse(
            "devicetimer/closed.html",
             {"request":request,"device":device,"switch":switch})

    if result == PaymentAllowed.WAIT:
        return ImportError

        return devicetimer_renderer().TemplateResponse(
            "devicetimer/wait.html",
            {"request":request,"device":device,"switch":switch})


    if result == PaymentAllowed.OPEN:
        return devicetimer_renderer().TemplateResponse(
            "devicetimer/open.html",
            {"request":request,"device":device,"switch":switch})

    
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail="Unknown Feeder state"
    )


def proxy_allowed(url: str):
    if not url:
        raise
    if 'localhost' in url.lower():
        raise
    if '127.0.0.1' in url:
        raise
    if url.startswith("https://"):
        return
    raise

@devicetimer_ext.get("/device/{deviceid}/{switchid}/qrcode")
async def devicetimer_qrcode(request: Request, deviceid: str, switchid: str):
    """
    return the landing page for a device where the customer
    kan initiate the feeding or when it is a allowed, an LNURL payment
    """
    device = await get_device(deviceid)
    if not device:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Device does not exist"
        )

    switch = None
    for _switch in device.switches:
        if _switch.id == switchid:
            switch = _switch

    if not switch:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Switch does not exist"
        )

    result = await get_payment_allowed(device,switch)
    logger.info(f"PaymentAllowd == {result}")
    
    if result == PaymentAllowed.CLOSED:
        async with httpx.AsyncClient() as client:              
            try: 
                proxy_allowed(device.closed_url)
                response = await client.get(device.closed_url)                
                return Response(response.content)
            except:
                raise HTTPException(status_code=404, detail="Item not found")

    if result == PaymentAllowed.WAIT:
        async with httpx.AsyncClient() as client:   
            try:
                proxy_allowed(device.wait_url)
                response = await client.get(device.wait_url)
                return Response(response.content)
            except:
                raise HTTPException(status_code=404, detail="Item not found")

    qr = pyqrcode.create(switch.lnurl)
    stream = BytesIO()
    qr.svg(stream, scale=3)
    stream.seek(0)

    async def _generator(stream: BytesIO):
        yield stream.getvalue()

    return StreamingResponse(
        _generator(stream),
        headers={
            "Content-Type": "image/svg+xml",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )
    
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail="Unknown Feeder state"
    )
    

