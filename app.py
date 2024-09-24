import streamlit as st
from models.rag_model import CreateEmbeddings
from models.gemini_model import run_full_chain, conv_history
from dotenv import load_dotenv
load_dotenv() 

def main():
    st.title("Note AI")
    st.markdown("""
    This app allows you to upload a PDF file, extracts the text, and performs
    Retrieval-Augmented Generation (RAG) on the document content. Ask questions
    based on the uploaded PDF and get intelligent responses.
    """)
    
    if 'file_uploaded' not in st.session_state:
        st.session_state['file_uploaded'] = False

    if 'note_value' not in st.session_state:
        st.session_state['note_value'] = ""    

    if not st.session_state['file_uploaded']:
        uploaded_file = st.file_uploader("Choose a pdf file", type="pdf")
        if uploaded_file is not None:
           embeddings = CreateEmbeddings(uploaded_file, uploaded_file.name)
           embeddings.extract_text()
           st.success("File uploaded successfully")
           st.session_state['file_uploaded'] = True

    if st.session_state['file_uploaded']:
        st.info("PDF converted into Embeddings successfully")

      # Add input field for note value 
    note_value = st.text_input("Enter your note name for this session:",value=st.session_state['note_value'])
    if note_value != st.session_state['note_value']:
        st.session_state['note_value'] = note_value
        if note_value == True:
            st.success(f"Successfully selected {note_value}")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
             st.markdown(message["content"])         

    if prompt := st.chat_input("Ask any question"):
       st.session_state.messages.append({"role": "user", "content": prompt})
       with st.chat_message("user"):
            st.markdown(prompt)

       response = run_full_chain(conv_history, prompt,note_value)  

       st.session_state.messages.append({"role": "assistant", "content": response}) 
       with st.chat_message("assistant"):
           st.markdown(response)    

if __name__ == "__main__":
    main()