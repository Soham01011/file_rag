import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB Connection URI
MONGO_URI = "mongodb://localhost:27017"  # Change if needed
DB_NAME = "test_db"  # Change to your database name

# Create MongoDB Client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

async def test_db_connection():
    """Test MongoDB connection by running a ping command."""
    try:
        await db.command("ping")
        print("✅ MongoDB Connection Successful!")
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_db_connection())
