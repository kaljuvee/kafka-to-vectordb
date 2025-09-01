import streamlit as st
import time
import os
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

from src.kafka_producer import DocumentProducer
from config.config import KAFKA_TOPIC

st.set_page_config(
    page_title="Kafka Producer - Kafka to VectorDB Demo",
    page_icon="📤",
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

if 'generated_documents' not in st.session_state:
    st.session_state.generated_documents = []

def send_documents_to_kafka(delay: float):
    """Send documents to Kafka or SQLite queue"""
    if not st.session_state.generated_documents:
        st.error("No documents to send")
        return
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize producer
        status_text.text("Initializing producer...")
        producer = DocumentProducer()
        
        if not producer.connect():
            st.error("❌ Failed to connect to message queue")
            return
        
        # Show connection type
        queue_type = "SQLite" if producer.use_sqlite else "Kafka"
        st.info(f"📡 Connected to {queue_type} message queue")
        
        documents = st.session_state.generated_documents
        total_docs = len(documents)
        sent_count = 0
        
        for i, doc in enumerate(documents):
            status_text.text(f"Sending document {i+1}/{total_docs}: {doc['title'][:50]}...")
            
            if producer.send_document(doc):
                sent_count += 1
            
            progress_bar.progress((i + 1) / total_docs)
            time.sleep(delay)
        
        producer.close()
        
        # Update statistics
        st.session_state.demo_stats['documents_sent'] += sent_count
        st.session_state.demo_stats['last_activity'] = datetime.now().strftime("%H:%M:%S")
        
        if sent_count == total_docs:
            st.success(f"✅ Successfully sent {sent_count} documents to {queue_type}!")
        else:
            st.warning(f"⚠️ Sent {sent_count}/{total_docs} documents (some failed)")
    
    except Exception as e:
        st.error(f"❌ Error sending documents: {e}")
    finally:
        progress_bar.empty()
        status_text.empty()

def main():
    st.title("📤 Kafka Producer")
    
    st.markdown(f"""
    Send generated documents to Kafka topic `{KAFKA_TOPIC}` for processing by the vector database pipeline.
    """)
    
    if not st.session_state.generated_documents:
        st.warning("⚠️ No documents generated yet. Please generate documents first in the Data Generation page.")
        
        if st.button("📝 Go to Data Generation", type="primary"):
            st.switch_page("pages/1_📝_Data_Generation.py")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### 📊 Ready to Send")
        st.info(f"You have {len(st.session_state.generated_documents)} documents ready to send to Kafka.")
        
        send_delay = st.slider("Delay between sends (seconds)", 0.1, 5.0, 0.5, 0.1)
        
        if st.button("📤 Send to Kafka", type="primary"):
            send_documents_to_kafka(send_delay)
    
    with col2:
        st.markdown("### Kafka Configuration")
        st.caption(f"**Topic:** {KAFKA_TOPIC}")
        st.caption("**Broker:** localhost:9092")
        st.caption("**Serialization:** JSON")
        st.caption("**Key:** Document ID")
        st.caption("**Value:** Document + Metadata")
    
    # Show document summary
    if st.session_state.generated_documents:
        st.markdown("### 📋 Document Summary")
        
        doc_types = {}
        total_words = 0
        
        for doc in st.session_state.generated_documents:
            doc_type = doc['document_type'].replace('_', ' ').title()
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            total_words += doc['word_count']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Documents", len(st.session_state.generated_documents))
        
        with col2:
            st.metric("Total Words", f"{total_words:,}")
        
        with col3:
            st.metric("Document Types", len(doc_types))
        
        # Document types breakdown
        st.markdown("**Document Types:**")
        for doc_type, count in doc_types.items():
            st.caption(f"• {doc_type}: {count}")
    
    # Next steps
    if st.session_state.demo_stats['documents_sent'] > 0:
        st.markdown("### 🚀 Next Steps")
        st.success("Documents sent to Kafka! Go to the Pipeline page to process them into the vector database.")
        
        if st.button("⚙️ Go to Pipeline", type="secondary"):
            st.switch_page("pages/3_⚙️_Pipeline.py")

if __name__ == "__main__":
    main()

