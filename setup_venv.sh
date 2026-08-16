#!/bin/bash

echo "🚀 Setting up clean Python Virtual Environment for Live Viewer..."
cd /Users/kayrayavuz/Desktop/DATA/

python3 -m venv kafka_env
source kafka_env/bin/activate

echo "📦 Installing required packages (kafka-python, matplotlib, numpy)..."
pip install kafka-python matplotlib numpy

echo "✅ Environment ready! To run the viewer, use:"
echo "source kafka_env/bin/activate"
echo "python live_kafka_viewer.py"
