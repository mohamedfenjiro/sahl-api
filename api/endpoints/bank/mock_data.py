"""
Mock data for the Sahl Bank API
"""
import datetime
import random
from typing import Dict, List, Any

# Mock bank accounts
ACCOUNTS = {
    "acc_1": {
        "account_id": "acc_1",
        "balances": {
            "available": 5000.75,
            "current": 5100.75,
            "limit": None,
            "iso_currency_code": "MAD",
            "unofficial_currency_code": None
        },
        "mask": "1234",
        "name": "Compte Courant Al Amal",
        "official_name": "Compte Courant Premium Al Amal",
        "subtype": "checking",
        "type": "depository"
    },
    "acc_2": {
        "account_id": "acc_2",
        "balances": {
            "available": 12500.00,
            "current": 12500.00,
            "limit": None,
            "iso_currency_code": "MAD",
            "unofficial_currency_code": None
        },
        "mask": "5678",
        "name": "Compte Épargne Al Baraka",
        "official_name": "Compte Épargne Rendement Élevé Al Baraka",
        "subtype": "savings",
        "type": "depository"
    },
    "acc_3": {
        "account_id": "acc_3",
        "balances": {
            "available": 7500.00,
            "current": 7500.00,
            "limit": 10000.00,
            "iso_currency_code": "MAD",
            "unofficial_currency_code": None
        },
        "mask": "9012",
        "name": "Carte de Crédit Al Yosr",
        "official_name": "Carte de Crédit Récompenses Al Yosr",
        "subtype": "credit card",
        "type": "credit"
    }
}

# Mock account numbers (Moroccan format)
ACCOUNT_NUMBERS = {
    "acc_1": {
        "account": "007780000123456789012345",
        "account_id": "acc_1",
        "routing": "007780000",  # Attijariwafa Bank code
        "wire_routing": "BCMAMAMC"  # Moroccan bank SWIFT code
    },
    "acc_2": {
        "account": "013450000234567890123456",
        "account_id": "acc_2",
        "routing": "013450000",  # BMCE Bank code
        "wire_routing": "BMCEMAMC"  # Moroccan bank SWIFT code
    },
    "acc_3": {
        "account": "022780000345678901234567",
        "account_id": "acc_3",
        "routing": "022780000",  # Crédit Agricole du Maroc code
        "wire_routing": "CNCARMMR"  # Moroccan bank SWIFT code
    }
}

# Mock transactions
def generate_transactions(account_id: str, count: int = 20) -> List[Dict[str, Any]]:
    """Generate mock transactions for an account"""
    transactions = []
    
    # Get account details
    account = ACCOUNTS.get(account_id)
    if not account:
        return []
    
    # Transaction categories
    categories = [
        ["Food and Drink", "Restaurants"],
        ["Food and Drink", "Cafés"],
        ["Shops", "Souk"],
        ["Shops", "Épicerie"],
        ["Transfer", "Dépôt"],
        ["Transfer", "Retrait"],
        ["Service", "Abonnement"],
        ["Travel", "Royal Air Maroc"],
        ["Travel", "Riads"],
        ["Payment", "Carte de Crédit"],
        ["Recreation", "Divertissement"],
        ["Family", "Aïd al-Fitr"],
        ["Family", "Aïd al-Adha"]
    ]
    
    # Transaction names
    merchant_names = [
        "Marjane", "Carrefour Market", "Aswak Assalam", "Café Maure",
        "Hammam Traditionnel", "Patisserie Marocaine", "Pharmacie Atlas",
        "Royal Air Maroc", "Riad Al Andalous", "Maroc Telecom",
        "INWI", "ONEE", "LYDEC", "Salle de Sport Casablanca",
        "Electroplanet", "Acima", "Virement Salaire",
        "Souk El Had", "Artisanat Maroc", "Fès Medina Shop",
        "Tanger Med Port", "Marrakech Henna Art"
    ]
    
    # Generate transactions
    today = datetime.datetime.now()
    for i in range(count):
        # Random date within the last 30 days
        days_ago = random.randint(0, 30)
        date = today - datetime.timedelta(days=days_ago)
        
        # Random amount (negative for expenses, positive for income)
        is_income = random.random() < 0.2  # 20% chance of income
        amount = round(random.uniform(5, 500), 2)
        if not is_income:
            amount = -amount
            
        # Select category and merchant
        category = random.choice(categories)
        merchant = random.choice(merchant_names)
        
        # Create transaction
        transaction = {
            "transaction_id": f"tx_{account_id}_{i}",
            "account_id": account_id,
            "amount": amount,
            "date": date.strftime("%Y-%m-%d"),
            "datetime": date.isoformat(),
            "name": merchant,
            "merchant_name": merchant,
            "pending": False,
            "category": category,
            "location": {
                "address": random.choice([
                    "Avenue Mohammed V, 123",
                    "Rue Allal Ben Abdellah, 45",
                    "Boulevard Anfa, 78",
                    "Quartier Habous, 15",
                    "Avenue Hassan II, 67",
                    "Rue Bab Agnaou, 22",
                    "Boulevard Zerktouni, 90"
                ]),
                "city": random.choice([
                    "Casablanca", "Rabat", "Marrakech", "Fès",
                    "Tanger", "Agadir", "Meknès", "Oujda",
                    "Tétouan", "Essaouira", "Chefchaouen"
                ]),
                "region": random.choice([
                    "Casablanca-Settat", "Rabat-Salé-Kénitra", "Marrakech-Safi",
                    "Fès-Meknès", "Tanger-Tétouan-Al Hoceima", "Souss-Massa"
                ]),
                "postal_code": random.choice([
                    "20000", "10000", "40000", "30000",
                    "90000", "80000", "50000", "60000"
                ]),
                "country": "MA",
                "lat": random.uniform(31.0, 35.8),
                "lon": random.uniform(-10.0, -1.0)
            }
        }
        
        transactions.append(transaction)
    
    # Sort by date (newest first)
    transactions.sort(key=lambda x: x["date"], reverse=True)
    
    return transactions

# Mock statements
def generate_statements(account_id: str, count: int = 6) -> List[Dict[str, Any]]:
    """Generate mock statements for an account"""
    statements = []
    
    # Get account details
    account = ACCOUNTS.get(account_id)
    if not account:
        return []
    
    # Generate statements (monthly)
    today = datetime.datetime.now()
    current_month = today.replace(day=1)
    
    for i in range(count):
        # Statement for previous months
        statement_date = current_month - datetime.timedelta(days=1)
        current_month = current_month.replace(month=current_month.month-1 if current_month.month > 1 else 12)
        if current_month.month == 12:
            current_month = current_month.replace(year=current_month.year-1)
        
        # Random balance
        ending_balance = round(random.uniform(1000, 10000), 2)
        starting_balance = round(ending_balance - random.uniform(-1000, 1000), 2)
        
        # Create statement
        statement = {
            "statement_id": f"stmt_{account_id}_{i}",
            "account_id": account_id,
            "start_date": current_month.strftime("%Y-%m-%d"),
            "end_date": statement_date.strftime("%Y-%m-%d"),
            "starting_balance": starting_balance,
            "ending_balance": ending_balance,
            "total_deposits": round(random.uniform(500, 3000), 2),
            "total_withdrawals": round(random.uniform(500, 3000), 2),
            "pdf_url": f"/bank/statements/{account_id}/{statement_date.strftime('%Y-%m')}.pdf"
        }
        
        statements.append(statement)
    
    return statements

# Mock items
ITEMS = {
    "item_1": {
        "item_id": "item_1",
        "institution_id": "ins_sahl_bank_maroc",
        "available_products": ["auth", "transactions", "statements"],
        "billed_products": ["auth", "transactions", "statements"],
        "consent_expiration_time": None,
        "error": None,
        "institution_name": "Banque Sahl Al-Maghrib",
        "webhook": "https://webhook.sahlfinancial.com"
    }
}

# Test user credentials
USER_CREDENTIALS = {
    "username1234": "password1234"
}

# Client credentials for multitenancy
CLIENT_CREDENTIALS = {
    "client_123456": "secret_abcdef123456",
    "client_654321": "secret_fedcba654321"
}

# Map access tokens to items and accounts
ACCESS_TOKEN_MAP = {
    "access-token-1": {
        "item_id": "item_1",
        "accounts": ["acc_1", "acc_2"],
        "user_id": "username1234"
    },
    "access-token-2": {
        "item_id": "item_1",
        "accounts": ["acc_3"],
        "user_id": "username1234"
    }
}

# Function to get accounts by access token
def get_accounts_by_token(access_token: str) -> List[Dict[str, Any]]:
    """Get accounts associated with an access token"""
    token_data = ACCESS_TOKEN_MAP.get(access_token)
    if not token_data:
        return []
    
    return [ACCOUNTS[acc_id] for acc_id in token_data["accounts"] if acc_id in ACCOUNTS]

# Function to get account numbers by access token
def get_account_numbers_by_token(access_token: str) -> Dict[str, List[Dict[str, Any]]]:
    """Get account numbers associated with an access token"""
    token_data = ACCESS_TOKEN_MAP.get(access_token)
    if not token_data:
        return {"ach": []}
    
    account_numbers = []
    for acc_id in token_data["accounts"]:
        if acc_id in ACCOUNT_NUMBERS:
            account_numbers.append(ACCOUNT_NUMBERS[acc_id])
    
    return {"ach": account_numbers}

# Function to get item by access token
def get_item_by_token(access_token: str) -> Dict[str, Any]:
    """Get item associated with an access token"""
    token_data = ACCESS_TOKEN_MAP.get(access_token)
    if not token_data or token_data["item_id"] not in ITEMS:
        return {}
    
    return ITEMS[token_data["item_id"]]

# Function to get transactions by access token
def get_transactions_by_token(access_token: str, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
    """Get transactions associated with an access token"""
    token_data = ACCESS_TOKEN_MAP.get(access_token)
    if not token_data:
        return {"transactions": [], "accounts": []}
    
    accounts = [ACCOUNTS[acc_id] for acc_id in token_data["accounts"] if acc_id in ACCOUNTS]
    
    all_transactions = []
    for acc_id in token_data["accounts"]:
        transactions = generate_transactions(acc_id, 20)
        
        # Filter by date if provided
        if start_date and end_date:
            transactions = [t for t in transactions if start_date <= t["date"] <= end_date]
            
        all_transactions.extend(transactions)
    
    # Sort by date (newest first)
    all_transactions.sort(key=lambda x: x["date"], reverse=True)
    
    return {
        "accounts": accounts,
        "transactions": all_transactions,
        "item": get_item_by_token(access_token),
        "total_transactions": len(all_transactions)
    }

# Function to get statements by access token
def get_statements_by_token(access_token: str) -> Dict[str, Any]:
    """Get statements associated with an access token"""
    token_data = ACCESS_TOKEN_MAP.get(access_token)
    if not token_data:
        return {"statements": [], "accounts": []}
    
    accounts = [ACCOUNTS[acc_id] for acc_id in token_data["accounts"] if acc_id in ACCOUNTS]
    
    all_statements = []
    for acc_id in token_data["accounts"]:
        statements = generate_statements(acc_id, 6)
        all_statements.extend(statements)
    
    # Sort by date (newest first)
    all_statements.sort(key=lambda x: x["end_date"], reverse=True)
    
    return {
        "accounts": accounts,
        "statements": all_statements,
        "item": get_item_by_token(access_token),
        "total_statements": len(all_statements)
    }