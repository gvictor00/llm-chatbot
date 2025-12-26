# LLM Chatbot with RAG

A FastAPI-based chatbot application with Retrieval-Augmented Generation (RAG) capabilities for document processing and CI&T Flow API integration.

## Features

- 📄 Document loading and processing (TXT, PDF, DOCX)
- 🔍 RAG-based document retrieval
- 🚀 FastAPI REST API
- 🔗 CI&T Flow API integration
- 📊 Document statistics and metadata extraction
- 🛡️ Secure configuration management

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd llm-chatbot
```

### 2. Create a virtual environment
```bash
python -m venv venv

# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure the application

- Create a `config.yaml` file in the `src/config/` directory with the following structure:
```yaml
# Copy the example configuration
cp src/config/config-example.yaml src/config/config.yaml

# Edit the configuration file with your actual values
nano src/config/config.yaml  # or use your preferred editor
```

### 5. Create documents directory
```bash
mkdir -p files
# Add your documents (TXT, PDF, DOCX) to the 'files' directory
echo "Place your documents in the 'files' directory." > files/test.txt
```

### 6. Run the application
```bash
# Using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Or using the run script
python run.py
```

The API will be available at http://127.0.0.1:8000

### 7. API Documentation

| Method | Endpoint | Description | 
|--------|----------|-------------| 
| GET | / | Health check endpoint | 
| GET | /health | Check Flow API connection status | 
| GET | /load_documents | Load and process RAG documents | 
| GET | /documents/stats | Get document statistics |

#### Example API Request

```bash
# Health check
curl http://127.0.0.1:8000/

# Load documents
curl http://127.0.0.1:8000/load_documents

# Get document statistics
curl http://127.0.0.1:8000/documents/stats
```

#### Configuration

```
client:
  client_id: "YOUR_CLIENT_ID_HERE"         # Your Flow API client ID
  client_secret: "YOUR_CLIENT_SECRET_HERE" # Your Flow API client secret
  tenant: "YOUR_TENANT_HERE"               # Your tenant identifier
  base_url: "YOUR_BASE_URL_HERE"           # Flow API base URL

rag:
  documents_path: "files"                  # Path to your documents folder
  supported_file_types:                    # Supported document types
    - ".txt"
    - ".pdf"
    - ".docx"
  recurse_folders: false       
  ```

## Project Structure

```
llm-chatbot/
├── src/
│   ├── config/
│   │   ├── config.yaml          # Your configuration (not in git)
│   │   ├── config-example.yaml  # Configuration template
│   │   └── config.py            # Configuration loader
│   ├── flow_api/
│   │   └── flow_client.py       # Flow API client
│   ├── rag/
│   │   ├── embedder.py          # Document embedding logic
│   │   ├── loader.py            # Document loading logic
│   │   └── models.py            # Data models
│   └── main.py                  # FastAPI application
├── files/                       # Document storage (not in git)
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Development

### Adding New Document Types

To add support for new document types:

1. Update supported_file_types in your config
2. Add a new loader in src/rag/loader.py
3. Install any required dependencies

## Security Notes

Security Notes
⚠️ Important Security Considerations:

- Never commit `config.yaml` files containing real credentials to version control
- Use environment variables for production deployments
- Keep the `files/` directory in `.gitignore` to avoid committing sensitive documents
- Regularly rotate API keys and secrets
- Use HTTPS in production environments