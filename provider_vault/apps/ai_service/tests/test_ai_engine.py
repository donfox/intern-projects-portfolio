# tests/test_ai_engine.py

import pytest
from ai_engine import (
    generate_specialty_description,
    suggest_related_specialties,
    analyze_provider_distribution,
    recommend_provider_by_symptoms,
    semantic_search_providers
)

# ============================================
# FAST TESTS (Run every time - use mocks)
# ============================================

@pytest.mark.unit
def test_specialty_description_structure():
    """Test without calling API - mock the response"""
    # TODO: Add mock
    pass

# ============================================
# SLOW TESTS (Run occasionally - real API)
# ============================================

@pytest.mark.integration
@pytest.mark.slow
def test_specialty_description_real_api():
    """Integration test with real OpenAI call"""
    result = generate_specialty_description("Cardiology")
    
    # Structural tests
    assert isinstance(result, str)
    assert 50 < len(result) < 2000
    assert "heart" in result.lower() or "cardiac" in result.lower()

@pytest.mark.integration
@pytest.mark.slow
def test_symptom_emergency_detection():
    """Test that emergency symptoms are flagged correctly"""
    
    # Critical symptoms
    result = recommend_provider_by_symptoms("crushing chest pain, trouble breathing")
    assert result['urgency_level'] in ['high', 'emergency']
    assert result['emergency_action'] is not None
    
    # Minor symptoms
    result = recommend_provider_by_symptoms("paper cut on finger")
    assert result['urgency_level'] in ['low', 'medium']

@pytest.mark.integration
@pytest.mark.slow  
def test_semantic_search_intent_understanding():
    """Test that AI understands natural language queries"""
    result = semantic_search_providers("doctor for memory problems")
    
    # Should identify cognitive-related specialties
    specialties_lower = [s.lower() for s in result['recommended_specialties']]
    cognitive_specialties = ['neurology', 'psychiatry', 'geriatrics', 'psychology']
    
    # At least one should match
    assert any(spec in cognitive_specialties for spec in specialties_lower)