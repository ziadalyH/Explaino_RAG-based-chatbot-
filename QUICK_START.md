# Quick Start Guide - Explaino RAG

Get your RAG system running in 5 minutes!

## Prerequisites Checklist

- [ ] Docker & Docker Compose installed
- [ ] OpenAI API key ready
- [ ] 4GB RAM available
- [ ] 2GB disk space free

## Step 1: Clone & Setup (1 minute)

```bash
# Clone the repository
git clone https://github.com/ziadalyH/Explaino_RAG_AIFounding.git
cd Explaino_RAG_AIFounding

# Create environment file
cp .env.example .env
```

## Step 2: Configure (1 minute)

Edit `.env` and add your OpenAI API key:

```bash
nano .env
# or
code .env
# or
vim .env
```

**Required**: Change this line:

```
OPENAI_API_KEY=your_openai_api_key_here
```

To your actual key:

```
OPENAI_API_KEY=sk-proj-...
```

## Step 3: Start Services (2 minutes)

```bash
# Start everything with Docker Compose
docker-compose up -d

# Watch the logs (optional)
docker-compose logs -f rag-backend
```

**What's happening**:

- ✓ OpenSearch starting (vector database)
- ✓ RAG backend starting
- ✓ MPNet model downloading (~420MB, first time only)
- ✓ Indexing your data files
- ✓ System ready!

## Step 4: Add Your Data (30 seconds)

### Add Video Transcripts

Create `data/transcripts/my_video.json`:

```json
{
  "video_id": "my_first_video",
  "pdf_reference": "my_document.pdf",
  "video_transcripts": [
    { "id": 1, "timestamp": 0.0, "word": "Hello" },
    { "id": 2, "timestamp": 0.5, "word": "world" }
  ]
}
```

### Add PDF Documents

Copy your PDF files to `data/pdfs/`:

```bash
cp ~/Documents/my_document.pdf data/pdfs/
```

## Step 5: Index Your Data (1 minute)

```bash
# Rebuild index with your new data
docker-compose exec rag-backend python main.py index --rebuild
```

## Step 6: Ask Questions! (30 seconds)

```bash
# Ask your first question
docker-compose exec rag-backend python main.py query \
  --question "What is this document about?"

# Try another
docker-compose exec rag-backend python main.py query \
  --question "Explain the main concepts"
```

## Success! 🎉

You now have a working RAG system!

## Next Steps

### Customize Configuration

Edit `.env` to tune the system:

```bash
# Adjust relevance threshold (0-1)
RELEVANCE_THRESHOLD=0.5  # Lower = more results

# Change LLM model
LLM_MODEL=gpt-4o-mini  # or gpt-4, gpt-3.5-turbo

# Adjust max results
MAX_RESULTS=5  # Top-k results to return
```

### Use Python API

```python
from src.rag_system import RAGSystem
from src.config import Config

# Initialize
config = Config.from_env()
rag = RAGSystem(config)

# Ask questions
response = rag.answer_question("What is a database?")
print(response.generated_answer)
```

### Monitor System

```bash
# Check logs
docker-compose logs -f rag-backend

# Check OpenSearch health
curl http://localhost:9200/_cluster/health?pretty

# Check indexed documents
curl http://localhost:9200/rag-pdf-index/_count
curl http://localhost:9200/rag-video-index/_count
```

## Common Issues

### "Connection refused" error

```bash
# Check if OpenSearch is running
docker-compose ps

# Restart if needed
docker-compose restart opensearch
```

### "No results found"

```bash
# Check if data is indexed
curl http://localhost:9200/rag-pdf-index/_count

# Rebuild index
docker-compose exec rag-backend python main.py index --rebuild
```

### "OpenAI API error"

```bash
# Verify API key
echo $OPENAI_API_KEY

# Check it's set in .env
cat .env | grep OPENAI_API_KEY
```

## Need Help?

- 📖 **Full Documentation**: See [README.md](README.md)
- 🏗️ **Architecture Details**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/ziadalyH/Explaino_RAG_AIFounding/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ziadalyH/Explaino_RAG_AIFounding/discussions)

## Stopping the System

```bash
# Stop services
docker-compose down

# Stop and remove data (careful!)
docker-compose down -v
```

---

**Happy RAG-ing! 🚀**
