import asyncio
from typing import List

from fastapi import APIRouter
from loguru import logger
from fastapi.staticfiles import StaticFiles

from lnbits.db import Database
from lnbits.helpers import template_renderer
from lnbits.tasks import create_permanent_unique_task

db = Database("ext_devicetimer")

devicetimer_ext: APIRouter = APIRouter(prefix="/devicetimer", tags=["devicetimer"])

devicetimer_static_files = [
    {
        "path": "/devicetimer/static",
        "app": StaticFiles(directory="lnbits/extensions/devicetimer/static"),
        "name": "devicetimer_static",
    }
]


def devicetimer_renderer():
    return template_renderer(["lnbits/extensions/devicetimer/templates"])


from .lnurl import *  # noqa: F401,F403
from .tasks import wait_for_paid_invoices
from .views import *  # noqa: F401,F403
from .views_api import *  # noqa: F401,F403

scheduled_tasks: list[asyncio.Task] = []

def devicetimer_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)

def devicetimer_start():
    task = create_permanent_unique_task("ext_devicetimer", wait_for_paid_invoices)
    scheduled_tasks.append(task)
