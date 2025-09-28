#!/bin/bash

echo "🏠 Setting up Supabase environment variables for Bedathon..."
echo ""

# Get Supabase credentials from user
echo "Please provide your Supabase credentials:"
echo "You can find these in your Supabase project dashboard under Settings > API"
echo ""

read -p "Enter your Supabase Project URL: " SUPABASE_URL
read -p "Enter your Supabase Anon Key: " SUPABASE_ANON_KEY
read -p "Enter your Supabase Service Role Key: " SUPABASE_SERVICE_ROLE_KEY
read -p "Enter your Anthropic API Key (optional): " ANTHROPIC_API_KEY

echo ""
echo "Creating frontend .env.local file..."

# Create frontend .env.local
cat > frontend/.env.local << EOF
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=$SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
EOF

echo "✅ Created frontend/.env.local"

echo ""
echo "Creating backend .env file..."

# Create backend .env
cat > backend/.env << EOF
# Supabase Configuration
SUPABASE_URL=$SUPABASE_URL
SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY

# Database Configuration
DATABASE_URL=sqlite:///./bedathon.db

# Anthropic API (for Claude agent)
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
EOF

echo "✅ Created backend/.env"

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Restart your servers:"
echo "   Frontend: cd frontend && npm run dev"
echo "   Backend:  cd backend && python app.py"
echo ""
echo "2. Test the integration:"
echo "   Visit: http://localhost:3002/roommate-matching"
echo ""
echo "Your roommate matching system is now fully integrated with Supabase! 🏠✨"
