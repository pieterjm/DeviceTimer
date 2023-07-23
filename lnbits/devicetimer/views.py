from http import HTTPStatus

from fastapi import Depends, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, FileResponse

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
        return FileResponse(
            "lnbits/extensions/devicetimer/static/image/keine-fuetterung.png",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            })

    if result == PaymentAllowed.WAIT:
        return FileResponse(
            "lnbits/extensions/devicetimer/static/image/keine-fuetterung.png",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            })


    if result == PaymentAllowed.OPEN:
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
    

