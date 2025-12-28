"""
FastAPI HTTP Wrapper for Provider Vault AI Service

REST API endpoints for all AI functions.
Prepares the service for Phoenix web integration.

Run with: uvicorn api:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import ai_engine
import db_client

# Initialize FastAPI app
app = FastAPI(
    title="Provider Vault AI Service",
    description="AI-powered medical provider intelligence API",
    version="2.0.0"
)


# ============================================
# Request/Response Models
# ============================================

class SpecialtyDescriptionRequest(BaseModel):
    specialty: str = Field(..., example="Cardiology")

class SpecialtyDescriptionResponse(BaseModel):
    specialty: str
    description: str

class RelatedSpecialtiesRequest(BaseModel):
    specialty: str = Field(..., example="Cardiology")
    count: int = Field(default=3, ge=1, le=10)

class RelatedSpecialty(BaseModel):
    specialty: str
    reason: str

class RelatedSpecialtiesResponse(BaseModel):
    specialty: str
    related_specialties: List[RelatedSpecialty]

class ProviderAnalysisRequest(BaseModel):
    specialty: str = Field(..., example="Cardiology")
    limit: int = Field(default=20, ge=1, le=100)

class ProviderAnalysisResponse(BaseModel):
    specialty: str
    provider_count: int
    analysis: str

class SymptomRecommendationRequest(BaseModel):
    symptoms: str = Field(..., example="chest pain, shortness of breath")
    location_state: Optional[str] = Field(None, example="TX")

class SymptomRecommendationResponse(BaseModel):
    symptoms: str
    recommended_specialties: List[str]
    reasoning: str
    urgency_level: str
    emergency_action: Optional[str]
    disclaimer: str
    available_providers: List[dict] = []

class SemanticSearchRequest(BaseModel):
    query: str = Field(..., example="doctor for memory problems")
    limit: int = Field(default=10, ge=1, le=50)

class SemanticSearchResponse(BaseModel):
    query: str
    understood_intent: str
    search_terms: List[str]
    recommended_specialties: List[str]
    total_found: int
    providers: List[dict]

class Message(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str

class FAQRequest(BaseModel):
    question: str = Field(..., example="How many providers do you have in Texas?")
    conversation_history: Optional[List[Message]] = Field(default=None, example=None)

class FAQResponse(BaseModel):
    answer: str
    data_retrieved: dict
    follow_up_suggestions: List[str]
    conversation_history: List[dict]


# ============================================
# Health Check Endpoint
# ============================================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Provider Vault AI Service",
        "version": "2.0.0",
        "endpoints": [
            "/docs",
            "/api/specialty/describe",
            "/api/specialty/related",
            "/api/providers/analyze",
            "/api/symptoms/recommend",
            "/api/search",
            "/api/faq"
        ]
    }

@app.get("/health")
def health_check():
    """Detailed health check with database status"""
    try:
        db_stats = db_client.test_connection()
        return {
            "status": "healthy",
            "database": "connected",
            "providers": db_stats['total_providers'],
            "specialties": db_stats['total_specialties']
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")


# ============================================
# AI Function Endpoints
# ============================================

@app.post("/api/specialty/describe", response_model=SpecialtyDescriptionResponse)
def describe_specialty(request: SpecialtyDescriptionRequest):
    """
    Generate a patient-friendly description of a medical specialty.
    
    Returns:
    - specialty: The specialty name
    - description: Patient-friendly explanation
    """
    try:
        description = ai_engine.generate_specialty_description(request.specialty)
        
        if description.startswith("Error"):
            raise HTTPException(status_code=500, detail=description)
        
        return {
            "specialty": request.specialty,
            "description": description
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/specialty/related", response_model=RelatedSpecialtiesResponse)
def get_related_specialties(request: RelatedSpecialtiesRequest):
    """
    Get related medical specialties for referral purposes.
    
    Returns:
    - specialty: The original specialty
    - related_specialties: List of related specialties with reasons
    """
    try:
        related = ai_engine.suggest_related_specialties(request.specialty, request.count)
        
        return {
            "specialty": request.specialty,
            "related_specialties": related
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/providers/analyze", response_model=ProviderAnalysisResponse)
def analyze_providers(request: ProviderAnalysisRequest):
    """
    Analyze provider distribution patterns for a specialty.
    
    Returns:
    - specialty: The specialty analyzed
    - provider_count: Number of providers analyzed
    - analysis: AI-generated insights and recommendations
    """
    try:
        # Fetch providers from database
        providers = db_client.get_providers_by_specialty(request.specialty, request.limit)
        
        if not providers:
            raise HTTPException(status_code=404, detail=f"No providers found for specialty: {request.specialty}")
        
        # Generate analysis
        analysis = ai_engine.analyze_provider_distribution(providers)
        
        return {
            "specialty": request.specialty,
            "provider_count": len(providers),
            "analysis": analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/symptoms/recommend", response_model=SymptomRecommendationResponse)
def recommend_by_symptoms(request: SymptomRecommendationRequest):
    """
    Recommend medical specialties based on patient symptoms.
    
    Includes urgency assessment and emergency detection.
    
    Returns:
    - symptoms: Original symptom description
    - recommended_specialties: Suggested specialties (priority order)
    - reasoning: Explanation for recommendations
    - urgency_level: low, medium, high, or emergency
    - emergency_action: Emergency instructions (if applicable)
    - disclaimer: Medical disclaimer
    - available_providers: Matching providers (if location provided)
    """
    try:
        recommendation = ai_engine.recommend_provider_by_symptoms(
            request.symptoms,
            request.location_state
        )
        
        return {
            "symptoms": request.symptoms,
            **recommendation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search", response_model=SemanticSearchResponse)
def semantic_search(request: SemanticSearchRequest):
    """
    Natural language search for providers.
    
    Understands intent from plain English queries like:
    - "doctor for memory problems"
    - "knee pain from running"
    
    Returns:
    - query: Original search query
    - understood_intent: AI's interpretation
    - search_terms: Extracted medical concepts
    - recommended_specialties: Relevant specialties
    - total_found: Number of matching providers
    - providers: Matching provider records
    """
    try:
        results = ai_engine.semantic_search_providers(request.query, request.limit)
        
        return {
            "query": request.query,
            **results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/faq", response_model=FAQResponse)
def faq_chatbot(request: FAQRequest):
    """
    FAQ chatbot for conversational questions about the provider network.
    
    Supports multi-turn conversations with context maintenance.
    
    Examples:
    - "How many cardiologists do you have?"
    - "What specialties are available?"
    - "Do you have any providers in Texas?"
    
    Returns:
    - answer: Conversational response to the question
    - data_retrieved: Relevant database information used
    - follow_up_suggestions: Suggested next questions
    - conversation_history: Updated history for next turn
    """
    try:
        # Convert Pydantic models to dicts for ai_engine
        history = None
        if request.conversation_history:
            history = [{"role": msg.role, "content": msg.content} 
                      for msg in request.conversation_history]
        
        result = ai_engine.faq_chatbot(request.question, history)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Utility Endpoints
# ============================================

@app.get("/api/specialties")
def list_specialties():
    """Get list of all available specialties in the database"""
    try:
        specialties = db_client.get_all_specialties()
        return {
            "count": len(specialties),
            "specialties": specialties
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
def get_stats():
    """Get database statistics"""
    try:
        stats = db_client.test_connection()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Run Instructions
# ============================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Provider Vault AI Service...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Interactive API: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000)
