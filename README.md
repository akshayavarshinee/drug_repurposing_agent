# Drug Repurposing Platform

A full-stack pharmaceutical research web application powered by AI agents that allows researchers to query natural language questions about drug repurposing and receive comprehensive, evidence-backed reports.

## Features

- **User Authentication**: Secure JWT-based authentication with bcrypt password hashing
- **Natural Language Queries**: Submit pharmaceutical research questions in plain English
- **AI Agent System**: Multi-agent architecture for intelligent data retrieval and analysis
- **Comprehensive Reports**: Automatic generation of detailed pharmaceutical research reports with:
  - Target-disease mechanistic insights
  - Clinical trial data from ClinicalTrials.gov
  - Patent landscape analysis
  - Global trade and market intelligence
  - Safety profiles and contraindications
- **Report History**: View and access all past reports
- **Modern UI**: Clean, professional interface with custom color scheme

## Tech Stack

### Backend

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust relational database for data persistence
- **SQLAlchemy**: ORM for database operations
- **JWT**: Secure token-based authentication
- **Bcrypt**: Password hashing for security
- **Google AI Agents SDK**: Multi-agent orchestration framework

### Frontend

- **HTML5 + Jinja2**: Template-based rendering
- **Tailwind CSS**: Utility-first CSS framework
- **Vanilla JavaScript**: No heavy frontend frameworks

### AI & Data Sources

- **ChEMBL API**: Drug molecules, mechanisms, indications, warnings
- **BindingDB API**: Target-drug binding affinities
- **ClinicalTrials.gov API v2**: Clinical trial data
- **Serper API**: Web search for patents, trade data, and market intelligence
- **Open Targets API**: Disease-target associations
- **Europe PMC API**: Literature evidence counts

## AI Agent Architecture

The platform uses a multi-agent system where specialized agents collaborate to gather and analyze pharmaceutical data:

### Core Agents

#### 1. **Unified Pipeline Agent** (`unified_pipeline_agent.py`)

- **Role**: Main orchestrator that calls the unified repurposing pipeline
- **Input**: Drug name or disease query
- **Output**: Comprehensive structured data including targets, mechanisms, clinical trials, patents, trade, and market data
- **Model**: GPT-4o-mini

#### 2. **Clinical Trials Research Agent** (`clinical_trails_research_agent.py`)

- **Role**: Discovers repurposing signals from clinical trial data
- **Data Source**: ClinicalTrials.gov API v2
- **Capabilities**:
  - Searches trials by intervention, condition, phase, status
  - Extracts endpoints, biomarkers, and subgroup signals
  - Identifies failure patterns and safety flags
- **Output**: Trial IDs, phases, statuses, conditions, interventions

#### 3. **Patent Research Agent** (`patent_research_agent.py`)

- **Role**: Analyzes patent landscape for Freedom-to-Operate (FTO) assessment
- **Data Source**: Serper API (Google Patents search)
- **Capabilities**:
  - Searches pharmaceutical and biotech patents
  - Extracts patent numbers, assignees, filing dates
  - Identifies secondary medical use opportunities
  - Assesses white-space for repurposing
- **Output**: Patent details, FTO risk assessment, repurposing opportunities

#### 4. **EXIM Trade Agent** (`exim_trade_agent.py`)

- **Role**: Provides global trade and supply chain intelligence
- **Data Source**: Serper API (web search)
- **Capabilities**:
  - Searches for import/export trends
  - Identifies key manufacturing and trading countries
  - Assesses supply chain risks
- **Output**: Trade trends, partner countries, market insights

#### 5. **Market Insights Agent** (`market_insights_agent.py`)

- **Role**: Gathers commercial and market intelligence
- **Data Source**: Serper API (web search)
- **Capabilities**:
  - Searches for sales data, market size, revenue figures
  - Identifies growth projections and CAGR
  - Analyzes competitive landscape
- **Output**: Market size, revenue estimates, growth trends, key players

#### 6. **Report Generation Agent** (`report_generation_agent.py`)

- **Role**: Synthesizes all research data into executive reports
- **Input**: Context from all other agents
- **Capabilities**:
  - Extracts data from multiple agent outputs
  - Creates structured tables and summaries
  - Provides repurposing feasibility scores
- **Output**: Publication-ready markdown reports with:
  - Drug profile & molecular characteristics
  - Target-disease mechanistic insights
  - Clinical trial landscape
  - Patent & IP analysis
  - Trade & supply chain intelligence
  - Market & commercial intelligence
  - Safety & risk profile
  - Repurposing feasibility score (0.0-1.0)

### Supporting Agents

#### 7. **Web Intelligence Agent** (`web_intelligence_research_agent.py`)

- **Role**: General web search for supplementary information
- **Data Source**: Serper API

#### 8. **ChEMBL Research Agent** (`chembl_research_agent.py`)

- **Role**: Queries ChEMBL database for drug and target data
- **Data Source**: ChEMBL REST API

#### 9. **Open Targets Agent** (`open_targets_research_agent.py`)

- **Role**: Retrieves disease-target associations
- **Data Source**: Open Targets GraphQL API

## Unified Repurposing Pipeline

The core of the system is the `unified_repurposing_pipeline.py` which orchestrates data collection from multiple APIs:

### Pipeline A: Drug-Based Repurposing

**Input**: Drug name (e.g., "Imatinib")

**10-Step Process**:

1. **ChEMBL Lookup**: Find drug molecule and SMILES structure
2. **BindingDB Targets**: Retrieve target-drug binding affinities
3. **Mechanisms**: Get mechanism of action data
4. **Indications**: Fetch approved and investigational indications
5. **Warnings**: Retrieve safety warnings and contraindications
6. **Similar Drugs**: Find structurally similar compounds
7. **Clinical Trials**: Search ClinicalTrials.gov for trial data
8. **Patents**: Analyze patent landscape
9. **Trade Data**: Gather import/export intelligence
10. **Market Insights**: Collect sales and market data

**Output**: Comprehensive drug profile with all enrichment data

### Pipeline B: Disease-Based Repurposing

**Input**: Disease name (e.g., "Type 2 Diabetes")

**Process**:

1. **Open Targets**: Find disease-associated targets
2. **ChEMBL**: For each target, find drugs with high binding affinity
3. **Enrichment**: Run Pipeline A for top drug candidates
4. **Ranking**: Score and rank candidates by repurposing potential

**Output**: Ranked list of drug candidates with full profiles

## Project Structure

```
├── app/
│   ├── main.py                          # FastAPI application entry point
│   ├── database.py                      # Database configuration
│   ├── auth/                            # Authentication module
│   ├── users/                           # User management
│   ├── queries/                         # Query submission
│   └── results/                         # Report retrieval
├── pharma_agents/
│   ├── unified_pipeline_agent.py        # Main pipeline orchestrator
│   ├── clinical_trails_research_agent.py # Clinical trials intelligence
│   ├── patent_research_agent.py         # Patent landscape analysis
│   ├── exim_trade_agent.py              # Trade & supply chain
│   ├── market_insights_agent.py         # Market intelligence
│   ├── report_generation_agent.py       # Report synthesis
│   ├── web_intelligence_research_agent.py # Web search
│   ├── chembl_research_agent.py         # ChEMBL queries
│   ├── open_targets_research_agent.py   # Open Targets queries
│   ├── async_orchestrator.py            # Multi-agent orchestration
│   └── tools/
│       ├── unified_repurposing_pipeline.py # Core pipeline logic
│       ├── chembl_tools.py              # ChEMBL API functions
│       ├── bindingdb_tools.py           # BindingDB API functions
│       └── open_targets_tools.py        # Open Targets API functions
├── static/                              # Frontend assets
├── templates/                           # HTML templates
└── requirements.txt                     # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL database

### Environment Variables

Create a `.env` file with the following:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Authentication
SESSION_SECRET=your-secret-key-here

# API Keys
SERPER_API_KEY=your-serper-api-key  # Required for patents, trade, market data
OPENAI_API_KEY=your-openai-key      # Optional, for trace export
```

### Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. The database tables will be created automatically on first startup.

3. Run the application:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000
```

4. Access the application at `http://localhost:5000`

## API Endpoints

### Authentication

- `POST /auth/register`: Register new user
- `POST /auth/login`: Login user
- `POST /auth/logout`: Logout user

### Users

- `GET /users/profile`: Get current user profile

### Queries

- `POST /api/query/submit`: Submit a pharmaceutical research query

### Results

- `GET /api/results/{id}`: Get specific report by ID
- `GET /api/results/`: Get all reports for current user

## Database Schema

### Users

- id (Primary Key)
- username (Unique)
- email (Unique)
- hashed_password
- created_at

### Queries

- id (Primary Key)
- user_id (Foreign Key)
- question
- created_at

### Reports

- id (Primary Key)
- query_id (Foreign Key, Unique)
- user_id (Foreign Key)
- title
- report_text
- created_at

## Example Queries

### Drug-Based Queries

- "What are the repurposing opportunities for Metformin?"
- "Analyze the patent landscape for Imatinib"
- "Find clinical trials for Thalidomide"

### Disease-Based Queries

- "Find drug candidates for Type 2 Diabetes"
- "What drugs target Alzheimer's disease?"
- "Repurposing opportunities for COVID-19"

## Testing

Run individual agent tests:

```bash
# Test Clinical Trials API
python debug_ct_api.py

# Test Patents API
python debug_patents_api.py

# Test full pipeline
python test_unified_pipeline.py

# Test with specific drug
python verify_thalidomide_pipeline.py
```

## Security

- Passwords are hashed using bcrypt
- JWT tokens for session management
- HTTPOnly cookies to prevent XSS attacks
- SQL injection prevention through SQLAlchemy ORM
- API keys stored in environment variables

## Performance Considerations

- BindingDB queries limited to similarity cutoff 0.85 to reduce API load
- Clinical trials limited to 20 results per query
- Patent searches limited to 10-20 results
- Disease pipeline limits drugs per target to prevent timeouts
- Async agent orchestration for parallel data gathering

## Known Limitations

- PatentsView API replaced with Serper due to access restrictions
- Some APIs may have rate limits (ChEMBL, BindingDB)
- Clinical trial data quality depends on ClinicalTrials.gov completeness
- Market data relies on web search results accuracy

## Future Enhancements

- PDF export functionality
- Data visualizations and interactive charts
- Report sharing between users
- Advanced search and filtering
- Real-time collaboration features
- Integration with additional pharmaceutical databases
- Machine learning-based candidate ranking
- Automated literature review synthesis

## License

This project is for educational and research purposes.

## Acknowledgments

- **ChEMBL**: European Bioinformatics Institute (EMBL-EBI)
- **BindingDB**: University of California San Diego
- **ClinicalTrials.gov**: U.S. National Library of Medicine
- **Open Targets**: EMBL-EBI, Wellcome Sanger Institute, GSK
- **Serper API**: Google search API wrapper

## Features

- **User Authentication**: Secure JWT-based authentication with bcrypt password hashing
- **Natural Language Queries**: Submit pharmaceutical research questions
- **Report Generation**: Automatic generation of detailed pharmaceutical research reports
- **Report History**: View and access all past reports
- **Modern UI**: Clean, professional interface with custom color scheme

## Tech Stack

### Backend

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust relational database for data persistence
- **SQLAlchemy**: ORM for database operations
- **JWT**: Secure token-based authentication
- **Bcrypt**: Password hashing for security

### Frontend

- **HTML5 + Jinja2**: Template-based rendering
- **Tailwind CSS**: Utility-first CSS framework
- **Vanilla JavaScript**: No heavy frontend frameworks

## Project Structure

```
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database configuration
│   ├── auth/
│   │   ├── routes.py           # Authentication endpoints
│   │   ├── hashing.py          # Password hashing utilities
│   │   └── jwt_handler.py      # JWT token management
│   ├── users/
│   │   ├── models.py           # User database model
│   │   └── routes.py           # User management endpoints
│   ├── queries/
│   │   ├── models.py           # Query database model
│   │   └── routes.py           # Query submission endpoints
│   └── results/
│       ├── models.py           # Report database model
│       └── routes.py           # Report retrieval endpoints
├── static/
│   ├── css/
│   │   └── styles.css          # Custom styling
│   └── js/
│       ├── main.js             # Common JavaScript
│       ├── auth.js             # Authentication logic
│       ├── query.js            # Query submission
│       ├── results.js          # Results display
│       └── history.js          # History page
├── templates/
│   ├── base.html               # Base template
│   ├── landing.html            # Landing page
│   ├── signup.html             # Registration page
│   ├── login.html              # Login page
│   ├── query.html              # Query/chat interface
│   ├── results.html            # Report display
│   └── history.html            # Report history
└── requirements.txt            # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL database

### Environment Variables

The following environment variables are required:

- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Secret key for JWT token generation

### Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. The database tables will be created automatically on first startup.

3. Run the application:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000
```

4. Access the application at `http://localhost:5000`

## API Endpoints

### Authentication

- `POST /auth/register`: Register new user
- `POST /auth/login`: Login user
- `POST /auth/logout`: Logout user

### Users

- `GET /users/profile`: Get current user profile

### Queries

- `POST /api/query/submit`: Submit a pharmaceutical research query

### Results

- `GET /api/results/{id}`: Get specific report by ID
- `GET /api/results/`: Get all reports for current user

## Database Schema

### Users

- id (Primary Key)
- username (Unique)
- email (Unique)
- hashed_password
- created_at

### Queries

- id (Primary Key)
- user_id (Foreign Key)
- question
- created_at

### Reports

- id (Primary Key)
- query_id (Foreign Key, Unique)
- user_id (Foreign Key)
- title
- report_text
- created_at

## Future Enhancements

- Integration with real pharmaceutical data APIs
- AI agent system for intelligent data retrieval
- PDF export functionality
- Data visualizations and charts
- Report sharing between users
- Advanced search and filtering

## Security

- Passwords are hashed using bcrypt
- JWT tokens for session management
- HTTPOnly cookies to prevent XSS attacks
- SQL injection prevention through SQLAlchemy ORM

## License

This project is for educational and research purposes.
