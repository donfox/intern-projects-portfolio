"""
Test Script for Provider Vault AI Engine

Interactive testing tool for experimenting with AI functions.
Run in two modes:
  - Automated: python test_ai.py
  - Interactive: python test_ai.py -i
"""

import sys
import ai_engine
import db_client


def print_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subheader(title):
    """Print a formatted subsection header."""
    print(f"\n{title}")
    print("-" * 70)


def test_specialty_description(specialty=None):
    """Test the specialty description function."""
    if not specialty:
        specialty = "Cardiology"
    
    print_subheader(f"📝 Specialty Description: {specialty}")
    description = ai_engine.generate_specialty_description(specialty)
    print(description)


def test_related_specialties(specialty=None, count=3):
    """Test the related specialties function."""
    if not specialty:
        specialty = "Cardiology"
    
    print_subheader(f"🔗 Related Specialties for: {specialty}")
    related = ai_engine.suggest_related_specialties(specialty, count)
    
    for i, item in enumerate(related, 1):
        print(f"\n{i}. {item['specialty']}")
        print(f"   Reason: {item['reason']}")


def test_provider_analysis(specialty=None, limit=20):
    """Test the provider distribution analysis function."""
    if not specialty:
        specialty = "Cardiology"
    
    print_subheader(f"📊 Provider Analysis: {specialty}")
    
    try:
        providers = db_client.get_providers_by_specialty(specialty, limit)
        
        if not providers:
            print(f"No providers found for specialty: {specialty}")
            return
        
        print(f"Analyzing {len(providers)} {specialty} providers...\n")
        analysis = ai_engine.analyze_provider_distribution(providers)
        print(analysis)
        
    except Exception as e:
        print(f"Error fetching providers: {e}")


def run_automated_tests():
    """Run a suite of automated tests with different specialties."""
    print_header("🧪 AUTOMATED TEST SUITE")
    
    # Get available specialties from database
    try:
        specialties = db_client.get_all_specialties()
        print(f"\nAvailable specialties in database: {len(specialties)}")
        print(f"Sample: {', '.join(specialties[:5])}...\n")
    except Exception as e:
        print(f"Could not fetch specialties: {e}")
        specialties = ["Cardiology", "Neurology", "Orthopedic Surgery"]
    
    # Test with first specialty
    test_specialty = specialties[0] if specialties else "Cardiology"
    
    print_header(f"Testing with: {test_specialty}")
    
    # Test 1: Description
    test_specialty_description(test_specialty)
    
    # Test 2: Related specialties
    test_related_specialties(test_specialty)
    
    # Test 3: Provider analysis
    test_provider_analysis(test_specialty)
    
    print_header("✅ AUTOMATED TESTS COMPLETE")


def run_interactive_mode():
    """Run interactive testing mode."""
    print_header("🎮 INTERACTIVE MODE")
    print("\nCommands:")
    print("  describe <specialty>    - Generate specialty description")
    print("  related <specialty>     - Find related specialties")
    print("  analyze <specialty>     - Analyze provider distribution")
    print("  symptoms <description>  - Get provider recommendations based on symptoms")
    print("  search <query>          - Natural language provider search")
    print("  faq <question>          - Ask FAQ chatbot (with conversation memory)")
    print("  list                    - Show all available specialties")
    print("  stats                   - Show database statistics")
    print("  quit                    - Exit interactive mode")
    print()
    
    # Cache specialties
    try:
        all_specialties = db_client.get_all_specialties()
    except:
        all_specialties = []
    
    # Conversation history for FAQ
    faq_history = None
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
            
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else None
            
            if command == "quit" or command == "exit":
                print("\n👋 Goodbye!")
                break
            
            elif command == "list":
                print_subheader("📋 Available Specialties")
                for i, spec in enumerate(all_specialties, 1):
                    print(f"{i:2d}. {spec}")
            
            elif command == "stats":
                print_subheader("📊 Database Statistics")
                stats = db_client.test_connection()
                print(f"Total Providers: {stats['total_providers']}")
                print(f"Total Specialties: {stats['total_specialties']}")
                print(f"Total States: {stats['total_states']}")
            
            elif command == "describe":
                if not arg:
                    print("Usage: describe <specialty>")
                    continue
                test_specialty_description(arg)
            
            elif command == "related":
                if not arg:
                    print("Usage: related <specialty>")
                    continue
                test_related_specialties(arg)
            
            elif command == "analyze":
                if not arg:
                    print("Usage: analyze <specialty>")
                    continue
                test_provider_analysis(arg)
            
            elif command == "symptoms":
                if not arg:
                    print("Usage: symptoms <symptom description>")
                    print("Example: symptoms chest pain, shortness of breath")
                    continue
                print_subheader(f"🩺 Symptom-Based Recommendation")
                recommendation = ai_engine.recommend_provider_by_symptoms(arg)
                print(f"\nRecommended Specialties: {', '.join(recommendation['recommended_specialties'])}")
                print(f"Reasoning: {recommendation['reasoning']}")
                print(f"Urgency Level: {recommendation['urgency_level'].upper()}")
                if recommendation.get('emergency_action'):
                    print(f"\n⚠️  {recommendation['emergency_action']}")
                print(f"\n{recommendation['disclaimer']}")
            
            elif command == "search":
                if not arg:
                    print("Usage: search <natural language query>")
                    print("Example: search doctor for memory problems")
                    continue
                print_subheader(f"🔍 Semantic Search")
                results = ai_engine.semantic_search_providers(arg)
                print(f"\nIntent: {results['understood_intent']}")
                print(f"Key Terms: {', '.join(results['search_terms'])}")
                print(f"Specialties: {', '.join(results['recommended_specialties'])}")
                print(f"\nFound {results['total_found']} providers")
                if results['providers']:
                    print("\nTop matches:")
                    for i, p in enumerate(results['providers'][:5], 1):
                        print(f"  {i}. Dr. {p['name']} - {p['specialty']} ({p['city']}, {p['state']})")
            
            elif command == "faq":
                if not arg:
                    print("Usage: faq <question>")
                    print("Example: faq How many cardiologists do you have?")
                    continue
                print_subheader(f"💬 FAQ Chatbot")
                result = ai_engine.faq_chatbot(arg, conversation_history=faq_history)
                print(f"\nAssistant: {result['answer']}")
                
                # Update conversation history for next turncle
                faq_history = result['conversation_history']
                
                # Show follow-up suggestions
                if result['follow_up_suggestions']:
                    print(f"\n💡 Suggested follow-ups:")
                    for i, suggestion in enumerate(result['follow_up_suggestions'], 1):
                        print(f"  {i}. {suggestion}")
                
                # Show what data was retrieved (debug info)
                if result['data_retrieved'].get('specialty_providers'):
                    sp = result['data_retrieved']['specialty_providers']
                    print(f"\n📊 [Retrieved: {sp['count']} {sp['specialty']} providers]")
                elif result['data_retrieved'].get('state_data'):
                    sd = result['data_retrieved']['state_data']
                    print(f"\n📊 [Retrieved: {sd['provider_count']} providers in {sd['state']}]")
            
            else:
                print(f"Unknown command: {command}")
                print("Type 'quit' to exit or try: describe, related, analyze, symptoms, search, faq, list, stats")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point."""
    
    # Check for interactive flag
    if len(sys.argv) > 1 and sys.argv[1] in ['-i', '--interactive']:
        run_interactive_mode()
    else:
        run_automated_tests()


if __name__ == "__main__":
    main()
