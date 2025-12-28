# Intern Projects Portfolio

A monorepo showcasing diverse software engineering projects developed during internships, demonstrating skills in blockchain data processing, AI engineering, healthcare data integration, and polyglot microservices architecture.

## Projects Overview

### 1. Blockchain Data Processing

#### [Blockchain Indexer](blockchain/blockchain_indexer/)
Production-ready blockchain block indexer combining batch processing with multiprocessing for efficient block collection and gap detection.

**Key Features:**
- Batch processing with configurable size
- Python multiprocessing (no Redis dependency)
- Dual storage: PostgreSQL + JSON files
- Automatic gap detection and fixing
- Comprehensive metrics and health checks

**Tech Stack:** Python, PostgreSQL, Multiprocessing

[View detailed documentation →](blockchain/blockchain_indexer/README.md)

#### [Redis Block Extractor](blockchain/redis_block_extractor/)
Concurrent blockchain block collector using Redis for inter-process communication.

**Key Features:**
- Continuous/incremental block monitoring
- Concurrent Python scripts coordinated via Redis
- Automatic gap detection and filling
- Demonstrates distributed systems patterns

**Tech Stack:** Python, Redis, Bash

[View detailed documentation →](blockchain/redis_block_extractor/README.md)

### 2. AI Engineering & Microservices

#### [Provider Vault](provider_vault/)
Pedagogical polyglot microservices project demonstrating AI engineering, concurrent data fetching, and modern web development using medical provider data.

**Key Features:**
- AI-powered features: FAQ chatbot with RAG, symptom search, semantic search
- Polyglot microservices: Elixir/Phoenix web app + Python/FastAPI AI service
- 20+ test cases for non-deterministic AI
- Professional testing strategies (structure, semantic, mock, integration)

**Tech Stack:** Elixir/Phoenix, Python/FastAPI, PostgreSQL, OpenAI GPT-4, Tailwind CSS

**What You'll Learn:**
- AI engineering patterns (RAG, prompt engineering, intent detection)
- Testing non-deterministic systems
- Microservices communication
- Concurrent data processing with Elixir

[View detailed documentation →](provider_vault/README.md)

### 3. Healthcare Data Integration

#### [PyX12 837P to JSON Converter](pyx12_837p_to_json/)
Python toolkit for converting X12 837P (Professional Healthcare Claims) EDI files to JSON format.

**Key Features:**
- Two parsing approaches: structured (claims hierarchy) and flat (raw segments)
- Extracts claim-level and service line-level data
- Command-line interface and Python API
- HIPAA-compliant EDI transaction processing

**Tech Stack:** Python, PyX12

**Use Cases:**
- Healthcare claims processing
- EDI file debugging and exploration
- Building custom claims parsers

[View detailed documentation →](pyx12_837p_to_json/README.md)

## Repository Structure

```
intern-projects-portfolio/
├── blockchain/
│   ├── blockchain_indexer/      # Production blockchain indexer
│   └── redis_block_extractor/   # Redis-based concurrent collector
├── provider_vault/
│   ├── apps/
│   │   ├── web/                 # Phoenix web application
│   │   └── ai_service/          # Python AI service
│   └── prototypes/              # CLI prototypes
├── pyx12_837p_to_json/          # X12 EDI to JSON converter
└── README.md                     # This file
```

## Skills Demonstrated

### Languages & Frameworks
- **Python**: FastAPI, multiprocessing, async/await, PyX12
- **Elixir**: Phoenix, Ecto, Task.async_stream, concurrency
- **SQL**: PostgreSQL, complex queries, schema design
- **Shell**: Bash scripting, process orchestration

### Software Engineering Practices
- **Architecture**: Microservices, polyglot systems, service boundaries
- **Testing**: Unit tests, integration tests, mocking, testing AI systems
- **Data Processing**: Batch processing, concurrent execution, gap detection
- **AI Engineering**: RAG patterns, prompt engineering, intent detection
- **DevOps**: Database management, service orchestration, health checks

### Domain Knowledge
- **Blockchain**: Block collection, indexing, data integrity
- **Healthcare**: X12 EDI, HIPAA compliance, claims processing
- **AI/ML**: OpenAI API integration, semantic search, chatbots

## Getting Started

Each project has its own README with detailed setup instructions. Quick links:

1. [Blockchain Indexer Setup](blockchain/blockchain_indexer/README.md#installation)
2. [Redis Block Extractor Setup](blockchain/redis_block_extractor/README.md#installation)
3. [Provider Vault Setup](provider_vault/README.md#installation)
4. [PyX12 Converter Setup](pyx12_837p_to_json/README.md#installation)

## Project Evolution

These projects demonstrate progressive learning and skill development:

1. **Initial Exploration** - Redis-based concurrent processing
2. **Production Refinement** - Blockchain indexer with batch processing and comprehensive error handling
3. **AI Integration** - Provider Vault with OpenAI API and testing strategies
4. **Healthcare Domain** - EDI parsing and healthcare data standards

## Technologies Used

| Category | Technologies |
|----------|-------------|
| Languages | Python, Elixir, SQL, Bash, JavaScript |
| Frameworks | FastAPI, Phoenix, PyX12 |
| Databases | PostgreSQL, Redis |
| AI/ML | OpenAI GPT-4, RAG patterns |
| Testing | pytest, mock, integration tests |
| Web | Tailwind CSS, LiveView |

## About

These projects were developed during internships to demonstrate practical software engineering skills across multiple domains including blockchain technology, AI engineering, healthcare data integration, and modern web development.

## License

Individual projects may have their own licenses. Please refer to each project's README for specific licensing information.

## Contact

Don Fox
GitHub: [@donfox](https://github.com/donfox)

For questions about specific projects, please refer to the individual project READMEs.
