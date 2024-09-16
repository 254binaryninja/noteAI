from langchain_community.vectorstores import SupabaseVectorStore
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from supabase.client import create_client
from langchain.chains import RetrievalQA,LLMChain

supabase_url = os.environ.get("SUPABASE_PROJECT_URL")
supabase_key = os.environ.get("SUPABASE_API_KEY")


llm = ChatGoogleGenerativeAI(
  model='gemini-1.5-flash',
    verbose=True,
    google_api_key=os.getenv("GOOGLE_API_KEY")   
)

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

supabase_client = create_client(supabase_url, supabase_key)

conv_history = []

standaloneQuestionTemplate = """Given some conversation history (if any) and a question, convert the question to a standalone question.

Conversation history: {conv_history}
Question: {question}

Standalone question:
"""

standaloneQuestionPrompt = PromptTemplate(
    input_variables=["conv_history", "question"],
    template=standaloneQuestionTemplate
)

answerTemplate = """You are a friendly and knowledgeable AI teacher, always excited to help students learn. Use the following information to answer the user's question in a supportive and encouraging manner. If you're not sure about something, it's okay to say so and suggest ways to find out more.

Let's explore this topic together!

Context: {context}
Student's Question: {question}

Now, let's break this down and provide a clear, engaging answer:
"""

answerPrompt = PromptTemplate(
    input_variables=["context", "question"],
    template=answerTemplate
)

vector_store = SupabaseVectorStore(
    client=supabase_client,
    table_name="documents",
    embedding=embeddings,
    query_name="match_docs",
)


## 1 define function to turn prompt to standalone question

def convert_to_stanalone(conv_history,question):
    ## use llm cahin to generate standalone question
    standalone_question_chain  = LLMChain(llm=llm, prompt=standaloneQuestionPrompt)
    return standalone_question_chain.run({
         "conv_history": conv_history,
         "question": question
    }) 


## define function to retreive relevant docs from supabase
def retreive_relevant_documents(standalone_question):
    ## Use vector store to search for relevant docs
    relevant_docs = vector_store.similarity_search(standalone_question, k=5)
    return relevant_docs

## define function to generate final function
def generate_answer(relevant_docs,questions):
    # combine content of the relevant document
    context = relevant_docs
    # use llm chain to generate  final answer
    answer_chain = LLMChain(llm=llm, prompt=answerPrompt)
    return answer_chain.run({
        "context":context,
        "question":questions
    })

def append_conv_history(conv_history,user_question,ai_response):
    conv_history.append({
        "human":user_question,
        "AI":ai_response
    })

# run the entire chain

def run_full_chain(conv_history,user_question):
    # Convert the user question to a standalone question
    standalone_question = convert_to_stanalone(conv_history, user_question)
    
    # Retrieve relevant documents based on the standalone question
    relevant_docs = retreive_relevant_documents(standalone_question)
    
    # Generate the final answer using the retrieved documents and user question
    final_answer = generate_answer(relevant_docs, standalone_question)
    
    # Append the user's question and AI's response to the conversation history
    append_conv_history(conv_history, user_question, final_answer)
    
    return final_answer