-- Table for storing feedback entries
-- Each feedback represents a conversation that resulted in some user feedback
CREATE TABLE IF NOT EXISTS feedbacks (
    id SERIAL PRIMARY KEY,

    -- The actual feedback text content
    feedback_text TEXT NOT NULL,

    -- Model configuration used for this conversation (stored as JSON)
    -- Example: {"name": "gemini-flash", "model": "gemini/gemini-2.5-flash", "temperature": 0}
    model_manifest JSONB,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for efficient time-based queries
CREATE INDEX IF NOT EXISTS idx_feedbacks_created_at ON feedbacks(created_at);
