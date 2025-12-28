# Provider Vault AI Service

Python-based AI service providing medical provider intelligence and conversational capabilities using OpenAI's GPT-4.

## Overview

This FastAPI service powers the AI features in Provider Vault's Phoenix web application. It demonstrates professional AI engineering practices including RAG (Retrieval Augmented Generation), prompt engineering, and comprehensive testing of non-deterministic systems.

## Features

### 6 AI Functions

1. **Specialty Descriptions** (`generate_specialty_description`) - Patient-friendly explanations of medical specialties
2. **Related Specialties** (`suggest_related_specialties`) - Referral network and related field suggestions
3. **Provider Distribution Analysis** (`analyze_provider_distribution`) - Geographic and demographic insights
4. **Symptom Recommendations** (`recommend_provider_by_symptoms`) - Medical triage with urgency detection
5. **Semantic Search** (`semantic_search_providers`) - Natural language search with intent understanding
6. **FAQ Chatbot** (`faq_chatbot`) - Conversational AI with memory and RAG pattern

### RAG Implementation

The FAQ chatbot demonstrates Retrieval Augmented Generation:
- Queries PostgreSQL database for real-time data
- Includes network statistics in system prompt
- Maintains conversation history across turns
- Grounds AI responses in actual database content

### Professional Testing

- **20+ test cases** covering all AI functions
- **5 testing strategies**: structure, semantic, business logic, mocking, consistency
- Unit tests (fast, mocked) + Integration tests (real API calls)
- Eval framework for manual quality assessment

## Quick Start

### Prerequisites

- Python 3.11+
- uv package manager
- PostgreSQL database (managed by Phoenix app)
- OpenAI API key

### Setup
```bash
cd apps/ai_service

# Create virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install fastapi uvicorn openai python-dotenv psycopg2-binary httpx pytest pytest-cov

# Create .env file
cat > .env << 'ENVFILE'
DATABASE_URL=postgresql://postgres@localhost:5432/provider_vault_dev
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
ENVFILE
```

### Start the Service
```bash
# Development mode (auto-reload)
uvicorn api:app --reload --port 8000

# Production mode
uvicorn api:app --host 0.0.0.0 --port 8000
```

**Service URLs:**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health & Info
```bash
GET /health              # Service health check
GET /api/stats          # Database statistics
GET /api/specialties    # List all specialties
```

### AI Functions
```bash
# Specialty description
POST /api/specialty/describe
{"specialty": "Cardiology"}

# Related specialties
POST /api/specialty/related
{"specialty": "Cardiology", "count": 3}

# Provider distribution analysis
POST /api/providers/analyze
{"specialty": "Cardiology", "limit": 20}

# Symptom recommendations (with urgency assessment)
POST /api/symptoms/recommend
{"symptoms": "chest pain, shortness of breath", "location_state": "TX"}

# Semantic search (natural language)
POST /api/search
{"query": "doctor for memory problems", "limit": 10}

# FAQ chatbot (with conversation history)
POST /api/faq
{
  "question": "How many cardiologists do you have?",
  "conversation_history": []
}
```

### Example Responses

**Symptom Recommendation:**
```json
{
  "recommended_specialties": ["Cardiology", "Emergency Medicine"],
  "reasoning": "Chest pain and shortness of breath require immediate cardiac evaluation...",
  "urgency_level": "emergency",
  "emergency_action": "CALL 911 IMMEDIATELY - These symptoms may indicate a heart attack",
  "available_providers": [...],
  "location_checked": "TX"
}
```

**FAQ Chatbot:**
```json
{
  "answer": "We currently have 6 cardiologists in our network...",
  "data_retrieved": {
    "network_stats": {"total_providers": 60, "total_specialties": 16},
    "available_specialties": ["Cardiology", ...]
  },
  "follow_up_suggestions": [
    "Which states have the most cardiologists?",
    "Do you have cardiologists in Texas?"
  ],
  "conversation_history": [...]
}
```

## Interactive Demo

Test AI functions from the command line:
```bash
python interactive_demo.py -i
```

**Available Commands:**
- `desc <specialty>` - Generate description
- `related <specialty>` - Find related specialties
- `dist <specialty>` - Analyze distribution
- `symptoms <description>` - Get recommendations
- `search <query>` - Natural language search
- `faq <question>` - Ask chatbot (maintains history)
- `list` - Show all specialties
- `stats` - Database statistics
- `quit` - Exit

## Testing

### Run Tests
```bash
# All tests
pytest -v

# Fast unit tests only (mocked, no API costs)
pytest -m unit -v

# Integration tests only (real API calls, ~$0.02 per run)
pytest -m integration -v

# With coverage report
pytest --cov=. --cov-report=html
```

### Test Organization

**Unit Tests** (`tests/test_ai_engine_unit.py`):
- Mock OpenAI API responses
- Test parsing and structure validation
- Fast feedback loop (< 1 second)
- No API costs

**Integration Tests** (`tests/test_ai_engine_comprehensive.py`):
- Real OpenAI API calls
- Validate actual AI behavior
- Slower (~45 seconds)
- Small API costs (~$0.02/run)

### Eval Framework

For manual quality assessment:
```bash
# Generate traces for review
python eval_runner.py --generate-traces

# Run automated checks
python eval_runner.py --run-automated
```

See `EVAL_FRAMEWORK.md` for detailed methodology.

## Project Structure
```
apps/ai_service/
├── ai_engine.py                    # 6 core AI functions
├── api.py                          # FastAPI endpoints (337 lines)
├── db_client.py                    # PostgreSQL client
├── interactive_demo.py             # CLI testing tool
├── eval_runner.py                  # Evaluation framework
├── pytest.ini                      # Test configuration
├── .env                            # Configuration (not in git)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── EVAL_FRAMEWORK.md              # Testing methodology
├── tests/
│   ├── test_ai_engine_unit.py     # Fast mocked tests
│   └── test_ai_engine_comprehensive.py  # Integration tests
└── .venv/                          # Virtual environment
```

## Integration with Phoenix

The Phoenix web application (port 4000) communicates with this service via HTTP:
```elixir
# Example: Phoenix controller calling FAQ endpoint
def ask(conn, %{"question" => question, "conversation_history" => history}) do
  case HTTPoison.post("http://localhost:8000/api/faq",
    Jason.encode!(%{question: question, conversation_history: history}),
    [{"Content-Type", "application/json"}]) do
    
    {:ok, %{status_code: 200, body: body}} ->
      json(conn, Jason.decode!(body))
      
    {:error, reason} ->
      conn
      |> put_status(:service_unavailable)
      |> json(%{error: "AI service unavailable"})
  end
end
```

## AI Engineering Concepts Demonstrated

### Prompt Engineering
- System prompts for role assignment
- Few-shot examples for format guidance
- Structured output with delimiters
- Temperature control for consistency

### RAG (Retrieval Augmented Generation)
- Database queries before AI generation
- Context injection into system prompts
- Grounding responses in real data
- Preventing hallucination

### Safety & Guardrails
- Emergency detection in symptom search
- Urgency level classification
- Emergency action instructions
- Medical disclaimer language

### Testing Non-Deterministic Systems
1. **Structure Testing** - Response format validation
2. **Semantic Testing** - Keyword/concept checking
3. **Business Logic** - Rule enforcement
4. **Mock Testing** - Fast unit tests
5. **Consistency Testing** - Pattern validation

## Configuration

Environment variables in `.env`:
```bash
# Required
DATABASE_URL=postgresql://user:pass@host:port/database
OPENAI_API_KEY=sk-your-key-here

# Optional
OPENAI_MODEL=gpt-4o-mini          # or gpt-4, gpt-4-turbo
OPENAI_TEMPERATURE=0.7            # 0.0-2.0 (lower = more consistent)
OPENAI_MAX_TOKENS=1000            # Response length limit
```

## Development Tips

### Testing Without API Costs

Use unit tests during development:
```bash
pytest -m unit -v  # No API calls, instant feedback
```

### Debugging AI Responses

Use the interactive demo for quick testing:
```bash
python interactive_demo.py -i
>>> faq How many providers?
```

### Monitoring API Usage

Check OpenAI dashboard for:
- Token usage per request
- Daily/monthly costs
- Error rates

## Cost Estimates

- **Development**: ~$0.10/day with unit tests
- **Integration tests**: ~$0.02 per full test run
- **Production**: Depends on traffic (~$0.001 per request)

## License

Part of Provider Vault - Educational project demonstrating AI engineering practices.

## Resources

- FastAPI Docs: https://fastapi.tiangolo.com
- OpenAI API: https://platform.openai.com/docs
- Testing Guide: See `TESTING_GUIDE.md`
- Eval Framework: See `EVAL_FRAMEWORK.md`
