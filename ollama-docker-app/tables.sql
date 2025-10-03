CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    profile_image_url VARCHAR(500),
    display_name VARCHAR(150),
    preferences JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);

-- Add comments
COMMENT ON TABLE user_profiles IS 'Extended user profile information';
COMMENT ON COLUMN user_profiles.user_id IS 'Foreign key to users table';
COMMENT ON COLUMN user_profiles.first_name IS 'User first name';
COMMENT ON COLUMN user_profiles.last_name IS 'User last name';
COMMENT ON COLUMN user_profiles.profile_image_url IS 'URL to profile image in SelfDB storage';
COMMENT ON COLUMN user_profiles.display_name IS 'Optional display name (defaults to first_name last_name)';
COMMENT ON COLUMN user_profiles.preferences IS 'User preferences like theme, default model, etc.';

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    model_name VARCHAR(100) NOT NULL,
    is_archived BOOLEAN NOT NULL DEFAULT false,
    is_pinned BOOLEAN NOT NULL DEFAULT false,
    metadata JSONB,
    last_message_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_archived ON conversations(user_id, is_archived);
CREATE INDEX IF NOT EXISTS idx_conversations_user_last_message ON conversations(user_id, last_message_at DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_conversations_user_pinned ON conversations(user_id, is_pinned);

-- Add comments
COMMENT ON TABLE conversations IS 'User chat conversations with Ollama AI models';
COMMENT ON COLUMN conversations.title IS 'Auto-generated or user-defined conversation title';
COMMENT ON COLUMN conversations.model_name IS 'Ollama model used (e.g., llama2, mistral, qwen2.5)';
COMMENT ON COLUMN conversations.metadata IS 'Additional conversation data (tags, folder, custom fields)';
COMMENT ON COLUMN conversations.last_message_at IS 'Timestamp of last message for sorting';


CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    model_name VARCHAR(100),
    token_count INTEGER,
    metadata JSONB,
    parent_message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    is_edited BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created ON messages(conversation_id, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_messages_parent_id ON messages(parent_message_id);

-- Add comments
COMMENT ON TABLE messages IS 'Individual messages within chat conversations';
COMMENT ON COLUMN messages.role IS 'Message sender: user or assistant';
COMMENT ON COLUMN messages.content IS 'The actual message text content';
COMMENT ON COLUMN messages.model_name IS 'AI model that generated this response (for assistant messages)';
COMMENT ON COLUMN messages.token_count IS 'Approximate token count for tracking usage';
COMMENT ON COLUMN messages.metadata IS 'Additional stats like tokens_per_second, duration, etc.';
COMMENT ON COLUMN messages.parent_message_id IS 'For conversation branching/editing history';