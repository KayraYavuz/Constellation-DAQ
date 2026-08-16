import json
import time
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from kafka import KafkaConsumer

# Configuration
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'bl4s_events'
CHANNELS = 16  # Calorimeter channels (4x4 or 16 bars)

# Global variables to hold data
energy_histogram = np.zeros(CHANNELS)
data_lock = threading.Lock()
running = True

def consume_kafka_messages():
    """Background thread to consume messages from Kafka as fast as possible"""
    global energy_histogram, running
    
    print(f"Connecting to Kafka broker at {KAFKA_BROKER}...")
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset='latest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        print(f"Successfully connected to Kafka topic: {KAFKA_TOPIC}")
        print("Waiting for calorimeter events...")
        
        for message in consumer:
            if not running:
                break
                
            event = message.value
            
            # Expecting event format: {"ch": channel_id, "energy": energy_val, "timestamp": ts}
            ch = event.get('ch', -1)
            energy = event.get('energy', 0.0)
            
            if 0 <= ch < CHANNELS:
                with data_lock:
                    energy_histogram[ch] += energy
                    
    except Exception as e:
        print(f"Kafka Consumer Error: {e}")
        print("Make sure Kafka is running and the reverse SSH tunnel is active!")

def update_plot(frame):
    """Function called periodically by FuncAnimation to update the plot"""
    with data_lock:
        # Copy data so we don't hold the lock during plotting
        current_data = energy_histogram.copy()
        
    # Update bars
    for bar, val in zip(bars, current_data):
        bar.set_height(val)
        
    # Adjust y-axis limit dynamically
    max_val = np.max(current_data) if np.max(current_data) > 0 else 100
    ax.set_ylim(0, max_val * 1.1)
    
    # Calculate total energy and hit rate loosely
    total_e = np.sum(current_data)
    ax.set_title(f"🔴 LIVE Calorimeter Energy (Kafka Stream) | Total E: {total_e:.1f}", color='white', fontsize=14, pad=20)
    
    return bars

if __name__ == "__main__":
    plt.style.use('dark_background')
    
    # Setup Figure
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('#2d2d2d')
    
    channels = np.arange(CHANNELS)
    bars = ax.bar(channels, np.zeros(CHANNELS), color='#00ffcc', alpha=0.8, edgecolor='white')
    
    ax.set_xlabel('Calorimeter Channel ID', color='white', fontsize=12)
    ax.set_ylabel('Accumulated Energy (ADC counts)', color='white', fontsize=12)
    ax.set_xticks(channels)
    ax.tick_params(colors='white')
    ax.grid(True, axis='y', alpha=0.2, color='gray')
    
    # Start Kafka Consumer Thread
    consumer_thread = threading.Thread(target=consume_kafka_messages, daemon=True)
    consumer_thread.start()
    
    print("Starting Live Matplotlib Animation...")
    # Update plot every 100ms (10 FPS) to avoid freezing
    ani = FuncAnimation(fig, update_plot, interval=100, cache_frame_data=False)
    
    try:
        plt.show()
    except KeyboardInterrupt:
        pass
    finally:
        running = False
        print("Shutting down...")
