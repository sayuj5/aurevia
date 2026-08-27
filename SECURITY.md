# Security

Security and privacy are paramount for Aurevia given the sensitive nature of the problem statement and the vulnerable populations it serves. 

## Security Philosophy
Aurevia is designed with defense-in-depth principles. While this is a hackathon project, we strive to implement robust security practices for authentication, data handling, and API communication.

## Authentication & Authorization
- **JWT Authentication**: All protected endpoints require a Bearer JSON Web Token (JWT).
- **Password Practices**: Passwords are never stored in plaintext. We use `passlib` with `bcrypt` for strong, salted cryptographic hashing.
- **Authorization**: Role-based routing isolates user data from caseworker/administrative views. Users can only access their own journal entries and chat histories.

## Secret Management
- **Environment Variables**: All secrets (database URLs, API keys, JWT secret keys) are managed via `.env` files.
- **No Hardcoded Secrets**: Secrets are never hardcoded in the repository. The `.env.example` files are provided as templates only.

## API Security
- **Input Validation**: All API inputs are strictly validated using `Pydantic` schemas in FastAPI to prevent injection attacks and ensure data integrity.
- **CORS**: Cross-Origin Resource Sharing is restricted via backend configuration to approved frontend origins.

## File & Audio Upload Considerations
- Audio and file uploads (where implemented in the AI service) are processed in isolated pipelines.
- Temporary files are validated for size and MIME type before processing and are discarded securely after extraction.

## AI-Specific Security Considerations
- **Data Privacy in AI**: When using the Real AI Mode, models run *locally* on the host server. Sensitive user journal entries and chat texts are not sent to third-party APIs unless explicitly configured by the deployment administrator.
- **Safety Layer**: A lightweight keyword safety layer is implemented in the chat service (`app/services/ai_service.py`) to intercept crisis-related language and provide emergency resource messaging.

## Logging Considerations
- Request logging is handled by middleware to aid in debugging.
- **PII Protection**: Care is taken to ensure that Personally Identifiable Information (PII) and sensitive journal/chat content are not written to standard application logs.

## Dependency Security
- Dependencies are locked in `requirements.txt` and `package-lock.json` to ensure reproducible and verifiable builds.

## Reporting Security Issues
As a hackathon project, there is no formal bug bounty program. However, if you discover a security vulnerability, please open an issue in the repository or contact the project members directly. Do not exploit vulnerabilities against any hosted demo instances.
