from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import os
import google.generativeai as genai

router = APIRouter()

# Configure the Google AI API key
genai.configure(api_key=os.getenv("GOOGLE_AI_API_KEY"))

class PromptSuggestionRequest(BaseModel):
    prompt: str

class PromptSuggestionResponse(BaseModel):
    improved_prompt: str
    suggestions: List[str]
    tags: List[str]

@router.post("/suggestions", response_model=PromptSuggestionResponse)
async def get_prompt_suggestions(request: PromptSuggestionRequest):
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create the prompt for the AI
        prompt_text = f"""You are an expert prompt engineer. Please improve the following prompt and provide suggestions:
        
        Original Prompt: "{request.prompt}"
        
        Please respond in the following JSON format:
        {{
          "improved_prompt": "The improved version of the prompt",
          "suggestions": [
            "Suggestion 1 for improvement",
            "Suggestion 2 for improvement"
          ],
          "tags": ["tag1", "tag2", "tag3"]
        }}"""
        
        # Generate content
        response = model.generate_content(prompt_text)
        
        # Parse the response
        try:
            import json
            # Extract JSON from the response text
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]  # Remove markdown code block
            
            result = json.loads(response_text)
            
            return {
                "improved_prompt": result.get("improved_prompt", request.prompt),
                "suggestions": result.get("suggestions", []),
                "tags": result.get("tags", [])
            }
        except (json.JSONDecodeError, AttributeError) as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse AI response: {str(e)}. Response: {response_text}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting AI suggestions: {str(e)}"
        )
