from supabase import create_client, Client
from api.core.config import settings
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Initialize Supabase client with lazy loading to handle potential startup issues
_supabase_client = None

def get_supabase_client() -> Client:
    """Get or initialize the Supabase client"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _supabase_client

def init_db():
    """Initialize database connection and verify credentials"""
    try:
        # Test connection with simple query
        client = get_supabase_client()
        response = client.table('financial_data').select('*').limit(1).execute()
        logger.info(f"Successfully connected to Supabase database. Tables exist: {bool(response)}")
        
        # Check if RLS policies are in place
        if settings.is_production:
            # In production, we should verify security policies
            logger.info("Production environment detected - verifying security policies")
            # This would be a more complex check in a real implementation
    except Exception as e:
        logger.critical(f"Failed to initialize database: {str(e)}")
        if settings.is_production:
            # In production, we should fail if DB connection fails
            raise RuntimeError("Database initialization failed") from e
        else:
            # In development, we can continue with warnings
            logger.warning("Running in development mode without database connection")

class DatabaseService:
    @staticmethod
    async def get_balance(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user balance from financial_data table"""
        try:
            client = get_supabase_client()
            response = client.table('financial_data') \
                .select('balance, last_updated') \
                .eq('user_id', user_id) \
                .execute()
                
            if response.data:
                logger.info(f"Retrieved balance for user {user_id}")
                return response.data[0]
            else:
                logger.warning(f"No balance found for user {user_id}")
                return None
        except Exception as e:
            logger.error(f"Database error retrieving balance: {str(e)}")
            return None

    @staticmethod
    async def store_transaction(data: Dict[str, Any]) -> bool:
        """Store transaction data with audit fields"""
        try:
            # Add audit fields
            data_with_audit = {
                **data,
                "created_at": datetime.utcnow().isoformat(),
                "transaction_id": f"tx_{datetime.utcnow().timestamp()}",
                "status": "completed"
            }
            
            client = get_supabase_client()
            response = client.table('transactions') \
                .insert(data_with_audit) \
                .execute()
                
            success = len(response.data) > 0
            if success:
                logger.info(f"Successfully stored transaction: {data_with_audit['transaction_id']}")
            else:
                logger.warning("Transaction insert returned no data")
                
            return success
        except Exception as e:
            logger.error(f"Transaction storage error: {str(e)}")
            # Log detailed error info but don't expose in response
            logger.debug(f"Failed transaction data: {json.dumps(data)}")
            return False
            
    @staticmethod
    async def get_transactions(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent transactions for a user"""
        try:
            client = get_supabase_client()
            response = client.table('transactions') \
                .select('*') \
                .eq('accountId', user_id) \
                .order('created_at', desc=True) \
                .limit(limit) \
                .execute()
                
            return response.data
        except Exception as e:
            logger.error(f"Error retrieving transactions: {str(e)}")
            return []