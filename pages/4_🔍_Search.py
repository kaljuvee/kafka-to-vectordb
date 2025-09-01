import streamlit as st
import os
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

from src.kafka_to_vectordb import KafkaToVectorDBPipeline

st.set_page_config(
    page_title="Search - Kafka to VectorDB Demo",
    page_icon="🔍",
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

if 'query_history' not in st.session_state:
    st.session_state.query_history = []

def execute_search(query: str, num_results: int):
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
                    st.text_area(f"Content {i}", result['content'], height=100, disabled=True, key=f"result_{i}_{query}")
                    
                    st.markdown("---")
    
    except Exception as e:
        st.error(f"❌ Search error: {e}")

def main():
    st.title("🔍 Semantic Search")
    
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
        execute_search(query, num_results)
    
    # Sample queries
    st.markdown("### 💡 Sample Queries")
    st.markdown("Click any of these sample queries to try them out:")
    
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
                execute_search(sample_query, num_results)
    
    # Search tips
    st.markdown("### 💡 Search Tips")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Effective Query Strategies:**
        - Use natural language descriptions
        - Include specific topics or keywords
        - Ask questions as you would to a colleague
        - Combine related concepts in one query
        """)
    
    with col2:
        st.markdown("""
        **Example Query Types:**
        - "How do I request time off?"
        - "What are the safety requirements?"
        - "Employee training programs available"
        - "Remote work eligibility criteria"
        """)
    
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
    
    # Search statistics
    if st.session_state.demo_stats['queries_executed'] > 0:
        st.markdown("### 📊 Search Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Queries", st.session_state.demo_stats['queries_executed'])
        
        with col2:
            st.metric("Query History", len(st.session_state.query_history))
        
        with col3:
            if st.session_state.demo_stats['last_activity']:
                st.metric("Last Search", st.session_state.demo_stats['last_activity'])

if __name__ == "__main__":
    main()

