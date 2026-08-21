CREATE TABLE analysts (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT
);

INSERT INTO analysts (name, email) VALUES
    ('Analyste SOC 1', 'analyst1@sentra.local'),
    ('Analyste SOC 2', 'analyst2@sentra.local');

CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    correlated_event_id TEXT UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    src_ip INET,
    dest_ip INET,
    signature TEXT,
    mitre_tactic TEXT,
    mitre_technique_id TEXT,
    mitre_technique_name TEXT,
    risk_score NUMERIC(5,1),
    risk_level TEXT,
    status TEXT NOT NULL DEFAULT 'new',
    assigned_analyst_id INTEGER REFERENCES analysts(id),
    enrichment JSONB
);

CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_risk_level ON incidents(risk_level);
CREATE INDEX idx_incidents_src_ip ON incidents(src_ip);
CREATE INDEX idx_incidents_created_at ON incidents(created_at);

CREATE TABLE incident_audit_log (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL REFERENCES incidents(id),
    action TEXT NOT NULL,           -- created | status_change | assignment_change
    field_changed TEXT,
    old_value TEXT,
    new_value TEXT,
    actor TEXT NOT NULL DEFAULT 'system',
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_incident_id ON incident_audit_log(incident_id);