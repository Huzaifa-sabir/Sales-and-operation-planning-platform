# Lightweight backfill script for existing S&OP cycles new fields
# Usage: run in an environment with DB configured or adapt to your connection

from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/sop_portal')
DB_NAME = os.getenv('DB_NAME', 'sop_portal')

async def backfill():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    col = db.sop_cycles

    cursor = col.find({})
    updated = 0
    async for doc in cursor:
        sets = {}
        # Backfill year/month from cycleYear/cycleMonth
        if 'year' not in doc and 'cycleYear' in doc:
            sets['year'] = doc.get('cycleYear')
        if 'month' not in doc and 'cycleMonth' in doc:
            sets['month'] = doc.get('cycleMonth')
        # Backfill planningStartMonth from planningPeriod
        pp = doc.get('planningPeriod') or {}
        sy, sm = pp.get('startYear'), pp.get('startMonth')
        if ('planningStartMonth' not in doc) and sy and sm:
            try:
                sets['planningStartMonth'] = datetime(int(sy), int(sm), 1)
            except Exception:
                pass
        if sets:
            await col.update_one({'_id': doc['_id']}, {'$set': sets})
            updated += 1
    print(f"Backfill complete. Updated {updated} documents.")

if __name__ == '__main__':
    asyncio.run(backfill())
