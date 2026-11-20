import base64
import io
from datetime import datetime
from pathlib import Path

import streamlit as st
from PIL import Image

# Project root folder (birthday_surprise/)
BASE_DIR = Path(__file__).resolve().parent.parent


def load_css(relative_path: str) -> str:
    """Read a CSS file from the project."""
    return (BASE_DIR / relative_path).read_text(encoding="utf-8")


@st.cache_data(show_spinner=False)
def image_to_data_uri(relative_path: str, max_size: int = 900) -> str:
    """Resize an image and convert it to a base64 string for the HTML gallery."""
    img = Image.open(BASE_DIR / relative_path).convert("RGB")
    img.thumbnail((max_size, max_size))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=88)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def time_until_birthday(month: int, day: int, now=None):
    """
    Returns a timedelta until the next birthday.
    Returns None if today is the birthday.
    """
    now = now or datetime.now()
    if now.month == month and now.day == day:
        return None
    target = datetime(now.year, month, day)
    if target < now:
        target = datetime(now.year + 1, month, day)
    return target - now