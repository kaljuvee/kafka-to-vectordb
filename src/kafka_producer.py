import json
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError
from typing import Dict, Any, List
from data_generator import HRDataGenerator
import sys
import os

# Add config to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from config.config import KAFKA_BROKER, KAFKA_TOPIC

# Import SQLite fallback
from sqlite_message_queue import SQLiteProducer

class DocumentProducer:
    """Kafka producer for sending HR documents to the pipeline with SQLite fallback"""
    
    def __init__(self, bootstrap_servers: str = KAFKA_BROKER):
        self.bootstrap_servers = bootstrap_servers
        self.topic = KAFKA_TOPIC
        self.producer = None
        self.use_sqlite = False
        self.sqlite_producer = None
        self.data_generator = HRDataGenerator()
        
    def connect(self) -> bool:
        """Connect to Kafka broker or fallback to SQLite"""
        try:
            print(f"🔄 Attempting to connect to Kafka broker: {self.bootstrap_servers}")
            self.producer = KafkaProducer(
                bootstrap_servers=[self.bootstrap_servers],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas to acknowledge
                retries=1,  # Reduced retries for faster fallback
                retry_backoff_ms=500,
                request_timeout_ms=5000,  # 5 second timeout
                max_block_ms=3000  # 3 second max block
            )
            
            # Test the connection with a small timeout
            test_future = self.producer.send(self.topic, key="test", value={"test": "connection"})
            test_future.get(timeout=3)  # Wait up to 3 seconds
            
            print("✅ Connected to Kafka broker successfully")
            self.use_sqlite = False
            return True
            
        except Exception as e:
            print(f"⚠️  Kafka connection failed: {e}")
            print("🔄 Falling back to SQLite message queue...")
            
            try:
                self.sqlite_producer = SQLiteProducer()
                self.use_sqlite = True
                print("✅ SQLite message queue initialized successfully")
                return True
            except Exception as sqlite_error:
                print(f"❌ SQLite fallback failed: {sqlite_error}")
                return False
    
    def send_document(self, document: Dict[str, Any]) -> bool:
        """Send a single document to the message queue"""
        try:
            doc_id = document.get('id', 'unknown')
            
            # Create message payload
            message = {
                "text": document["content"],
                "metadata": {
                    "id": document["id"],
                    "title": document["title"],
                    "document_type": document["document_type"],
                    "department": document["department"],
                    "author": document["author"],
                    "created_date": document["created_date"],
                    "word_count": document["word_count"]
                }
            }
            
            if self.use_sqlite:
                success = self.sqlite_producer.send(self.topic, doc_id, message)
                if success:
                    print(f"📤 Document sent to SQLite queue: {document['title'][:50]}...")
                return success
            else:
                future = self.producer.send(
                    self.topic,
                    key=doc_id,
                    value=message
                )
                
                # Wait for the message to be sent
                record_metadata = future.get(timeout=10)
                print(f"📤 Document sent to Kafka: {document['title'][:50]}... "
                      f"(partition: {record_metadata.partition}, offset: {record_metadata.offset})")
                return True
                
        except Exception as e:
            print(f"❌ Failed to send document: {e}")
            return False
    
    def send_batch(self, documents: List[Dict[str, Any]], delay: float = 0.5) -> Dict[str, Any]:
        """Send a batch of documents with optional delay"""
        stats = {
            'total': len(documents),
            'sent': 0,
            'failed': 0,
            'start_time': time.time(),
            'queue_type': 'SQLite' if self.use_sqlite else 'Kafka'
        }
        
        for i, doc in enumerate(documents):
            if self.send_document(doc):
                stats['sent'] += 1
            else:
                stats['failed'] += 1
            
            # Add delay between sends
            if delay > 0 and i < len(documents) - 1:
                time.sleep(delay)
        
        stats['end_time'] = time.time()
        stats['duration'] = stats['end_time'] - stats['start_time']
        stats['rate'] = stats['sent'] / stats['duration'] if stats['duration'] > 0 else 0
        
        return stats
    
    def generate_and_send_documents(self, num_docs: int = 10, delay: float = 0.5) -> Dict[str, Any]:
        """Generate and send documents in one operation"""
        print(f"📝 Generating {num_docs} documents...")
        documents = self.data_generator.generate_batch(num_docs)
        
        print(f"📤 Sending {len(documents)} documents...")
        return self.send_batch(documents, delay)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get message queue statistics"""
        if self.use_sqlite and self.sqlite_producer:
            stats = self.sqlite_producer.queue.get_topic_stats(self.topic)
            stats['queue_type'] = 'SQLite'
            return stats
        else:
            return {
                'message_count': 0, 
                'first_message': None, 
                'last_message': None,
                'queue_type': 'Kafka'
            }
    
    def clear_queue(self) -> bool:
        """Clear all messages from the queue"""
        if self.use_sqlite and self.sqlite_producer:
            return self.sqlite_producer.queue.clear_topic(self.topic)
        else:
            print("⚠️  Cannot clear Kafka topic from producer")
            return False
    
    def close(self):
        """Close the producer connection"""
        try:
            if self.use_sqlite and self.sqlite_producer:
                self.sqlite_producer.close()
                print("🔒 SQLite producer closed")
            elif self.producer:
                self.producer.flush()
                self.producer.close()
                print("🔒 Kafka producer closed")
        except Exception as e:
            print(f"⚠️  Error closing producer: {e}")


def demo_producer():
    """Demonstrate the document producer functionality"""
    print("🚀 Starting Document Producer Demo")
    print("=" * 50)
    
    # Initialize producer
    producer = DocumentProducer()
    if not producer.connect():
        print("❌ Failed to initialize producer")
        return
    
    # Generate and send documents
    stats = producer.generate_and_send_documents(5, delay=0.2)
    
    print("\n📊 Sending Statistics:")
    print(f"  Queue Type: {stats['queue_type']}")
    print(f"  Total documents: {stats['total']}")
    print(f"  Successfully sent: {stats['sent']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Duration: {stats['duration']:.2f} seconds")
    print(f"  Rate: {stats['rate']:.2f} documents/second")
    
    # Get queue stats
    queue_stats = producer.get_queue_stats()
    print(f"\n📈 Queue Statistics:")
    print(f"  Queue Type: {queue_stats['queue_type']}")
    print(f"  Total messages: {queue_stats['message_count']}")
    print(f"  First message: {queue_stats['first_message']}")
    print(f"  Last message: {queue_stats['last_message']}")
    
    # Close producer
    producer.close()
    print("\n🎉 Producer demo completed!")


if __name__ == "__main__":
    demo_producer()

