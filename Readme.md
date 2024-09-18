## PDF Education Assistant

# NoteAI
This project is a web-based application built with Streamlit that allows users to chat with their PDFs to streamline their learning. The app leverages AI language models (such as Gemini or Ollama offline models) to answer questions about the uploaded PDF, making the learning process interactive and efficient.

## Features
- Upload PDF documents
- Chat with the content of your PDFs
- Get AI-generated summaries, explanations, or answers based on the document
- Responsive and user-friendly interface built with Streamlit

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- [Gemini](https://www.gemini.ai/) API key
- [Supabase](https://supabase.com/) account and API key

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/254binaryninja/noteAI.git
   cd noteAI

2. Create Environment 
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. Install dependancies
   ```bash
   pip install -r requirements.txt

4. Run app
   ```bash
   streamlit run app.py
