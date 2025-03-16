from fastapi import Request, HTTPException, Depends, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Dict, Optional, Tuple
import secrets
import time
import logging
import hashlib
import hmac
import os

logger = logging.getLogger(__name__)

# In a real application, these would be stored in a secure database
# and not hardcoded in the source code
CLIENT_CREDENTIALS = {
    "client_123456": "secret_abcdef123456",
    "client_654321": "secret_fedcba654321",
}

class APIKeyAuth:
    def __init__(self):
        self.security = HTTPBasic()
        
    async def __call__(
        self, 
        request: Request,
        client_id: Optional[str] = Header(None, alias="X-Client-ID"),
        client_secret: Optional[str] = Header(None, alias="X-Client-Secret")
    ) -> Tuple[str, str]:
        """
        Validate client credentials from headers
        """
        if not client_id or not client_secret:
            logger.warning("Missing authentication credentials")
            raise HTTPException(
                status_code=401,
                detail="Missing authentication credentials",
                headers={"WWW-Authenticate": "Basic"},
            )
            
        if client_id not in CLIENT_CREDENTIALS or CLIENT_CREDENTIALS[client_id] != client_secret:
            logger.warning(f"Invalid credentials for client_id: {client_id}")
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Basic"},
            )
            
        # Log successful authentication
        logger.info(f"Successful authentication for client_id: {client_id}")
        return client_id, client_secret

# Create an instance to use as a dependency
api_key_auth = APIKeyAuth()

def generate_link_token(client_id: str, user_id: str) -> Dict:
    """
    Generate a secure link token for client-side initialization
    """
    # In a real application, this would be more sophisticated
    timestamp = int(time.time())
    random_part = secrets.token_hex(16)
    
    # Create a unique token that expires in 30 minutes
    raw_token = f"{client_id}:{user_id}:{timestamp}:{random_part}"
    
    # In a real application, this would use a proper signing key
    signature = hmac.new(
        key=os.environ.get("JWT_SECRET", "your_jwt_secret_here").encode(),
        msg=raw_token.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return {
        "link_token": f"{raw_token}:{signature}",
        "expiration": timestamp + 1800,  # 30 minutes
        "request_id": f"req_{random_part[:8]}"
    }

def exchange_public_token(public_token: str) -> Dict:
    """
    Exchange a public token for an access token
    """
    # In a real application, this would validate the public token
    # and generate a secure access token
    
    # For this mock implementation, we'll just generate a random token
    access_token = f"access-{secrets.token_hex(16)}"
    item_id = f"item-{secrets.token_hex(8)}"
    
    return {
        "access_token": access_token,
        "item_id": item_id,
        "request_id": f"req_{secrets.token_hex(8)}"
    }

def validate_access_token(access_token: str) -> bool:
    """
    Validate an access token
    """
    # In a real application, this would check if the token is valid
    # For this mock implementation, we'll just check if it starts with "access-"
    return access_token.startswith("access-")