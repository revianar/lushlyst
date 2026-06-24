# Lushlyst: AI Agent in Chemical Risk Evaluation

## Overview

Lushlyst is a production-grade chemical risk evaluation platform that combines deterministic scientific scoring with LLM-based molecular extraction. It fetches chemical properties from PubChem, applies a 5-criteria Environmental, Health, and Safety (EHS) scoring matrix, and uses OpenAI structured outputs to extract chemical names from unstructured laboratory text.

## License

This project is licensed under the MIT License. See the [LICENSE] file for details.

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| Backend API | FastAPI (Async) |
| Frontend UI | Streamlit (Thin HTTP Client) |
| Database | PostgreSQL 16 (via SQLAlchemy 2.0 async) |
| AI/LLM | OpenAI API (gpt-4o-mini with Pydantic structured outputs) |
| External Data | PubChem REST API |
| Containerization | Docker and Docker Compose |
| CI/CD | GitHub Actions |

## Architecture

The system follows a strict decoupled microservice architecture:

| Layer | Purpose |
|---|---|
| Streamlit UI | Acts purely as a presentation layer. Contains zero business logic and communicates with the backend exclusively via HTTP REST calls. |
| FastAPI Backend | The single source of truth. Handles routing, JWT authentication, database transactions, and LLM orchestration. |
| Core Engine | Pure Python deterministic logic for the 5-criteria EHS scoring. No AI is used for mathematical or rule-based scoring, ensuring 100% reproducibility. |
| Data Layer | An idempotent ETL pipeline fetches data from PubChem and upserts it into PostgreSQL to act as a semantic cache, preventing redundant API calls and reducing LLM costs. |

## Quick Start

1. Clone the repository and navigate into the folder:

```bash
git clone https://github.com/yourusername/lushlyst.git
cd lushlyst
```

2. Create a Python 3.12 virtual environment and activate it:

```bash
python3.12 -m venv .venv312
source .venv312/bin/activate  # Linux/macOS
# OR
.\.venv312\Scripts\Activate.ps1  # Windows PowerShell
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your PostgreSQL connection string and OpenAI API key:

```env
DATABASE_URL="postgresql+asyncpg://lushlyst_user:lushlyst_pass@localhost:5433/lushlyst_db"
OPENAI_API_KEY="sk-your-key-here"
```

5. Start the PostgreSQL database using Docker:

```bash
docker run -d \
  --name lushlyst-db \
  -e POSTGRES_USER=lushlyst_user \
  -e POSTGRES_PASSWORD=lushlyst_pass \
  -e POSTGRES_DB=lushlyst_db \
  -p 5433:5432 \
  postgres:16
```

6. Initialize the database schema:

```bash
python -m data.database
```

7. Run the ETL pipeline to cache chemical data:

```bash
python -m data.etl_pipeline
```

8. Start the backend API:

```bash
uvicorn api.main:app --reload --port 8000
```

9. Start the frontend UI in a new terminal:

```bash
streamlit run ui/app.py
```

## API Usage

The backend exposes a REST API. Here is how to trigger an evaluation:

**Endpoint:** `POST /api/v1/evaluate`

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
  "input_text": "Mixed 50ml of H2SO4 with some acetone and toluene"
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "input_text": "Mixed 50ml of H2SO4 with some acetone and toluene",
  "extracted_chemicals": ["acetone", "toluene"],
  "overall_risk_score": 77.5,
  "chemical_details": [
    {
      "name": "acetone",
      "total_score": 75,
      "acute_health": 30,
      "flammability": 0,
      "environmental": 20,
      "volatility": 15,
      "sustainability": 10
    }
  ]
}
```

## Project Structure

```
lushlyst/
├── api/                  # FastAPI routes, dependencies, and main entrypoint
├── core/                 # Deterministic EHS scoring logic and PubChem client
├── data/                 # SQLAlchemy models, Pydantic schemas, and ETL pipeline
├── ai/                   # OpenAI service, prompt versioning, and cost tracking
├── evaluation/           # LLM accuracy test suite (JSONL datasets)
├── ui/                   # Streamlit frontend application
├── tests/                # Pytest unit and integration tests
├── docker-compose.yml    # Orchestrates Postgres, API, and UI
├── Dockerfile            # Multi-stage build for the FastAPI app
└── requirements.txt      # Python dependencies
```

**Note:** The `.env` file, virtual environments (`.venv`), and Python cache folders (`__pycache__`) are excluded from version control via `.gitignore`.

## Scope and Limitations

This platform quantifies chemical risk using a deterministic 5-criteria EHS matrix and LLM-based molecular extraction. It is designed for laboratory safety assessments and educational purposes.

It does **not** provide:
- Regulatory compliance advice (OSHA, REACH)
- Medical toxicology consultation
- Real-time exposure monitoring

The scoring matrix is a proxy for true EHS risk and relies on the availability of experimental data in the PubChem database.
