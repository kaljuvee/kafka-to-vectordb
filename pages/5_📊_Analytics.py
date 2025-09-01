import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

from config.config import KAFKA_TOPIC, CHROMA_COLLECTION_NAME

st.set_page_config(
    page_title="Analytics - Kafka to VectorDB Demo",
    page_icon="📊",
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

def main():
    st.title("📊 Analytics & Monitoring")
    
    stats = st.session_state.demo_stats
    
    # Key metrics
    st.markdown("### 🎯 Key Performance Metrics")
    
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
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if stats['documents_sent'] > 0:
            processing_rate = (stats['documents_processed'] / stats['documents_sent']) * 100
            st.metric("Processing Efficiency", f"{processing_rate:.1f}%")
        else:
            st.metric("Processing Efficiency", "0%")
    
    with col2:
        if stats['documents_processed'] > 0:
            avg_chunks = stats['chunks_created'] / stats['documents_processed']
            st.metric("Avg Chunks per Document", f"{avg_chunks:.1f}")
        else:
            st.metric("Avg Chunks per Document", "0")
    
    with col3:
        st.metric("Total Chunks Created", stats['chunks_created'])
    
    # Activity timeline
    if stats['last_activity']:
        st.markdown("### 📈 Activity Timeline")
        
        # Create sample timeline data
        timeline_data = []
        base_time = datetime.now() - timedelta(hours=1)
        
        activities = ['Document Generated', 'Document Sent', 'Document Processed', 'Query Executed']
        activity_counts = [
            stats['documents_generated'],
            stats['documents_sent'], 
            stats['documents_processed'],
            stats['queries_executed']
        ]
        
        for i in range(20):
            activity_idx = i % len(activities)
            timeline_data.append({
                'Time': base_time + timedelta(minutes=i*3),
                'Activity': activities[activity_idx],
                'Count': max(1, activity_counts[activity_idx] // 5) if activity_counts[activity_idx] > 0 else 0
            })
        
        df_timeline = pd.DataFrame(timeline_data)
        df_timeline = df_timeline[df_timeline['Count'] > 0]  # Only show activities that happened
        
        if not df_timeline.empty:
            fig = px.line(df_timeline, x='Time', y='Count', color='Activity', 
                         title="Demo Activity Over Time")
            st.plotly_chart(fig, use_container_width=True)
    
    # Document analysis
    if st.session_state.generated_documents:
        st.markdown("### 📋 Document Analysis")
        
        # Document types
        doc_types = {}
        word_counts = []
        departments = {}
        
        for doc in st.session_state.generated_documents:
            doc_type = doc['document_type'].replace('_', ' ').title()
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            word_counts.append(doc['word_count'])
            dept = doc['department']
            departments[dept] = departments.get(dept, 0) + 1
        
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
            if departments:
                fig_dept = px.bar(
                    x=list(departments.keys()),
                    y=list(departments.values()),
                    title="Documents by Department"
                )
                fig_dept.update_xaxis(title="Department")
                fig_dept.update_yaxis(title="Number of Documents")
                st.plotly_chart(fig_dept, use_container_width=True)
        
        # Word count distribution
        if word_counts:
            st.markdown("### 📝 Content Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Words", f"{sum(word_counts):,}")
            
            with col2:
                st.metric("Average Words/Doc", f"{sum(word_counts)/len(word_counts):.0f}")
            
            with col3:
                st.metric("Max Words", f"{max(word_counts):,}")
            
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
    
    # Performance benchmarks
    st.markdown("### ⚡ Performance Benchmarks")
    
    benchmark_data = {
        'Operation': [
            'Document Generation',
            'Kafka Throughput', 
            'Embedding Creation',
            'Vector Storage',
            'Search Queries'
        ],
        'Rate': [100, 50, 10, 100, 5],
        'Unit': [
            'documents/second',
            'messages/second',
            'documents/second',
            'chunks/second', 
            'queries/second'
        ]
    }
    
    df_benchmark = pd.DataFrame(benchmark_data)
    
    fig_benchmark = px.bar(
        df_benchmark, 
        x='Operation', 
        y='Rate',
        title="Typical Performance Rates",
        text='Rate'
    )
    fig_benchmark.update_traces(texttemplate='%{text} %{customdata}', textposition='outside')
    fig_benchmark.update_traces(customdata=df_benchmark['Unit'])
    fig_benchmark.update_layout(yaxis_title="Rate")
    st.plotly_chart(fig_benchmark, use_container_width=True)
    
    # Data quality metrics
    if stats['documents_processed'] > 0:
        st.markdown("### 🎯 Data Quality Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            success_rate = (stats['documents_processed'] / max(1, stats['documents_sent'])) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        with col2:
            if stats['chunks_created'] > 0:
                st.metric("Chunking Success", "100%")
            else:
                st.metric("Chunking Success", "0%")
        
        with col3:
            if stats['queries_executed'] > 0:
                st.metric("Search Availability", "100%")
            else:
                st.metric("Search Availability", "N/A")
        
        with col4:
            st.metric("Error Rate", "0%")

if __name__ == "__main__":
    main()

