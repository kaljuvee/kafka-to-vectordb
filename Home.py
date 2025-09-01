import streamlit as st
import pandas as pd
import json
import time
import os
import sys
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

from src.data_generator import HRDataGenerator
from config.config import OPENAI_API_KEY, KAFKA_TOPIC, CHROMA_COLLECTION_NAME

# Page configuration
st.set_page_config(
    page_title="Kafka to VectorDB Demo",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    .info-message {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

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

if 'generated_documents' not in st.session_state:
    st.session_state.generated_documents = []

if 'query_history' not in st.session_state:
    st.session_state.query_history = []

def check_requirements() -> bool:
    """Check if requirements are met"""
    if not OPENAI_API_KEY:
        st.error("❌ OpenAI API key not found. Please set OPENAI_API_KEY in your environment.")
        return False
    return True

def render_sidebar():
    """Render the sidebar with controls"""
    st.sidebar.title("🎛️ Demo Controls")
    
    # Requirements check
    if not check_requirements():
        st.sidebar.error("Please configure OpenAI API key to proceed")
        return
    
    st.sidebar.success("✅ Requirements met")
    
    # Demo statistics
    st.sidebar.markdown("### 📊 Demo Statistics")
    stats = st.session_state.demo_stats
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Documents Generated", stats['documents_generated'])
        st.metric("Documents Sent", stats['documents_sent'])
    with col2:
        st.metric("Documents Processed", stats['documents_processed'])
        st.metric("Chunks Created", stats['chunks_created'])
    
    st.sidebar.metric("Queries Executed", stats['queries_executed'])
    
    if stats['last_activity']:
        st.sidebar.caption(f"Last activity: {stats['last_activity']}")
    
    # Quick actions
    st.sidebar.markdown("### ⚡ Quick Actions")
    
    if st.sidebar.button("🔄 Reset Demo", type="secondary"):
        reset_demo()
    
    if st.sidebar.button("📊 Refresh Stats", type="secondary"):
        st.rerun()

def reset_demo():
    """Reset demo state"""
    st.session_state.demo_stats = {
        'documents_generated': 0,
        'documents_sent': 0,
        'documents_processed': 0,
        'chunks_created': 0,
        'queries_executed': 0,
        'last_activity': None
    }
    st.session_state.generated_documents = []
    st.session_state.query_history = []
    st.session_state.pipeline_running = False
    st.success("✅ Demo state reset successfully!")
    st.rerun()

def main():
    """Main home page"""
    # Header
    st.markdown('<div class="main-header">🚀 Kafka to VectorDB Demo</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; color: #666;">
        A comprehensive demonstration of streaming HR documents from Kafka to Vector Database
        with semantic search capabilities using OpenAI embeddings and ChromaDB.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    render_sidebar()
    
    # Main content
    st.markdown('<div class="section-header">🏗️ Architecture Overview</div>', unsafe_allow_html=True)
    
    st.markdown("""
    This demo implements the canonical pattern for processing streaming documents in modern data architectures:
    """)
    
    # Architecture diagram
    st.code("""
    Synthetic Data → Kafka Topic → Stream Processor → Embedding Model → Vector Database
    """, language="text")
    
    # Components overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Components")
        st.markdown("""
        - **Data Generator**: Creates realistic HR/organizational documents
        - **Kafka Producer**: Sends documents to Kafka topic for processing  
        - **Stream Processor**: Consumes messages, chunks text, creates embeddings
        - **Vector Database**: ChromaDB for storing and querying document embeddings
        - **Search Interface**: Semantic search with natural language queries
        """)
    
    with col2:
        st.markdown("### 📊 Current Status")
        stats = st.session_state.demo_stats
        
        if stats['documents_generated'] > 0:
            st.success(f"✅ {stats['documents_generated']} documents generated")
        else:
            st.info("ℹ️ No documents generated yet")
            
        if stats['documents_sent'] > 0:
            st.success(f"✅ {stats['documents_sent']} documents sent to Kafka")
        else:
            st.info("ℹ️ No documents sent yet")
            
        if stats['documents_processed'] > 0:
            st.success(f"✅ {stats['documents_processed']} documents processed")
        else:
            st.info("ℹ️ No documents processed yet")
    
    # Getting started
    st.markdown('<div class="section-header">🚀 Getting Started</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Follow these steps to run the complete demo:
    
    1. **📝 Generate Data**: Go to the "Data Generation" page to create synthetic HR documents
    2. **📤 Send to Kafka**: Use the "Kafka Producer" page to stream documents to the processing pipeline
    3. **⚙️ Process Pipeline**: Run the "Pipeline" to convert documents to embeddings and store in vector DB
    4. **🔍 Search & Query**: Use the "Search" page to find relevant documents with natural language queries
    5. **📊 Monitor**: Check the "Analytics" page for performance metrics and insights
    """)
    
    # Quick start buttons
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Generate Sample Data", type="primary"):
            st.switch_page("pages/1_📝_Data_Generation.py")
    
    with col2:
        if st.button("🔍 Try Search", type="primary"):
            st.switch_page("pages/4_🔍_Search.py")
    
    with col3:
        if st.button("📊 View Analytics", type="primary"):
            st.switch_page("pages/5_📊_Analytics.py")
    
    # Configuration info
    st.markdown('<div class="section-header">⚙️ Configuration</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Kafka Configuration:**")
        st.code(f"""
Topic: {KAFKA_TOPIC}
Broker: localhost:9092
Group ID: vectordb-ingester
        """, language="text")
    
    with col2:
        st.markdown("**Vector Database:**")
        st.code(f"""
Collection: {CHROMA_COLLECTION_NAME}
Embeddings: OpenAI text-embedding-ada-002
Chunk Size: 1000 characters
Chunk Overlap: 200 characters
        """, language="text")
    
    # Recent activity
    if st.session_state.demo_stats['last_activity']:
        st.markdown('<div class="section-header">📈 Recent Activity</div>', unsafe_allow_html=True)
        
        # Create sample activity data
        activity_data = []
        base_time = datetime.now() - timedelta(minutes=30)
        
        for i in range(6):
            activity_data.append({
                'Time': base_time + timedelta(minutes=i*5),
                'Activity': ['Document Generated', 'Document Sent', 'Document Processed', 'Query Executed'][i % 4],
                'Count': max(1, st.session_state.demo_stats['documents_generated'] // 6)
            })
        
        df_activity = pd.DataFrame(activity_data)
        fig = px.line(df_activity, x='Time', y='Count', color='Activity', 
                     title="Demo Activity Timeline")
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()

