-- Create financial_data table
CREATE TABLE IF NOT EXISTS public.financial_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    balance DECIMAL(15, 2) NOT NULL,
    account_id TEXT NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT now(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create transactions table
CREATE TABLE IF NOT EXISTS public.transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id TEXT NOT NULL,
    accountId TEXT NOT NULL,
    balance DECIMAL(15, 2) NOT NULL,
    amount DECIMAL(15, 2),
    description TEXT,
    category TEXT,
    status TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Add Row Level Security (RLS) policies
ALTER TABLE public.financial_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

-- Create policy for financial_data
CREATE POLICY "Users can view their own financial data"
    ON public.financial_data
    FOR SELECT
    USING (auth.uid()::text = user_id);

CREATE POLICY "Users can update their own financial data"
    ON public.financial_data
    FOR UPDATE
    USING (auth.uid()::text = user_id);

-- Create policy for transactions
CREATE POLICY "Users can view their own transactions"
    ON public.transactions
    FOR SELECT
    USING (auth.uid()::text = accountId);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_financial_data_user_id ON public.financial_data(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON public.transactions(accountId);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON public.transactions(created_at);

-- Sample data for testing (optional)
INSERT INTO public.financial_data (user_id, balance, account_id)
VALUES 
    ('test-user-1', 5000.00, 'acc-123456'),
    ('test-user-2', 7500.50, 'acc-789012');

INSERT INTO public.transactions (transaction_id, accountId, balance, amount, description, category, status)
VALUES 
    ('tx_1234567890', 'test-user-1', 5000.00, -25.50, 'Coffee Shop', 'Food & Drink', 'completed'),
    ('tx_0987654321', 'test-user-1', 5025.50, 1000.00, 'Salary Deposit', 'Income', 'completed'),
    ('tx_5678901234', 'test-user-2', 7500.50, -120.75, 'Grocery Store', 'Shopping', 'completed');