import streamlit as st
from utils.config import typing_effect
from utils.pdf import sidebar_and_pdf_display
from models.rag_model import CreateEmbeddings
from models.gemini_model import run_full_chain, conv_history

def main():
    st.title("Note AI")
    st.markdown("""
      This app allows you to upload a PDF file, extracts the text, and performs
      Retrieval-Augmented Generation (RAG) on the document content. Ask questions
      based on the uploaded PDF and get intelligent responses.
      """)

    # Call the sidebar display function to get selected PDF and unit
    selected_pdf, unit = sidebar_and_pdf_display()

    # File uploader
    uploaded_file = st.sidebar.file_uploader("Upload a new PDF", type="pdf")

    if uploaded_file:
        embed_creator = CreateEmbeddings(uploaded_file, uploaded_file.name, unit)
        if embed_creator.extract_text():
            st.sidebar.success("PDF processed and saved successfully!")
        else:
            st.sidebar.error("Error processing the PDF.")

    # Initialize session state for messages if not already done
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input for new user question
    if prompt := st.chat_input("Ask any question"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = run_full_chain(conv_history, prompt, unit)  # Pass the unit here

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

if __name__ == "__main__":
    main()