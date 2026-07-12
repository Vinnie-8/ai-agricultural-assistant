from sqlalchemy import create_engine
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

try:
    with engine.connect() as connection:
        print("✅ Connected to PostgreSQL successfully!")
except Exception as e:
    print("❌ Connection failed")
    print(e)