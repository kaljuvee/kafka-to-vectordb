import json
import os
import uuid
import sys
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from langchain.text_splitter import RecursiveCharacterTextSplitter
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

class KafkaToVectorDBPipeline:
    """Kafka to VectorDB ingestion pipeline"""
    
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
            
            # Initialize Kafka consumer
            print(f"📡 Connecting to Kafka broker: {self.kafka_broker}")
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=[self.kafka_broker],
                group_id=self.group_id,
                enable_auto_commit=False,  # Manual offset commit for at-least-once delivery
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=10000,  # 10 second timeout for demo purposes
                auto_offset_reset='earliest'  # Start from beginning if no offset
            )
            
            # Initialize embeddings
            print("🧠 Initializing OpenAI embeddings...")
            self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            
            # Initialize vector store
            print(f"🗄️  Initializing ChromaDB at: {self.chroma_path}")
            os.makedirs(os.path.dirname(self.chroma_path), exist_ok=True)
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.chroma_path
            )
            
            # Initialize text splitter
            print(f"✂️  Initializing text splitter (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                separators=["\\n\\n", "\\n", ". ", " ", ""]
            )
            
            print("✅ Pipeline initialization complete!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize pipeline: {e}")
            return False
    
    def process_message(self, message) -> bool:
        """Process a single Kafka message"""
        try:
            payload = message.value
            
            # Extract text and metadata
            text = payload.get("text", "")
            meta = payload.get("meta", {})
            
            if not text.strip():
                print(f"⚠️  Skipping empty message at offset {message.offset}")
                return True
            
            # Add Kafka metadata
            meta.update({
                "kafka_topic": message.topic,
                "kafka_partition": message.partition,
                "kafka_offset": message.offset,
                "kafka_timestamp": message.timestamp,
                "processed_at": time.time()
            })
            
            # Split text into chunks
            docs = self.text_splitter.split_documents([
                Document(page_content=text, metadata=meta)
            ])
            
            if not docs:
                print(f"⚠️  No chunks created from message at offset {message.offset}")
                return True
            
            # Generate stable IDs for idempotency
            ids = []
            for i, doc in enumerate(docs):
                # Create deterministic ID based on content and metadata
                content_hash = str(uuid.uuid5(
                    uuid.NAMESPACE_DNS, 
                    f"{doc.page_content}_{meta.get('id', '')}_{i}"
                ))
                ids.append(content_hash)
            
            # Upsert to vector store
            self.vectorstore.add_documents(documents=docs, ids=ids)
            self.vectorstore.persist()
            
            # Update statistics
            self.processed_chunks += len(docs)
            
            print(f"✅ Processed message offset {message.offset}: "
                  f"{len(docs)} chunks from '{meta.get('title', 'Unknown')}' "
                  f"({meta.get('document_type', 'unknown')})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing message at offset {message.offset}: {e}")
            self.errors += 1
            return False
    
    def run(self, max_messages: int = None, timeout_seconds: int = None) -> Dict[str, Any]:
        """Run the ingestion pipeline"""
        if not self.consumer or not self.vectorstore:
            print("❌ Pipeline not initialized. Call initialize() first.")
            return {"error": "Pipeline not initialized"}
        
        print(f"🚀 Starting Kafka to VectorDB ingestion...")
        print(f"📊 Topic: {self.topic}, Group: {self.group_id}")
        print(f"🎯 Max messages: {max_messages or 'unlimited'}")
        print(f"⏰ Timeout: {timeout_seconds or 'none'} seconds")
        print("Press Ctrl+C to stop gracefully\\n")
        
        self.start_time = time.time()
        
        try:
            message_count = 0
            
            for message in self.consumer:
                # Process the message
                if self.process_message(message):
                    # Commit offset only after successful processing
                    self.consumer.commit()
                    self.processed_messages += 1
                    message_count += 1
                    
                    # Check if we've reached the maximum number of messages
                    if max_messages and message_count >= max_messages:
                        print(f"🎯 Reached maximum message limit: {max_messages}")
                        break
                    
                    # Progress update every 10 messages
                    if message_count % 10 == 0:
                        elapsed = time.time() - self.start_time
                        rate = message_count / elapsed if elapsed > 0 else 0
                        print(f"📊 Progress: {message_count} messages, "
                              f"{self.processed_chunks} chunks, "
                              f"{rate:.1f} msg/sec")
                
                # Check timeout
                if timeout_seconds:
                    elapsed = time.time() - self.start_time
                    if elapsed >= timeout_seconds:
                        print(f"⏰ Timeout reached: {timeout_seconds} seconds")
                        break
        
        except KeyboardInterrupt:
            print("\\n🛑 Graceful shutdown requested...")
        
        except Exception as e:
            print(f"\\n❌ Pipeline error: {e}")
            self.errors += 1
        
        finally:
            # Final statistics
            elapsed = time.time() - self.start_time
            stats = self.get_statistics(elapsed)
            self.print_statistics(stats)
            
            # Close consumer
            if self.consumer:
                self.consumer.close()
                print("✅ Kafka consumer closed")
            
            return stats
    
    def get_statistics(self, elapsed_time: float = None) -> Dict[str, Any]:
        """Get pipeline statistics"""
        if elapsed_time is None and self.start_time:
            elapsed_time = time.time() - self.start_time
        
        return {
            "processed_messages": self.processed_messages,
            "processed_chunks": self.processed_chunks,
            "errors": self.errors,
            "elapsed_time": elapsed_time or 0,
            "messages_per_second": self.processed_messages / elapsed_time if elapsed_time > 0 else 0,
            "chunks_per_second": self.processed_chunks / elapsed_time if elapsed_time > 0 else 0,
            "collection_name": self.collection_name,
            "chroma_path": self.chroma_path
        }
    
    def print_statistics(self, stats: Dict[str, Any]):
        """Print pipeline statistics"""
        print("\\n" + "="*50)
        print("📊 PIPELINE STATISTICS")
        print("="*50)
        print(f"Messages processed: {stats['processed_messages']}")
        print(f"Chunks created: {stats['processed_chunks']}")
        print(f"Errors: {stats['errors']}")
        print(f"Elapsed time: {stats['elapsed_time']:.1f} seconds")
        print(f"Processing rate: {stats['messages_per_second']:.1f} messages/sec")
        print(f"Chunk rate: {stats['chunks_per_second']:.1f} chunks/sec")
        print(f"Collection: {stats['collection_name']}")
        print(f"Database path: {stats['chroma_path']}")
        print("="*50)
    
    def query_vectorstore(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Query the vector store for similar documents"""
        if not self.vectorstore:
            print("❌ Vector store not initialized")
            return []
        
        try:
            print(f"🔍 Searching for: '{query}'")
            docs = self.vectorstore.similarity_search(query, k=k)
            
            results = []
            for i, doc in enumerate(docs, 1):
                result = {
                    "rank": i,
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                }
                results.append(result)
                
                print(f"\\n{i}. {doc.metadata.get('title', 'Unknown Title')}")
                print(f"   Type: {doc.metadata.get('document_type', 'unknown')}")
                print(f"   Department: {doc.metadata.get('department', 'unknown')}")
                print(f"   Content: {result['content']}")
                print(f"   ---")
            
            return results
            
        except Exception as e:
            print(f"❌ Error querying vector store: {e}")
            return []

def main():
    """Command line interface for the pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kafka to VectorDB ingestion pipeline")
    parser.add_argument("--broker", default=KAFKA_BROKER,
                       help="Kafka broker address")
    parser.add_argument("--topic", default=KAFKA_TOPIC,
                       help="Kafka topic to consume from")
    parser.add_argument("--group-id", default=KAFKA_GROUP_ID,
                       help="Kafka consumer group ID")
    parser.add_argument("--max-messages", type=int,
                       help="Maximum number of messages to process")
    parser.add_argument("--timeout", type=int,
                       help="Timeout in seconds")
    parser.add_argument("--query", type=str,
                       help="Query the vector store instead of consuming")
    parser.add_argument("--query-limit", type=int, default=5,
                       help="Number of results for query (default: 5)")
    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = KafkaToVectorDBPipeline(
        kafka_broker=args.broker,
        topic=args.topic,
        group_id=args.group_id
    )
    
    # Initialize pipeline
    if not pipeline.initialize():
        print("❌ Failed to initialize pipeline")
        return 1
    
    try:
        if args.query:
            # Query mode
            results = pipeline.query_vectorstore(args.query, args.query_limit)
            print(f"\\n🔍 Found {len(results)} results for query: '{args.query}'")
        else:
            # Ingestion mode
            stats = pipeline.run(
                max_messages=args.max_messages,
                timeout_seconds=args.timeout
            )
            
            if stats.get("error"):
                return 1
    
    except KeyboardInterrupt:
        print("\\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

