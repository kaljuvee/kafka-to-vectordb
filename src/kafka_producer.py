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

class DocumentProducer:
    """Kafka producer for sending HR documents to the pipeline"""
    
    def __init__(self, bootstrap_servers: str = KAFKA_BROKER):
        self.bootstrap_servers = bootstrap_servers
        self.topic = KAFKA_TOPIC
        self.producer = None
        self.data_generator = HRDataGenerator()
        
    def connect(self):
        """Initialize Kafka producer connection"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[self.bootstrap_servers],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,
                retry_backoff_ms=1000,
                request_timeout_ms=30000
            )
            print(f"✅ Connected to Kafka broker at {self.bootstrap_servers}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            return False
    
    def send_document(self, document: Dict[str, Any]) -> bool:
        """Send a single document to Kafka topic"""
        if not self.producer:
            print("❌ Producer not connected. Call connect() first.")
            return False
        
        try:
            # Create message payload
            message = {
                "text": document["content"],
                "meta": {
                    "id": document["id"],
                    "title": document["title"],
                    "document_type": document["document_type"],
                    "department": document["department"],
                    "created_date": document["created_date"],
                    "author": document["author"],
                    "version": document["version"],
                    "tags": document["tags"],
                    "word_count": document["word_count"],
                    "metadata": document["metadata"]
                }
            }
            
            # Send message
            future = self.producer.send(
                self.topic,
                key=document["id"],
                value=message
            )
            
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            
            print(f"✅ Sent document '{document['title']}' to topic '{record_metadata.topic}' "
                  f"partition {record_metadata.partition} offset {record_metadata.offset}")
            return True
            
        except KafkaError as e:
            print(f"❌ Kafka error sending document: {e}")
            return False
        except Exception as e:
            print(f"❌ Error sending document: {e}")
            return False
    
    def send_batch(self, documents: List[Dict[str, Any]], delay_seconds: float = 1.0) -> int:
        """Send a batch of documents with optional delay between sends"""
        if not self.producer:
            print("❌ Producer not connected. Call connect() first.")
            return 0
        
        sent_count = 0
        total_docs = len(documents)
        
        print(f"📤 Sending {total_docs} documents to topic '{self.topic}'...")
        
        for i, document in enumerate(documents, 1):
            if self.send_document(document):
                sent_count += 1
            
            # Progress indicator
            if i % 10 == 0 or i == total_docs:
                print(f"📊 Progress: {i}/{total_docs} documents sent")
            
            # Add delay between sends if specified
            if delay_seconds > 0 and i < total_docs:
                time.sleep(delay_seconds)
        
        print(f"✅ Batch complete: {sent_count}/{total_docs} documents sent successfully")
        return sent_count
    
    def generate_and_send(self, num_documents: int = 10, delay_seconds: float = 1.0) -> int:
        """Generate synthetic documents and send them to Kafka"""
        print(f"🔄 Generating {num_documents} synthetic HR documents...")
        documents = self.data_generator.generate_batch(num_documents)
        
        return self.send_batch(documents, delay_seconds)
    
    def send_continuous(self, documents_per_batch: int = 5, batch_delay_seconds: float = 10.0):
        """Send documents continuously (for demo purposes)"""
        print(f"🔄 Starting continuous document generation...")
        print(f"📊 Sending {documents_per_batch} documents every {batch_delay_seconds} seconds")
        print("Press Ctrl+C to stop")
        
        batch_number = 1
        try:
            while True:
                print(f"\n📦 Batch {batch_number}:")
                documents = self.data_generator.generate_batch(documents_per_batch)
                sent_count = self.send_batch(documents, delay_seconds=0.5)
                
                print(f"⏰ Waiting {batch_delay_seconds} seconds before next batch...")
                time.sleep(batch_delay_seconds)
                batch_number += 1
                
        except KeyboardInterrupt:
            print(f"\n🛑 Stopped continuous sending after {batch_number - 1} batches")
    
    def close(self):
        """Close the producer connection"""
        if self.producer:
            self.producer.flush()  # Ensure all messages are sent
            self.producer.close()
            print("✅ Producer connection closed")

def main():
    """Command line interface for the document producer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Send HR documents to Kafka topic")
    parser.add_argument("--broker", default=KAFKA_BROKER, 
                       help="Kafka broker address (default: localhost:9092)")
    parser.add_argument("--num-docs", type=int, default=10,
                       help="Number of documents to generate and send (default: 10)")
    parser.add_argument("--delay", type=float, default=1.0,
                       help="Delay between sends in seconds (default: 1.0)")
    parser.add_argument("--continuous", action="store_true",
                       help="Send documents continuously")
    parser.add_argument("--batch-size", type=int, default=5,
                       help="Documents per batch in continuous mode (default: 5)")
    parser.add_argument("--batch-delay", type=float, default=10.0,
                       help="Delay between batches in continuous mode (default: 10.0)")
    
    args = parser.parse_args()
    
    # Create and connect producer
    producer = DocumentProducer(args.broker)
    
    if not producer.connect():
        print("❌ Failed to connect to Kafka. Make sure Kafka is running.")
        return 1
    
    try:
        if args.continuous:
            producer.send_continuous(args.batch_size, args.batch_delay)
        else:
            sent_count = producer.generate_and_send(args.num_docs, args.delay)
            print(f"\n📊 Final result: {sent_count} documents sent successfully")
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        producer.close()
    
    return 0

if __name__ == "__main__":
    exit(main())

