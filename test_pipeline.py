#!/usr/bin/env python3
"""
Test script for the Kafka to VectorDB pipeline components
"""

import os
import sys
import json
import tempfile
from typing import Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

def test_data_generator():
    """Test the data generator"""
    print("🧪 Testing Data Generator...")
    
    try:
        from src.data_generator import HRDataGenerator
        
        generator = HRDataGenerator()
        
        # Test single document generation
        doc = generator.generate_document()
        assert 'id' in doc
        assert 'title' in doc
        assert 'content' in doc
        assert 'document_type' in doc
        assert len(doc['content']) > 0
        
        print(f"✅ Single document: {doc['title']} ({doc['document_type']})")
        
        # Test batch generation
        batch = generator.generate_batch(5)
        assert len(batch) == 5
        assert all('id' in doc for doc in batch)
        
        print(f"✅ Batch generation: {len(batch)} documents")
        
        # Test different document types
        doc_types = set(doc['document_type'] for doc in batch)
        print(f"✅ Document types: {', '.join(doc_types)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data generator test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("🧪 Testing Configuration...")
    
    try:
        from config.config import (
            KAFKA_BROKER, KAFKA_TOPIC, KAFKA_GROUP_ID,
            CHROMA_DB_PATH, CHROMA_COLLECTION_NAME,
            CHUNK_SIZE, CHUNK_OVERLAP
        )
        
        # Check that all required config values are present
        assert KAFKA_BROKER is not None
        assert KAFKA_TOPIC is not None
        assert KAFKA_GROUP_ID is not None
        assert CHROMA_DB_PATH is not None
        assert CHROMA_COLLECTION_NAME is not None
        assert CHUNK_SIZE > 0
        assert CHUNK_OVERLAP >= 0
        
        print(f"✅ Kafka Broker: {KAFKA_BROKER}")
        print(f"✅ Kafka Topic: {KAFKA_TOPIC}")
        print(f"✅ Chroma Collection: {CHROMA_COLLECTION_NAME}")
        print(f"✅ Chunk Size: {CHUNK_SIZE}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_text_processing():
    """Test text processing components"""
    print("🧪 Testing Text Processing...")
    
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.schema import Document
        from config.config import CHUNK_SIZE, CHUNK_OVERLAP
        
        # Create text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        
        # Test with sample text
        sample_text = """
        This is a sample HR document for testing purposes. It contains multiple paragraphs
        and should be split into appropriate chunks for processing.
        
        The document discusses employee benefits, including health insurance, retirement plans,
        and paid time off policies. These are important topics for all employees to understand.
        
        Additionally, the document covers workplace policies such as code of conduct,
        safety guidelines, and professional development opportunities.
        """
        
        # Create document and split
        doc = Document(page_content=sample_text, metadata={"test": "document"})
        chunks = text_splitter.split_documents([doc])
        
        assert len(chunks) > 0
        assert all(len(chunk.page_content) <= CHUNK_SIZE + CHUNK_OVERLAP for chunk in chunks)
        
        print(f"✅ Text splitting: {len(chunks)} chunks created")
        print(f"✅ Chunk sizes: {[len(chunk.page_content) for chunk in chunks]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Text processing test failed: {e}")
        return False

def test_kafka_producer_init():
    """Test Kafka producer initialization (without connecting)"""
    print("🧪 Testing Kafka Producer Initialization...")
    
    try:
        from src.kafka_producer import DocumentProducer
        
        # Test producer creation
        producer = DocumentProducer()
        assert producer.bootstrap_servers is not None
        assert producer.topic is not None
        assert producer.data_generator is not None
        
        print(f"✅ Producer initialized with broker: {producer.bootstrap_servers}")
        print(f"✅ Producer topic: {producer.topic}")
        
        return True
        
    except Exception as e:
        print(f"❌ Kafka producer test failed: {e}")
        return False

def test_pipeline_init():
    """Test pipeline initialization (without OpenAI key)"""
    print("🧪 Testing Pipeline Initialization...")
    
    try:
        from src.kafka_to_vectordb import KafkaToVectorDBPipeline
        
        # Test pipeline creation
        pipeline = KafkaToVectorDBPipeline()
        assert pipeline.kafka_broker is not None
        assert pipeline.topic is not None
        assert pipeline.group_id is not None
        assert pipeline.chroma_path is not None
        assert pipeline.collection_name is not None
        
        print(f"✅ Pipeline initialized with broker: {pipeline.kafka_broker}")
        print(f"✅ Pipeline topic: {pipeline.topic}")
        print(f"✅ Pipeline collection: {pipeline.collection_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline initialization test failed: {e}")
        return False

def test_cli_script():
    """Test CLI script imports"""
    print("🧪 Testing CLI Script...")
    
    try:
        # Test that the CLI script can be imported
        import demo_cli
        
        # Test that the demo class can be created
        demo = demo_cli.KafkaVectorDBDemo()
        assert demo is not None
        
        print("✅ CLI script imports successfully")
        print("✅ Demo class can be instantiated")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI script test failed: {e}")
        return False

def test_streamlit_app():
    """Test Streamlit app imports"""
    print("🧪 Testing Streamlit App...")
    
    try:
        # Add streamlit_app to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'streamlit_app'))
        
        # Test that the app can be imported
        import app
        
        # Test that the demo class can be created
        demo = app.StreamlitKafkaVectorDBDemo()
        assert demo is not None
        assert demo.data_generator is not None
        
        print("✅ Streamlit app imports successfully")
        print("✅ Streamlit demo class can be instantiated")
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit app test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Running Kafka to VectorDB Pipeline Tests")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_data_generator,
        test_text_processing,
        test_kafka_producer_init,
        test_pipeline_init,
        test_cli_script,
        test_streamlit_app
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print()
        try:
            if test():
                passed += 1
                print("✅ PASSED")
            else:
                failed += 1
                print("❌ FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ FAILED: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The pipeline is ready for use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

def main():
    """Main test runner"""
    success = run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())

