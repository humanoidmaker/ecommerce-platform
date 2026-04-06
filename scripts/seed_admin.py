import asyncio
import sys
import uuid

sys.path.insert(0, ".")

from app.database import async_session_factory, engine, Base
from app.models.user import User
from app.utils.hashing import hash_password


async def seed_admin():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.email == "admin@ecommerce.local"))
        if result.scalar_one_or_none():
            print("Admin user already exists.")
            return

        admin = User(
            id=uuid.uuid4(),
            email="admin@ecommerce.local",
            password_hash=hash_password("admin123"),
            first_name="Admin",
            last_name="User",
            role="superadmin",
            is_active=True,
            email_verified=True,
        )
        session.add(admin)
        await session.commit()
        print("Admin user created: admin@ecommerce.local / admin123")


if __name__ == "__main__":
    asyncio.run(seed_admin())
