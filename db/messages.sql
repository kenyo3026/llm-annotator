-- Table for storing conversation messages that led to the feedback
-- Each feedback can have multiple messages (conversation history)
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,

    -- Foreign key to feedbacks table
    feedback_id INT REFERENCES feedbacks(id) ON DELETE CASCADE,

    -- Message role: 'user' or 'assistant'
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),

    -- Message content
    content TEXT NOT NULL,

    -- Order of this message in the conversation (0-indexed)
    message_index INT NOT NULL,

    -- Model configuration used for this message (stored as JSON)
    -- NULL for user messages; populated for assistant messages
    model_manifest JSONB,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_messages_feedback_id ON messages(feedback_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
