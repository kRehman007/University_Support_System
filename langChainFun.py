# langchain.py
import os
from dotenv import load_dotenv
load_dotenv()

# ============= KEYS =============
groq_api_key = os.getenv("GROQ_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")

# ============= LLM =============
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# ============= LOAD DOCUMENTS =============
from langchain_community.document_loaders import TextLoader

# folder = "./school_knowledge_base"
folder = "./dataset"
docs = []

for file in os.listdir(folder):
    docs.extend(TextLoader(os.path.join(folder, file)).load())

# ============= CHUNKING =============
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(docs)

# ============= EMBEDDINGS =============
from langchain_huggingface import HuggingFaceEmbeddings

def download_embedding():
    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": False}
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )

embeddings = download_embedding()

# ============= PINECONE SETUP =============
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

pc = Pinecone(api_key=pinecone_api_key)
# index_name = "school-support-system"
index_name = "university-support-system"

# Check if index exists → create or load
if index_name not in pc.list_indexes().names():
    print("Creating new Pinecone index...")

    pc.create_index(
        name=index_name,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

    vector_store = PineconeVectorStore.from_documents(
        chunks,
        embedding=embeddings,
        index_name=index_name
    )
    print("Pinecone index created and documents added.")
else:
    print("Loading existing Pinecone index...")

    vector_store = PineconeVectorStore.from_existing_index(
        embedding=embeddings,
        index_name=index_name
    )
    print("Pinecone index loaded.")

# ============= RETRIEVER =============
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 3, "score_threshold": 0.5},
)
