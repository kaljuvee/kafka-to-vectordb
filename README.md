# Kafka to VectorDB Demo

A comprehensive demonstration of streaming HR documents from Apache Kafka to a Vector Database with semantic search capabilities using OpenAI embeddings and ChromaDB.

## 🚀 Overview

This project implements the canonical pattern for processing streaming documents in modern data architectures:

```
Synthetic Data → Kafka Topic → Stream Processor → Embedding Model → Vector Database
```

The demo showcases how to build a complete pipeline that can handle real-time document ingestion, processing, and semantic search - perfect for applications like knowledge bases, document retrieval systems, and recommendation engines.

## 🎥 Demo Video

Watch the complete Kafka to VectorDB pipeline demonstration:

[![Kafka to VectorDB Demo](https://img.shields.io/badge/▶️-Watch%20Demo%20Video-blue?style=for-the-badge)](./demo_video.mp4)

The video showcases:
- **Data Generation**: Creating synthetic HR documents
- **Message Queue**: Sending documents to Kafka/SQLite queue  
- **Pipeline Processing**: Converting documents to vector embeddings
- **Semantic Search**: Natural language querying capabilities
- **Analytics Dashboard**: Performance monitoring and metrics

## 🏗️ Architecture

### Components

- **Data Generator**: Creates realistic HR/organizational documents using Faker
- **Kafka Producer**: Sends documents to Kafka topic for processing  
- **Stream Processor**: Consumes messages, chunks text, and creates embeddings
- **Vector Database**: ChromaDB for storing and querying document embeddings
- **Search Interface**: Both CLI and web-based semantic search

### Data Flow

1. **Document Generation**: Synthetic HR documents are generated with realistic content
2. **Kafka Ingestion**: Documents are sent to a Kafka topic as JSON messages
3. **Stream Processing**: Consumer reads messages, splits text into chunks
4. **Embedding Creation**: OpenAI API converts text chunks to vector embeddings
5. **Vector Storage**: Embeddings stored in ChromaDB with metadata
6. **Semantic Search**: Natural language queries find relevant documents

## 📋 Prerequisites

- Python 3.11+
- OpenAI API key
- Apache Kafka (optional - demo can run without real Kafka)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/kaljuvee/kafka-to-vectordb.git
   cd kafka-to-vectordb
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.template .env
   # Edit .env and add your OpenAI API key
   ```

## 🎯 Quick Start

### Option 1: Full Demo (Recommended)

Run the complete pipeline demonstration:

```bash
python demo_cli.py
```

This will:
- Generate 15 synthetic HR documents
- Send them to Kafka topic
- Process them through the vector pipeline
- Demonstrate semantic search queries

### Option 2: Streamlit Web Interface

Launch the interactive web application:

```bash
python run_streamlit.py
```

Then open http://localhost:8501 in your browser.

### Option 3: Individual Components

**Generate synthetic data**:
```bash
cd src
python data_generator.py
```

**Send documents to Kafka**:
```bash
python demo_cli.py --producer-only --num-docs 20
```

**Process documents**:
```bash
python demo_cli.py --consumer-only --timeout 60
```

**Query the database**:
```bash
python demo_cli.py --interactive
```

## 📚 Usage Examples

### Command Line Interface

The CLI provides several modes of operation:

```bash
# Run full demo
python demo_cli.py

# Generate and send 25 documents
python demo_cli.py --producer-only --num-docs 25

# Process messages with 2-minute timeout
python demo_cli.py --consumer-only --timeout 120

# Interactive query mode
python demo_cli.py --interactive

# Run sample queries only
python demo_cli.py --query-only
```

### Option 2: Streamlit Web Interface

Launch the interactive web application:

```bash
python run_streamlit.py
# or directly:
streamlit run Home.py
```

Then open http://localhost:8501 in your browser.

The web interface provides six main pages:

1. **Home**: Overview and getting started guide
2. **Data Generation**: Create synthetic HR documents
3. **Kafka Producer**: Send documents to Kafka topic
4. **Pipeline**: Process documents into vector database
5. **Search**: Semantic search with natural language queries
6. **Analytics**: Monitor pipeline performance and statistics
7. **About**: Documentation and architecture information

### Sample Queries

Try these semantic search queries:

- "employee benefits and health insurance"
- "remote work policy and guidelines"
- "performance review process"
- "safety guidelines and procedures"
- "training and development programs"
- "code of conduct and ethics"
- "onboarding process for new employees"

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (defaults provided)
KAFKA_BROKER=localhost:9092
KAFKA_TOPIC=hr-documents
KAFKA_GROUP_ID=vectordb-ingester
CHROMA_DB_PATH=./data/chroma_db
CHROMA_COLLECTION_NAME=hr_documents
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
NUM_SYNTHETIC_DOCS=50
```

### Customization

**Document Types**: The data generator creates 10 types of HR documents:
- Employee Handbook sections
- Job Descriptions
- Policy Documents
- Training Materials
- Performance Reviews
- Company Announcements
- Benefits Guides
- Code of Conduct
- Safety Guidelines
- Onboarding Checklists

**Text Processing**: Adjust chunking parameters in `config/config.py`:
- `CHUNK_SIZE`: Maximum characters per chunk (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)

## 🧪 Testing

Run the test suite to verify all components:

```bash
python test_pipeline.py
```

The tests verify:
- Configuration loading
- Data generation
- Text processing
- Component initialization
- Import compatibility

## 📊 Performance

### Benchmarks

Typical performance on standard hardware:

- **Document Generation**: ~100 documents/second
- **Kafka Throughput**: ~50 messages/second
- **Embedding Creation**: ~10 documents/second (OpenAI API limited)
- **Vector Storage**: ~100 chunks/second
- **Search Queries**: ~5 queries/second

### Scaling Considerations

For production deployments:

- **Horizontal Scaling**: Use multiple consumer instances with same group ID
- **Batch Processing**: Process multiple documents per API call
- **Caching**: Cache embeddings for frequently accessed content
- **Database**: Consider Qdrant or Milvus for larger scale

## 🔍 Document Types Generated

The synthetic data generator creates realistic HR documents across multiple categories:

### Employee Handbook Sections
- Welcome messages and company culture
- Core values and work environment
- Benefits packages and time-off policies
- Workplace guidelines and conduct standards

### Policy Documents
- Remote work policies with eligibility and security requirements
- Expense reimbursement procedures and limits
- Paid time off accrual and usage guidelines
- Information security standards and compliance

### Job Descriptions
- Position overviews with key responsibilities
- Required and preferred qualifications
- Compensation ranges and benefits
- Application procedures

### Training Materials
- Learning objectives and module content
- Best practices and case studies
- Assessment criteria and resources
- Professional development opportunities

## 🛡️ Security & Privacy

### Data Protection
- All synthetic data is generated locally
- No real employee information is used
- OpenAI API calls use encrypted connections
- Vector database stored locally by default

### API Key Management
- Store OpenAI API key in environment variables
- Never commit API keys to version control
- Use separate keys for development and production
- Monitor API usage and costs

## 🚀 Deployment

### Local Development
The demo runs entirely locally with no external dependencies except OpenAI API.

### Production Considerations
For production deployments:

1. **Kafka Cluster**: Use managed Kafka service (Confluent, AWS MSK)
2. **Vector Database**: Deploy ChromaDB server or use managed service
3. **Monitoring**: Add metrics collection and alerting
4. **Scaling**: Implement horizontal scaling for consumers
5. **Security**: Add authentication and authorization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Apache Kafka](https://kafka.apache.org/) for stream processing
- [ChromaDB](https://www.trychroma.com/) for vector database
- [OpenAI](https://openai.com/) for embeddings API
- [LangChain](https://python.langchain.com/) for text processing
- [Streamlit](https://streamlit.io/) for web interface

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check the documentation in the `docs/` folder
- Review the example code in `examples/`

---

**Built with ❤️ for the data engineering community**

