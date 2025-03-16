import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// Mock data for accounts (Moroccan themed)
const ACCOUNTS = {
  "acc_1": {
    "account_id": "acc_1",
    "balances": {
      "available": 5000.75,
      "current": 5100.75,
      "limit": null,
      "iso_currency_code": "MAD",
      "unofficial_currency_code": null
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
      "limit": null,
      "iso_currency_code": "MAD",
      "unofficial_currency_code": null
    },
    "mask": "5678",
    "name": "Compte Épargne Al Baraka",
    "official_name": "Compte Épargne Rendement Élevé Al Baraka",
    "subtype": "savings",
    "type": "depository"
  }
};

// Mock account numbers (Moroccan format)
const ACCOUNT_NUMBERS = {
  "acc_1": {
    "account": "007780000123456789012345",
    "account_id": "acc_1",
    "routing": "007780000",  // Attijariwafa Bank code
    "wire_routing": "BCMAMAMC"  // Moroccan bank SWIFT code
  },
  "acc_2": {
    "account": "013450000234567890123456",
    "account_id": "acc_2",
    "routing": "013450000",  // BMCE Bank code
    "wire_routing": "BMCEMAMC"  // Moroccan bank SWIFT code
  }
};

// Mock access tokens
const ACCESS_TOKEN_MAP = {
  "access-token-1": {
    "item_id": "item_1",
    "accounts": ["acc_1", "acc_2"]
  }
};

// Test user credentials
const USER_CREDENTIALS = {
  "username1234": "password1234"
};

// Client credentials for multitenancy
const CLIENT_CREDENTIALS = {
  "client_123456": "secret_abcdef123456",
  "client_654321": "secret_fedcba654321",
};

// Generate transactions
function generateTransactions(accountId: string, count = 20) {
  const transactions = [];
  const categories = [
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
    ["Family", "Aïd al-Fitr"],
    ["Family", "Aïd al-Adha"]
  ];
  
  const merchantNames = [
    "Marjane", "Carrefour Market", "Aswak Assalam", "Café Maure",
    "Hammam Traditionnel", "Patisserie Marocaine", "Pharmacie Atlas",
    "Royal Air Maroc", "Riad Al Andalous", "Maroc Telecom",
    "INWI", "ONEE", "LYDEC", "Souk El Had",
    "Artisanat Maroc", "Fès Medina Shop"
  ];
  
  const today = new Date();
  
  for (let i = 0; i < count; i++) {
    const daysAgo = Math.floor(Math.random() * 30);
    const date = new Date(today);
    date.setDate(date.getDate() - daysAgo);
    
    const isIncome = Math.random() < 0.2;
    let amount = Math.round(Math.random() * 495 + 5) / 100;
    if (!isIncome) amount = -amount;
    
    const category = categories[Math.floor(Math.random() * categories.length)];
    const merchant = merchantNames[Math.floor(Math.random() * merchantNames.length)];
    
    transactions.push({
      "transaction_id": `tx_${accountId}_${i}`,
      "account_id": accountId,
      "amount": amount,
      "date": date.toISOString().split('T')[0],
      "datetime": date.toISOString(),
      "name": merchant,
      "merchant_name": merchant,
      "pending": false,
      "category": category
    });
  }
  
  return transactions.sort((a, b) => b.date.localeCompare(a.date));
}

// Generate statements
function generateStatements(accountId: string, count = 6) {
  const statements = [];
  const today = new Date();
  let currentMonth = new Date(today.getFullYear(), today.getMonth(), 1);
  
  for (let i = 0; i < count; i++) {
    const statementDate = new Date(currentMonth);
    statementDate.setDate(statementDate.getDate() - 1);
    
    currentMonth.setMonth(currentMonth.getMonth() - 1);
    
    const endingBalance = Math.round(Math.random() * 9000 + 1000) / 100;
    const startingBalance = Math.round((endingBalance - (Math.random() * 2000 - 1000)) * 100) / 100;
    
    statements.push({
      "statement_id": `stmt_${accountId}_${i}`,
      "account_id": accountId,
      "start_date": currentMonth.toISOString().split('T')[0],
      "end_date": statementDate.toISOString().split('T')[0],
      "starting_balance": startingBalance,
      "ending_balance": endingBalance,
      "total_deposits": Math.round(Math.random() * 2500 + 500) / 100,
      "total_withdrawals": Math.round(Math.random() * 2500 + 500) / 100,
      "pdf_url": `https://api.sahlfinancial.com/statements/${accountId}/${statementDate.toISOString().split('T')[0].substring(0, 7)}.pdf`
    });
  }
  
  return statements;
}

// Validate client credentials
function validateCredentials(clientId: string, clientSecret: string) {
  return CLIENT_CREDENTIALS[clientId] === clientSecret;
}

// Generate link token
function generateLinkToken(clientId: string, userId: string) {
  const timestamp = Math.floor(Date.now() / 1000);
  const randomPart = crypto.randomUUID().replace(/-/g, '');
  
  return {
    "link_token": `link-${clientId}-${userId}-${timestamp}-${randomPart}`,
    "expiration": timestamp + 1800,
    "request_id": `req_${randomPart.substring(0, 8)}`
  };
}

// Exchange public token
function exchangePublicToken(publicToken: string) {
  const accessToken = `access-${crypto.randomUUID().replace(/-/g, '')}`;
  const itemId = `item-${crypto.randomUUID().replace(/-/g, '').substring(0, 8)}`;
  
  return {
    "access_token": accessToken,
    "item_id": itemId,
    "request_id": `req_${crypto.randomUUID().replace(/-/g, '').substring(0, 8)}`
  };
}

// Get accounts by token
function getAccountsByToken(accessToken: string) {
  const tokenData = ACCESS_TOKEN_MAP[accessToken];
  if (!tokenData) return [];
  
  return tokenData.accounts.map(accId => ACCOUNTS[accId]).filter(Boolean);
}

// Get account numbers by token
function getAccountNumbersByToken(accessToken: string) {
  const tokenData = ACCESS_TOKEN_MAP[accessToken];
  if (!tokenData) return { ach: [] };
  
  const accountNumbers = tokenData.accounts
    .filter(accId => ACCOUNT_NUMBERS[accId])
    .map(accId => ACCOUNT_NUMBERS[accId]);
  
  return { ach: accountNumbers };
}

// Get transactions by token
function getTransactionsByToken(accessToken: string, startDate?: string, endDate?: string) {
  const tokenData = ACCESS_TOKEN_MAP[accessToken];
  if (!tokenData) return { transactions: [], accounts: [] };
  
  const accounts = tokenData.accounts.map(accId => ACCOUNTS[accId]).filter(Boolean);
  
  let allTransactions = [];
  for (const accId of tokenData.accounts) {
    let transactions = generateTransactions(accId, 20);
    
    if (startDate && endDate) {
      transactions = transactions.filter(t => 
        t.date >= startDate && t.date <= endDate
      );
    }
    
    allTransactions = [...allTransactions, ...transactions];
  }
  
  allTransactions.sort((a, b) => b.date.localeCompare(a.date));
  
  return {
    accounts,
    transactions: allTransactions,
    total_transactions: allTransactions.length
  };
}

// Get statements by token
function getStatementsByToken(accessToken: string) {
  const tokenData = ACCESS_TOKEN_MAP[accessToken];
  if (!tokenData) return { statements: [], accounts: [] };
  
  const accounts = tokenData.accounts.map(accId => ACCOUNTS[accId]).filter(Boolean);
  
  let allStatements = [];
  for (const accId of tokenData.accounts) {
    const statements = generateStatements(accId, 6);
    allStatements = [...allStatements, ...statements];
  }
  
  allStatements.sort((a, b) => b.end_date.localeCompare(a.end_date));
  
  return {
    accounts,
    statements: allStatements,
    total_statements: allStatements.length
  };
}

// Main handler
serve(async (req) => {
  // CORS headers
  const headers = new Headers({
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Client-ID, X-Client-Secret",
    "Content-Type": "application/json"
  });
  
  // Handle preflight requests
  if (req.method === "OPTIONS") {
    return new Response(null, { headers, status: 204 });
  }
  
  // Get client credentials from headers
  const clientId = req.headers.get("X-Client-ID");
  const clientSecret = req.headers.get("X-Client-Secret");
  
  // Validate client credentials
  if (!clientId || !clientSecret || !validateCredentials(clientId, clientSecret)) {
    return new Response(
      JSON.stringify({ error: "Invalid client credentials" }),
      { headers, status: 401 }
    );
  }
  
  const url = new URL(req.url);
  const path = url.pathname.replace(/^\/sahl-bank-api/, "");
  
  try {
    // Bank info endpoint
    if (path === "/info" && req.method === "GET") {
      return new Response(
        JSON.stringify({
          name: "Banque Sahl Al-Maghrib API",
          version: "1.0.0",
          description: "API bancaire simulée pour les tests au Maroc",
          endpoints: [
            "/link/token/create",
            "/item/public_token/exchange",
            "/auth/get",
            "/transactions/get",
            "/statements/get",
            "/info"
          ],
          documentation: "https://docs.sahlfinancial.com"
        }),
        { headers, status: 200 }
      );
    }
    
    // Link token creation endpoint
    if (path === "/link/token/create" && req.method === "POST") {
      const body = await req.json();
      
      if (!body.user || !body.user.client_user_id) {
        return new Response(
          JSON.stringify({ error: "Missing required fields" }),
          { headers, status: 400 }
        );
      }
      
      const userId = body.user.client_user_id;
      const tokenData = generateLinkToken(clientId, userId);
      
      return new Response(
        JSON.stringify(tokenData),
        { headers, status: 200 }
      );
    }
    
    // Public token exchange endpoint
    if (path === "/item/public_token/exchange" && req.method === "POST") {
      const body = await req.json();
      
      if (!body.public_token) {
        return new Response(
          JSON.stringify({ error: "Missing public_token" }),
          { headers, status: 400 }
        );
      }
      
      const tokenData = exchangePublicToken(body.public_token);
      
      return new Response(
        JSON.stringify(tokenData),
        { headers, status: 200 }
      );
    }
    
    // Auth endpoint
    if (path === "/auth/get" && req.method === "POST") {
      const body = await req.json();
      
      if (!body.access_token) {
        return new Response(
          JSON.stringify({ error: "Missing access_token" }),
          { headers, status: 400 }
        );
      }
      
      const accounts = getAccountsByToken(body.access_token);
      const numbers = getAccountNumbersByToken(body.access_token);
      
      return new Response(
        JSON.stringify({
          accounts,
          numbers,
          request_id: `req_${Date.now()}`
        }),
        { headers, status: 200 }
      );
    }
    
    // Transactions endpoint
    if (path === "/transactions/get" && req.method === "POST") {
      const body = await req.json();
      
      if (!body.access_token) {
        return new Response(
          JSON.stringify({ error: "Missing access_token" }),
          { headers, status: 400 }
        );
      }
      
      const today = new Date().toISOString().split('T')[0];
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      const startDate = body.start_date || thirtyDaysAgo.toISOString().split('T')[0];
      const endDate = body.end_date || today;
      
      const transactionsData = getTransactionsByToken(body.access_token, startDate, endDate);
      
      return new Response(
        JSON.stringify({
          ...transactionsData,
          request_id: `req_${Date.now()}`
        }),
        { headers, status: 200 }
      );
    }
    
    // Statements endpoint
    if (path === "/statements/get" && req.method === "POST") {
      const body = await req.json();
      
      if (!body.access_token) {
        return new Response(
          JSON.stringify({ error: "Missing access_token" }),
          { headers, status: 400 }
        );
      }
      
      const statementsData = getStatementsByToken(body.access_token);
      
      return new Response(
        JSON.stringify({
          ...statementsData,
          request_id: `req_${Date.now()}`
        }),
        { headers, status: 200 }
      );
    }
    
    // Not found
    return new Response(
      JSON.stringify({ error: "Endpoint not found" }),
      { headers, status: 404 }
    );
  } catch (error) {
    console.error("Error processing request:", error);
    
    return new Response(
      JSON.stringify({ error: "Internal server error" }),
      { headers, status: 500 }
    );
  }
});