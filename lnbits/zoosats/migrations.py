import json

from lnbits.db import Database

async def m001_initial(db):
    """
    Initial device table.
    """
    await db.execute(
        f"""
        CREATE TABLE zoosats.device (
            id TEXT NOT NULL PRIMARY KEY,
            key TEXT NOT NULL,
            title TEXT NOT NULL,
            wallet TEXT NOT NULL,
            currency TEXT NOT NULL,
            switches TEXT,
            timestamp TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
    """
    )

    
    await db.execute(
        f"""
        CREATE TABLE zoosats.payment (
            id TEXT NOT NULL PRIMARY KEY,
            deviceid TEXT NOT NULL,
            switchid TEXT NOT NULL,
            payhash TEXT,
            payload TEXT NOT NULL,
            sats {db.big_int},
            timestamp TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
    """
    )

async def m002_redux(db):
    await db.execute(
        "ALTER TABLE zoosats.device ADD COLUMN available_start INT DEFAULT 540;"
    )

    await db.execute(
        "ALTER TABLE zoosats.device ADD COLUMN available_stop INT DEFAULT 1020;"
    )

async def m003_redux(db):
    await db.execute(
        "ALTER TABLE zoosats.device DROP COLUMN available_start;"
    )

    await db.execute(
        "ALTER TABLE zoosats.device DROP COLUMN available_stop;"
    )
    
    await db.execute(
        "ALTER TABLE zoosats.device ADD COLUMN available_start TEXT DEFAULT '09:00';"
    )

    await db.execute(
        "ALTER TABLE zoosats.device ADD COLUMN available_stop TEXT DEFAULT '17:00';"
    )
    


