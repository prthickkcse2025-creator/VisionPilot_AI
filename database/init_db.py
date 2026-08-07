import asyncio
import os
import sys

# Add E:\VisionPilot_AI to path so backend module can be imported
sys.path.append("E:\\VisionPilot_AI")

from backend.db import engine, Base
from backend.models_db import (
    User,
    Image,
    ProcessingHistory,
    OCRResult,
    DetectionResult,
    PackagingResult,
    PipelineLog,
    Setting
)

async def init_models():
    print("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init_models())
