import os
import json
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

logger = logging.getLogger("visionpilot.db")

# Load Configuration
CONFIG_PATH = os.path.join("E:\\VisionPilot_AI", "configs", "config.json")
Base = declarative_base()

try:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
except Exception as e:
    logger.warning(f"Failed to load config, using default DB paths. Error: {e}")
    config = {
        "database": {
            "postgresql_url": "postgresql+asyncpg://visionpilot:visionpilot@localhost/visionpilot_db",
            "sqlite_fallback_url": "sqlite+aiosqlite:///E:/VisionPilot_AI/database/visionpilot.db",
            "use_sqlite_fallback": true
        }
    }

db_config = config.get("database", {})
db_url = db_config.get("postgresql_url")
sqlite_url = db_config.get("sqlite_fallback_url")
use_sqlite = db_config.get("use_sqlite_fallback", True)

# Environment Overrides (Railway/Docker envs)
env_db_url = os.environ.get("DATABASE_URL")
if env_db_url:
    if env_db_url.startswith("postgres://"):
        env_db_url = env_db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif env_db_url.startswith("postgresql://"):
        env_db_url = env_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    db_url = env_db_url
    use_sqlite = False
    logger.info("DATABASE_URL environment variable detected. Disabling SQLite fallback.")

# Initialize Engine
if use_sqlite:
    logger.info("Using SQLite database fallback.")
    # Ensure database dir exists
    db_dir = os.path.dirname(sqlite_url.replace("sqlite+aiosqlite:///", ""))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    engine = create_async_engine(sqlite_url, connect_args={"check_same_thread": False})
else:
    logger.info("Using PostgreSQL database engine.")
    engine = create_async_engine(db_url)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    """Dependency for API endpoints to retrieve DB sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
