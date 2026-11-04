# Documents Q&A

A RAG backend for asking questions over your own PDF and text documents. Answers are generated strictly from the retrieved content, with Arabic and English prompt templates and swappable LLM and vector DB providers.

## Overview

1. **Upload** a file to a project.
2. **Process** it into chunks.
3. **Index** the chunks as embeddings in the vector DB.
4. **Ask** a question and get an answer grounded in the retrieved chunks.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/data/upload/{project_id}` | Upload a file |
| POST | `/api/v1/data/process/{project_id}` | Split files into chunks |
| POST | `/api/v1/nlp/index/push/{project_id}` | Embed and index chunks |
| GET | `/api/v1/nlp/index/info/{project_id}` | Get collection info |
| POST | `/api/v1/nlp/index/query/{project_id}` | Semantic search |
| POST | `/api/v1/nlp/index/answer/{project_id}` | RAG answer |

## Requirements

- Python 3.10
- Docker and Docker Compose

#### Install system dependencies

```
sudo apt update
sudo apt install libpq-dev gcc python3-dev
```

#### Install Python using MiniConda

1. Download and install MiniConda from [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)
2. Create a new environment:

```
$ conda create -n documents-qa python=3.10
```

3. Activate the environment:

```
$ conda activate documents-qa
```

## Installation

### Install the required packages

```
$ cd src
$ pip install -r requirements.txt
```

### Setup the environment variables

```
$ cp .env.example .env
```

Set your values in the `.env` file, like `GROQ_API_KEY` and `COHERE_API_KEY`.

### Run Alembic Migration

```
$ cd src/models/db_schemes/rag
$ cp alembic.ini.example alembic.ini
```

Update `sqlalchemy.url` in `alembic.ini` with your database credentials, then run:

```
$ alembic upgrade head
```

## Run Docker Compose Services

```
$ cd docker/env
$ cp .env.app.example .env.app
$ cp .env.postgres.example .env.postgres
$ cp .env.grafana.example .env.grafana
$ cp .env.postgres-exporter.example .env.postgres-exporter

$ cd ../rag
$ cp alembic.ini.example alembic.ini
```

- update the `.env.*` files with your credentials

```
$ cd docker
$ sudo docker compose up --build -d
```

Migrations run automatically when the `fastapi` container starts.

## Access Services

- **FastAPI**: [http://localhost:8000](http://localhost:8000) (docs at `/docs`)
- **Nginx**: [http://localhost](http://localhost)
- **Grafana**: [http://localhost:3000](http://localhost:3000)
- **Prometheus**: [http://localhost:9090](http://localhost:9090)
- **Qdrant**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

## Run the FastAPI server (Development Mode)

Start the database first, then run the app:

```
$ cd docker
$ sudo docker compose up -d pgvector
$ cd ../src
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## Deployment

Every push to `main` triggers the GitHub Actions workflow, which connects to the server over SSH, pulls the latest code, and restarts the Docker Compose stack through `rag.service`.