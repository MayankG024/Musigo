# Musigo

An intelligent music discovery platform powered by AI and RAG (Retrieval-Augmented Generation) technology. Discover music through natural language queries, get personalized recommendations, and explore music in entirely new ways.

## 🎵 Features

- **🔓 No Authentication Required**: Seamless experience with instant access to all features
- **🗣️ Natural Language Music Discovery**: Search for music using descriptions like "upbeat songs for a morning workout" or "melancholic jazz for a rainy day"
- **🤖 AI-Powered Recommendations**: Get personalized music suggestions based on listening patterns
- **🔍 Semantic Search**: Find music based on mood, energy, tempo, and other audio features
- **📝 Smart Playlists**: Create and manage playlists with automatic ordering
- **📊 Audio Feature Analysis**: Extract and analyze musical features from audio files
- **🎨 Modern UI**: Beautiful, responsive interface built with Next.js and Tailwind CSS
- **⚡ Public Demo Mode**: All users share a common experience - perfect for demos and public deployments

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: ORM for database management
- **ChromaDB**: Vector database for semantic search
- **LangChain**: Framework for building AI applications
- **Sentence Transformers**: For generating music embeddings
- **Librosa**: Audio feature extraction
- **Celery + Redis**: Background task processing

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching
- **Zustand**: State management
- **Framer Motion**: Animations

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- Redis (optional, for background tasks)
- PostgreSQL (optional, SQLite used by default)

## 🚀 Quick Start

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the API server:
```bash
python -m api.main
# or
uvicorn api.main:app --reload --port 8000
```

The API will be available at http://localhost:8000
API documentation: http://localhost:8000/docs

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Create a `.env.local` file:
```bash
cp .env.local.example .env.local
# Edit .env.local if needed
```

4. Run the development server:
```bash
npm run dev
# or
yarn dev
```

The app will be available at http://localhost:3000

## 📁 Project Structure

```
ai-music-discovery-platform/
├── backend/
│   ├── api/              # FastAPI application
│   │   ├── routers/      # API endpoints
│   │   └── core/         # Core configurations
│   ├── models/           # Database models
│   ├── rag_system/       # RAG and vector search
│   ├── services/         # Business logic
│   ├── utils/            # Utility functions
│   └── tests/            # Unit tests
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js app router
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom hooks
│   │   └── lib/          # Utility libraries
│   └── public/           # Static assets
├── data/                 # Data storage
├── scripts/              # Automation scripts
└── docs/                 # Documentation
```

## 🔧 Development

### Running Tests

Backend:
```bash
cd backend
python -m pytest tests/ -v
```

Frontend:
```bash
cd frontend
npm test
```

### Code Formatting

Backend:
```bash
black backend/
flake8 backend/
```

Frontend:
```bash
npm run lint
npm run format
```

## 🎯 Usage Examples

### Discover Music with Natural Language

```python
# API Request
POST /api/discovery/discover
{
  "query": "energetic electronic music for working out",
  "limit": 10
}
```

### Get Recommendations

```python
# API Request
POST /api/discovery/recommend
{
  "song_ids": ["song1", "song2", "song3"],
  "limit": 20
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

No licensing as of now!

## 🙏 Acknowledgments

- OpenAI for language models
- Spotify Web API for music metadata
- The open-source community for amazing tools and libraries
