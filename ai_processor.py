import os
import base64
import json
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4-vision-preview")

DISEASE_LIST = [
    "Acne", "Eczema", "Psoriasis", "Fungal Infection", "Vitiligo",
    "Dermatitis", "Conjunctivitis", "Oral Ulcer", "Rash", "Unknown"
]

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def stage1_validate_image(image_path):
    base64_image = encode_image(image_path)
    
    prompt = """You are a medical image validator.

Determine whether this image shows a visible human medical condition 
related to skin, eyes, or oral regions.

Respond strictly in JSON:

{
  "is_medical_image": true or false,
  "reason": "short explanation"
}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ],
        max_tokens=300
    )
    
    result = json.loads(response.choices[0].message.content)
    return result

def stage2_detect_disease(image_path):
    base64_image = encode_image(image_path)
    
    prompt = f"""You are a dermatology analysis assistant.

From the provided image, select the most likely visible condition 
from the following list:

{', '.join(DISEASE_LIST)}

Respond strictly in JSON:

{{
  "detected_disease": "Disease Name",
  "confidence_score": number between 0 and 1
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ],
        max_tokens=300
    )
    
    result = json.loads(response.choices[0].message.content)
    return result

def stage3_vitamin_inference(detected_disease):
    prompt = f"""You are a nutrition and medical reasoning assistant.

Based on the detected disease: {detected_disease}

Provide:

1. Possible associated vitamin deficiencies
2. Brief reasoning
3. Recommended food sources for each vitamin

Respond strictly in JSON format:

{{
  "vitamin_deficiencies": [
    {{
      "vitamin": "Vitamin Name",
      "reason": "short explanation",
      "recommended_foods": ["Food 1", "Food 2", "Food 3"]
    }}
  ]
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    
    result = json.loads(response.choices[0].message.content)
    return result

def process_image(image_path):
    validation = stage1_validate_image(image_path)
    if not validation.get("is_medical_image"):
        return {"error": "Uploaded image is not medically relevant.", "reason": validation.get("reason")}
    
    disease_result = stage2_detect_disease(image_path)
    if disease_result.get("confidence_score", 0) < 0.6:
        return {"error": "Unable to determine condition with sufficient confidence."}
    
    vitamin_result = stage3_vitamin_inference(disease_result["detected_disease"])
    
    return {
        "detected_disease": disease_result["detected_disease"],
        "confidence_score": disease_result["confidence_score"],
        "vitamin_deficiencies": vitamin_result["vitamin_deficiencies"]
    }
