
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline
from llama_index.llms.openai import OpenAI
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
import json
import nest_asyncio
from dotenv import load_dotenv

load_dotenv()

def get_documents():
    with open("data.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    documents = []
    for item in data:
        text = f"Name: {item['name']}\nRelation: {item['relation']}\nDescription: {item['description']}\nEmail: {item['email']}"
        doc = Document(
            text=text,
            metadata={
                "name": item["name"],
                "relation": item["relation"], 
                "email": item["email"]
            }
        )
        documents.append(doc)

    return documents


docs = get_documents()

db = chromadb.PersistentClient(path="./invites_chroma_db")
chroma_collection = db.get_or_create_collection(name="invites")

vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
splitter = SentenceSplitter()


pipeline = IngestionPipeline(
    transformations=[
        splitter,
        embed_model
    ],
    vector_store=vector_store,
)


nodes = pipeline.run(documents=docs)


index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store, embed_model=embed_model
)

nest_asyncio.apply()

llm = OpenAI(model="gpt-4o-mini")
query_engine = index.as_query_engine(
    llm=llm,
    response_mode="tree_summarize",
)
response = query_engine.query(
    "Respond using a invites_list who will come to party?"
)
print(response)