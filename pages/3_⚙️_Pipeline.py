import streamlit as st
import time
import os
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

from src.kafka_to_vectordb import KafkaToVectorDBPipeline
from config.config import CHROMA_COLLECTION_NAME

st.set_page_config(
    page_title="Pipeline - Kafka to VectorDB Demo",
    page_icon="⚙️",
    layout="wide"
)

# Initialize session state
if 'demo_stats' not in st.session_state:
    st.session_state.demo_stats = {
        'documents_generated': 0,
        'documents_sent': 0,
        'documents_processed': 0,
        'chunks_created': 0,
        'queries_executed': 0,
        'last_activity': None
    }

if 'pipeline_running' not in st.session_state:
    st.session_state.pipeline_running = False

def run_pipeline(max_messages: int, timeout_seconds: int):
    """Run the vector database pipeline"""
    st.session_state.pipeline_running = True
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("Initializing pipeline...")
        pipeline = KafkaToVectorDBPipeline()
        
        if not pipeline.initialize():
            st.error("❌ Failed to initialize pipeline")
            return
        
        status_text.text("Processing messages from Kafka...")
        progress_bar.progress(0.3)
        
        # Run pipeline
        stats = pipeline.run(max_messages=max_messages, timeout_seconds=timeout_seconds)
        progress_bar.progress(1.0)
        
        if not stats.get("error"):
            # Update statistics
            st.session_state.demo_stats['documents_processed'] += stats.get('processed_messages', 0)
            st.session_state.demo_stats['chunks_created'] += stats.get('processed_chunks', 0)
            st.session_state.demo_stats['last_activity'] = datetime.now().strftime("%H:%M:%S")
            
            st.success(f"✅ Pipeline completed successfully!")
            
            # Display statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Messages Processed", stats.get('processed_messages', 0))
            with col2:
                st.metric("Chunks Created", stats.get('processed_chunks', 0))
            with col3:
                st.metric("Processing Rate", f"{stats.get('messages_per_second', 0):.1f} msg/sec")
        else:
            st.error("❌ Pipeline failed to complete")
    
    except Exception as e:
        st.error(f"❌ Pipeline error: {e}")
    finally:
        st.session_state.pipeline_running = False
        progress_bar.empty()
        status_text.empty()

def main():
    st.title("⚙️ Vector Database Pipeline")
    
    st.markdown(f"""
    Process documents from Kafka, create embeddings using OpenAI, and store in ChromaDB 
    collection `{CHROMA_COLLECTION_NAME}` for semantic search.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔧 Pipeline Configuration")
        
        max_messages = st.number_input("Max messages to process", 1, 100, 20)
        timeout_seconds = st.number_input("Timeout (seconds)", 10, 300, 60)
        
        if st.button("⚙️ Start Pipeline", type="primary", disabled=st.session_state.pipeline_running):
            run_pipeline(max_messages, timeout_seconds)
    
    with col2:
        st.markdown("### Pipeline Settings")
        st.caption("**Embeddings:** OpenAI text-embedding-ada-002")
        st.caption("**Vector DB:** ChromaDB")
        st.caption("**Chunk Size:** 1000 characters")
        st.caption("**Chunk Overlap:** 200 characters")
        st.caption("**Processing:** At-least-once delivery")
        st.caption("**Idempotency:** Deterministic IDs")
    
    if st.session_state.pipeline_running:
        st.info("🔄 Pipeline is running... Please wait for completion.")
    
    # Pipeline process explanation
    st.markdown("### 🔄 Pipeline Process")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Step 1: Message Consumption**
        - Connect to Kafka broker
        - Subscribe to HR documents topic
        - Consume messages with JSON deserialization
        
        **Step 2: Text Processing**
        - Extract document content and metadata
        - Split text into overlapping chunks
        - Prepare chunks for embedding
        """)
    
    with col2:
        st.markdown("""
        **Step 3: Embedding Creation**
        - Send text chunks to OpenAI API
        - Generate vector embeddings
        - Handle API rate limits and errors
        
        **Step 4: Vector Storage**
        - Store embeddings in ChromaDB
        - Preserve document metadata
        - Commit Kafka offsets on success
        """)
    
    # Current statistics
    if st.session_state.demo_stats['documents_processed'] > 0:
        st.markdown("### 📊 Processing Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Documents Processed", st.session_state.demo_stats['documents_processed'])
        
        with col2:
            st.metric("Chunks Created", st.session_state.demo_stats['chunks_created'])
        
        with col3:
            avg_chunks = st.session_state.demo_stats['chunks_created'] / max(1, st.session_state.demo_stats['documents_processed'])
            st.metric("Avg Chunks/Doc", f"{avg_chunks:.1f}")
        
        with col4:
            if st.session_state.demo_stats['last_activity']:
                st.metric("Last Activity", st.session_state.demo_stats['last_activity'])
    
    # Next steps
    if st.session_state.demo_stats['documents_processed'] > 0:
        st.markdown("### 🚀 Next Steps")
        st.success("Documents processed into vector database! Go to the Search page to query them.")
        
        if st.button("🔍 Go to Search", type="secondary"):
            st.switch_page("pages/4_🔍_Search.py")

if __name__ == "__main__":
    main()

