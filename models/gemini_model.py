from langchain_community.vectorstores import SupabaseVectorStore
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from supabase.client import create_client
from langchain.chains import RetrievalQA, LLMChain
from dotenv import load_dotenv
from langchain.schema import Document
from utils.config import draw_graph
import ast

load_dotenv()

# Load Supabase credentials
supabase_url = os.getenv("SUPABASE_PROJECT_URL")
supabase_key = os.getenv("SUPABASE_API_KEY")
supabase_client = create_client(supabase_url, supabase_key)

# Initialize LLM and Embeddings
llm = ChatGoogleGenerativeAI(
    model='gemini-1.5-flash',
    verbose=True,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

conv_history = []

# Define Prompt Templates
standaloneQuestionTemplate = """Given some conversation history (if any) and a question, convert the question to a standalone question.

Conversation history: {conv_history}
Question: {question}

Standalone question:
"""

standaloneQuestionPrompt = PromptTemplate(
    input_variables=["conv_history", "question"],
    template=standaloneQuestionTemplate
)

answerTemplate = """
You are a friendly and knowledgeable AI teacher, always excited to help students learn. Use the following information to answer the user's question in a supportive and encouraging manner. If you're not sure about something, it's okay to say so and suggest ways to find out more.

If you think a graph could help explain the concept, you can say something like: "Draw graph with data: [(x1, y1), (x2, y2), ...]".

Let's explore this topic together!

Context: {context}
Student's Question: {question}

Now, let's break this down and provide a clear, engaging answer:
"""

answerPrompt = PromptTemplate(
    input_variables=["context", "question"],
    template=answerTemplate
)


# Function to convert prompt to a standalone question
def convert_to_standalone(conv_history, question):
    standalone_question_chain = LLMChain(llm=llm, prompt=standaloneQuestionPrompt)
    return standalone_question_chain.run({
        "conv_history": conv_history,
        "question": question
    })


# Function to retrieve relevant documents from Supabase based on the given unit
import json

def retrieve_relevant_documents(standalone_question, unit):
    # Use the vector store to search for relevant docs from the appropriate unit table
    query_embedding = embeddings.embed_query(standalone_question)
    print(f"Query embedding: {json.dumps(query_embedding)}")

    # Use the `match_documents` RPC function to search for documents in the specific unit table
    results = supabase_client.rpc(
        'match_documents',
        {
            'query_embedding': query_embedding,
            'match_threshold': 0.3,  # Adjust the threshold as needed
            'match_count': 10,  # Adjust the number of documents to retrieve
            'table_name': f'pdf_embeddings_unit_{unit}'
        }
    ).execute()

    if not results.data:
        print("No documents retrieved.")
    else:
        print(f"Retrieved documents: {json.dumps(results.data)}")

    relevant_docs = [
        Document(page_content=row['content'], metadata={'id': row['id']})
        for row in results.data
    ]
    return relevant_docs

# Function to generate the final answer using relevant documents
def generate_answer(relevant_docs, question):
    # Combine the content of the relevant documents
    context = "\n".join([doc.page_content for doc in relevant_docs])

    # Use the LLM chain to generate the final answer
    answer_chain = LLMChain(llm=llm, prompt=answerPrompt)
    return answer_chain.run({
        "context": context,
        "question": question
    })


# Append conversation history with the human question and AI response
def append_conv_history(conv_history, user_question, ai_response):
    conv_history.append({
        "human": user_question,
        "AI": ai_response
    })


def run_full_chain(conv_history, user_question, unit):
    print("Starting RAG process...")

    # Convert to standalone question
    standalone_question = convert_to_standalone(conv_history, user_question)
    print(f"Standalone question: {standalone_question}")

    # Retrieve relevant documents
    relevant_docs = retrieve_relevant_documents(standalone_question, unit)
    print(f"Retrieved {len(relevant_docs)} relevant documents")

    # Generate the final answer
    final_answer = generate_answer(relevant_docs, standalone_question)
    print(f"Generated answer: {final_answer}")

    # Check if the final answer requests drawing a graph
    if "Draw graph with data:" in final_answer:
        # Extract the data part from the response
        try:
            # Assuming the response includes something like "Draw graph with data: [(x1, y1), (x2, y2), ...]"
            data_str = final_answer.split("Draw graph with data:")[-1].strip()
            data_list = ast.literal_eval(data_str)

            # Draw the graph using the extracted data
            draw_graph(data_list)
            print("Graph drawn successfully")
        except Exception as e:
            print(f"Error parsing graph data: {e}")

    # Append conversation history
    append_conv_history(conv_history, user_question, final_answer)
    print("Updated conversation history")

    return final_answer