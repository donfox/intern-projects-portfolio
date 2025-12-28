"""
Comprehensive Test Suite for Provider Vault AI Engine

Testing Strategies for Non-Deterministic AI Responses:
1. Structure Testing - Validate response format and data types
2. Semantic Testing - Check for relevant keywords and concepts
3. Business Logic Testing - Verify rules and constraints
4. Mock Testing - Fast unit tests without API calls
5. Consistency Testing - Validate expected patterns

Based on patterns from "Common Sense Guide to AI Engineering"
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

# Import functions to test
from ai_engine import (
    generate_specialty_description,
    suggest_related_specialties,
    analyze_provider_distribution,
    recommend_provider_by_symptoms,
    semantic_search_providers,
    faq_chatbot
)


# ============================================
# UNIT TESTS (Fast - Use Mocks)
# ============================================

@pytest.mark.unit
def test_specialty_description_structure_with_mock():
    """Test response structure without calling OpenAI API"""
    
    # Mock the OpenAI client response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Cardiology is the medical specialty focused on heart health. Cardiologists diagnose and treat conditions like heart disease, high blood pressure, and arrhythmias. You might need a cardiologist if you experience chest pain, shortness of breath, or have risk factors for heart disease."
    
    with patch('ai_engine.client.chat.completions.create', return_value=mock_response):
        result = generate_specialty_description("Cardiology")
        
        # Structure tests
        assert isinstance(result, str)
        assert len(result) > 50
        assert len(result) < 2000
        
        # Semantic tests - should mention relevant concepts
        result_lower = result.lower()
        assert any(word in result_lower for word in ['heart', 'cardiac', 'cardio'])


@pytest.mark.unit
def test_related_specialties_parsing():
    """Test that we correctly parse AI responses into structured data"""
    
    # Mock response in expected format
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = """1. Cardiac Surgery: Performs surgical procedures for heart conditions that cardiologists diagnose.
2. Vascular Surgery: Treats blood vessel conditions that often relate to heart health.
3. Internal Medicine: Provides primary care and often refers patients to cardiologists."""
    
    with patch('ai_engine.client.chat.completions.create', return_value=mock_response):
        result = suggest_related_specialties("Cardiology", count=3)
        
        # Structure tests
        assert isinstance(result, list)
        assert len(result) == 3
        
        # Each item should have correct structure
        for item in result:
            assert 'specialty' in item
            assert 'reason' in item
            assert isinstance(item['specialty'], str)
            assert isinstance(item['reason'], str)
            assert len(item['specialty']) > 0
            assert len(item['reason']) > 10


@pytest.mark.unit
def test_symptom_recommendation_parsing():
    """Test parsing of symptom recommendation responses"""
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = """SPECIALTIES: Emergency Medicine, Cardiology
REASONING: Chest pain and difficulty breathing could indicate a heart attack or other cardiac emergency.
URGENCY: emergency
EMERGENCY_ACTION: Call 911 immediately. Do not drive yourself. These symptoms require immediate medical evaluation."""
    
    with patch('ai_engine.client.chat.completions.create', return_value=mock_response):
        result = recommend_provider_by_symptoms("chest pain, can't breathe")
        
        # Structure tests
        assert isinstance(result, dict)
        assert 'recommended_specialties' in result
        assert 'reasoning' in result
        assert 'urgency_level' in result
        assert 'emergency_action' in result
        assert 'disclaimer' in result
        
        # Business logic tests
        assert isinstance(result['recommended_specialties'], list)
        assert len(result['recommended_specialties']) > 0
        assert result['urgency_level'] in ['low', 'medium', 'high', 'emergency']


@pytest.mark.unit
def test_semantic_search_parsing():
    """Test semantic search response parsing"""
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = """INTENT: Patient seeking help for memory-related issues
KEY_TERMS: memory, cognitive, elderly, dementia
SPECIALTIES: Neurology, Geriatrics, Psychiatry"""
    
    with patch('ai_engine.client.chat.completions.create', return_value=mock_response):
        with patch('ai_engine.db_client.get_providers_by_specialty', return_value=[]):
            result = semantic_search_providers("memory problems")
            
            # Structure tests
            assert isinstance(result, dict)
            assert 'understood_intent' in result
            assert 'search_terms' in result
            assert 'recommended_specialties' in result
            assert 'providers' in result
            assert 'total_found' in result
            
            # Type tests
            assert isinstance(result['search_terms'], list)
            assert isinstance(result['recommended_specialties'], list)
            assert isinstance(result['providers'], list)
            assert isinstance(result['total_found'], int)


@pytest.mark.unit
def test_faq_chatbot_structure_with_mock():
    """Test FAQ chatbot response structure"""
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "We have 8 cardiologists in our network across multiple states."
    
    mock_followup = Mock()
    mock_followup.choices = [Mock()]
    mock_followup.choices[0].message.content = """- Where are the cardiologists located?
- What other specialties do you have?
- Can you show me providers in Texas?"""
    
    with patch('ai_engine.client.chat.completions.create', side_effect=[mock_response, mock_followup]):
        with patch('ai_engine.db_client.test_connection', return_value={'total_providers': 60, 'total_specialties': 16, 'total_states': 15}):
            with patch('ai_engine.db_client.get_all_specialties', return_value=['Cardiology', 'Neurology']):
                result = faq_chatbot("How many cardiologists do you have?")
                
                # Structure tests
                assert isinstance(result, dict)
                assert 'answer' in result
                assert 'data_retrieved' in result
                assert 'follow_up_suggestions' in result
                assert 'conversation_history' in result
                
                # Type tests
                assert isinstance(result['answer'], str)
                assert isinstance(result['data_retrieved'], dict)
                assert isinstance(result['follow_up_suggestions'], list)
                assert isinstance(result['conversation_history'], list)
                
                # Content tests
                assert len(result['answer']) > 10
                assert len(result['follow_up_suggestions']) <= 3


# ============================================
# BUSINESS LOGIC TESTS (No API calls needed)
# ============================================

@pytest.mark.unit
def test_urgency_classification_logic():
    """Test that urgency levels follow expected patterns"""
    
    # Emergency symptoms should trigger high/emergency
    mock_emergency = Mock()
    mock_emergency.choices = [Mock()]
    mock_emergency.choices[0].message.content = """SPECIALTIES: Emergency Medicine
REASONING: Severe chest pain requires immediate evaluation.
URGENCY: emergency
EMERGENCY_ACTION: Call 911 immediately."""
    
    with patch('ai_engine.client.chat.completions.create', return_value=mock_emergency):
        result = recommend_provider_by_symptoms("crushing chest pain")
        assert result['urgency_level'] in ['high', 'emergency']
        assert result['emergency_action'] is not None
    
    # Minor symptoms should trigger low/medium
    mock_minor = Mock()
    mock_minor.choices = [Mock()]
    mock_minor.choices[0].message.content = """SPECIALTIES: Primary Care
REASONING: Minor cut can be handled by primary care.
URGENCY: low
EMERGENCY_ACTION: N/A"""
    
    with patch('ai_engine.client.chat.completions.create', return_value=mock_minor):
        result = recommend_provider_by_symptoms("small paper cut")
        assert result['urgency_level'] in ['low', 'medium']


@pytest.mark.unit
def test_faq_conversation_history_management():
    """Test that conversation history is properly maintained"""
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test response"
    
    mock_followup = Mock()
    mock_followup.choices = [Mock()]
    mock_followup.choices[0].message.content = "- Question 1?"
    
    with patch('ai_engine.client.chat.completions.create', side_effect=[mock_response, mock_followup]):
        with patch('ai_engine.db_client.test_connection', return_value={'total_providers': 60, 'total_specialties': 16, 'total_states': 15}):
            with patch('ai_engine.db_client.get_all_specialties', return_value=['Cardiology']):
                
                # First turn
                result1 = faq_chatbot("Question 1")
                history1 = result1['conversation_history']
                
                assert len(history1) == 2  # user + assistant
                assert history1[0]['role'] == 'user'
                assert history1[1]['role'] == 'assistant'
                
                # Mock second turn
                result2 = faq_chatbot("Question 2", conversation_history=history1)
                history2 = result2['conversation_history']
                
                assert len(history2) == 4  # 2 previous + 2 new


# ============================================
# INTEGRATION TESTS (Real API - Slow, Costs Money)
# ============================================

@pytest.mark.integration
@pytest.mark.slow
def test_specialty_description_real_api():
    """Integration test with real OpenAI API call"""
    result = generate_specialty_description("Cardiology")
    
    # Structure tests
    assert isinstance(result, str)
    assert 50 < len(result) < 2000
    
    # Semantic tests - should contain relevant medical concepts
    result_lower = result.lower()
    heart_terms = ['heart', 'cardiac', 'cardio', 'cardiovascular']
    assert any(term in result_lower for term in heart_terms), \
        f"Expected heart-related terms, got: {result[:100]}..."
    
    # Quality tests
    assert not result.startswith("Error"), "API call should not error"
    assert "cardiolog" in result_lower, "Should mention the specialty name"


@pytest.mark.integration
@pytest.mark.slow
def test_related_specialties_real_api():
    """Test that related specialties are medically relevant"""
    result = suggest_related_specialties("Cardiology", count=3)
    
    # Structure tests
    assert isinstance(result, list)
    assert len(result) == 3
    
    # Each specialty should be medically related
    specialties = [item['specialty'].lower() for item in result]
    
    # Should include medically relevant specialties
    relevant_specialties = [
        'cardiac', 'vascular', 'surgery', 'internal medicine',
        'pulmonology', 'endocrinology', 'nephrology'
    ]
    
    # At least one should match
    found_relevant = any(
        any(rel in spec for rel in relevant_specialties)
        for spec in specialties
    )
    assert found_relevant, f"Expected relevant specialties, got: {specialties}"


@pytest.mark.integration
@pytest.mark.slow
def test_symptom_emergency_detection_real_api():
    """Test that emergency symptoms are properly detected"""
    
    # Test emergency symptoms
    emergency_result = recommend_provider_by_symptoms(
        "crushing chest pain, left arm numb, trouble breathing"
    )
    
    assert emergency_result['urgency_level'] in ['high', 'emergency'], \
        f"Emergency symptoms should trigger high/emergency, got: {emergency_result['urgency_level']}"
    assert emergency_result['emergency_action'] is not None, \
        "Emergency symptoms should include action instructions"
    assert '911' in emergency_result['emergency_action'].lower() or \
           'emergency' in emergency_result['emergency_action'].lower(), \
        "Emergency action should mention calling 911 or emergency services"
    
    # Test minor symptoms
    minor_result = recommend_provider_by_symptoms("small paper cut on finger")
    
    assert minor_result['urgency_level'] in ['low', 'medium'], \
        f"Minor symptoms should be low/medium, got: {minor_result['urgency_level']}"


@pytest.mark.integration
@pytest.mark.slow
def test_semantic_search_intent_understanding_real_api():
    """Test that AI correctly understands search intent"""
    
    # Test memory-related search
    memory_result = semantic_search_providers("doctor for memory problems")
    
    specialties_lower = [s.lower() for s in memory_result['recommended_specialties']]
    cognitive_specialties = ['neurology', 'neurologist', 'psychiatry', 
                            'geriatrics', 'psychology', 'cognitive']
    
    # Should identify at least one cognitive specialty
    found_cognitive = any(
        any(cog in spec for cog in cognitive_specialties)
        for spec in specialties_lower
    )
    assert found_cognitive, \
        f"Memory problems should map to cognitive specialties, got: {specialties_lower}"
    
    # Test orthopedic search
    knee_result = semantic_search_providers("knee pain from running")
    
    specialties_lower = [s.lower() for s in knee_result['recommended_specialties']]
    ortho_specialties = ['orthopedic', 'orthopaedic', 'sports medicine', 
                        'physical medicine', 'rehabilitation']
    
    found_ortho = any(
        any(orth in spec for orth in ortho_specialties)
        for spec in specialties_lower
    )
    assert found_ortho, \
        f"Knee pain should map to orthopedic specialties, got: {specialties_lower}"


@pytest.mark.integration
@pytest.mark.slow
def test_faq_chatbot_real_api():
    """Test FAQ chatbot with real API calls"""
    
    # Test basic question
    result = faq_chatbot("How many providers do you have?")
    
    # Structure tests
    assert isinstance(result['answer'], str)
    assert len(result['answer']) > 20
    assert 'data_retrieved' in result
    assert 'network_stats' in result['data_retrieved']
    
    # Should mention a number
    import re
    numbers = re.findall(r'\d+', result['answer'])
    assert len(numbers) > 0, "Answer should contain numbers about provider count"
    
    # Test conversation context
    result2 = faq_chatbot(
        "What about in Texas?",
        conversation_history=result['conversation_history']
    )
    
    assert 'texas' in result2['answer'].lower() or 'tx' in result2['answer'].lower(), \
        "Follow-up should reference Texas"


# ============================================
# CONSISTENCY TESTS
# ============================================

@pytest.mark.integration
@pytest.mark.slow
def test_specialty_description_consistency():
    """Test that multiple calls produce consistent structure and quality"""
    
    results = []
    for _ in range(3):
        result = generate_specialty_description("Cardiology")
        results.append(result)
    
    # All should be valid strings
    assert all(isinstance(r, str) for r in results)
    
    # All should be reasonable length
    assert all(50 < len(r) < 2000 for r in results)
    
    # All should mention heart-related terms
    assert all(
        any(term in r.lower() for term in ['heart', 'cardiac', 'cardio'])
        for r in results
    ), "All responses should mention heart-related terms"
    
    # Should not be identical (showing temperature > 0)
    assert len(set(results)) > 1, "Responses should vary slightly"


@pytest.mark.integration
@pytest.mark.slow
def test_urgency_consistency():
    """Test that urgency classification is consistent across calls"""
    
    # Test same symptoms multiple times
    results = []
    for _ in range(3):
        result = recommend_provider_by_symptoms("chest pain and shortness of breath")
        results.append(result['urgency_level'])
    
    # All should be high or emergency
    assert all(level in ['high', 'emergency'] for level in results), \
        f"Chest pain should consistently be high/emergency, got: {results}"


# ============================================
# ERROR HANDLING TESTS
# ============================================

@pytest.mark.unit
def test_api_error_handling():
    """Test graceful handling of API errors"""
    
    # Mock an API error
    with patch('ai_engine.client.chat.completions.create', side_effect=Exception("API Error")):
        result = generate_specialty_description("Cardiology")
        
        # Should return error message, not raise exception
        assert isinstance(result, str)
        assert "Error" in result


@pytest.mark.unit
def test_invalid_specialty_handling():
    """Test handling of invalid specialty names"""
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "I'm not familiar with that specialty."
    
    with patch('ai_engine.client.chat.completions.create', return_value=mock_response):
        result = generate_specialty_description("XyzInvalidSpecialty123")
        
        # Should still return a string response
        assert isinstance(result, str)


# ============================================
# PROPERTY-BASED TESTS
# ============================================

@pytest.mark.unit
def test_all_functions_return_expected_types():
    """Property test: All functions should return their documented types"""
    
    # Mock all API calls
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test response"
    
    with patch('ai_engine.client.chat.completions.create', return_value=mock_response):
        with patch('ai_engine.db_client.get_providers_by_specialty', return_value=[]):
            with patch('ai_engine.db_client.test_connection', return_value={}):
                with patch('ai_engine.db_client.get_all_specialties', return_value=[]):
                    
                    # Test return types
                    desc = generate_specialty_description("Test")
                    assert isinstance(desc, str)
                    
                    related = suggest_related_specialties("Test")
                    assert isinstance(related, list)
                    
                    analysis = analyze_provider_distribution([])
                    assert isinstance(analysis, str)
                    
                    symptoms = recommend_provider_by_symptoms("test")
                    assert isinstance(symptoms, dict)
                    
                    search = semantic_search_providers("test")
                    assert isinstance(search, dict)
                    
                    faq = faq_chatbot("test")
                    assert isinstance(faq, dict)


if __name__ == "__main__":
    print("🧪 Provider Vault AI Engine Test Suite")
    print("=" * 70)
    print("\nTest Categories:")
    print("  • Unit Tests (fast, mocked) - marked with @pytest.mark.unit")
    print("  • Integration Tests (slow, real API) - marked with @pytest.mark.integration")
    print("\nRun with:")
    print("  pytest -v                    # All tests")
    print("  pytest -m unit -v            # Fast unit tests only")
    print("  pytest -m integration -v     # Integration tests only")
    print("  pytest --cov -v              # With coverage report")
