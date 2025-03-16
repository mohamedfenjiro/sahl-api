#!/bin/bash
# Script to deploy Sahl Bank API to Supabase Edge Functions

# Check if supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI is not installed. Please install it first:"
    echo "npm install -g supabase"
    exit 1
fi

# Check if user is logged in to Supabase
if ! supabase projects list &> /dev/null; then
    echo "❌ You are not logged in to Supabase. Please login first:"
    echo "supabase login"
    exit 1
fi

# Check if the Edge Function exists
if [ ! -d "supabase/functions/sahl-bank-api" ]; then
    echo "❌ Edge Function not found at supabase/functions/sahl-bank-api"
    exit 1
fi

# Get Supabase project reference
echo "Enter your Supabase project reference (found in your project URL):"
read project_ref

if [ -z "$project_ref" ]; then
    echo "❌ Project reference is required."
    exit 1
fi

echo "🚀 Deploying Sahl Bank API to Supabase Edge Functions..."

# Deploy the Edge Function
supabase functions deploy sahl-bank-api --project-ref "$project_ref"

# Allow public access (for testing)
echo "Do you want to allow public access to the API? (y/n)"
read allow_public

if [ "$allow_public" = "y" ] || [ "$allow_public" = "Y" ]; then
    echo "🔓 Allowing public access to the API..."
    supabase functions deploy sahl-bank-api --project-ref "$project_ref" --no-verify-jwt
fi

echo "✅ Deployment complete!"
echo ""
echo "📝 Your API is now available at:"
echo "https://$project_ref.supabase.co/functions/v1/sahl-bank-api"
echo ""
echo "📝 Next steps:"
echo "1. Update the API URL in your client applications"
echo "2. Test the API using the examples in SANDBOX.md"