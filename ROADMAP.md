# Aurevia Roadmap

This roadmap outlines the development phases of the Aurevia platform.

## ✅ Completed (MVP)

- **Frontend Foundation**: React 19 + Vite setup with Tailwind CSS and Zustand state management.
- **Backend Architecture**: FastAPI setup, SQLAlchemy ORM, and database configurations.
- **Authentication**: JWT-based secure login and registration flows.
- **Journaling System**: Secure endpoints for users to log and manage entries.
- **AI Service Foundation**: Separate FastAPI microservice for intelligence processing.
- **AI Chat Companion**: Base integration for conversational support with a lightweight safety/crisis keyword interceptor.
- **NLP Text Pipeline**: Support for text evaluation using `distilbert` (Demo and Real modes).
- **Audio Pipeline Framework**: Scaffolding for audio feature extraction (`whisper-tiny`).
- **Embedding Support**: RAG capabilities enabled via `sentence-transformers`.

## 🚧 Current Development

- Hardening the internal RPC connection between the Core Backend and AI Service.
- Refining frontend data visualizations (Recharts) and mapping components (Leaflet) for caseworker dashboards.
- Expanding the test suite coverage across backend services.

## 🔮 Future Work

*Note: The following features represent our long-term vision for Aurevia but are not currently implemented.*

- **Production Deployment Strategy**: Container orchestration (Kubernetes) and CI/CD pipelines.
- **Advanced Background Processing**: Integration with Redis and Celery to handle heavy asynchronous AI tasks and notification queues.
- **Real-Time Communication**: WebSocket support for live chat streaming and instant caseworker alerts.
- **Advanced Intelligence**: Stronger, clinically-informed risk modeling and dynamic case prioritization algorithms.
- **Comprehensive Admin Dashboard**: Full reporting and analytics suite for the Ministry of Social Justice and Empowerment (MoSJE).
- **Multi-lingual Support**: Expanding NLP and Audio pipelines to support regional Indian languages effectively.
