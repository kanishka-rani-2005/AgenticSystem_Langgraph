# ChatsGPT

ChatsGPT is an agentic AI chatbot built with FastAPI, LangGraph, Google Gemini, Tavily, ChromaDB, and SQLite. It supports streaming answers, web search, document question-answering, persistent chat history, and saved memories.

## Features

- Streaming AI responses in a responsive web chat interface
- Gemini model selection from the frontend
- Document upload and retrieval-augmented answers (RAG)
- Tavily web search for current information
- Per-conversation memory and chat history
- Voice dictation where supported by the browser
- Docker support and GitHub Actions deployment to EC2 via Docker Hub

## Tech stack

| Area | Technology |
| --- | --- |
| API and UI server | FastAPI, Uvicorn, Jinja2 |
| Agent orchestration | LangGraph, LangChain |
| Models and embeddings | Google Gemini |
| Web search | Tavily |
| Document search | ChromaDB |
| Conversation storage | SQLite |
| Deployment | Docker, Docker Hub, GitHub Actions, AWS EC2 |

## Prerequisites

- Python 3.11+
- A Google AI API key
- A Tavily API key
- Docker (for containerized runs and deployment)

## Local setup

```powershell
git clone <your-repository-url>
cd Multiagent-Langgraph
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_ai_api_key
TAVILY_API_KEY=your_tavily_api_key

# Optional backend fallback model.
GEMINI_MODEL=gemini-3.5-flash-lite

# Optional LangSmith tracing.
# LANGSMITH_TRACING=true
# LANGSMITH_ENDPOINT=https://api.smith.langchain.com
# LANGSMITH_API_KEY=your_langsmith_api_key
# LANGSMITH_PROJECT=chatsgpt
```

Start the application:

```powershell
python app.py
```

For auto-reload during development:

```powershell
uvicorn app:app --reload --port 8080
```

Open [http://localhost:8080](http://localhost:8080). The readiness endpoint is [http://localhost:8080/health](http://localhost:8080/health).

## Using ChatsGPT

1. Start a new conversation.
2. Choose a model from the model selector.
3. Ask a question, ask for current information, or upload a document with the `+` button.
4. After uploading, ask questions about that document in the same conversation.

Supported document types: PDF, DOCX, TXT, Markdown, Python, CSV, and JSON.

## Docker

Build the image:

```powershell
docker build -t chatsgpt:local .
```

Run the container:

```powershell
docker run --rm -p 8080:8080 `
  -e GOOGLE_API_KEY="your_google_ai_api_key" `
  -e TAVILY_API_KEY="your_tavily_api_key" `
  chatsgpt:local
```

Open [http://localhost:8080](http://localhost:8080).

## CI/CD: Docker Hub and AWS EC2

The workflow at [.github/workflows/cicd.yaml](.github/workflows/cicd.yaml) runs when code is pushed to `main`.

1. Checks Python syntax and validates the Docker build.
2. Publishes the image to Docker Hub.
3. Uses AWS credentials to confirm the target EC2 instance is running.
4. Pulls the Docker Hub image from the EC2 self-hosted GitHub Actions runner.
5. Replaces the `chatsgpt` container and verifies `/health`.

Images are stored in Docker Hub, not Amazon ECR:

```text
<DOCKER_USERNAME>/<IMAGE_NAME>:main
<DOCKER_USERNAME>/<IMAGE_NAME>:sha-<git-commit-sha>
```

### Required GitHub secrets

Configure these in **GitHub repository → Settings → Secrets and variables → Actions**.

| Secret | Purpose |
| --- | --- |
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub access token (recommended) |
| `IMAGE_NAME` | Docker Hub repository name, for example `chatsgpt` |
| `GOOGLE_API_KEY` | Google Gemini API key |
| `TAVILY_API_KEY` | Tavily API key |
| `AWS_ACCESS_KEY_ID` | AWS IAM access key for EC2 validation |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |
| `AWS_DEFAULT_REGION` | AWS region, for example `ap-south-1` |
| `EC2_INSTANCE_ID` | Target EC2 instance ID |

Optional secrets: `GEMINI_MODEL`, `LANGSMITH_TRACING`, `LANGSMITH_ENDPOINT`, `LANGSMITH_API_KEY`, and `LANGSMITH_PROJECT`.

### EC2 requirements

- Docker installed and usable by the GitHub Actions runner user
- A self-hosted GitHub Actions runner connected to this repository
- Inbound security-group access to port `8080`, or a reverse proxy in front of it
- An IAM identity allowed to run `ec2:DescribeInstances` for the target instance

The workflow creates persistent Docker volumes for chat data, uploads, and ChromaDB, so deployments do not erase conversations or documents.

## Project structure

```text
.
├── app.py                      # FastAPI routes and answer streaming
├── agent.py                    # LangGraph agent and Gemini configuration
├── tools.py                    # Search, calculator, memory, and document tools
├── rag.py                      # File ingestion and ChromaDB retrieval
├── database.py                 # SQLite chat and memory storage
├── templates/index.html        # Chat interface markup
├── static/                     # CSS and browser JavaScript
├── Dockerfile                  # Production container image
└── .github/workflows/cicd.yaml # Docker Hub + EC2 workflow
```

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | ChatsGPT web interface |
| `GET` | `/health` | Readiness check |
| `GET` | `/conversations` | Conversation list |
| `GET` | `/history/{thread_id}` | Conversation messages |
| `POST` | `/upload` | Upload and index a document |
| `POST` | `/chat/stream` | Stream an AI answer with Server-Sent Events |

## Security notes

- Never commit `.env`, API keys, Docker Hub passwords, or AWS credentials.
- Use a Docker Hub access token instead of your password.
- Limit the AWS IAM policy to the minimum required permissions.
- Put ChatsGPT behind HTTPS before exposing it publicly.
