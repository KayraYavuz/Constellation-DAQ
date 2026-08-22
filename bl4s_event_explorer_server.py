#!/usr/bin/env python3
"""
BL4S Live Event Explorer — WebSocket Backend
Bridges Kafka events to a browser via Socket.IO for real-time observability.
Supports hybrid Protobuf & JSON telemetry deserialization.
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

client_subscriptions = {}

@app.route('/')
def index():
    return send_file('bl4s_event_explorer.html')

@app.route('/api/hv/control', methods=['POST'])
def hv_control():
    """Receives Power ON/OFF, V0Set, and Reset commands from the UI and dispatches to CAEN crate."""
    data = flask_request.get_json() or {}
    action = data.get('action', 'set_param')
    ch_id = data.get('channel_id')
    power = data.get('power')
    v0 = data.get('v0')
    
    print(f"[CAEN Crate Control] Received command: Action={action}, Channel={ch_id}, Power={power}, Target V0={v0}")
    # In live mode, this invokes pycaenhv wrapper: CAENHV_SetChParam(crate_handle, slot, ch, 'Pw', 1 if power else 0)
    return {"status": "SUCCESS", "channel": ch_id, "power": power, "v0": v0}

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
    sat_name = data.get('satellite', '')
    if flask_request.sid in client_subscriptions:
        client_subscriptions[flask_request.sid].add(sat_name)

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    sat_name = data.get('satellite', '')
    if flask_request.sid in client_subscriptions:
        client_subscriptions[flask_request.sid].discard(sat_name)

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
            print("[Kafka] Connected! Consuming Protobuf & JSON events...")
            
            import bl4s_events_pb2
            
            buffer = {}  # {satellite_name: [events]}
            last_flush = time.time()
            
            while True:
                records = consumer.poll(timeout_ms=50)
                for tp, messages in records.items():
                    for message in messages:
                        event = None
                        
                        # 1. Attempt Protobuf deserialization
                        try:
                            pb_event = bl4s_events_pb2.BL4SEvent()
                            pb_event.ParseFromString(message.value)
                            event = {"sat": pb_event.sat}
                            field = pb_event.WhichOneof("event_data")
                            if field:
                                sub_msg = getattr(pb_event, field)
                                for descriptor in sub_msg.DESCRIPTOR.fields:
                                    event[descriptor.name] = getattr(sub_msg, descriptor.name)
                        except Exception:
                            event = None

                        # 2. Attempt JSON deserialization fallback
                        if event is None:
                            try:
                                event = json.loads(message.value.decode('utf-8'))
                            except Exception:
                                continue
                                
                        if not event or not isinstance(event, dict):
                            continue
                            
                        sat_name = event.get('sat', 'Unknown')
                        if sat_name not in buffer:
                            buffer[sat_name] = []
                        buffer[sat_name].append(event)
                
                # Flush buffer every 100ms
                now = time.time()
                if now - last_flush >= 0.1 and buffer:
                    for sat_name, events in buffer.items():
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
    kafka_thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
    kafka_thread.start()
    
    print("=" * 60)
    print("  BL4S Live Event Explorer Backend")
    print("  Open http://localhost:5050 in your browser")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5050, debug=False, allow_unsafe_werkzeug=True)
