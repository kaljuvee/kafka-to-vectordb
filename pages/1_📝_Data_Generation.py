import streamlit as st
import pandas as pd
import json
import time
import os
import sys
from datetime import datetime
import plotly.express as px

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

try:
    from src.data_generator import HRDataGenerator
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

st.set_page_config(
    page_title="Data Generation - Kafka to VectorDB Demo",
    page_icon="📝",
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
    st.title("📝 Synthetic Data Generation")
    
    st.markdown("""
    Generate realistic HR and organizational documents including employee handbooks, 
    job descriptions, policies, training materials, and more.
    """)
    
    data_generator = HRDataGenerator()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        num_docs = st.slider("Number of documents to generate", 1, 50, 10)
        
        if st.button("🎲 Generate Documents", type="primary"):
            with st.spinner("Generating synthetic HR documents..."):
                documents = data_generator.generate_batch(num_docs)
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
        
        # Next step
        st.markdown("### 🚀 Next Steps")
        st.info("Documents generated! Go to the Kafka Producer page to send them to the processing pipeline.")
        
        if st.button("📤 Go to Kafka Producer", type="secondary"):
            st.switch_page("pages/2_📤_Kafka_Producer.py")

if __name__ == "__main__":
    main()

