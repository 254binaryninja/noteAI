from supabase import create_client,Client
import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import time


supabase_url = os.getenv("SUPABASE_PROJECT_URL")
supabase_key = os.getenv("SUPABASE_API_KEY")

def get_supabase_client():
    return create_client(supabase_url, supabase_key)

supabase_client: Client = get_supabase_client()


def typing_effect(text, role="assistant", delay=0.05):
    """Simulate typing effect by gradually displaying the content."""
    message_placeholder = st.chat_message(role).empty()
    typed_text = ""

    for char in text:
        typed_text += char
        message_placeholder.markdown(typed_text + "▌")  # Adding a cursor effect
        time.sleep(delay)  # Delay to simulate typing speed

    message_placeholder.markdown(typed_text)