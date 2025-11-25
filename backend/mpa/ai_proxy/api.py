import os
import google.generativeai as genai
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

# --- Gemini Proxy Configuration ---
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("ADVERTENCIA: La variable de entorno GOOGLE_API_KEY no está configurada. El proxy de Gemini no funcionará.")

class GeminiProxyRequest(BaseModel):
    prompt: str

router = APIRouter(tags=["MPA - AI Proxy"])

@router.post("/proxy/gemini")
async def gemini_proxy(request: GeminiProxyRequest = Body(...)):
    """
    Secure proxy endpoint to interact with the Gemini API.
    The API key is handled on the server-side.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="El servicio de IA no está configurado en el servidor.")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(request.prompt)
        return {"text": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al contactar el servicio de IA: {str(e)}")
