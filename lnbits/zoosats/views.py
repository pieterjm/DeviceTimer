from http import HTTPStatus

from fastapi import Depends, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from lnbits.core.crud import update_payment_status
from lnbits.core.models import User
from lnbits.core.views.api import api_payment
from lnbits.decorators import check_user_exists

from . import zoosats_ext, zoosats_renderer
from .crud import get_device, get_payment, get_payment_allowed

from .models import PaymentAllowed

from loguru import logger


templates = Jinja2Templates(directory="templates")


@zoosats_ext.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return zoosats_renderer().TemplateResponse(
        "zoosats/index.html",
        {"request": request, "user": user.dict()},
    )

@zoosats_ext.get("/device/{deviceid}/{switchid}")
async def zoosats_device(request: Request, deviceid: str, switchid: str):
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
        return zoosats_renderer().TemplateResponse(
            "zoosats/closed.html",
            {"request":request})

    if result == PaymentAllowed.WAIT:
        return zoosats_renderer().TemplateResponse(
            "zoosats/wait.html",
            {"request":request})

    if result == PaymentAllowed.OPEN:
        return zoosats_renderer().TemplateResponse(
            "zoosats/open.html",
            {"request":request,"device":device,"switch":switch})

    
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail="Unknown Feeder state"
    )

    


