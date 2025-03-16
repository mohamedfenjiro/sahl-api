# Communication Between Sahl API and Sahl API Sandbox

This document explains how the Sahl API and Sahl API Sandbox repositories communicate with each other.

## Overview

The Sahl API and Sahl API Sandbox are designed to work together, with the Sandbox providing a user-friendly interface for testing the API endpoints. The communication between the two is handled via HTTP requests from the Sandbox to the API.

## Communication Flow

1. The Sandbox makes HTTP requests to the API endpoints
2. The API processes the requests and returns responses
3. The Sandbox displays the responses to the user

## API Configuration

The API is configured to allow cross-origin requests from the Sandbox domain. This is done in the `api/core/config.py` file:

```python
# CORS settings
CORS_ORIGINS: list[str] = [
    "https://sahlfinancial.com",
    "https://app.sahlfinancial.com",
    "https://sahl-api-sandbox.onrender.com",
    "http://localhost:8080"
]
```

This allows the Sandbox to make requests to the API from any of these domains.

## Sandbox Configuration

The Sandbox is configured to make requests to the API at the URL specified by the `API_URL` environment variable. This is set in the `render.yaml` file:

```yaml
envVars:
  - key: API_URL
    value: https://sahl-bank-api.onrender.com
```

At runtime, the `entrypoint.sh` script replaces the API URL in the HTML file with the value from the environment variable:

```bash
# Replace any API URL in the index.html file with the environment variable
sed -i "s|value=\"https://[^\"]*\"|value=\"$API_URL\"|g" /usr/share/nginx/html/index.html
```

## Authentication

The API requires client credentials for authentication. The Sandbox includes these credentials in the request headers:

```javascript
const headers = {
    'X-Client-ID': clientId,
    'X-Client-Secret': clientSecret,
    'Content-Type': 'application/json'
};
```

## Deployment Considerations

When deploying the two repositories separately, ensure that:

1. The API's CORS settings include the domain of the deployed Sandbox
2. The Sandbox's API_URL environment variable points to the deployed API
3. Both services are accessible to each other (no network restrictions)

## Testing the Communication

To test the communication between the two repositories:

1. Deploy both repositories to their respective URLs
2. Open the Sandbox in a web browser
3. Use the Sandbox to make requests to the API
4. Verify that the responses are displayed correctly

## Troubleshooting

If the Sandbox cannot communicate with the API:

1. Check that the API URL is correct in the Sandbox
2. Verify that the API's CORS settings include the Sandbox domain
3. Ensure there are no network restrictions blocking the connection
4. Check the browser console for any error messages