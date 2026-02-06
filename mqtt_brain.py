import time
import json
import base64
import io
import queue
import threading
import paho.mqtt.client as mqtt
import onnxruntime_genai as og
from PIL import Image
from main import analyze_image

# --- CONFIGURATION ---
BROKER_ADDRESS = "your-oracle-server-ip.com" # Ask Infra Lead
BROKER_PORT = 1883 # Or 8883 for SSL
TOPIC_INPUT = "blind_aid/camera/frame"
TOPIC_OUTPUT = "blind_aid/feedback/alert"

# --- GLOBAL SHARED QUEUE ---
# This separates the Networking (Fast) from the AI (Slow)
job_queue = queue.Queue(maxsize=1) # Dropping frames is better than lag

# --- 1. THE AI WORKER THREAD ---
def brain_loop():
    print("[Brain] Loading VLM Model...")
    # Load your model (Phi-3.5 Vision)
    model_path = "./snapdragon_vlm_final/cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4"
    model = og.Model(model_path)
    processor = model.create_multimodal_processor()
    tokenizer = model.create_tokenizer()
    print("[Brain] Model Loaded. Waiting for jobs...")

    while True:
        try:
            # Wait for an image from the MQTT thread
            payload = job_queue.get() 
            
            # Extract Data
            label = payload['label']
            image_b64 = payload['image']
            
            # Run Inference
            verdict = analyze_image(model, processor, tokenizer, image_b64, label)
            
            # Send Result back to MQTT thread to publish
            response_payload = json.dumps({
                "hazard": verdict["hazard"],
                "desc": verdict["desc"],
                "level": verdict["level"]
            })
            
            # Publish specifically to the feedback topic
            client.publish(TOPIC_OUTPUT, response_payload, qos=1)
            print(f"[Brain] Sent verdict: {verdict['level']}")
            
            job_queue.task_done()
            
        except Exception as e:
            print(f"[Brain] Error: {e}")

# (Reuse the analyze_image logic from previous answer here)
# def analyze_image(model, processor, tokenizer, b64_string, label):
#     # ... [Insert the VLM logic I gave you previously] ...
#     # Mock return for testing:
#     return {"hazard": True, "level": "critical", "desc": "Wet cement detected"}

# --- 2. THE MQTT NETWORK THREAD ---
def on_connect(client, userdata, flags, rc):
    print(f"[Net] Connected to Oracle MQTT (Code: {rc})")
    client.subscribe(TOPIC_INPUT)

def on_message(client, userdata, msg):
    # This function must be FAST (<10ms)
    try:
        payload = json.loads(msg.payload.decode())
        
        # Put in queue. If queue is full (Brain is busy), skip this frame.
        # This prevents "Lag Buildup" where the blind person gets alerts 
        # for obstacles they passed 5 seconds ago.
        if job_queue.empty():
            job_queue.put(payload)
        else:
            print("[Net] Brain busy, dropping frame (Good behavior)")
            
    except Exception as e:
        print(f"[Net] Bad message: {e}")

# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    # Start AI Thread
    t = threading.Thread(target=brain_loop)
    t.daemon = True
    t.start()

    # Start Network
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Optional: Username/Password if Infra Lead set it up
    # client.username_pw_set("user", "pass")

    print("[Net] Connecting to Broker...")
    client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
    
    # Blocking loop that handles network traffic automatically
    client.loop_forever()