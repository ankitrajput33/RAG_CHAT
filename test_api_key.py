import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    print("GOOGLE_API_KEY loaded successfully!")
else:
    print("GOOGLE_API_KEY was NOT found.")

