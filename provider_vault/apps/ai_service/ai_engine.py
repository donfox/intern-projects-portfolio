"""
AI Engine for Provider Vault

Core AI functions using OpenAI API for provider-related intelligence.
Focus: Learning AI engineering and prompt engineering fundamentals.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import db_client

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')


def generate_specialty_description(specialty):
    """
    Generate a patient-friendly description of a medical specialty.
    
    This is your first AI function! It demonstrates:
    - Basic OpenAI API usage
    - Prompt engineering for clear, helpful responses
    - Practical application of AI for healthcare context
    
    Args:
        specialty (str): Medical specialty name (e.g., "Cardiology")
        
    Returns:
        str: Patient-friendly description of the specialty
    """
    
    prompt = f"""You are a helpful medical information assistant. 

Generate a clear, patient-friendly description of the medical specialty: {specialty}

Requirements:
- Write in simple, accessible language (8th grade reading level)
- 2-3 paragraphs maximum
- Explain what this type of doctor does
- Mention common conditions they treat
- Help patients understand when they might need this specialist
- Use a warm, reassuring tone

Do not include:
- Medical jargon without explanation
- Technical details about training/certification
- Promotional language"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful medical information assistant who explains healthcare topics in patient-friendly language."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Balanced creativity and consistency
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error generating description: {str(e)}"


def suggest_related_specialties(specialty, count=3):
    """
    Suggest related medical specialties for referral purposes.
    
    This demonstrates:
    - Structured output from AI
    - Medical knowledge application
    - Practical clinical workflow support
    
    Args:
        specialty (str): Medical specialty name
        count (int): Number of related specialties to suggest (default: 3)
        
    Returns:
        list[dict]: List of related specialties with reasons
            Format: [{"specialty": "...", "reason": "..."}, ...]
    """
    
    prompt = f"""You are a medical referral coordinator.

For the specialty "{specialty}", suggest {count} related medical specialties that commonly work together or receive referrals.

For each specialty, provide:
1. The specialty name
2. A brief reason why they often collaborate

Format your response as a simple list:
1. [Specialty Name]: [One sentence reason]
2. [Specialty Name]: [One sentence reason]
etc.

Focus on practical, common referral patterns in healthcare."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a medical referral coordinator with deep knowledge of healthcare specialties."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,  # Lower temperature for more consistent results
            max_tokens=250
        )
        
        # Parse the response into structured data
        content = response.choices[0].message.content.strip()
        suggestions = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering/bullets
                clean_line = line.lstrip('0123456789.-) ')
                if ':' in clean_line:
                    specialty_name, reason = clean_line.split(':', 1)
                    suggestions.append({
                        'specialty': specialty_name.strip(),
                        'reason': reason.strip()
                    })
        
        return suggestions[:count]  # Ensure we return exactly count items
        
    except Exception as e:
        return [{"specialty": "Error", "reason": str(e)}]


def analyze_provider_distribution(providers):
    """
    Analyze patterns in a list of providers and generate insights.
    
    This demonstrates:
    - AI analysis of structured data
    - Pattern recognition
    - Generating actionable insights
    
    Args:
        providers (list[dict]): List of provider records from database
        
    Returns:
        str: Analysis summary with insights
    """
    
    if not providers:
        return "No providers to analyze."
    
    # Prepare summary statistics
    total_count = len(providers)
    
    # Count by specialty
    specialty_counts = {}
    for p in providers:
        specialty = p.get('specialty', 'Unknown')
        specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1
    
    # Count by state
    state_counts = {}
    for p in providers:
        state = p.get('state', 'Unknown')
        state_counts[state] = state_counts.get(state, 0) + 1
    
    # Build context for AI
    context = f"""Provider Dataset Analysis:

Total Providers: {total_count}

Specialty Distribution:
{chr(10).join([f"  - {spec}: {count}" for spec, count in sorted(specialty_counts.items(), key=lambda x: x[1], reverse=True)])}

Geographic Distribution (by state):
{chr(10).join([f"  - {state}: {count}" for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True)])}"""

    prompt = f"""You are a healthcare network analyst.

Based on this provider data, generate a brief analysis (2-3 paragraphs) that includes:
1. Key patterns you observe
2. Potential gaps in coverage
3. One actionable recommendation

{context}

Focus on practical insights that would help a healthcare administrator."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a healthcare network analyst who identifies patterns and provides actionable insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=350
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error analyzing providers: {str(e)}"


def recommend_provider_by_symptoms(symptoms, location_state=None):
    """
    Recommend appropriate medical specialty based on patient symptoms.
    
    This demonstrates:
    - Medical reasoning with AI
    - Safety-conscious prompt engineering
    - Structured output with urgency assessment
    - Integration with real provider availability
    
    Args:
        symptoms (str): Patient-described symptoms (e.g., "chest pain, shortness of breath")
        location_state (str, optional): Two-letter state code to check provider availability
        
    Returns:
        dict: {
            'recommended_specialties': [list of specialties in priority order],
            'reasoning': str explaining recommendations,
            'urgency_level': 'low' | 'medium' | 'high' | 'emergency',
            'emergency_action': str or None (instructions if emergency),
            'disclaimer': str (medical disclaimer),
            'available_providers': [list of matching providers if location provided]
        }
    """
    
    prompt = f"""You are a medical triage assistant helping patients find appropriate care.

PATIENT SYMPTOMS: {symptoms}

Your task:
1. Recommend 2-3 medical specialties that could help (priority order)
2. Explain your reasoning
3. Assess urgency level: low, medium, high, or emergency
4. If emergency, provide specific emergency action

CRITICAL SAFETY RULES:
- If symptoms suggest life-threatening emergency (heart attack, stroke, severe bleeding, difficulty breathing), 
  set urgency to "emergency" and tell patient to call 911 immediately
- Always include appropriate disclaimers
- Be cautious but helpful

Format your response EXACTLY like this:

SPECIALTIES: [Specialty1], [Specialty2], [Specialty3]
REASONING: [Brief explanation of why these specialties]
URGENCY: [low|medium|high|emergency]
EMERGENCY_ACTION: [Call 911 immediately because... OR N/A if not emergency]

Examples:

Input: "paper cut on finger"
SPECIALTIES: Primary Care, Urgent Care
REASONING: Minor wound can be treated by primary care or urgent care for cleaning and possible bandaging.
URGENCY: low
EMERGENCY_ACTION: N/A

Input: "crushing chest pain, left arm numbness, shortness of breath"
SPECIALTIES: Emergency Medicine, Cardiology
REASONING: These are classic signs of a possible heart attack requiring immediate emergency evaluation.
URGENCY: emergency
EMERGENCY_ACTION: Call 911 immediately. Do not drive yourself. These symptoms suggest a possible heart attack."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a medical triage assistant focused on patient safety and appropriate care routing."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Low temperature for safety-critical responses
            max_tokens=300
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse structured response
        specialties = []
        reasoning = ""
        urgency = "medium"
        emergency_action = None
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('SPECIALTIES:'):
                spec_text = line.replace('SPECIALTIES:', '').strip()
                specialties = [s.strip() for s in spec_text.split(',')]
            elif line.startswith('REASONING:'):
                reasoning = line.replace('REASONING:', '').strip()
            elif line.startswith('URGENCY:'):
                urgency = line.replace('URGENCY:', '').strip().lower()
            elif line.startswith('EMERGENCY_ACTION:'):
                emergency_action = line.replace('EMERGENCY_ACTION:', '').strip()
        
        result = {
            'recommended_specialties': specialties,
            'reasoning': reasoning,
            'urgency_level': urgency,
            'emergency_action': emergency_action if emergency_action != "N/A" else None,
            'disclaimer': "⚠️ This is not medical advice. Always consult with a qualified healthcare provider for proper diagnosis and treatment.",
            'available_providers': []
        }
        
        # Look up providers if location provided
        if location_state and specialties:
            try:
                primary_specialty = specialties[0]
                providers = db_client.get_providers_by_state(location_state, limit=50)
                
                matching_providers = [
                    p for p in providers 
                    if p.get('specialty', '').lower() == primary_specialty.lower()
                ]
                
                result['available_providers'] = matching_providers[:5]
                result['location_checked'] = location_state
                
            except Exception as e:
                result['provider_search_error'] = str(e)
        
        return result
        
    except Exception as e:
        return {
            'error': f"Error processing symptoms: {str(e)}",
            'recommended_specialties': [],
            'reasoning': '',
            'urgency_level': 'unknown',
            'disclaimer': "⚠️ System error. Please consult a healthcare provider directly."
        }


def semantic_search_providers(query, limit=10):
    """
    Natural language search for providers.
    
    This demonstrates:
    - Intent understanding from natural language
    - Query expansion and synonym matching
    - Practical application of AI for search
    
    Args:
        query (str): Natural language query (e.g., "doctor for my elderly parent's memory issues")
        limit (int): Maximum number of results to return
        
    Returns:
        dict: {
            'understood_intent': str,
            'search_terms': [list of extracted terms],
            'recommended_specialties': [list of specialties],
            'providers': [list of matching providers],
            'total_found': int
        }
    """
    
    analysis_prompt = f"""You are a medical search assistant analyzing a patient's search query.

QUERY: "{query}"

Your task:
1. Understand what the patient is looking for
2. Extract key medical concepts, symptoms, or conditions mentioned
3. Identify 2-4 relevant medical specialties that could help
4. Consider synonyms and related terms (e.g., "memory problems" → dementia, Alzheimer's, cognitive decline)

Format your response EXACTLY like this:

INTENT: [One sentence describing what the patient needs]
KEY_TERMS: [term1], [term2], [term3]
SPECIALTIES: [Specialty1], [Specialty2], [Specialty3]

Examples:
- Query: "doctor for my knee pain from running"
  INTENT: Patient has knee pain related to running/sports activity
  KEY_TERMS: knee, pain, sports, orthopedic
  SPECIALTIES: Orthopedics, Sports Medicine, Physical Medicine

- Query: "someone to help with anxiety and stress"
  INTENT: Patient seeking mental health support for anxiety
  KEY_TERMS: anxiety, stress, mental health, therapy
  SPECIALTIES: Psychiatry, Clinical Psychology, Counseling"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical search assistant who understands patient needs and maps them to appropriate medical specialties."
                },
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.4,
            max_tokens=250
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse response
        intent = ""
        key_terms = []
        specialties = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('INTENT:'):
                intent = line.replace('INTENT:', '').strip()
            elif line.startswith('KEY_TERMS:'):
                terms_text = line.replace('KEY_TERMS:', '').strip()
                key_terms = [t.strip() for t in terms_text.split(',')]
            elif line.startswith('SPECIALTIES:'):
                spec_text = line.replace('SPECIALTIES:', '').strip()
                specialties = [s.strip() for s in spec_text.split(',')]
        
        # Search database for matching providers
        all_matches = []
        
        for specialty in specialties:
            try:
                providers = db_client.get_providers_by_specialty(specialty, limit=20)
                all_matches.extend(providers)
            except:
                pass  # Skip if specialty not found
        
        # Deduplicate providers
        seen_npis = set()
        unique_providers = []
        for p in all_matches:
            if p['npi'] not in seen_npis:
                seen_npis.add(p['npi'])
                unique_providers.append(p)
        
        return {
            'understood_intent': intent,
            'search_terms': key_terms,
            'recommended_specialties': specialties,
            'providers': unique_providers[:limit],
            'total_found': len(unique_providers)
        }
        
    except Exception as e:
        return {
            'error': f"Error in semantic search: {str(e)}",
            'understood_intent': '',
            'search_terms': [],
            'recommended_specialties': [],
            'providers': [],
            'total_found': 0
        }


def faq_chatbot(question, conversation_history=None):
    """
    Answer questions about the Provider Vault network using conversational AI.
    
    This demonstrates:
    - Conversational AI with context
    - RAG (Retrieval Augmented Generation) pattern
    - Dynamic knowledge retrieval from database
    - Multi-turn conversation handling
    
    Args:
        question (str): User's question about providers, specialties, or the network
        conversation_history (list[dict], optional): Previous messages in format:
            [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            
    Returns:
        dict: {
            'answer': str (conversational response),
            'data_retrieved': dict (relevant data from database, if any),
            'follow_up_suggestions': list[str] (suggested next questions),
            'conversation_history': list[dict] (updated history for next turn)
        }
    """
    
    if conversation_history is None:
        conversation_history = []
    
    # Retrieve relevant context from database based on question
    context_data = {}
    
    try:
        # Get network statistics
        stats = db_client.test_connection()
        context_data['network_stats'] = stats
        
        # Get specialty list
        specialties = db_client.get_all_specialties()
        context_data['available_specialties'] = specialties
        
        # Check if question mentions specific specialty
        question_lower = question.lower()
        for specialty in specialties:
            if specialty.lower() in question_lower:
                # Fetch providers for mentioned specialty
                providers = db_client.get_providers_by_specialty(specialty, limit=10)
                context_data['specialty_providers'] = {
                    'specialty': specialty,
                    'count': len(providers),
                    'sample_providers': providers[:3]
                }
                break
        
        # Get geographic distribution if question mentions location
        states = ['CA', 'TX', 'NY', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
        for state in states:
            if state.lower() in question_lower or f" {state} " in f" {question_lower} ":
                state_providers = db_client.get_providers_by_state(state, limit=50)
                context_data['state_data'] = {
                    'state': state,
                    'provider_count': len(state_providers)
                }
                break
                
    except Exception as e:
        context_data['error'] = f"Database query error: {str(e)}"
    
    # Build system prompt with retrieved context
    system_prompt = f"""You are a helpful assistant for Provider Vault, a medical provider network.

NETWORK INFORMATION:
- Total Providers: {context_data.get('network_stats', {}).get('total_providers', 'N/A')}
- Total Specialties: {context_data.get('network_stats', {}).get('total_specialties', 'N/A')}
- Coverage States: {context_data.get('network_stats', {}).get('total_states', 'N/A')}

AVAILABLE SPECIALTIES:
{', '.join(context_data.get('available_specialties', [])[:20])}...

Your role:
- Answer questions about our provider network
- Help users find providers by specialty or location
- Explain what different medical specialties do
- Provide helpful, accurate information
- Be conversational and friendly
- If you don't have specific data, say so honestly

Keep responses concise (2-3 paragraphs max) unless more detail is requested."""

    # Add specialty-specific context if found
    if 'specialty_providers' in context_data:
        sp = context_data['specialty_providers']
        system_prompt += f"\n\nRELEVANT DATA FOR THIS QUESTION:\n"
        system_prompt += f"We have {sp['count']} {sp['specialty']} providers in our network.\n"
        if sp['sample_providers']:
            system_prompt += f"Sample providers: "
            system_prompt += ", ".join([f"Dr. {p['name']} ({p['city']}, {p['state']})" 
                                       for p in sp['sample_providers']])
    
    if 'state_data' in context_data:
        sd = context_data['state_data']
        system_prompt += f"\n\nLOCATION DATA:\n"
        system_prompt += f"We have {sd['provider_count']} providers in {sd['state']}."
    
    # Build messages for API
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history
    messages.extend(conversation_history)
    
    # Add current question
    messages.append({"role": "user", "content": question})
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,  # Conversational but consistent
            max_tokens=400
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Generate follow-up suggestions
        follow_up_prompt = f"""Based on this Q&A, suggest 2-3 brief follow-up questions the user might ask.

Question: {question}
Answer: {answer}

Format as a simple list:
- Question 1?
- Question 2?
- Question 3?"""

        follow_up_response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You generate helpful follow-up questions."},
                {"role": "user", "content": follow_up_prompt}
            ],
            temperature=0.6,
            max_tokens=150
        )
        
        # Parse follow-up suggestions
        follow_ups = []
        for line in follow_up_response.choices[0].message.content.strip().split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•')):
                follow_ups.append(line.lstrip('-• ').strip())
        
        # Update conversation history
        updated_history = conversation_history + [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer}
        ]
        
        # Keep only last 10 messages to manage context window
        if len(updated_history) > 10:
            updated_history = updated_history[-10:]
        
        return {
            'answer': answer,
            'data_retrieved': context_data,
            'follow_up_suggestions': follow_ups[:3],
            'conversation_history': updated_history
        }
        
    except Exception as e:
        return {
            'answer': f"I apologize, but I encountered an error: {str(e)}",
            'data_retrieved': context_data,
            'follow_up_suggestions': [],
            'conversation_history': conversation_history,
            'error': str(e)
        }


# Test function
if __name__ == "__main__":
    print("🧪 Testing AI Engine Functions\n")
    print("=" * 70)
    
    # Test 1: Specialty Description
    print("\n📝 Test 1: Generate Specialty Description")
    print("-" * 70)
    test_specialty = "Cardiology"
    print(f"Specialty: {test_specialty}\n")
    description = generate_specialty_description(test_specialty)
    print(description)
    
    # Test 2: Related Specialties
    print("\n\n🔗 Test 2: Suggest Related Specialties")
    print("-" * 70)
    print(f"For specialty: {test_specialty}\n")
    related = suggest_related_specialties(test_specialty, count=3)
    for i, item in enumerate(related, 1):
        print(f"{i}. {item['specialty']}")
        print(f"   → {item['reason']}\n")
    
    # Test 3: Provider Distribution Analysis
    print("\n📊 Test 3: Analyze Provider Distribution")
    print("-" * 70)
    try:
        providers = db_client.get_providers_by_specialty("Cardiology", limit=20)
        if providers:
            print(f"Analyzing {len(providers)} Cardiology providers...\n")
            analysis = analyze_provider_distribution(providers)
            print(analysis)
        else:
            print("No providers found for analysis.")
    except Exception as e:
        print(f"Could not fetch providers: {e}")
        
    # Test 4: Symptom-Based Recommendation
    print("\n\n🩺 Test 4: Recommend Provider by Symptoms")
    print("-" * 70)
    test_symptoms = "chest pain, shortness of breath, feeling tired"
    print(f"Symptoms: {test_symptoms}\n")
    recommendation = recommend_provider_by_symptoms(test_symptoms, location_state="TX")
    print(f"Recommended Specialties: {', '.join(recommendation['recommended_specialties'])}")
    print(f"Reasoning: {recommendation['reasoning']}")
    print(f"Urgency Level: {recommendation['urgency_level'].upper()}")
    if recommendation.get('emergency_action'):
        print(f"⚠️  {recommendation['emergency_action']}")
    print(f"\n{recommendation['disclaimer']}")
    if recommendation.get('available_providers'):
        print(f"\nAvailable providers in TX: {len(recommendation['available_providers'])}")
        for i, p in enumerate(recommendation['available_providers'][:3], 1):
            print(f"  {i}. Dr. {p['name']} - {p['city']}, TX")
    
    # Test 5: Semantic Search
    print("\n\n🔍 Test 5: Semantic Search")
    print("-" * 70)
    test_query = "I need help with my elderly parent's memory problems"
    print(f"Query: \"{test_query}\"\n")
    search_results = semantic_search_providers(test_query, limit=5)
    print(f"Intent Understood: {search_results['understood_intent']}")
    print(f"Search Terms: {', '.join(search_results['search_terms'])}")
    print(f"Recommended Specialties: {', '.join(search_results['recommended_specialties'])}")
    print(f"\nFound {search_results['total_found']} matching providers")
    if search_results['providers']:
        print("\nTop matches:")
        for i, p in enumerate(search_results['providers'][:3], 1):
            print(f"  {i}. Dr. {p['name']} - {p['specialty']} ({p['city']}, {p['state']})")
    
    # Test 6: FAQ Chatbot (NEW!)
    print("\n\n💬 Test 6: FAQ Chatbot")
    print("-" * 70)
    
    # First question
    q1 = "How many cardiologists do you have?"
    print(f"User: {q1}\n")
    result1 = faq_chatbot(q1)
    print(f"Assistant: {result1['answer']}\n")
    if result1['follow_up_suggestions']:
        print("Suggested follow-ups:")
        for i, suggestion in enumerate(result1['follow_up_suggestions'], 1):
            print(f"  {i}. {suggestion}")
    
    # Second question with conversation history
    print("\n" + "-" * 70)
    q2 = "What about in Texas?"
    print(f"User: {q2}\n")
    result2 = faq_chatbot(q2, conversation_history=result1['conversation_history'])
    print(f"Assistant: {result2['answer']}")
    
    print("\n" + "=" * 70)
    print("✅ All 6 tests complete!")
