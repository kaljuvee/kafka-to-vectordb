import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Kafka Configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'hr-documents')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'vectordb-ingester')

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# ChromaDB Configuration
CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', './data/chroma_db')
CHROMA_COLLECTION_NAME = os.getenv('CHROMA_COLLECTION_NAME', 'hr_documents')

# Text Processing Configuration
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))

# Streamlit Configuration
STREAMLIT_PORT = int(os.getenv('STREAMLIT_PORT', '8501'))

# Data Generation Configuration
NUM_SYNTHETIC_DOCS = int(os.getenv('NUM_SYNTHETIC_DOCS', '50'))

