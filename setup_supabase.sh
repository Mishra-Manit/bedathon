#!/bin/bash

echo "🏠 Setting up Supabase connection for Bedathon..."
echo "Supabase URL: https://slrjbjfpkdsmstjmajjh.supabase.co"
echo ""

# Get Supabase API keys from user
echo "Please get your API keys from your Supabase dashboard:"
echo "Go to: https://supabase.com/dashboard/project/slrjbjfpkdsmstjmajjh/settings/api"
echo ""

read -p "Enter your Supabase Anon Key: " SUPABASE_ANON_KEY
read -p "Enter your Supabase Service Role Key: " SUPABASE_SERVICE_ROLE_KEY
read -p "Enter your Anthropic API Key (optional): " ANTHROPIC_API_KEY

echo ""
echo "Creating frontend .env.local file..."

# Create frontend .env.local
cat > frontend/.env.local << EOF
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://slrjbjfpkdsmstjmajjh.supabase.co
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
SUPABASE_URL=https://slrjbjfpkdsmstjmajjh.supabase.co
SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY

# Database Configuration
DATABASE_URL=sqlite:///./bedathon.db

# Anthropic API (for Claude agent)
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
EOF

echo "✅ Created backend/.env"

echo ""
echo "🎉 Supabase setup complete!"
echo ""
echo "Your Supabase project: https://slrjbjfpkdsmstjmajjh.supabase.co"
echo ""
echo "Next steps:"
echo "1. Restart your servers:"
echo "   Frontend: cd frontend && npm run dev"
echo "   Backend:  cd backend && python app.py"
echo ""
echo "2. The system will now use your real Supabase data including:"
echo "   - Skylar, Jordan, Ryler profiles (if they exist in your database)"
echo "   - All your real apartment data"
echo "   - Real user authentication"
echo ""
echo "Your roommate matching system is now connected to Supabase! 🏠✨"
