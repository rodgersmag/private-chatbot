#!/bin/bash
# Initialize chat tables for the Ollama UI

echo "📊 Initializing chat tables..."

# Load environment variables
source .env

# Wait for backend to be ready
echo "⏳ Waiting for SelfDB backend to be ready..."
for i in {1..3}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        break
    fi
    echo -n "."
    sleep 2
done

# Login as admin to get access token
echo ""
echo "🔐 Authenticating as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "apikey: ${ANON_KEY}" \
  -d "username=${DEFAULT_ADMIN_EMAIL}&password=${DEFAULT_ADMIN_PASSWORD}")

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Failed to authenticate as admin"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "✅ Admin authenticated successfully"

# Execute SQL to create tables
echo "📝 Creating chat tables if they don't exist..."

SQL_QUERY=$(cat <<'EOF'
-- Create the 'chats' table
CREATE TABLE IF NOT EXISTS chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create the 'messages' table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Optional: Indexes for performance
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id);
CREATE INDEX IF NOT EXISTS idx_chats_created_at ON chats(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
EOF
)

SQL_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/sql/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "apikey: ${ANON_KEY}" \
  -d "{\"query\": $(echo "$SQL_QUERY" | jq -Rs .)}")

# Check if the response indicates success
if echo "$SQL_RESPONSE" | grep -q '"success":true'; then
    echo "✅ Chat tables initialized successfully"
    
    # Verify tables were created
    echo "🔍 Verifying tables..."
    VERIFY_RESPONSE=$(curl -s "http://localhost:8000/api/v1/tables" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "apikey: ${ANON_KEY}")
    
    if echo "$VERIFY_RESPONSE" | grep -q '"chats"' && echo "$VERIFY_RESPONSE" | grep -q '"messages"'; then
        echo "✅ Tables 'chats' and 'messages' verified in database"
    else
        echo "⚠️  Tables may not have been created properly"
    fi
else
    echo "⚠️  Warning: Issue creating tables (they may already exist)"
    echo "Response: $SQL_RESPONSE"
fi

echo "✨ Chat tables initialization complete"
