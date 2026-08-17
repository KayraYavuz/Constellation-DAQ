#!/usr/bin/env python3
"""
BL4S Live Event Explorer — WebSocket Backend
Bridges Kafka events to a browser via Socket.IO for real-time observability.
"""
import json
import threading
import time
from flask import Flask, send_file, send_from_directory, request as flask_request
from flask_socketio import SocketIO, emit
from kafka import KafkaConsumer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bl4s_secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# --- Configuration ---
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'bl4s_events'

# Track which satellites each client is subscribed to
client_subscriptions = {}

@app.route('/')
def index():
    return send_file('bl4s_event_explorer.html')

@socketio.on('connect')
def handle_connect():
    print(f"[+] Client connected: {flask_request.sid}")
    client_subscriptions[flask_request.sid] = set()

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[-] Client disconnected: {flask_request.sid}")
    client_subscriptions.pop(flask_request.sid, None)

@socketio.on('subscribe')
def handle_subscribe(data):
    """Client subscribes to a specific satellite's data."""
    sat_name = data.get('satellite', '')
    if flask_request.sid in client_subscriptions:
        client_subscriptions[flask_request.sid].add(sat_name)
        print(f"[>] {flask_request.sid} subscribed to: {sat_name}")

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """Client unsubscribes from a specific satellite's data."""
    sat_name = data.get('satellite', '')
    if flask_request.sid in client_subscriptions:
        client_subscriptions[flask_request.sid].discard(sat_name)
        print(f"[<] {flask_request.sid} unsubscribed from: {sat_name}")

def kafka_consumer_thread():
    """Background thread consuming from Kafka and broadcasting to subscribed clients."""
    print(f"[Kafka] Connecting to {KAFKA_BROKER}, topic: {KAFKA_TOPIC}...")
    
    while True:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=[KAFKA_BROKER],
                auto_offset_reset='latest',
                enable_auto_commit=True,
                value_deserializer=lambda x: x,
                consumer_timeout_ms=1000
            )
            print("[Kafka] Connected! Consuming Protobuf events...")
            
            import bl4s_events_pb2
            
            # Buffer events and emit in batches for performance
            buffer = {}  # {satellite_name: [events]}
            last_flush = time.time()
            
            while True:
                # Poll for messages
                records = consumer.poll(timeout_ms=50)
                for tp, messages in records.items():
                    for message in messages:
                        pb_event = bl4s_events_pb2.BL4SEvent()
                        try:
                            pb_event.ParseFromString(message.value)
                        except Exception as e:
                            continue
                            
                        # Flatten the protobuf to a standard dict for the frontend
                        event = {"sat": pb_event.sat}
                        field = pb_event.WhichOneof("event_data")
                        if field:
                            sub_msg = getattr(pb_event, field)
                            for descriptor in sub_msg.DESCRIPTOR.fields:
                                event[descriptor.name] = getattr(sub_msg, descriptor.name)
                                
                        sat_name = event.get('sat', 'Unknown')
                        if sat_name not in buffer:
                            buffer[sat_name] = []
                        buffer[sat_name].append(event)
                
                # Flush buffer every 100ms
                now = time.time()
                if now - last_flush >= 0.1 and buffer:
                    for sat_name, events in buffer.items():
                        # Only emit to clients that subscribed to this satellite
                        socketio.emit('event_batch', {
                            'satellite': sat_name,
                            'events': events
                        })
                    buffer.clear()
                    last_flush = now
                    
        except Exception as e:
            print(f"[Kafka] Error: {e}. Retrying in 3 seconds...")
            time.sleep(3)

if __name__ == '__main__':
    # Start Kafka consumer in background thread
    kafka_thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
    kafka_thread.start()
    
    print("=" * 60)
    print("  BL4S Live Event Explorer")
    print("  Open http://localhost:5050 in your browser")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5050, debug=False, allow_unsafe_werkzeug=True)
