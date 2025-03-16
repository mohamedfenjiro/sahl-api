# Sahl API

This repository contains the main Sahl API service, which provides backend functionality for financial data processing.

## Features

- PDF parsing for financial documents
- Data storage and retrieval
- Web scraping for financial data
- Bank API for account information, transactions, and statements

## Getting Started

### Prerequisites

- Python 3.9+
- Docker (optional)
- Supabase account (for database)

### Environment Setup

1. Copy the example environment file:
   ```
   cp .env.example .env
   ```

2. Update the environment variables in the `.env` file:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ENVIRONMENT=development
   ```

### Running Locally

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the API:
   ```
   uvicorn main:app --reload
   ```

3. Access the API at http://localhost:8000

### Running with Docker

1. Build the Docker image:
   ```
   docker build -t sahl-api .
   ```

2. Run the container:
   ```
   docker run -p 8000:8000 --env-file .env sahl-api
   ```

## Deployment

### Deploying to Render

Use the provided script to deploy to Render:

```
./deploy_to_render.sh
```

### Deploying to Supabase

Use the provided script to deploy the Supabase functions:

```
./deploy_to_supabase.sh
```

## API Documentation

When running in development mode, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Communication with Sandbox

This API is designed to work with the [Sahl API Sandbox](https://github.com/yourusername/sahl-api-sandbox), which provides a user-friendly interface for testing the API endpoints.

The API allows cross-origin requests from the following domains:
- https://sahlfinancial.com
- https://app.sahlfinancial.com
- https://sahl-api-sandbox.onrender.com
- http://localhost:8080

## License

[Your License Here]