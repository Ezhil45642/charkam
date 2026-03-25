import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

def generate_legal_response(query):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system_prompt = """You are Chakravyuha, a highly intelligent multilingual AI Legal Assistant designed for India.
You MUST analyze the language of the user's query and provide your response in the EXACT SAME LANGUAGE (e.g., if they speak Hindi, reply in Hindi; if Tamil, reply in Tamil, etc).
Provide your answer in strict JSON format exactly as follows, with no markdown code blocks:
{
  "law": "Applicable Indian Law/Section (translated)",
  "explanation": "Simple explanation of the legal situation (translated)",
  "steps": ["Step 1...", "Step 2..."]
}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            response_format={ "type": "json_object" }
        )
        
        result_str = response.choices[0].message.content
        result = json.loads(result_str)
        return {
            "law": result.get("law", "General Law"),
            "explanation": result.get("explanation", "Could not determine explanation."),
            "steps": result.get("steps", [])
        }
    except Exception as e:
        print(f"RAG Error: {e}")
        return {
            "law": "System Error",
            "explanation": f"Oops, I could not generate a response. Error: {e}",
            "steps": []
        }
