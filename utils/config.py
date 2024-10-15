import numpy as np
from supabase import create_client,Client
import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import time
import matplotlib as plt

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


def draw_graph(data):
    # Ensure data is a list or np.array
    if not isinstance(data, (list, np.ndarray)):
        st.error("Invalid data format for graph plotting.")
        return

    # Create x-axis points (length should match data)
    x = np.arange(len(data))
    y = data

    # Create a line plot
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker='o', linestyle='-', color='b')
    plt.title('Sample Graph')
    plt.xlabel('X-axis Label')
    plt.ylabel('Y-axis Label')
    plt.xticks(x, [f'Data {i}' for i in range(len(data))])
    plt.grid()

    # Display the plot in Streamlit
    st.pyplot(plt)

    # Close the figure to avoid issues with overlapping figures
    plt.close()