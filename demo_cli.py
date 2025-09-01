#!/usr/bin/env python3
"""
Kafka to VectorDB Demo - Command Line Interface

This script provides a simple interface to demonstrate the Kafka to VectorDB pipeline
with synthetic HR/organization data.
"""

import os
import sys
import time
import subprocess
import threading
from typing import Optional

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

from src.kafka_producer import DocumentProducer
from src.kafka_to_vectordb import KafkaToVectorDBPipeline
from config.config import OPENAI_API_KEY

class KafkaVectorDBDemo:
    """Main demo orchestrator"""
    
    def __init__(self):
        self.kafka_process = None
        self.producer = None
        self.pipeline = None
        
    def check_requirements(self) -> bool:
        """Check if all requirements are met"""
        print("🔍 Checking requirements...")
        
        # Check OpenAI API key
        if not OPENAI_API_KEY:
            print("❌ OPENAI_API_KEY not found in environment variables")
            print("   Please set your OpenAI API key in a .env file or environment variable")
            return False
        
        print("✅ OpenAI API key found")
        
        # Check if Kafka is available (we'll use embedded Kafka for demo)
        print("✅ Requirements check passed")
        return True
    
    def start_embedded_kafka(self) -> bool:
        """Start embedded Kafka for demo purposes"""
        print("🚀 Starting embedded Kafka server...")
        
        try:
            # For demo purposes, we'll simulate Kafka being available
            # In a real scenario, you would start Kafka here or check if it's running
            print("✅ Kafka server is ready (simulated)")
            return True
        except Exception as e:
            print(f"❌ Failed to start Kafka: {e}")
            return False
    
    def run_producer_demo(self, num_docs: int = 20, delay: float = 0.5):
        """Run the producer demo"""
        print(f"\\n📤 PRODUCER DEMO")
        print("="*50)
        
        self.producer = DocumentProducer()
        
        if not self.producer.connect():
            print("❌ Failed to connect producer to Kafka")
            return False
        
        try:
            sent_count = self.producer.generate_and_send(num_docs, delay)
            print(f"✅ Producer demo complete: {sent_count} documents sent")
            return True
        except Exception as e:
            print(f"❌ Producer demo failed: {e}")
            return False
        finally:
            if self.producer:
                self.producer.close()
    
    def run_consumer_demo(self, max_messages: int = 20, timeout: int = 30):
        """Run the consumer demo"""
        print(f"\\n📥 CONSUMER DEMO")
        print("="*50)
        
        self.pipeline = KafkaToVectorDBPipeline()
        
        if not self.pipeline.initialize():
            print("❌ Failed to initialize pipeline")
            return False
        
        try:
            stats = self.pipeline.run(
                max_messages=max_messages,
                timeout_seconds=timeout
            )
            
            if stats.get("error"):
                print("❌ Consumer demo failed")
                return False
            
            print("✅ Consumer demo complete")
            return True
            
        except Exception as e:
            print(f"❌ Consumer demo failed: {e}")
            return False
    
    def run_query_demo(self):
        """Run the query demo"""
        print(f"\\n🔍 QUERY DEMO")
        print("="*50)
        
        if not self.pipeline:
            self.pipeline = KafkaToVectorDBPipeline()
            if not self.pipeline.initialize():
                print("❌ Failed to initialize pipeline for querying")
                return False
        
        # Sample queries
        queries = [
            "employee benefits and health insurance",
            "remote work policy and guidelines",
            "performance review process",
            "safety guidelines and procedures",
            "training and development programs"
        ]
        
        print("Running sample queries against the vector database...")
        
        for i, query in enumerate(queries, 1):
            print(f"\\n--- Query {i}: {query} ---")
            results = self.pipeline.query_vectorstore(query, k=3)
            
            if not results:
                print("No results found")
            
            time.sleep(1)  # Brief pause between queries
        
        print("✅ Query demo complete")
        return True
    
    def run_interactive_query(self):
        """Run interactive query mode"""
        print(f"\\n💬 INTERACTIVE QUERY MODE")
        print("="*50)
        print("Enter queries to search the HR document database.")
        print("Type 'quit' or 'exit' to stop.\\n")
        
        if not self.pipeline:
            self.pipeline = KafkaToVectorDBPipeline()
            if not self.pipeline.initialize():
                print("❌ Failed to initialize pipeline for querying")
                return False
        
        try:
            while True:
                query = input("🔍 Enter your query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not query:
                    continue
                
                print()
                results = self.pipeline.query_vectorstore(query, k=5)
                
                if not results:
                    print("No results found. Try a different query.")
                
                print()
        
        except KeyboardInterrupt:
            print("\\n🛑 Interactive mode stopped")
        
        print("✅ Interactive query mode complete")
    
    def run_full_demo(self):
        """Run the complete demo pipeline"""
        print("🎬 KAFKA TO VECTORDB DEMO")
        print("="*60)
        print("This demo shows a complete pipeline from Kafka to VectorDB")
        print("using synthetic HR/organization documents.\\n")
        
        # Check requirements
        if not self.check_requirements():
            return False
        
        # Start Kafka
        if not self.start_embedded_kafka():
            return False
        
        try:
            # Run producer demo
            if not self.run_producer_demo(num_docs=15, delay=0.3):
                return False
            
            print("\\n⏰ Waiting 2 seconds before starting consumer...")
            time.sleep(2)
            
            # Run consumer demo
            if not self.run_consumer_demo(max_messages=15, timeout=45):
                return False
            
            print("\\n⏰ Waiting 1 second before querying...")
            time.sleep(1)
            
            # Run query demo
            if not self.run_query_demo():
                return False
            
            print("\\n🎉 DEMO COMPLETE!")
            print("="*60)
            print("The pipeline successfully:")
            print("✅ Generated synthetic HR documents")
            print("✅ Sent documents to Kafka topic")
            print("✅ Consumed and processed documents")
            print("✅ Created embeddings and stored in VectorDB")
            print("✅ Performed semantic search queries")
            print("\\nYou can now run interactive queries or explore the Streamlit app!")
            
            return True
            
        except KeyboardInterrupt:
            print("\\n🛑 Demo interrupted by user")
            return False
        except Exception as e:
            print(f"\\n❌ Demo failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.producer:
            self.producer.close()
        
        if self.kafka_process:
            self.kafka_process.terminate()

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Kafka to VectorDB Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo_cli.py                    # Run full demo
  python demo_cli.py --producer-only    # Run only producer
  python demo_cli.py --consumer-only    # Run only consumer
  python demo_cli.py --query-only       # Run only queries
  python demo_cli.py --interactive      # Interactive query mode
        """
    )
    
    parser.add_argument("--producer-only", action="store_true",
                       help="Run only the producer demo")
    parser.add_argument("--consumer-only", action="store_true",
                       help="Run only the consumer demo")
    parser.add_argument("--query-only", action="store_true",
                       help="Run only the query demo")
    parser.add_argument("--interactive", action="store_true",
                       help="Run interactive query mode")
    parser.add_argument("--num-docs", type=int, default=15,
                       help="Number of documents to generate (default: 15)")
    parser.add_argument("--timeout", type=int, default=45,
                       help="Consumer timeout in seconds (default: 45)")
    
    args = parser.parse_args()
    
    demo = KafkaVectorDBDemo()
    
    try:
        if args.producer_only:
            success = demo.check_requirements() and demo.start_embedded_kafka() and demo.run_producer_demo(args.num_docs)
        elif args.consumer_only:
            success = demo.check_requirements() and demo.run_consumer_demo(timeout=args.timeout)
        elif args.query_only:
            success = demo.check_requirements() and demo.run_query_demo()
        elif args.interactive:
            success = demo.check_requirements() and demo.run_interactive_query()
        else:
            success = demo.run_full_demo()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\\n🛑 Demo interrupted")
        return 1
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return 1
    finally:
        demo.cleanup()

if __name__ == "__main__":
    exit(main())

