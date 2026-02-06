import asyncio
import websockets
import json
import base64
import io
import onnxruntime_genai as og
from PIL import Image

# CONFIGURATION
ORACLE_RELAY_URL = "wss://your-oracle-endpoint.com/relay"
MODEL_PATH = "./snapdragon_vlm_final/cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4"

print("Loading VLM Brain...")
model = og.Model(MODEL_PATH)
processor = model.create_multimodal_processor()
tokenizer = model.create_tokenizer()
print("Brain Ready. Connecting to Oracle Relay...")

async def run_worker():
    async with websockets.connect(ORACLE_RELAY_URL) as websocket:
        print("Connected to Network. Waiting for images...")
        
        # Identify ourselves as the "BRAIN" so Oracle knows where to route images
        await websocket.send(json.dumps({"role": "brain", "status": "ready"}))

        while True:
            # 1. Wait for data from Phone
            message = await websocket.recv()
            data = json.loads(message)
            
            # 2. Extract Data
            image_b64 = data.get("image")
            suspected_label = data.get("label")
            
            print(f"Received request: Check {suspected_label}...")

            # 3. Run Inference (The VLM)
            verdict = analyze_image(image_b64, suspected_label)
            
            # 4. Send Answer back to Oracle (who sends it to Phone)
            response = {
                "target": "phone",
                "ai_verdict": verdict
            }
            await websocket.send(json.dumps(response))
            print("Verdict sent.")

def analyze_image(b64_string, suspected_label):
    try:
        # 1. Decode Image from Base64
        image_bytes = base64.b64decode(b64_string)
        
        # NOTE: onnxruntime-genai currently prefers file paths for the C++ backend.
        # We save to a temp file for 100% stability.
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_img:
            temp_img.write(image_bytes)
            temp_path = temp_img.name

        # 2. Load Image into GenAI Container
        # The VLM expects a specific object type, not a raw PIL image
        og_image = og.Images.open(temp_path)

        # 3. Construct the Phi-3-Vision Prompt
        # The <|image_1|> tag tells the model where to "look"
        prompt = (
            f"<|user|>\n<|image_1|>\n"
            f"SYSTEM ROLE: You are a navigation assistant for a blind person. Your priority is SAFETY.\n"
            f"CONTEXT: An edge detector flagged a potential obstacle here, possibly a '{suspected_label}'.\n"
            f"TASK: 1. Verify if '{suspected_label}' is present. 2. Scan for any other immediate tripping hazards or blockers.\n"
            f"OUTPUT FORMAT: Return ONLY valid JSON. No conversational text.\n"
            f"JSON SCHEMA: {{\n"
            f"  \"hazard_detected\": boolean,\n"
            f"  \"type\": \"string (e.g. 'wet_floor', 'construction_barrier')\",\n"
            f"  \"severity\": \"string (low/medium/critical)\",\n"
            f"  \"action\": \"string (e.g. 'Stop', 'Slow down', 'Go around')\",\n"
            f"  \"description\": \"string (max 10 words, concise for TTS)\"\n"
            f"}}\n"
            f"<|end|>\n<|assistant|>\n"
        )

        # 4. Process Inputs (Fuse Image + Text)
        # 'processor' was created globally in your main script
        inputs = processor(prompt, images=og_image)

        # 5. Configure Generation
        params = og.GeneratorParams(model)
        params.set_inputs(inputs) # Passes the fused image/text tensors
        params.set_search_options(max_length=256) # Keep it short for speed

        # 6. Run Inference (The Brain Loop)
        generator = og.Generator(model, params)
        generated_text = ""

        while not generator.is_done():
            generator.compute_logits()
            generator.generate_next_token()
            
            # Decode the new token
            new_token = generator.get_next_tokens()[0]
            word = tokenizer.decode(new_token)
            generated_text += word

        # 7. Cleanup
        # Delete the temp file to keep the PC clean
        try:
            os.remove(temp_path)
        except:
            pass

        # 8. Post-Process (Extract JSON)
        # The model might output: "Sure! Here is the JSON: { ... }"
        # We need to extract just the { ... } part.
        start = generated_text.find('{')
        end = generated_text.rfind('}') + 1

        if start != -1 and end != -1:
            json_str = generated_text[start:end]
            return json.loads(json_str)
        else:
            # Fallback if model fails to output JSON
            print(f"Model Hallucinated format: {generated_text}")
            return {"hazard": True, "level": "medium", "desc": "Object detected but AI format failed."}

    except Exception as e:
        print(f"VLM Error: {e}")
        return {"hazard": True, "level": "low", "desc": "AI Error. Proceed with caution."}

if __name__ == "__main__":
    asyncio.run(run_worker())