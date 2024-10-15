import os
from supabase.client import create_client
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pdfminer.high_level import extract_text
from typing import BinaryIO, List, Dict, Any
from dotenv import load_dotenv
from datetime import datetime
import base64

load_dotenv()

# Initialize embeddings model
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Supabase credentials
supabase_url = os.getenv("SUPABASE_PROJECT_URL")
supabase_key = os.getenv("SUPABASE_API_KEY")

# Create a single Supabase client instance
supabase_client = create_client(supabase_url, supabase_key)


class CreateEmbeddings:
    def __init__(self, file: BinaryIO, file_name: str, unit: int) -> None:
        self.file = file
        self.file_name = file_name
        self.unit = unit  # To dynamically select the right table

    def extract_text(self) -> bool:
        try:
            # Extract text from the PDF file
            text = extract_text(self.file)
            splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = splitter.split_text(text)

            embedding_data = []
            for chunk in chunks:
                # Generate embedding for each chunk
                embedding = embeddings.embed_query(chunk)
                embedding_data.append({
                    "content": chunk,
                    "embedding": embedding,  # Ensure embedding is in list format
                    "metadata": {"file_name": self.file_name}
                })

            # Save to Supabase
            self.save_to_supabase(embedding_data)
            return True
        except Exception as e:
            print(f"Error extracting text: {str(e)}")
            return False

    def save_to_supabase(self, embedding_data: List[Dict[str, Any]]) -> None:
        table_name = f"pdf_embeddings_unit_{self.unit}"
        try:
            # Insert embeddings into the appropriate unit table
            supabase_client.table(table_name).insert(embedding_data).execute()
            print(f"Data saved to Supabase in table {table_name}")
            self.save_pdf_file(self.file,self.file_name,self.unit)
        except Exception as e:
            print(f"Error saving to Supabase: {e}")

    def save_pdf_file(self, file, file_name,unit) -> None:
        try:
            # Save the file itself into the corresponding `pdf_files_unit_X` table
            table_name = f"pdf_files_unit_{unit}"
            file_content = file.read()

            # Encode the binary content to base64
            encoded_file_content = base64.b64encode(file_content).decode('utf-8')  # Convert bytes to string
            file_data = {
                "file_name": file_name,
                "file_content": encoded_file_content,
                "uploaded_at": datetime.utcnow().isoformat()
            }
            response = supabase_client.table(table_name).insert(file_data).execute()
            if response.data:
                print(f"File saved to Supabase in table {table_name}")
            else:
                print(f"Failed to save file: {response.error}")

        except Exception as e:
            print(f"Error saving PDF file to Supabase: {e}")


def get_pdf_files(unit: int):
    table_name = f"pdf_files_unit_{unit}"
    try:
        response = supabase_client.table(table_name).select('file_name').execute()
        return list(set([item['file_name'] for item in response.data]))
    except Exception as e:
        print(f"Error fetching PDF files from {table_name}: {str(e)}")
        return []


def setup_rag(file_name: str, unit: int):
    table_name = f"pdf_embeddings_unit_{unit}"
    try:
        response = supabase_client.table(table_name).select('content, embedding').eq('metadata->>file_name',
                                                                                     file_name).execute()
        return response.data
    except Exception as e:
        print(f"Error setting up RAG from {table_name}: {str(e)}")
        return []
