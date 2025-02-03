-- Security Events Table
CREATE TABLE security_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(50) NOT NULL,
    severity INTEGER CHECK (severity BETWEEN 1 AND 5),
    source_ip INET,
    destination_ip INET,
    user_id VARCHAR(100),
    description TEXT,
    raw_data JSONB,
    ml_score FLOAT CHECK (ml_score BETWEEN 0 AND 1),
    is_threat BOOLEAN,
    analyzed BOOLEAN DEFAULT FALSE
);

-- ML Model Metrics
CREATE TABLE model_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100) NOT NULL,
    accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Threat Intelligence
CREATE TABLE threat_intelligence (
    intel_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_type VARCHAR(50),
    indicator_value TEXT,
    confidence_score FLOAT,
    source VARCHAR(100),
    first_seen TIMESTAMP WITH TIME ZONE,
    last_seen TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);