from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Chargement variables d'environnement
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")

# MongoDB connection
client = AsyncIOMotorClient(MONGODB_URI)
db = client.flashcard_app
