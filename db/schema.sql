-- 1. THE USERS: Stores the identity and their "Golden Baseline"
CREATE TABLE UserProfiles (
    profile_id INT PRIMARY KEY,
    user_hash VARCHAR(64) NOT NULL, -- Anonymous ID (Privacy first!)
    device_type VARCHAR(20),        -- 'mobile' or 'desktop'
    avg_dwell FLOAT DEFAULT 0.0,    -- Avg time key is held down
    avg_flight FLOAT DEFAULT 0.0,   -- Avg time between keys
    session_count INT DEFAULT 0,    -- How many logins have we seen?
    last_updated DATETIME
);

-- 2. THE SESSIONS: Stores every single login attempt to track drift
CREATE TABLE BehaviorLogs (
    log_id UNIQUEIDENTIFIER PRIMARY KEY,
    profile_id INT,
    captured_score FLOAT,           -- How well did they match today?
    is_anomaly BIT DEFAULT 0,       -- 1 if behavior was a mismatch
    is_bot BIT DEFAULT 0,           -- 1 if variance was too low (perfect timing)
    raw_jitter FLOAT,               -- Store the variance score for debugging
    created_at DATETIME DEFAULT GETDATE()
);

-- 3. THE RAW DATA (Optional): For deep analysis later
CREATE TABLE RawEvents (
    event_id BIGINT PRIMARY KEY,
    log_id UNIQUEIDENTIFIER,
    event_type VARCHAR(10),         -- 'KEY' or 'MOUSE'
    delta_ms INT                    -- The actual timing in milliseconds
);
