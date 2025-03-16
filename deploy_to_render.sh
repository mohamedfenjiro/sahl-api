#!/bin/bash
# Script to deploy Sahl API to Render

# Check if render.yaml exists
if [ ! -f "render.yaml" ]; then
    echo "❌ render.yaml not found in the current directory."
    exit 1
fi

echo "🚀 Preparing to deploy Sahl API to Render..."

# Instructions for manual deployment
echo "To deploy to Render, follow these steps:"
echo ""
echo "1. Log in to your Render dashboard: https://dashboard.render.com"
echo "2. Click on 'New' and select 'Blueprint'"
echo "3. Connect your Git repository"
echo "4. Select the repository containing this project"
echo "5. Render will automatically detect the render.yaml file"
echo "6. Review the services to be created:"
echo "   - sahl-bank-api (Web Service)"
echo "7. Click 'Apply' to start the deployment"
echo ""
echo "📝 After deployment:"
echo "1. The API will be available at:"
echo "   https://sahl-bank-api.onrender.com"
echo ""
echo "Would you like to open the Render dashboard now? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    open "https://dashboard.render.com"
fi