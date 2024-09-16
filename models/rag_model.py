import os
from supabase.client import create_client
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pdfminer.high_level import extract_text
from typing import BinaryIO, List, Dict, Any

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

supabase_url = os.environ.get("SUPABASE_PROJECT_URL")
supabase_key = os.environ.get("SUPABASE_API_KEY")

supabase_client = create_client(supabase_url, supabase_key)



class CreateEmbeddings:
    def __init__(self, file: BinaryIO, file_name: str) -> None:
        self.file = file
        self.file_name = file_name

    def extract_text(self) -> None:
        try:
            text = extract_text(self.file)
            splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = splitter.split_text(text)
            embedding_data = []
            for chunk in chunks:
                embedding = embeddings.embed_query(chunk)
                embedding_data.append({
                    "notes": self.file_name,
                    "content": chunk,
                    "embedding": embedding
                })
            self.save_to_supabase(embedding_data)
        except Exception as e:
            print(f"Error extracting text: {str(e)}")

    def save_to_supabase(self, embedding_data: List[Dict[str, Any]]) -> None:
        try:
            response = supabase_client.table("documents").insert(embedding_data).execute()
            if response.status_code == 201:
                print("Embeddings created successfully")
            else:
                print(f"Error saving embeddings to supabase: {response.error_message}")
        except Exception as e:
            print(f"Error saving to Supabase: {str(e)}")

