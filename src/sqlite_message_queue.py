"""
SQLite-based message queue system to emulate Kafka functionality
for demo purposes when Kafka broker is not available.
"""

import sqlite3
import json
import time
import threading
import os
from typing import Dict, Any, List, Optional
from datetime import datetime


class SQLiteMessageQueue:
    """SQLite-based message queue that emulates Kafka topics"""
    
    def __init__(self, db_path: str = "./data/message_queue.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._ensure_db_exists()
        self._create_tables()
    
    def _ensure_db_exists(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _create_tables(self):
        """Create necessary tables for message queue"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    key TEXT,
                    value TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    consumed BOOLEAN DEFAULT FALSE,
                    consumer_group TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS consumer_offsets (
                    consumer_group TEXT,
                    topic TEXT,
                    last_offset INTEGER,
                    PRIMARY KEY (consumer_group, topic)
                )
            """)
            
            conn.commit()
    
    def send_message(self, topic: str, key: str, value: Dict[Any, Any]) -> bool:
        """Send a message to the specified topic"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO messages (topic, key, value, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (topic, key, json.dumps(value), time.time()))
                    conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def get_messages(self, topic: str, consumer_group: str, max_messages: int = 10) -> List[Dict[str, Any]]:
        """Get messages from the specified topic for a consumer group"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    # Get last consumed offset for this consumer group
                    cursor = conn.execute("""
                        SELECT last_offset FROM consumer_offsets 
                        WHERE consumer_group = ? AND topic = ?
                    """, (consumer_group, topic))
                    
                    result = cursor.fetchone()
                    last_offset = result[0] if result else 0
                    
                    # Get new messages
                    cursor = conn.execute("""
                        SELECT id, key, value, timestamp FROM messages 
                        WHERE topic = ? AND id > ? 
                        ORDER BY id LIMIT ?
                    """, (topic, last_offset, max_messages))
                    
                    messages = []
                    new_last_offset = last_offset
                    
                    for row in cursor.fetchall():
                        msg_id, key, value, timestamp = row
                        messages.append({
                            'id': msg_id,
                            'key': key,
                            'value': json.loads(value),
                            'timestamp': timestamp
                        })
                        new_last_offset = msg_id
                    
                    # Update consumer offset
                    if messages:
                        conn.execute("""
                            INSERT OR REPLACE INTO consumer_offsets 
                            (consumer_group, topic, last_offset) VALUES (?, ?, ?)
                        """, (consumer_group, topic, new_last_offset))
                        conn.commit()
                    
                    return messages
                    
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return []
    
    def get_topic_stats(self, topic: str) -> Dict[str, Any]:
        """Get statistics for a topic"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*), MIN(timestamp), MAX(timestamp) 
                    FROM messages WHERE topic = ?
                """, (topic,))
                
                count, min_time, max_time = cursor.fetchone()
                
                return {
                    'message_count': count or 0,
                    'first_message': datetime.fromtimestamp(min_time).isoformat() if min_time else None,
                    'last_message': datetime.fromtimestamp(max_time).isoformat() if max_time else None
                }
        except Exception as e:
            print(f"❌ Error getting topic stats: {e}")
            return {'message_count': 0, 'first_message': None, 'last_message': None}
    
    def clear_topic(self, topic: str) -> bool:
        """Clear all messages from a topic"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM messages WHERE topic = ?", (topic,))
                    conn.execute("DELETE FROM consumer_offsets WHERE topic = ?", (topic,))
                    conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error clearing topic: {e}")
            return False


class SQLiteProducer:
    """Producer interface that mimics Kafka producer"""
    
    def __init__(self, bootstrap_servers: List[str] = None, **kwargs):
        self.queue = SQLiteMessageQueue()
        self.connected = True
    
    def send(self, topic: str, key: str = None, value: Dict[Any, Any] = None) -> bool:
        """Send a message (mimics Kafka producer send)"""
        return self.queue.send_message(topic, key, value)
    
    def flush(self):
        """Flush any pending messages (no-op for SQLite)"""
        pass
    
    def close(self):
        """Close the producer"""
        self.connected = False


class SQLiteConsumer:
    """Consumer interface that mimics Kafka consumer"""
    
    def __init__(self, topics: List[str], bootstrap_servers: List[str] = None, 
                 group_id: str = "default", **kwargs):
        self.topics = topics
        self.group_id = group_id
        self.queue = SQLiteMessageQueue()
        self.connected = True
        self._timeout_ms = kwargs.get('consumer_timeout_ms', 10000)
    
    def poll(self, timeout_ms: int = 1000, max_records: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Poll for messages (mimics Kafka consumer poll)"""
        if not self.connected:
            return {}
        
        all_messages = {}
        for topic in self.topics:
            messages = self.queue.get_messages(topic, self.group_id, max_records)
            if messages:
                # Convert to Kafka-like format
                kafka_messages = []
                for msg in messages:
                    kafka_messages.append(type('Message', (), {
                        'key': msg['key'],
                        'value': msg['value'],
                        'topic': topic,
                        'partition': 0,
                        'offset': msg['id'],
                        'timestamp': msg['timestamp']
                    })())
                all_messages[topic] = kafka_messages
        
        return all_messages
    
    def commit(self):
        """Commit offsets (already handled in get_messages)"""
        pass
    
    def close(self):
        """Close the consumer"""
        self.connected = False
    
    def __iter__(self):
        """Iterator interface for consumer"""
        start_time = time.time()
        timeout_seconds = self._timeout_ms / 1000.0
        
        while self.connected:
            if time.time() - start_time > timeout_seconds:
                break
                
            messages_dict = self.poll(max_records=1)
            for topic, messages in messages_dict.items():
                for message in messages:
                    yield message
            
            if not any(messages_dict.values()):
                time.sleep(0.1)  # Small delay if no messages


def test_sqlite_queue():
    """Test the SQLite message queue functionality"""
    print("🧪 Testing SQLite Message Queue...")
    
    # Test producer
    producer = SQLiteProducer()
    test_message = {
        'id': 'test-123',
        'title': 'Test Document',
        'content': 'This is a test document for the message queue.',
        'document_type': 'test',
        'created_date': datetime.now().isoformat()
    }
    
    success = producer.send('test-topic', 'test-key', test_message)
    print(f"✅ Message sent: {success}")
    
    # Test consumer
    consumer = SQLiteConsumer(['test-topic'], group_id='test-group')
    messages = consumer.poll(max_records=5)
    print(f"✅ Messages received: {len(messages.get('test-topic', []))}")
    
    # Test stats
    queue = SQLiteMessageQueue()
    stats = queue.get_topic_stats('test-topic')
    print(f"✅ Topic stats: {stats}")
    
    # Cleanup
    queue.clear_topic('test-topic')
    producer.close()
    consumer.close()
    
    print("🎉 SQLite Message Queue test completed!")


if __name__ == "__main__":
    test_sqlite_queue()

