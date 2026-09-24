import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    try:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    except Exception:
        GOOGLE_API_KEY = None

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not configured.")