import streamlit as st

st.set_page_config(
    page_title="About - Kafka to VectorDB Demo",
    page_icon="ℹ️",
    layout="wide"
)

def main():
    st.title("ℹ️ About This Demo")
    
    st.markdown("""
    ## 🚀 Kafka to VectorDB Pipeline Demo
    
    This demonstration showcases a complete pipeline for processing streaming documents 
    from Apache Kafka into a vector database for semantic search capabilities.
    """)
    
    # Architecture section
    st.markdown("### 🏗️ Architecture")
    
    st.markdown("""
    The demo implements the canonical pattern for document processing:
    """)
    
    st.code("""
    Synthetic Data → Kafka Topic → Stream Processor → Embedding Model → Vector Database
    """, language="text")
    
    # Components
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔧 Components
        
        - **Data Generator**: Creates realistic HR/organizational documents using Faker
        - **Kafka Producer**: Sends documents to Kafka topic for processing
        - **Stream Processor**: Consumes messages, chunks text, and creates embeddings
        - **Vector Database**: ChromaDB for storing and querying document embeddings
        - **Search Interface**: Semantic search using OpenAI embeddings
        """)
    
    with col2:
        st.markdown("""
        ### 📚 Technologies Used
        
        - **Apache Kafka**: Message streaming platform
        - **OpenAI Embeddings**: Text-to-vector conversion
        - **ChromaDB**: Vector database for similarity search
        - **LangChain**: Text processing and chunking
        - **Streamlit**: Web application framework
        - **Python**: Core programming language
        """)
    
    # Use cases
    st.markdown("### 🎯 Use Cases")
    
    st.markdown("""
    This pattern is ideal for:
    - Document search and retrieval systems
    - Knowledge base applications
    - Recommendation engines
    - Anomaly detection in text streams
    - Real-time content analysis
    """)
    
    # Getting started
    st.markdown("### 🚦 Getting Started")
    
    st.markdown("""
    1. **Generate Data**: Create synthetic HR documents
    2. **Send to Kafka**: Stream documents to the processing pipeline
    3. **Process Pipeline**: Convert documents to embeddings and store in vector DB
    4. **Search & Query**: Use natural language to find relevant documents
    """)
    
    # Document types
    st.markdown("### 📋 Document Types Generated")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Employee Handbook Sections**
        - Welcome messages and company culture
        - Core values and work environment
        - Benefits packages and time-off policies
        - Workplace guidelines and conduct standards
        
        **Policy Documents**
        - Remote work policies with eligibility and security requirements
        - Expense reimbursement procedures and limits
        - Paid time off accrual and usage guidelines
        - Information security standards and compliance
        """)
    
    with col2:
        st.markdown("""
        **Job Descriptions**
        - Position overviews with key responsibilities
        - Required and preferred qualifications
        - Compensation ranges and benefits
        - Application procedures
        
        **Training Materials**
        - Learning objectives and module content
        - Best practices and case studies
        - Assessment criteria and resources
        - Professional development opportunities
        """)
    
    # Technical details
    st.markdown("### 🔧 Technical Implementation")
    
    with st.expander("Data Flow Details"):
        st.markdown("""
        1. **Document Generation**: Synthetic HR documents are generated with realistic content using the Faker library
        2. **Kafka Ingestion**: Documents are serialized as JSON and sent to a Kafka topic with document ID as key
        3. **Stream Processing**: Consumer reads messages, extracts text content and metadata
        4. **Text Chunking**: Documents are split into overlapping chunks of 1000 characters with 200 character overlap
        5. **Embedding Creation**: OpenAI API converts text chunks to 1536-dimensional vector embeddings
        6. **Vector Storage**: Embeddings stored in ChromaDB with preserved metadata for filtering and retrieval
        7. **Semantic Search**: Natural language queries are embedded and matched against stored vectors using cosine similarity
        """)
    
    with st.expander("Configuration Options"):
        st.markdown("""
        **Kafka Configuration:**
        - Broker: localhost:9092 (configurable)
        - Topic: hr-documents (configurable)
        - Consumer Group: vectordb-ingester
        - Serialization: JSON with UTF-8 encoding
        
        **Text Processing:**
        - Chunk Size: 1000 characters (configurable)
        - Chunk Overlap: 200 characters (configurable)
        - Text Splitter: Recursive character splitter with smart boundaries
        
        **Vector Database:**
        - Database: ChromaDB (local persistence)
        - Collection: hr_documents (configurable)
        - Embedding Model: OpenAI text-embedding-ada-002
        - Similarity Metric: Cosine similarity
        """)
    
    with st.expander("Performance Characteristics"):
        st.markdown("""
        **Typical Performance (standard hardware):**
        - Document Generation: ~100 documents/second
        - Kafka Throughput: ~50 messages/second
        - Embedding Creation: ~10 documents/second (OpenAI API limited)
        - Vector Storage: ~100 chunks/second
        - Search Queries: ~5 queries/second
        
        **Scaling Considerations:**
        - Horizontal Scaling: Use multiple consumer instances with same group ID
        - Batch Processing: Process multiple documents per API call
        - Caching: Cache embeddings for frequently accessed content
        - Database: Consider Qdrant or Milvus for larger scale
        """)
    
    # Security and privacy
    st.markdown("### 🛡️ Security & Privacy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Data Protection:**
        - All synthetic data is generated locally
        - No real employee information is used
        - OpenAI API calls use encrypted connections
        - Vector database stored locally by default
        """)
    
    with col2:
        st.markdown("""
        **API Key Management:**
        - Store OpenAI API key in environment variables
        - Never commit API keys to version control
        - Use separate keys for development and production
        - Monitor API usage and costs
        """)
    
    # Links and resources
    st.markdown("### 📖 Learn More")
    
    st.markdown("""
    - [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
    - [ChromaDB Documentation](https://docs.trychroma.com/)
    - [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
    - [LangChain Documentation](https://python.langchain.com/)
    - [Streamlit Documentation](https://docs.streamlit.io/)
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Built with ❤️ for the data engineering community**
    
    This demo showcases modern patterns for building real-time document processing pipelines
    with semantic search capabilities. The techniques demonstrated here can be applied to
    production systems handling millions of documents with appropriate scaling considerations.
    """)

if __name__ == "__main__":
    main()

