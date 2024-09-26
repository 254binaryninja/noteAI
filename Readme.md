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
   
   streamlit run app.py
   

## Supabase Configuration

1. **Create a Supabase project:** If you don't have one already, sign up for a free account at [https://supabase.com/](https://supabase.com/) and create a new project.

2. **Enable the pgvector extension:**
   - Go to your Supabase project dashboard.
   - Navigate to the **SQL Editor** tab.
   - Run the following SQL command to enable the `pgvector` extension:

     
     CREATE EXTENSION vector;
     

3. **Create the `documents` table and `pdf_check` function:**
   - In the same SQL Editor, run the following SQL commands:

     
     CREATE TABLE documents ( id uuid DEFAULT gen_random_uuid() PRIMARY KEY, content text, embedding vector(768) );

     CREATE OR REPLACE FUNCTION pdf_check( query_embedding vector, notes_value text ) RETURNS TABLE ( id uuid, content text, similarity float ) AS $ BEGIN RETURN QUERY SELECT d.id, d.content, 1 - (d.embedding <=> query_embedding) AS similarity FROM documents d WHERE d.notes = notes_value ORDER BY d.embedding <=> query_embedding LIMIT 10; END; $ LANGUAGE plpgsql;
     

4. **Get your Supabase URL and API key:**
   - Go to **Project Settings** -> **API** to find your Supabase project URL and API key. You'll need these to connect to your Supabase database from the application.

5. Run app
   
   streamlit run app.py
   