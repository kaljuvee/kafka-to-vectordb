import json
import os
import uuid
import sys
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from langchain.text_splitter import RecursiveCharacterTextSplitter
try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from typing import Dict, Any, List
import time

# Add config to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from config.config import (
    KAFKA_BROKER, KAFKA_TOPIC, KAFKA_GROUP_ID, OPENAI_API_KEY,
    CHROMA_DB_PATH, CHROMA_COLLECTION_NAME, CHUNK_SIZE, CHUNK_OVERLAP
)

# Import SQLite fallback
from sqlite_message_queue import SQLiteConsumer, SQLiteMessageQueue

class KafkaToVectorDBPipeline:
    """Kafka to VectorDB ingestion pipeline with SQLite fallback"""
    
    def __init__(self, 
                 kafka_broker: str = KAFKA_BROKER,
                 topic: str = KAFKA_TOPIC,
                 group_id: str = KAFKA_GROUP_ID,
                 chroma_path: str = CHROMA_DB_PATH,
                 collection_name: str = CHROMA_COLLECTION_NAME):
        
        self.kafka_broker = kafka_broker
        self.topic = topic
        self.group_id = group_id
        self.chroma_path = chroma_path
        self.collection_name = collection_name
        
        # Initialize components
        self.consumer = None
        self.vectorstore = None
        self.embeddings = None
        self.text_splitter = None
        self.use_sqlite = False
        self.sqlite_consumer = None
        self.sqlite_queue = None
        
        # Statistics
        self.processed_messages = 0
        self.processed_chunks = 0
        self.errors = 0
        self.start_time = None
        
    def initialize(self) -> bool:
        """Initialize all pipeline components"""
        try:
            print("🔄 Initializing Kafka to VectorDB pipeline...")
            
            # Check OpenAI API key
            if not OPENAI_API_KEY:
                print("❌ OPENAI_API_KEY not found in environment variables")
                return False
            
            # Try to initialize Kafka consumer first
            if not self._initialize_consumer():
                return False
            
            # Initialize embeddings
            print("🧠 Initializing OpenAI embeddings...")
            import os
            os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
            self.embeddings = OpenAIEmbeddings()
            
            # Initialize vector store
            print(f"🗄️  Initializing ChromaDB at: {self.chroma_path}")
            os.makedirs(os.path.dirname(self.chroma_path), exist_ok=True)
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.chroma_path
            )
            
            # Initialize text splitter
            print(f"📝 Initializing text splitter (chunk_size: {CHUNK_SIZE}, overlap: {CHUNK_OVERLAP})")
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            print("✅ Pipeline initialization completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Pipeline initialization failed: {e}")
            return False
    
    def _initialize_consumer(self) -> bool:
        """Initialize Kafka consumer or fallback to SQLite"""
        try:
            print(f"📡 Attempting to connect to Kafka broker: {self.kafka_broker}")
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=[self.kafka_broker],
                group_id=self.group_id,
                enable_auto_commit=False,  # Manual offset commit for at-least-once delivery
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=5000,  # 5 second timeout for faster fallback
                auto_offset_reset='earliest',  # Start from beginning if no offset
                request_timeout_ms=5000,
                session_timeout_ms=6000,
                heartbeat_interval_ms=2000
            )
            
            # Test the connection by trying to get metadata
            partitions = self.consumer.partitions_for_topic(self.topic)
            if partitions is None:
                raise Exception("Topic not found or broker unreachable")
            
            print("✅ Connected to Kafka broker successfully")
            self.use_sqlite = False
            return True
            
        except Exception as e:
            print(f"⚠️  Kafka connection failed: {e}")
            print("🔄 Falling back to SQLite message queue...")
            
            try:
                self.sqlite_consumer = SQLiteConsumer([self.topic], group_id=self.group_id)
                self.sqlite_queue = SQLiteMessageQueue()
                self.use_sqlite = True
                print("✅ SQLite message queue initialized successfully")
                return True
            except Exception as sqlite_error:
                print(f"❌ SQLite fallback failed: {sqlite_error}")
                return False
    
    def process_message(self, message_data: Dict[str, Any]) -> bool:
        """Process a single message and add to vector store"""
        try:
            # Extract text and metadata
            text = message_data.get("text", "")
            metadata = message_data.get("metadata", {})
            
            if not text:
                print("⚠️  Empty text content, skipping message")
                return False
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            if not chunks:
                print("⚠️  No chunks created from text, skipping message")
                return False
            
            # Create documents with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                # Create unique ID for each chunk
                chunk_id = f"{metadata.get('id', 'unknown')}_{i}"
                
                # Prepare chunk metadata
                chunk_metadata = {
                    **metadata,
                    "chunk_id": chunk_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk)
                }
                
                documents.append(Document(
                    page_content=chunk,
                    metadata=chunk_metadata
                ))
            
            # Add documents to vector store
            self.vectorstore.add_documents(documents)
            
            self.processed_chunks += len(documents)
            print(f"✅ Processed document: {metadata.get('title', 'Unknown')[:50]}... "
                  f"({len(documents)} chunks)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            self.errors += 1
            return False
    
    def run(self, max_messages: int = 50, timeout_seconds: int = 60) -> Dict[str, Any]:
        """Run the pipeline to process messages"""
        print(f"🚀 Starting pipeline (max_messages: {max_messages}, timeout: {timeout_seconds}s)")
        print(f"📊 Using {('SQLite' if self.use_sqlite else 'Kafka')} message queue")
        
        self.start_time = time.time()
        self.processed_messages = 0
        self.processed_chunks = 0
        self.errors = 0
        
        try:
            if self.use_sqlite:
                return self._run_sqlite_consumer(max_messages, timeout_seconds)
            else:
                return self._run_kafka_consumer(max_messages, timeout_seconds)
                
        except Exception as e:
            print(f"❌ Pipeline execution failed: {e}")
            return {
                "error": str(e),
                "processed_messages": self.processed_messages,
                "processed_chunks": self.processed_chunks,
                "errors": self.errors
            }
    
    def _run_sqlite_consumer(self, max_messages: int, timeout_seconds: int) -> Dict[str, Any]:
        """Run pipeline with SQLite consumer"""
        end_time = time.time() + timeout_seconds
        
        while self.processed_messages < max_messages and time.time() < end_time:
            # Get messages from SQLite queue
            messages_dict = self.sqlite_consumer.poll(max_records=min(5, max_messages - self.processed_messages))
            
            if not messages_dict or not messages_dict.get(self.topic):
                time.sleep(0.5)  # Wait a bit before next poll
                continue
            
            for message in messages_dict[self.topic]:
                if self.process_message(message.value):
                    self.processed_messages += 1
                
                if self.processed_messages >= max_messages:
                    break
            
            # Commit offsets (handled automatically in SQLite consumer)
            self.sqlite_consumer.commit()
        
        return self._get_run_stats()
    
    def _run_kafka_consumer(self, max_messages: int, timeout_seconds: int) -> Dict[str, Any]:
        """Run pipeline with Kafka consumer"""
        end_time = time.time() + timeout_seconds
        
        for message in self.consumer:
            if time.time() > end_time or self.processed_messages >= max_messages:
                break
            
            if self.process_message(message.value):
                self.processed_messages += 1
            
            # Commit offset for at-least-once delivery
            self.consumer.commit()
        
        return self._get_run_stats()
    
    def _get_run_stats(self) -> Dict[str, Any]:
        """Get pipeline execution statistics"""
        duration = time.time() - self.start_time
        
        stats = {
            "processed_messages": self.processed_messages,
            "processed_chunks": self.processed_chunks,
            "errors": self.errors,
            "duration": duration,
            "messages_per_second": self.processed_messages / duration if duration > 0 else 0,
            "chunks_per_second": self.processed_chunks / duration if duration > 0 else 0,
            "queue_type": "SQLite" if self.use_sqlite else "Kafka"
        }
        
        print(f"\n📊 Pipeline Statistics:")
        print(f"  Queue Type: {stats['queue_type']}")
        print(f"  Messages processed: {stats['processed_messages']}")
        print(f"  Chunks created: {stats['processed_chunks']}")
        print(f"  Errors: {stats['errors']}")
        print(f"  Duration: {stats['duration']:.2f} seconds")
        print(f"  Rate: {stats['messages_per_second']:.2f} messages/sec")
        
        return stats
    
    def query_vectorstore(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Query the vector store for similar documents"""
        try:
            if not self.vectorstore:
                print("❌ Vector store not initialized")
                return []
            
            # Perform similarity search
            results = self.vectorstore.similarity_search(query, k=k)
            
            # Format results
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error querying vector store: {e}")
            return []
    
    def get_vectorstore_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            if not self.vectorstore:
                return {"document_count": 0, "collection_name": self.collection_name}
            
            # Get collection info
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                "document_count": count,
                "collection_name": self.collection_name,
                "database_path": self.chroma_path
            }
            
        except Exception as e:
            print(f"❌ Error getting vector store stats: {e}")
            return {"document_count": 0, "collection_name": self.collection_name}
    
    def close(self):
        """Close all connections"""
        try:
            if self.use_sqlite and self.sqlite_consumer:
                self.sqlite_consumer.close()
                print("🔒 SQLite consumer closed")
            elif self.consumer:
                self.consumer.close()
                print("🔒 Kafka consumer closed")
        except Exception as e:
            print(f"⚠️  Error closing consumer: {e}")


def demo_pipeline():
    """Demonstrate the pipeline functionality"""
    print("🚀 Starting Pipeline Demo")
    print("=" * 50)
    
    # Initialize pipeline
    pipeline = KafkaToVectorDBPipeline()
    if not pipeline.initialize():
        print("❌ Failed to initialize pipeline")
        return
    
    # Run pipeline
    stats = pipeline.run(max_messages=10, timeout_seconds=30)
    
    if "error" not in stats:
        print("\n🎉 Pipeline completed successfully!")
        
        # Test querying
        print("\n🔍 Testing vector store queries...")
        test_queries = [
            "employee benefits",
            "remote work policy",
            "safety guidelines"
        ]
        
        for query in test_queries:
            results = pipeline.query_vectorstore(query, k=2)
            print(f"  Query: '{query}' -> {len(results)} results")
        
        # Get vector store stats
        vs_stats = pipeline.get_vectorstore_stats()
        print(f"\n📈 Vector Store Statistics:")
        print(f"  Documents: {vs_stats['document_count']}")
        print(f"  Collection: {vs_stats['collection_name']}")
    
    # Close pipeline
    pipeline.close()
    print("\n🎉 Pipeline demo completed!")


if __name__ == "__main__":
    demo_pipeline()

