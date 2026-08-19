#!/bin/bash

echo "🚀 Setting up clean Python Virtual Environment for BL4S Observability Suite..."
cd /Users/kayrayavuz/Desktop/DATA/

python3 -m venv kafka_env
source kafka_env/bin/activate

echo "📦 Installing required packages (kafka-python, flask, flask-socketio, matplotlib, numpy, protobuf)..."
pip install --upgrade pip
pip install kafka-python flask flask-socketio matplotlib numpy protobuf

echo "✅ Environment ready!"
echo "To start the Live Web Explorer backend, run:"
echo "  source kafka_env/bin/activate"
echo "  python bl4s_event_explorer_server.py"
echo "  (Open http://localhost:5050 in your browser)"
