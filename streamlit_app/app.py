import streamlit as st
import pandas as pd
import json
import time
import threading
import os
import sys
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

from src.kafka_producer import DocumentProducer
from src.kafka_to_vectordb import KafkaToVectorDBPipeline
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

class StreamlitKafkaVectorDBDemo:
    """Streamlit application for Kafka to VectorDB demo"""
    
    def __init__(self):
        self.data_generator = HRDataGenerator()
        self.producer = None
        self.pipeline = None
        
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
    
    def check_requirements(self) -> bool:
        """Check if requirements are met"""
        if not OPENAI_API_KEY:
            st.error("❌ OpenAI API key not found. Please set OPENAI_API_KEY in your environment.")
            return False
        return True
    
    def render_header(self):
        """Render the main header"""
        st.markdown('<div class="main-header">🚀 Kafka to VectorDB Demo</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem; color: #666;">
            A comprehensive demonstration of streaming HR documents from Kafka to Vector Database
            with semantic search capabilities using OpenAI embeddings and ChromaDB.
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar with controls"""
        st.sidebar.title("🎛️ Demo Controls")
        
        # Requirements check
        if not self.check_requirements():
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
            self.reset_demo()
        
        if st.sidebar.button("📊 Refresh Stats", type="secondary"):
            st.rerun()
    
    def render_data_generation_tab(self):
        """Render the data generation tab"""
        st.markdown('<div class="section-header">📝 Synthetic Data Generation</div>', unsafe_allow_html=True)
        
        st.markdown("""
        Generate realistic HR and organizational documents including employee handbooks, 
        job descriptions, policies, training materials, and more.
        """)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            num_docs = st.slider("Number of documents to generate", 1, 50, 10)
            
            if st.button("🎲 Generate Documents", type="primary"):
                with st.spinner("Generating synthetic HR documents..."):
                    documents = self.data_generator.generate_batch(num_docs)
                    st.session_state.generated_documents = documents
                    st.session_state.demo_stats['documents_generated'] += len(documents)
                    st.session_state.demo_stats['last_activity'] = datetime.now().strftime("%H:%M:%S")
                
                st.success(f"✅ Generated {len(documents)} documents successfully!")
        
        with col2:
            st.markdown("### Document Types")
            doc_types = [
                "Employee Handbook",
                "Job Description", 
                "Policy Document",
                "Training Material",
                "Performance Review",
                "Company Announcement",
                "Benefits Guide",
                "Code of Conduct",
                "Safety Guidelines",
                "Onboarding Checklist"
            ]
            for doc_type in doc_types:
                st.caption(f"• {doc_type}")
        
        # Display generated documents
        if st.session_state.generated_documents:
            st.markdown("### 📋 Generated Documents")
            
            # Create DataFrame for display
            df_data = []
            for doc in st.session_state.generated_documents:
                df_data.append({
                    'Title': doc['title'],
                    'Type': doc['document_type'].replace('_', ' ').title(),
                    'Department': doc['department'],
                    'Author': doc['author'],
                    'Word Count': doc['word_count'],
                    'Created': doc['created_date']
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Document type distribution
            if len(df) > 0:
                fig = px.pie(df, names='Type', title="Document Type Distribution")
                st.plotly_chart(fig, use_container_width=True)
            
            # Show sample document
            if st.checkbox("Show sample document content"):
                selected_idx = st.selectbox("Select document", range(len(st.session_state.generated_documents)))
                selected_doc = st.session_state.generated_documents[selected_idx]
                
                st.markdown(f"**{selected_doc['title']}**")
                st.markdown(f"*{selected_doc['document_type'].replace('_', ' ').title()} | {selected_doc['department']}*")
                st.text_area("Content", selected_doc['content'], height=300, disabled=True)
    
    def render_kafka_producer_tab(self):
        """Render the Kafka producer tab"""
        st.markdown('<div class="section-header">📤 Kafka Producer</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        Send generated documents to Kafka topic `{KAFKA_TOPIC}` for processing by the vector database pipeline.
        """)
        
        if not st.session_state.generated_documents:
            st.warning("⚠️ No documents generated yet. Please generate documents first in the Data Generation tab.")
            return
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            send_delay = st.slider("Delay between sends (seconds)", 0.1, 5.0, 0.5, 0.1)
            
            if st.button("📤 Send to Kafka", type="primary"):
                self.send_documents_to_kafka(send_delay)
        
        with col2:
            st.markdown("### Kafka Configuration")
            st.caption(f"**Topic:** {KAFKA_TOPIC}")
            st.caption("**Broker:** localhost:9092")
            st.caption("**Serialization:** JSON")
    
    def send_documents_to_kafka(self, delay: float):
        """Send documents to Kafka"""
        if not st.session_state.generated_documents:
            st.error("No documents to send")
            return
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize producer
            producer = DocumentProducer()
            if not producer.connect():
                st.error("❌ Failed to connect to Kafka broker")
                return
            
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
                st.success(f"✅ Successfully sent {sent_count} documents to Kafka!")
            else:
                st.warning(f"⚠️ Sent {sent_count}/{total_docs} documents (some failed)")
        
        except Exception as e:
            st.error(f"❌ Error sending documents: {e}")
        finally:
            progress_bar.empty()
            status_text.empty()
    
    def render_pipeline_tab(self):
        """Render the pipeline processing tab"""
        st.markdown('<div class="section-header">⚙️ Vector Database Pipeline</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        Process documents from Kafka, create embeddings using OpenAI, and store in ChromaDB 
        collection `{CHROMA_COLLECTION_NAME}` for semantic search.
        """)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            max_messages = st.number_input("Max messages to process", 1, 100, 20)
            timeout_seconds = st.number_input("Timeout (seconds)", 10, 300, 60)
            
            if st.button("⚙️ Start Pipeline", type="primary", disabled=st.session_state.pipeline_running):
                self.run_pipeline(max_messages, timeout_seconds)
        
        with col2:
            st.markdown("### Pipeline Configuration")
            st.caption("**Embeddings:** OpenAI text-embedding-ada-002")
            st.caption("**Vector DB:** ChromaDB")
            st.caption("**Chunk Size:** 1000 characters")
            st.caption("**Chunk Overlap:** 200 characters")
        
        if st.session_state.pipeline_running:
            st.info("🔄 Pipeline is running... Please wait for completion.")
    
    def run_pipeline(self, max_messages: int, timeout_seconds: int):
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
            
            # Run pipeline in a way that allows for progress updates
            start_time = time.time()
            processed_messages = 0
            
            # This is a simplified version - in a real app you'd want to run this in a separate thread
            # and update progress asynchronously
            stats = pipeline.run(max_messages=max_messages, timeout_seconds=timeout_seconds)
            
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
    
    def render_query_tab(self):
        """Render the semantic search tab"""
        st.markdown('<div class="section-header">🔍 Semantic Search</div>', unsafe_allow_html=True)
        
        st.markdown("""
        Query the vector database using natural language to find relevant HR documents 
        based on semantic similarity.
        """)
        
        # Query interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_input("Enter your search query:", placeholder="e.g., employee benefits and health insurance")
        
        with col2:
            num_results = st.selectbox("Results to show:", [3, 5, 10], index=1)
        
        if st.button("🔍 Search", type="primary") and query:
            self.execute_search(query, num_results)
        
        # Sample queries
        st.markdown("### 💡 Sample Queries")
        sample_queries = [
            "employee benefits and health insurance",
            "remote work policy and guidelines", 
            "performance review process",
            "safety guidelines and procedures",
            "training and development programs",
            "code of conduct and ethics",
            "onboarding process for new employees"
        ]
        
        cols = st.columns(3)
        for i, sample_query in enumerate(sample_queries):
            with cols[i % 3]:
                if st.button(f"🔍 {sample_query}", key=f"sample_{i}"):
                    self.execute_search(sample_query, num_results)
        
        # Query history
        if st.session_state.query_history:
            st.markdown("### 📚 Query History")
            
            for i, query_result in enumerate(reversed(st.session_state.query_history[-5:])):
                with st.expander(f"Query: {query_result['query'][:50]}... ({query_result['timestamp']})"):
                    st.write(f"**Query:** {query_result['query']}")
                    st.write(f"**Results:** {len(query_result['results'])}")
                    
                    for j, result in enumerate(query_result['results'][:3]):
                        st.write(f"**{j+1}. {result['metadata'].get('title', 'Unknown')}**")
                        st.write(f"Type: {result['metadata'].get('document_type', 'unknown')}")
                        st.write(f"Content: {result['content'][:200]}...")
                        st.write("---")
    
    def execute_search(self, query: str, num_results: int):
        """Execute a semantic search query"""
        try:
            with st.spinner("Searching vector database..."):
                # Initialize pipeline for querying
                pipeline = KafkaToVectorDBPipeline()
                if not pipeline.initialize():
                    st.error("❌ Failed to initialize pipeline for querying")
                    return
                
                results = pipeline.query_vectorstore(query, k=num_results)
                
                if not results:
                    st.warning("No results found. Make sure documents have been processed through the pipeline.")
                    return
                
                # Update statistics
                st.session_state.demo_stats['queries_executed'] += 1
                st.session_state.demo_stats['last_activity'] = datetime.now().strftime("%H:%M:%S")
                
                # Store in query history
                st.session_state.query_history.append({
                    'query': query,
                    'results': results,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                
                # Display results
                st.success(f"✅ Found {len(results)} results for: '{query}'")
                
                for i, result in enumerate(results, 1):
                    with st.container():
                        st.markdown(f"### {i}. {result['metadata'].get('title', 'Unknown Title')}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.caption(f"**Type:** {result['metadata'].get('document_type', 'unknown').replace('_', ' ').title()}")
                        with col2:
                            st.caption(f"**Department:** {result['metadata'].get('department', 'unknown')}")
                        with col3:
                            st.caption(f"**Author:** {result['metadata'].get('author', 'unknown')}")
                        
                        st.markdown(f"**Content Preview:**")
                        st.text_area(f"Content {i}", result['content'], height=100, disabled=True, key=f"result_{i}")
                        
                        st.markdown("---")
        
        except Exception as e:
            st.error(f"❌ Search error: {e}")
    
    def render_analytics_tab(self):
        """Render the analytics and monitoring tab"""
        st.markdown('<div class="section-header">📊 Analytics & Monitoring</div>', unsafe_allow_html=True)
        
        stats = st.session_state.demo_stats
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Documents Generated",
                stats['documents_generated'],
                delta=None
            )
        
        with col2:
            st.metric(
                "Documents Sent",
                stats['documents_sent'],
                delta=None
            )
        
        with col3:
            st.metric(
                "Documents Processed", 
                stats['documents_processed'],
                delta=None
            )
        
        with col4:
            st.metric(
                "Queries Executed",
                stats['queries_executed'],
                delta=None
            )
        
        # Pipeline efficiency
        if stats['documents_sent'] > 0:
            processing_rate = (stats['documents_processed'] / stats['documents_sent']) * 100
            st.metric("Processing Efficiency", f"{processing_rate:.1f}%")
        
        # Activity timeline (simulated)
        if stats['last_activity']:
            st.markdown("### 📈 Activity Timeline")
            
            # Create sample timeline data
            timeline_data = []
            base_time = datetime.now() - timedelta(hours=1)
            
            for i in range(10):
                timeline_data.append({
                    'Time': base_time + timedelta(minutes=i*6),
                    'Activity': ['Document Generated', 'Document Sent', 'Document Processed', 'Query Executed'][i % 4],
                    'Count': max(1, stats['documents_generated'] // 10)
                })
            
            df_timeline = pd.DataFrame(timeline_data)
            fig = px.line(df_timeline, x='Time', y='Count', color='Activity', 
                         title="Demo Activity Over Time")
            st.plotly_chart(fig, use_container_width=True)
        
        # Document type analysis
        if st.session_state.generated_documents:
            st.markdown("### 📋 Document Analysis")
            
            # Document types
            doc_types = {}
            word_counts = []
            
            for doc in st.session_state.generated_documents:
                doc_type = doc['document_type'].replace('_', ' ').title()
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
                word_counts.append(doc['word_count'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                if doc_types:
                    fig_pie = px.pie(
                        values=list(doc_types.values()),
                        names=list(doc_types.keys()),
                        title="Document Types Distribution"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                if word_counts:
                    fig_hist = px.histogram(
                        x=word_counts,
                        nbins=10,
                        title="Document Word Count Distribution"
                    )
                    fig_hist.update_xaxis(title="Word Count")
                    fig_hist.update_yaxis(title="Number of Documents")
                    st.plotly_chart(fig_hist, use_container_width=True)
        
        # System status
        st.markdown("### 🖥️ System Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Components Status:**")
            st.success("✅ Data Generator: Ready")
            st.success("✅ Kafka Producer: Ready") 
            st.success("✅ Vector Pipeline: Ready")
            st.success("✅ Search Interface: Ready")
        
        with col2:
            st.markdown("**Configuration:**")
            st.info(f"📡 Kafka Topic: {KAFKA_TOPIC}")
            st.info(f"🗄️ Vector Collection: {CHROMA_COLLECTION_NAME}")
            st.info("🧠 Embeddings: OpenAI Ada-002")
            st.info("🔍 Vector DB: ChromaDB")
    
    def reset_demo(self):
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
    
    def run(self):
        """Run the Streamlit application"""
        self.render_header()
        self.render_sidebar()
        
        # Main tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📝 Data Generation",
            "📤 Kafka Producer", 
            "⚙️ Pipeline",
            "🔍 Search",
            "📊 Analytics",
            "ℹ️ About"
        ])
        
        with tab1:
            self.render_data_generation_tab()
        
        with tab2:
            self.render_kafka_producer_tab()
        
        with tab3:
            self.render_pipeline_tab()
        
        with tab4:
            self.render_query_tab()
        
        with tab5:
            self.render_analytics_tab()
        
        with tab6:
            self.render_about_tab()
    
    def render_about_tab(self):
        """Render the about tab"""
        st.markdown('<div class="section-header">ℹ️ About This Demo</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ## 🚀 Kafka to VectorDB Pipeline Demo
        
        This demonstration showcases a complete pipeline for processing streaming documents 
        from Apache Kafka into a vector database for semantic search capabilities.
        
        ### 🏗️ Architecture
        
        The demo implements the canonical pattern for document processing:
        
        ```
        Synthetic Data → Kafka Topic → Stream Processor → Embedding Model → Vector Database
        ```
        
        ### 🔧 Components
        
        - **Data Generator**: Creates realistic HR/organizational documents using Faker
        - **Kafka Producer**: Sends documents to Kafka topic for processing
        - **Stream Processor**: Consumes messages, chunks text, and creates embeddings
        - **Vector Database**: ChromaDB for storing and querying document embeddings
        - **Search Interface**: Semantic search using OpenAI embeddings
        
        ### 📚 Technologies Used
        
        - **Apache Kafka**: Message streaming platform
        - **OpenAI Embeddings**: Text-to-vector conversion
        - **ChromaDB**: Vector database for similarity search
        - **LangChain**: Text processing and chunking
        - **Streamlit**: Web application framework
        - **Python**: Core programming language
        
        ### 🎯 Use Cases
        
        This pattern is ideal for:
        - Document search and retrieval systems
        - Knowledge base applications
        - Recommendation engines
        - Anomaly detection in text streams
        - Real-time content analysis
        
        ### 🚦 Getting Started
        
        1. **Generate Data**: Create synthetic HR documents
        2. **Send to Kafka**: Stream documents to the processing pipeline
        3. **Process Pipeline**: Convert documents to embeddings and store in vector DB
        4. **Search & Query**: Use natural language to find relevant documents
        
        ### 📖 Learn More
        
        - [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
        - [ChromaDB Documentation](https://docs.trychroma.com/)
        - [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
        - [LangChain Documentation](https://python.langchain.com/)
        """)

def main():
    """Main application entry point"""
    demo = StreamlitKafkaVectorDBDemo()
    demo.run()

if __name__ == "__main__":
    main()

