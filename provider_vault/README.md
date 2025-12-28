# Provider Vault

A pedagogical polyglot microservices project demonstrating AI engineering, concurrent data fetching, and modern web development using medical provider data.

## 🎯 Project Purpose

Provider Vault is designed to teach **AI engineering and modern software architecture** to interns and developers. It demonstrates:

- Real-world AI integration patterns (RAG, prompt engineering, testing non-deterministic systems)
- Polyglot microservices architecture
- Professional development practices
- Modern web development with Phoenix/Elixir

**Key Resource:** Based on concepts from "A Common-Sense Guide to AI Engineering"

## 🏗️ Architecture

This project showcases a realistic microservices architecture using multiple programming languages, each chosen for its specific strengths:
```
┌─────────────────────────────────────────────────┐
│  Phoenix Web App (Elixir) - Port 4000           │
│  ├── Provider listings & detail pages           │
│  ├── FAQ Chatbot interface                      │
│  ├── Symptom search form                        │
│  ├── Natural language search                    │
│  └── HTTP client to AI service                  │
└──────────────┬──────────────────────────────────┘
               │ HTTP (REST API)
               ↓
┌─────────────────────────────────────────────────┐
│  AI Service (Python/FastAPI) - Port 8000        │
│  ├── 6 AI Functions:                            │
│  │   • Specialty descriptions                   │
│  │   • Related specialty suggestions            │
│  │   • Provider distribution analysis           │
│  │   • Symptom-based recommendations            │
│  │   • Semantic search with intent detection    │
│  │   • FAQ chatbot with RAG pattern             │
│  ├── OpenAI API integration                     │
│  ├── PostgreSQL database client                 │
│  └── Comprehensive test suite                   │
└──────────────┬──────────────────────────────────┘
               │ SQL
               ↓
┌─────────────────────────────────────────────────┐
│  PostgreSQL Database - Port 5432                │
│  └── 60 healthcare providers across 16 states   │
└─────────────────────────────────────────────────┘
```

## ✨ Features

### 🤖 AI-Powered Features

1. **Provider Detail Pages** - AI-generated specialty descriptions and related specialty suggestions
2. **FAQ Chatbot** - Conversational AI with memory and RAG (Retrieval Augmented Generation)
3. **Symptom Search** - Medical triage with urgency assessment and emergency detection
4. **Natural Language Search** - Semantic search with intent understanding ("doctor for memory problems")

### 🧪 Professional Testing

- **20+ test cases** covering all AI functions
- **5 testing strategies** for non-deterministic AI:
  - Structure testing (format validation)
  - Semantic testing (keyword presence)
  - Business logic testing (rule verification)
  - Mock testing (fast unit tests)
  - Consistency testing (pattern validation)
- Unit tests (mocked, fast) + Integration tests (real API calls)

### 🏛️ Architecture Highlights

- **True polyglot microservices** - Elixir for web + concurrency, Python for AI/ML
- **Clean service boundaries** - Phoenix makes HTTP calls to Python AI service
- **RAG pattern implementation** - AI queries database before generating responses
- **Professional error handling** - Parameter validation, graceful degradation

## 📁 Project Structure
```
provider_vault/
├── apps/
│   ├── web/                    # Phoenix web application (Elixir)
│   │   ├── lib/
│   │   │   └── provider_vault_web_web/
│   │   │       ├── controllers/        # FAQ, Symptom, Search controllers
│   │   │       └── components/layouts/ # Navigation menu
│   │   └── README.md
│   │
│   └── ai_service/             # AI service with FastAPI (Python)
│       ├── ai_engine.py        # 6 core AI functions
│       ├── api.py              # FastAPI endpoints
│       ├── db_client.py        # PostgreSQL integration
│       ├── interactive_demo.py # CLI testing tool
│       ├── tests/              # Comprehensive test suite
│       ├── EVAL_FRAMEWORK.md   # Testing methodology
│       └── README.md
│
├── prototypes/
│   └── cli_v1_7/              # Original CLI prototype (preserved)
│
├── start.sh                    # Startup script (both services)
├── demo.sh                     # Interactive demo script
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- **Elixir** 1.19+ with Erlang/OTP 28+
- **Python** 3.11+ with uv package manager
- **PostgreSQL** 15+
- **OpenAI API key** (for AI features)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/donfox/provider_vault.git
cd provider_vault
```

2. **Set up AI Service**
```bash
cd apps/ai_service
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > .env
```

3. **Set up Database**
```bash
# Ensure PostgreSQL is running
# Database will be created automatically on first run
```

4. **Set up Phoenix Web App**
```bash
cd ../web
mix deps.get
mix ecto.create
```

5. **Start the application**
```bash
cd ../..
./start.sh
```

This starts both services:
- Python AI Service: http://localhost:8000
- Phoenix Web App: http://localhost:4000

### Usage

**Web Interface:**
- Home: http://localhost:4000
- Provider List: http://localhost:4000/providers
- FAQ Chatbot: http://localhost:4000/faq
- Symptom Search: http://localhost:4000/symptoms
- Natural Language Search: http://localhost:4000/search

**API Documentation:**
- FastAPI Docs: http://localhost:8000/docs
- Interactive testing available at `/docs` endpoint

**Interactive Demo (CLI):**
```bash
cd apps/ai_service
python interactive_demo.py -i
# Try commands: desc, related, dist, symptoms, search, faq
```

## �� Learning Objectives

### Phase 1: CLI Prototype (Elixir)
✅ Concurrent data fetching with Task.async_stream  
✅ Ecto database integration  
✅ PostgreSQL connection and queries  
✅ Command-line interface design  

### Phase 2: AI Service (Python)
✅ OpenAI API integration  
✅ FastAPI web service development  
✅ AI prompt engineering techniques  
✅ RAG (Retrieval Augmented Generation) pattern  
✅ Testing non-deterministic AI responses  
✅ Mock testing vs integration testing  

### Phase 3: Web Application (Phoenix)
✅ Phoenix framework and routing  
✅ Controller/View/Template pattern  
✅ HTTP client integration (microservices communication)  
✅ Form handling and validation  
✅ JavaScript integration for dynamic UIs  
✅ Navigation and user experience  

### Phase 4: Professional Practices
✅ Git workflow and version control  
✅ Code organization and modularity  
✅ Error handling and validation  
✅ Documentation and README maintenance  
✅ Testing strategies for AI systems  

## 🛠️ Tech Stack

- **Elixir/Phoenix**: Web framework, concurrency, HTTP routing
- **Python/FastAPI**: AI/ML service, async endpoints, OpenAPI docs
- **PostgreSQL**: Relational database for provider data
- **OpenAI GPT-4**: Large language model for AI features
- **Tailwind CSS**: Utility-first CSS framework
- **pytest**: Python testing framework
- **HTTPoison**: Elixir HTTP client

## 📚 Documentation

- [AI Service README](apps/ai_service/README.md) - AI functions and API endpoints
- [Web App README](apps/web/README.md) - Phoenix application structure
- [Testing Guide](apps/ai_service/TESTING_GUIDE.md) - Comprehensive testing strategies
- [Eval Framework](apps/ai_service/EVAL_FRAMEWORK.md) - Testing non-deterministic AI
- [CLI Prototype](prototypes/cli_v1_7/README.md) - Original development history

## 🧪 Testing

### Run Python AI Tests
```bash
cd apps/ai_service

# Run fast unit tests (mocked, no API costs)
pytest -m unit -v

# Run integration tests (real API calls, ~$0.02 cost)
pytest -m integration -v

# Run all tests
pytest -v
```

### Run Evaluation Framework
```bash
cd apps/ai_service

# Generate traces for manual review
python eval_runner.py --generate-traces

# Run automated checks
python eval_runner.py --run-automated
```

## 💡 Key Concepts Demonstrated

### AI Engineering Patterns
- **RAG (Retrieval Augmented Generation)**: FAQ chatbot queries database before answering
- **Prompt Engineering**: System prompts, few-shot examples, structured output
- **Intent Detection**: Natural language search understands user intent
- **Safety Guardrails**: Emergency detection in symptom search

### Testing Non-Deterministic Systems
- Structure validation (response format)
- Semantic checks (keyword presence)
- Business rule enforcement (urgency levels)
- Mock testing for speed
- Consistency across multiple calls

### Microservices Communication
- REST API between services
- JSON request/response format
- Error handling and status codes
- Service independence and scalability

## 🤝 Contributing

This is a pedagogical project designed for learning. Feel free to:
- Explore the code
- Extend features
- Experiment with AI prompts
- Add new test cases

## 📖 Resources

- **Book**: "A Common-Sense Guide to AI Engineering" (testing strategies, RAG patterns)
- **Phoenix Framework**: https://phoenixframework.org
- **FastAPI**: https://fastapi.tiangolo.com
- **OpenAI API**: https://platform.openai.com/docs

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built as a teaching tool to demonstrate professional AI engineering practices and modern polyglot microservices architecture.
