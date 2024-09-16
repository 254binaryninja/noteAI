import streamlit as st

def main():
    #Title for the app
    st.title("Note AI")
    st.markdown("""
    This app allows you to upload a PDF file, extracts the text, and performs
    Retrieval-Augmented Generation (RAG) on the document content. Ask questions
    based on the uploaded PDF and get intelligent responses.
    """)


    #file upload section
    uploaded_file = st.file_uploader("Choose a pdf file", type="pdf")

if __name__ == "__main__":
    main()
