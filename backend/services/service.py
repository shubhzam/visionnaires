import base64
import json
import os
import tempfile
import onnxruntime_genai as og
from schemas import HazardVerdict


class VLMService:
    """Vision Language Model service for hazard detection"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.processor = None
        self.tokenizer = None
        
    def load_model(self):
        """Load the Phi-3.5 Vision model into memory"""
        print(f"Loading VLM from {self.model_path}...")
        self.model = og.Model(self.model_path)
        self.processor = self.model.create_multimodal_processor()
        self.tokenizer = self.model.create_tokenizer()
        print("VLM loaded successfully.")
        
    def is_ready(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None
    
    def analyze_hazard(self, image_b64: str, suspected_label: str) -> HazardVerdict:
        """
        Run VLM inference on base64 image
        
        Args:
            image_b64: Base64 encoded image string
            suspected_label: Suspected obstacle type from edge detector
            
        Returns:
            HazardVerdict with analysis results
        """
        try:
            # Decode base64 to bytes
            image_bytes = base64.b64decode(image_b64)
            
            # Save to temp file (ONNX Runtime requirement)
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_img:
                temp_img.write(image_bytes)
                temp_path = temp_img.name
            
            # Load image into GenAI container
            og_image = og.Images.open(temp_path)
            
            # Construct Phi-3-Vision prompt
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
            
            # Process inputs (fuse image + text)
            inputs = self.processor(prompt, images=og_image)
            
            # Configure generation
            params = og.GeneratorParams(self.model)
            params.set_inputs(inputs)
            params.set_search_options(max_length=256)
            
            # Run inference
            generator = og.Generator(self.model, params)
            generated_text = ""
            
            while not generator.is_done():
                generator.compute_logits()
                generator.generate_next_token()
                new_token = generator.get_next_tokens()[0]
                word = self.tokenizer.decode(new_token)
                generated_text += word
            
            # Cleanup temp file
            try:
                os.remove(temp_path)
            except:
                pass
            
            # Extract JSON from response
            start = generated_text.find('{')
            end = generated_text.rfind('}') + 1
            
            if start != -1 and end != -1:
                json_str = generated_text[start:end]
                result = json.loads(json_str)
                return HazardVerdict(**result)
            else:
                # Fallback if model fails to output valid JSON
                print(f"Model output invalid format: {generated_text}")
                return HazardVerdict(
                    hazard_detected=True,
                    type="unknown",
                    severity="medium",
                    action="Proceed with caution",
                    description="Object detected but AI format failed"
                )
                
        except Exception as e:
            print(f"VLM Error: {e}")
            return HazardVerdict(
                hazard_detected=True,
                type="error",
                severity="low",
                action="Proceed with caution",
                description="AI error occurred"
            )


# Global service instance (singleton pattern)
vlm_service = None

def get_vlm_service() -> VLMService:
    """Dependency injection for FastAPI"""
    return vlm_service

def initialize_vlm(model_path: str):
    """Initialize global VLM service"""
    global vlm_service
    vlm_service = VLMService(model_path)
    vlm_service.load_model()