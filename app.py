import sys
import traceback
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os

init_error_log = []

# Optional heavy dependencies – provide fallbacks if not installed
try:
    from src.helper import download_hugging_face_embeddings
except Exception as e:
    init_error_log.append(f"Failed to import download_hugging_face_embeddings: {e}")
    download_hugging_face_embeddings = None

try:
    from langchain_pinecone import PineconeVectorStore
except Exception as e:
    init_error_log.append(f"Failed to import PineconeVectorStore: {e}")
    PineconeVectorStore = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception as e:
    init_error_log.append(f"Failed to import ChatGoogleGenerativeAI: {e}")
    ChatGoogleGenerativeAI = None

try:
    from langchain_classic.chains import create_retrieval_chain
    from langchain_classic.chains.combine_documents import create_stuff_documents_chain
    from langchain_core.prompts import ChatPromptTemplate
except Exception as e:
    init_error_log.append(f"Failed to import LangChain components: {e}")
    create_retrieval_chain = None
    create_stuff_documents_chain = None
    ChatPromptTemplate = None

try:
    from src.prompt import system_prompt
except Exception as e:
    system_prompt = "You are a helpful assistant."

app = Flask(__name__)

# Load environment variables
load_dotenv(override=True)

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

if PINECONE_API_KEY:
    os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

embeddings = None
if download_hugging_face_embeddings:
    try:
        embeddings = download_hugging_face_embeddings()
    except Exception as e:
        init_error_log.append(f"Embedding load failed: {str(e)}\n{traceback.format_exc()}")

if PineconeVectorStore and embeddings:
    index_name = "medibot"
    try:
        docsearch = PineconeVectorStore.from_existing_index(
            index_name=index_name,
            embedding=embeddings
        )
        retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    except Exception as e:
        init_error_log.append(f"Failed to load Pinecone Index: {str(e)}\n{traceback.format_exc()}")
        docsearch = None
        retriever = None
else:
    docsearch = None
    retriever = None

if ChatGoogleGenerativeAI:
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.4,
            max_output_tokens=4096
        )
    except Exception as e:
        init_error_log.append(f"Failed to init ChatGoogleGenerativeAI: {e}")
        llm = None
else:
    llm = None

if ChatPromptTemplate:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
else:
    prompt = None

if create_stuff_documents_chain and create_retrieval_chain and llm and prompt and retriever:
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
else:
    rag_chain = None

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form.get("msg", "")
    if rag_chain:
        try:
            response = rag_chain.invoke({"input": msg})
            answer = response.get("answer", "No answer")
        except Exception as e:
            answer = f"Error during RAG execution: {e}"
    else:
        # Return the exact error to the user interface!
        errors = "\n".join(init_error_log)
        if not errors:
            errors = "Some required components were missing but no exception was thrown."
        
        answer = f"SYSTEM ERROR DETECTED ON STARTUP:\n\n{errors}\n\nPlease check your API keys or installed packages!"
    
    return str(answer)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
