"""
Bank API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Body, Query, Response
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

from api.core.auth_middleware import api_key_auth, generate_link_token, exchange_public_token, validate_access_token
from api.endpoints.bank.mock_data import (
    get_accounts_by_token,
    get_account_numbers_by_token,
    get_item_by_token,
    get_transactions_by_token,
    get_statements_by_token
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Link token creation endpoint
@router.post("/link/token/create")
async def create_link_token(
    request: Dict[str, Any] = Body(...),
    auth: Any = Depends(api_key_auth)
) -> Dict[str, Any]:
    """
    Create a link token for client-side initialization
    Similar to Plaid's /link/token/create endpoint
    """
    client_id, _ = auth
    
    # Validate request
    if "user" not in request or "client_user_id" not in request["user"]:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    user_id = request["user"]["client_user_id"]
    
    # Generate link token
    token_data = generate_link_token(client_id, user_id)
    
    logger.info(f"Created link token for user {user_id}")
    
    return {
        "link_token": token_data["link_token"],
        "expiration": token_data["expiration"],
        "request_id": token_data["request_id"]
    }

# Public token exchange endpoint
@router.post("/item/public_token/exchange")
async def public_token_exchange(
    request: Dict[str, Any] = Body(...),
    auth: Any = Depends(api_key_auth)
) -> Dict[str, Any]:
    """
    Exchange a public token for an access token
    Similar to Plaid's /item/public_token/exchange endpoint
    """
    # Validate request
    if "public_token" not in request:
        raise HTTPException(status_code=400, detail="Missing public_token")
    
    # Exchange public token for access token
    token_data = exchange_public_token(request["public_token"])
    
    logger.info(f"Exchanged public token for access token {token_data['access_token']}")
    
    return token_data

# Auth endpoint
@router.post("/auth/get")
async def get_auth(
    request: Dict[str, Any] = Body(...),
    auth: Any = Depends(api_key_auth)
) -> Dict[str, Any]:
    """
    Get auth data for accounts
    Similar to Plaid's /auth/get endpoint
    """
    # Validate request
    if "access_token" not in request:
        raise HTTPException(status_code=400, detail="Missing access_token")
    
    access_token = request["access_token"]
    
    # Validate access token
    if not validate_access_token(access_token):
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    # Get accounts and account numbers
    accounts = get_accounts_by_token(access_token)
    numbers = get_account_numbers_by_token(access_token)
    item = get_item_by_token(access_token)
    
    logger.info(f"Retrieved auth data for {len(accounts)} accounts")
    
    return {
        "accounts": accounts,
        "numbers": numbers,
        "item": item,
        "request_id": f"req_{datetime.now().timestamp()}"
    }

# Transactions endpoint
@router.post("/transactions/get")
async def get_transactions(
    request: Dict[str, Any] = Body(...),
    auth: Any = Depends(api_key_auth)
) -> Dict[str, Any]:
    """
    Get transactions for accounts
    Similar to Plaid's /transactions/get endpoint
    """
    # Validate request
    if "access_token" not in request:
        raise HTTPException(status_code=400, detail="Missing access_token")
    
    access_token = request["access_token"]
    
    # Validate access token
    if not validate_access_token(access_token):
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    # Get date range (default to last 30 days if not provided)
    today = datetime.now().strftime("%Y-%m-%d")
    start_date = request.get("start_date", (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
    end_date = request.get("end_date", today)
    
    # Get transactions
    transactions_data = get_transactions_by_token(access_token, start_date, end_date)
    
    logger.info(f"Retrieved {len(transactions_data['transactions'])} transactions")
    
    return {
        "accounts": transactions_data["accounts"],
        "transactions": transactions_data["transactions"],
        "item": transactions_data["item"],
        "total_transactions": transactions_data["total_transactions"],
        "request_id": f"req_{datetime.now().timestamp()}"
    }

# Statements endpoint
@router.post("/statements/get")
async def get_statements(
    request: Dict[str, Any] = Body(...),
    auth: Any = Depends(api_key_auth)
) -> Dict[str, Any]:
    """
    Get statements for accounts
    Custom Sahl Bank endpoint for retrieving statements
    """
    # Validate request
    if "access_token" not in request:
        raise HTTPException(status_code=400, detail="Missing access_token")
    
    access_token = request["access_token"]
    
    # Validate access token
    if not validate_access_token(access_token):
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    # Get statements
    statements_data = get_statements_by_token(access_token)
    
    logger.info(f"Retrieved {len(statements_data['statements'])} statements")
    
    return {
        "accounts": statements_data["accounts"],
        "statements": statements_data["statements"],
        "item": statements_data["item"],
        "total_statements": statements_data["total_statements"],
        "request_id": f"req_{datetime.now().timestamp()}"
    }

# Statement PDF endpoint
@router.get("/statements/{account_id}/{statement_date}.pdf")
async def get_statement_pdf(
    account_id: str,
    statement_date: str,
    auth: Any = Depends(api_key_auth)
) -> Response:
    """
    Get a PDF statement for an account
    """
    # Import ACCOUNTS and ACCESS_TOKEN_MAP from mock_data
    from api.endpoints.bank.mock_data import ACCOUNTS, ACCESS_TOKEN_MAP
    
    # Get account details
    token_data = ACCESS_TOKEN_MAP.get("access-token-1")  # Using a default token for demo
    if token_data and account_id in token_data["accounts"]:
        account = ACCOUNTS.get(account_id)
    else:
        account = None
        
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Create a BytesIO buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Create the PDF object using ReportLab
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add bank logo and header
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, height - 50, "BANQUE SAHL AL-MAGHRIB")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, "Statement of Account")
    
    # Add a horizontal line
    p.line(50, height - 80, width - 50, height - 80)
    
    # Add account information
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 110, "Account Information")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 130, f"Account Number: {account_id}")
    p.drawString(50, height - 145, f"Account Name: {account['name']}")
    p.drawString(50, height - 160, f"Statement Period: {statement_date}")
    
    # Add current balance
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 190, "Balance Summary")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 210, f"Current Balance: {account['balances']['current']} {account['balances']['iso_currency_code']}")
    p.drawString(50, height - 225, f"Available Balance: {account['balances']['available']} {account['balances']['iso_currency_code']}")
    
    # Add transaction table
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 255, "Transaction History")
    
    # Create transaction data
    data = [
        ["Date", "Description", "Amount", "Balance"],
        [f"{statement_date}-01", "Opening Balance", "", "5,000.00 MAD"],
        [f"{statement_date}-05", "Salary Deposit", "+8,500.00", "13,500.00 MAD"],
        [f"{statement_date}-10", "Marjane Supermarket", "-450.75", "13,049.25 MAD"],
        [f"{statement_date}-15", "ATM Withdrawal", "-1,000.00", "12,049.25 MAD"],
        [f"{statement_date}-20", "LYDEC Utility Bill", "-785.50", "11,263.75 MAD"],
        [f"{statement_date}-25", "Restaurant Payment", "-320.00", "10,943.75 MAD"],
        [f"{statement_date}-28", "Closing Balance", "", "10,943.75 MAD"]
    ]
    
    # Create the table
    table = Table(data, colWidths=[80, 200, 80, 100])
    
    # Style the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    
    table.setStyle(style)
    
    # Draw the table on the PDF
    table.wrapOn(p, width - 100, height)
    table.drawOn(p, 50, height - 400)
    
    # Add footer
    p.setFont("Helvetica", 8)
    p.drawString(50, 50, "Thank you for banking with Banque Sahl Al-Maghrib.")
    p.drawString(50, 35, "For any inquiries, please contact customer service at 0800-123456.")
    p.drawString(width - 150, 20, f"Page 1 of 1")
    
    # Save the PDF
    p.showPage()
    p.save()
    
    # Get the PDF data from the buffer
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Create response with PDF data
    headers = {
        "Content-Disposition": f"attachment; filename={account_id}_{statement_date}.pdf",
        "Content-Type": "application/pdf"
    }
    
    return Response(content=pdf_data, headers=headers)
# Statement PDF endpoint (POST version)
@router.post("/statements/pdf")
async def get_statement_pdf_post(
    request: Dict[str, Any] = Body(...),
    auth: Any = Depends(api_key_auth)
) -> Response:
    """
    Get a PDF statement for an account using POST request with access token
    """
    # Validate request
    if "access_token" not in request:
        raise HTTPException(status_code=400, detail="Missing access_token")
    if "account_id" not in request:
        raise HTTPException(status_code=400, detail="Missing account_id")
    if "statement_date" not in request:
        raise HTTPException(status_code=400, detail="Missing statement_date")
    
    access_token = request["access_token"]
    account_id = request["account_id"]
    statement_date = request["statement_date"]
    
    # Validate access token
    if not validate_access_token(access_token):
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    # Import ACCOUNTS and ACCESS_TOKEN_MAP from mock_data
    from api.endpoints.bank.mock_data import ACCOUNTS, ACCESS_TOKEN_MAP
    
    # Get account details
    token_data = ACCESS_TOKEN_MAP.get(access_token)
    if token_data and account_id in token_data["accounts"]:
        account = ACCOUNTS.get(account_id)
    else:
        account = None
        
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Create a BytesIO buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Create the PDF object using ReportLab
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add bank logo and header
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, height - 50, "BANQUE SAHL AL-MAGHRIB")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, "Statement of Account")
    
    # Add a horizontal line
    p.line(50, height - 80, width - 50, height - 80)
    
    # Add account information
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 110, "Account Information")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 130, f"Account Number: {account_id}")
    p.drawString(50, height - 145, f"Account Name: {account['name']}")
    p.drawString(50, height - 160, f"Statement Period: {statement_date}")
    
    # Add current balance
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 190, "Balance Summary")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 210, f"Current Balance: {account['balances']['current']} {account['balances']['iso_currency_code']}")
    p.drawString(50, height - 225, f"Available Balance: {account['balances']['available']} {account['balances']['iso_currency_code']}")
    
    # Add transaction table
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 255, "Transaction History")
    
    # Create transaction data
    data = [
        ["Date", "Description", "Amount", "Balance"],
        [f"{statement_date}-01", "Opening Balance", "", "5,000.00 MAD"],
        [f"{statement_date}-05", "Salary Deposit", "+8,500.00", "13,500.00 MAD"],
        [f"{statement_date}-10", "Marjane Supermarket", "-450.75", "13,049.25 MAD"],
        [f"{statement_date}-15", "ATM Withdrawal", "-1,000.00", "12,049.25 MAD"],
        [f"{statement_date}-20", "LYDEC Utility Bill", "-785.50", "11,263.75 MAD"],
        [f"{statement_date}-25", "Restaurant Payment", "-320.00", "10,943.75 MAD"],
        [f"{statement_date}-28", "Closing Balance", "", "10,943.75 MAD"]
    ]
    
    # Create the table
    table = Table(data, colWidths=[80, 200, 80, 100])
    
    # Style the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    
    table.setStyle(style)
    
    # Draw the table on the PDF
    table.wrapOn(p, width - 100, height)
    table.drawOn(p, 50, height - 400)
    
    # Add footer
    p.setFont("Helvetica", 8)
    p.drawString(50, 50, "Thank you for banking with Banque Sahl Al-Maghrib.")
    p.drawString(50, 35, "For any inquiries, please contact customer service at 0800-123456.")
    p.drawString(width - 150, 20, f"Page 1 of 1")
    
    # Save the PDF
    p.showPage()
    p.save()
    
    # Get the PDF data from the buffer
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Create response with PDF data
    headers = {
        "Content-Disposition": f"attachment; filename={account_id}_{statement_date}.pdf",
        "Content-Type": "application/pdf"
    }
    
    logger.info(f"Generated PDF statement for account {account_id}, date {statement_date}")
    
    return Response(content=pdf_data, headers=headers)

# Bank info endpoint
@router.get("/info")
async def get_bank_info(
    auth: Any = Depends(api_key_auth)
) -> Dict[str, Any]:
    """
    Get information about Sahl Bank API
    """
    return {
        "name": "Sahl Bank API",
        "version": "1.0.0",
        "description": "Mock banking API for testing purposes",
        "endpoints": [
            "/bank/link/token/create",
            "/bank/item/public_token/exchange",
            "/bank/auth/get",
            "/bank/transactions/get",
            "/bank/statements/get",
            "/bank/statements/{account_id}/{statement_date}.pdf",
            "/bank/statements/pdf",
            "/bank/info"
        ],
        "documentation": "https://docs.sahlbank.com"
    }