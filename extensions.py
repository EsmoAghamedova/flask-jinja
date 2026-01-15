from flask_sqlalchemy import SQLAlchemy
import os
from groq import Groq

db = SQLAlchemy()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))