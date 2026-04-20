-- =====================================================================
-- OPENBEHAVIOR-AUTH DATABASE SCHEMA
-- Target: Oracle / Microsoft SQL Server
-- =====================================================================

-- 1. USER_PROFILES: Stores the 'Golden Baseline' for each user.
CREATE TABLE UserProfiles (
    UserID VARCHAR(50) PRIMARY KEY,
    EnrollmentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    SessionCount INT DEFAULT 0,
    BaseDwell FLOAT,
    BaseFlight FLOAT,
    BaseVariance FLOAT,
    LastKnownPlatform VARCHAR(50),
    LastKnownCores INT
);

-- 2. AUTH_AUDIT_LOGS: The Forensic Evidence for every login.
CREATE TABLE AuthAuditLogs (
    AuthID VARCHAR(100) PRIMARY KEY, 
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UserID VARCHAR(50),
    AuthStatus VARCHAR(20), 
    MatchScore FLOAT,
    
    -- Behavioral Analytics
    DwellTime FLOAT,
    FlightTime FLOAT,
    RhythmVariance FLOAT,
    MouseJitter FLOAT,
    MouseVelocity FLOAT,
    ClickDuration FLOAT,
    
    -- Environmental Fingerprinting
    ScreenResolution VARCHAR(20),
    ClientPlatform VARCHAR(50),
    HardwareCores INT,
    ClientTimezone VARCHAR(50),
    ClientLanguage VARCHAR(10),
    
    CONSTRAINT fk_user FOREIGN KEY (UserID) REFERENCES UserProfiles(UserID)
);

-- 3. INDEXING: Vital for fast query response in Banking Portals.
CREATE INDEX idx_audit_time ON AuthAuditLogs (Timestamp DESC);
CREATE INDEX idx_user_status ON AuthAuditLogs (UserID, AuthStatus);
