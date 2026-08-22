-- ============================================================
-- US Trends Platform — Canonical Initial Schema
-- Source of truth: docs/phase-a/database-schema.sql (sections 8-17)
-- Confirmed canonical per ADR-006. Pure executable SQL only.
-- ============================================================

-- 1. EXTENSIONS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- 2. ENUMS
CREATE TYPE confidence_tier AS ENUM (
    'OFFICIAL_MEASUREMENT',
    'ADMINISTRATIVE_RECORD',
    'SURVEY_ESTIMATE',
    'HISTORICAL_RECONSTRUCTION',
    'ACADEMIC_ESTIMATE',
    'MODELED_DERIVED',
    'UNKNOWN'
);

CREATE TYPE dataset_lifecycle_state AS ENUM (
    'IDENTIFIED', 'REGISTERED', 'RETRIEVED', 'VALIDATED',
    'STANDARDIZED', 'APPROVED', 'PUBLISHED', 'REVISED', 'DEPRECATED'
);

CREATE TYPE retrieval_method AS ENUM (
    'API', 'CSV_DOWNLOAD', 'JSON_DOWNLOAD', 'XLSX_DOWNLOAD',
    'PDF_EXTRACTION', 'FTP', 'MANUAL_ENTRY', 'MANUAL_IMPORT'
);

CREATE TYPE artifact_storage_type AS ENUM (
    'LOCAL_FILE', 'PARQUET_FILE', 'OBJECT_STORAGE', 'INLINE_JSON'
);

CREATE TYPE transformation_run_type AS ENUM (
    'STANDARDIZATION', 'DERIVATION', 'VALIDATION_REPROCESS', 'BACKFILL_NORMALIZATION'
);

CREATE TYPE missing_data_reason AS ENUM (
    'NO_AUTHORITATIVE_DATASET', 'NOT_YET_PUBLISHED', 'HISTORICAL_DATA_UNAVAILABLE',
    'METHODOLOGICAL_BREAK', 'SOURCE_DISCONTINUED', 'DATA_SUPPRESSION',
    'COLLECTION_NOT_STARTED', 'PENDING_RETRIEVAL', 'UNKNOWN_REASON'
);

CREATE TYPE cadence_type AS ENUM (
    'DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'ANNUAL', 'BIENNIAL',
    'TRIENNIAL', 'QUINQUENNIAL', 'DECENNIAL', 'IRREGULAR', 'EVENT_BASED'
);

CREATE TYPE observation_status AS ENUM ('CURRENT', 'SUPERSEDED');

-- 3. CORE REFERENCE TABLES
CREATE TABLE domains (
    domain_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(128) NOT NULL UNIQUE,
    description TEXT,
    display_order INT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE licenses (
    license_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(128) NOT NULL UNIQUE,
    short_code VARCHAR(64) NOT NULL UNIQUE,
    url TEXT,
    notes TEXT,
    is_open BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE confidence_tier_definitions (
    confidence_tier confidence_tier PRIMARY KEY,
    display_name VARCHAR(128) NOT NULL,
    description TEXT NOT NULL,
    display_order INT NOT NULL,
    color_token VARCHAR(64),
    line_style VARCHAR(32),
    badge_variant VARCHAR(32),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE missing_data_reason_definitions (
    missing_data_reason missing_data_reason PRIMARY KEY,
    display_name VARCHAR(128) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 4. SOURCE REGISTRY TABLES
CREATE TABLE sources (
    source_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    agency_name VARCHAR(255) NOT NULL,
    agency_level VARCHAR(64) NOT NULL DEFAULT 'FEDERAL',
    homepage_url TEXT,
    documentation_url TEXT,
    api_base_url TEXT,
    retrieval_notes TEXT,
    license_id UUID REFERENCES licenses(license_id),
    citation_text TEXT,
    priority_rank INT NOT NULL,
    is_authoritative BOOLEAN NOT NULL DEFAULT TRUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_sources_name_agency UNIQUE (name, agency_name)
);

CREATE TABLE datasets (
    dataset_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL REFERENCES sources(source_id),
    slug VARCHAR(128) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    dataset_external_id VARCHAR(255),
    access_url TEXT,
    documentation_url TEXT,
    cadence cadence_type NOT NULL,
    geographic_scope VARCHAR(128) NOT NULL DEFAULT 'US_NATIONAL',
    coverage_start_date DATE,
    coverage_end_date DATE,
    methodology_summary TEXT,
    lifecycle_state dataset_lifecycle_state NOT NULL DEFAULT 'IDENTIFIED',
    license_id UUID REFERENCES licenses(license_id),
    refresh_schedule_cron VARCHAR(128),
    retrieval_method retrieval_method NOT NULL,
    raw_retention_policy TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE dataset_versions (
    dataset_version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID NOT NULL REFERENCES datasets(dataset_id),
    source_version_label VARCHAR(255),
    source_revision_date DATE,
    schema_version VARCHAR(64),
    notes TEXT,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE dataset_series (
    dataset_series_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID NOT NULL REFERENCES datasets(dataset_id),
    series_code VARCHAR(255) NOT NULL,
    series_name VARCHAR(255) NOT NULL,
    description TEXT,
    units VARCHAR(128),
    cadence cadence_type,
    coverage_start_date DATE,
    coverage_end_date DATE,
    methodology_notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_dataset_series UNIQUE (dataset_id, series_code)
);

-- 5. METRIC REGISTRY TABLES
CREATE TABLE metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain_id UUID NOT NULL REFERENCES domains(domain_id),
    slug VARCHAR(128) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(128),
    definition TEXT NOT NULL,
    units VARCHAR(128),
    currency_code VARCHAR(3),
    inflation_basis_year INT,
    geographic_scope VARCHAR(128) NOT NULL DEFAULT 'US_NATIONAL',
    default_cadence cadence_type,
    methodology TEXT,
    known_limitations TEXT,
    comparison_note TEXT,
    first_available_date DATE,
    last_available_date DATE,
    is_monetary BOOLEAN NOT NULL DEFAULT FALSE,
    requires_real_and_nominal_display BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE metric_series_links (
    metric_series_link_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_id UUID NOT NULL REFERENCES metrics(metric_id),
    dataset_series_id UUID NOT NULL REFERENCES dataset_series(dataset_series_id),
    role VARCHAR(64) NOT NULL DEFAULT 'PRIMARY',
    start_date DATE,
    end_date DATE,
    is_preferred BOOLEAN NOT NULL DEFAULT FALSE,
    methodology_notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_metric_series_link UNIQUE (metric_id, dataset_series_id, start_date)
);

-- 6. INGESTION & RAW DATA TABLES (immutable)
CREATE TABLE ingestion_events (
    ingestion_event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_version_id UUID NOT NULL REFERENCES dataset_versions(dataset_version_id),
    retrieval_method retrieval_method NOT NULL,
    retrieved_at TIMESTAMP NOT NULL,
    initiated_by VARCHAR(128) NOT NULL DEFAULT 'system',
    source_http_status INT,
    source_checksum VARCHAR(128),
    row_count INT,
    file_count INT,
    status VARCHAR(32) NOT NULL DEFAULT 'SUCCESS',
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE raw_artifacts (
    raw_artifact_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ingestion_event_id UUID NOT NULL REFERENCES ingestion_events(ingestion_event_id),
    artifact_name VARCHAR(255) NOT NULL,
    artifact_storage_type artifact_storage_type NOT NULL,
    storage_uri TEXT NOT NULL,
    mime_type VARCHAR(128),
    file_size_bytes BIGINT,
    checksum_sha256 VARCHAR(128) NOT NULL,
    artifact_metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE raw_observations (
    raw_observation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    raw_artifact_id UUID NOT NULL REFERENCES raw_artifacts(raw_artifact_id),
    dataset_series_id UUID REFERENCES dataset_series(dataset_series_id),
    observation_key VARCHAR(255),
    raw_period_label VARCHAR(64),
    raw_date DATE,
    raw_value_text TEXT,
    raw_value_numeric NUMERIC,
    raw_units VARCHAR(128),
    raw_record JSONB NOT NULL,
    row_number_in_artifact INT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 7. VALIDATION & TRANSFORMATION TABLES
CREATE TABLE validation_rules (
    validation_rule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID NOT NULL REFERENCES datasets(dataset_id),
    rule_name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(64) NOT NULL,
    rule_definition JSONB NOT NULL,
    severity VARCHAR(32) NOT NULL DEFAULT 'ERROR',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE validation_runs (
    validation_run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ingestion_event_id UUID NOT NULL REFERENCES ingestion_events(ingestion_event_id),
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(32) NOT NULL,
    total_checks INT NOT NULL DEFAULT 0,
    failed_checks INT NOT NULL DEFAULT 0,
    summary JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE validation_issues (
    validation_issue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    validation_run_id UUID NOT NULL REFERENCES validation_runs(validation_run_id),
    validation_rule_id UUID REFERENCES validation_rules(validation_rule_id),
    raw_observation_id UUID REFERENCES raw_observations(raw_observation_id),
    issue_code VARCHAR(64) NOT NULL,
    severity VARCHAR(32) NOT NULL,
    message TEXT NOT NULL,
    issue_metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE transformation_scripts (
    transformation_script_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(64) NOT NULL,
    script_path TEXT NOT NULL,
    git_commit_sha VARCHAR(64),
    script_hash VARCHAR(128) NOT NULL,
    run_type transformation_run_type NOT NULL,
    description TEXT,
    methodology_notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMP,
    approved_by VARCHAR(128),
    CONSTRAINT uq_transformation_script UNIQUE (name, version)
);

CREATE TABLE transformation_runs (
    transformation_run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transformation_script_id UUID NOT NULL REFERENCES transformation_scripts(transformation_script_id),
    input_scope VARCHAR(255) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(32) NOT NULL,
    parameters JSONB,
    execution_log TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 8. PUBLISHED OBSERVATION TABLES
CREATE TABLE standardized_observations (
    standardized_observation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    raw_observation_id UUID NOT NULL REFERENCES raw_observations(raw_observation_id),
    metric_id UUID NOT NULL REFERENCES metrics(metric_id),
    dataset_series_id UUID REFERENCES dataset_series(dataset_series_id),
    transformation_run_id UUID NOT NULL REFERENCES transformation_runs(transformation_run_id),
    observation_date DATE NOT NULL,
    period_start DATE,
    period_end DATE,
    standardized_value NUMERIC,
    standardized_value_text TEXT,
    units VARCHAR(128) NOT NULL,
    currency_code VARCHAR(3),
    inflation_basis_year INT,
    confidence_tier confidence_tier NOT NULL,
    observation_status observation_status NOT NULL DEFAULT 'CURRENT',
    valid_from TIMESTAMP NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMP,
    revision_note TEXT,
    approval_status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    approved_at TIMESTAMP,
    approved_by VARCHAR(128),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_standardized_validity CHECK (
        (observation_status = 'CURRENT' AND valid_to IS NULL)
        OR (observation_status = 'SUPERSEDED' AND valid_to IS NOT NULL)
    ),
    CONSTRAINT chk_standardized_value_presence CHECK (
        standardized_value IS NOT NULL OR standardized_value_text IS NOT NULL
    )
);

CREATE TABLE derived_observations (
    derived_observation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_id UUID NOT NULL REFERENCES metrics(metric_id),
    transformation_run_id UUID NOT NULL REFERENCES transformation_runs(transformation_run_id),
    derivation_name VARCHAR(255) NOT NULL,
    derivation_formula TEXT NOT NULL,
    observation_date DATE,
    period_start DATE,
    period_end DATE,
    derived_value NUMERIC,
    units VARCHAR(128) NOT NULL,
    currency_code VARCHAR(3),
    inflation_basis_year INT,
    confidence_tier confidence_tier NOT NULL DEFAULT 'MODELED_DERIVED',
    methodology_note TEXT,
    observation_status observation_status NOT NULL DEFAULT 'CURRENT',
    valid_from TIMESTAMP NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE derived_observation_inputs (
    derived_observation_input_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    derived_observation_id UUID NOT NULL REFERENCES derived_observations(derived_observation_id),
    standardized_observation_id UUID NOT NULL REFERENCES standardized_observations(standardized_observation_id),
    input_role VARCHAR(64) NOT NULL DEFAULT 'SOURCE',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_derived_input UNIQUE (derived_observation_id, standardized_observation_id, input_role)
);

-- 9. MISSING DATA TABLE
CREATE TABLE missing_data_records (
    missing_data_record_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_id UUID NOT NULL REFERENCES metrics(metric_id),
    dataset_series_id UUID REFERENCES dataset_series(dataset_series_id),
    observation_date DATE NOT NULL,
    missing_data_reason missing_data_reason NOT NULL,
    explanation TEXT NOT NULL,
    earliest_available_date DATE,
    source_note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(128) NOT NULL DEFAULT 'system'
);

-- 10. GOVERNANCE & PUBLICATION TABLES
CREATE TABLE dataset_governance (
    dataset_governance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID NOT NULL REFERENCES datasets(dataset_id),
    lifecycle_state dataset_lifecycle_state NOT NULL,
    validation_status VARCHAR(32) NOT NULL,
    publication_status VARCHAR(32) NOT NULL,
    responsible_workstream VARCHAR(128),
    approved_by VARCHAR(128),
    approved_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE publication_releases (
    publication_release_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    release_version VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    released_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(128) NOT NULL
);

CREATE TABLE publication_release_items (
    publication_release_item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    publication_release_id UUID NOT NULL REFERENCES publication_releases(publication_release_id),
    dataset_id UUID REFERENCES datasets(dataset_id),
    metric_id UUID REFERENCES metrics(metric_id),
    notes TEXT
);

-- 11. HISTORICAL CONTEXT TABLES
CREATE TABLE historical_events (
    historical_event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(128) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    event_date DATE,
    effective_start_date DATE,
    effective_end_date DATE,
    category VARCHAR(128) NOT NULL,
    subcategory VARCHAR(128),
    description TEXT NOT NULL,
    historical_notes TEXT,
    confidence_tier confidence_tier NOT NULL DEFAULT 'UNKNOWN',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE event_domain_links (
    event_domain_link_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    historical_event_id UUID NOT NULL REFERENCES historical_events(historical_event_id),
    domain_id UUID NOT NULL REFERENCES domains(domain_id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_event_domain UNIQUE (historical_event_id, domain_id)
);

CREATE TABLE event_metric_links (
    event_metric_link_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    historical_event_id UUID NOT NULL REFERENCES historical_events(historical_event_id),
    metric_id UUID NOT NULL REFERENCES metrics(metric_id),
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_event_metric UNIQUE (historical_event_id, metric_id)
);

CREATE TABLE event_source_links (
    event_source_link_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    historical_event_id UUID NOT NULL REFERENCES historical_events(historical_event_id),
    source_id UUID NOT NULL REFERENCES sources(source_id),
    citation_note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_event_source UNIQUE (historical_event_id, source_id)
);

-- 12. CITATION & METADATA TABLES
CREATE TABLE citations (
    citation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID REFERENCES datasets(dataset_id),
    metric_id UUID REFERENCES metrics(metric_id),
    citation_format VARCHAR(32) NOT NULL,
    citation_text TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    generated_by VARCHAR(128) NOT NULL DEFAULT 'system'
);

CREATE TABLE metric_metadata_snapshots (
    metric_metadata_snapshot_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_id UUID NOT NULL REFERENCES metrics(metric_id),
    metadata_json JSONB NOT NULL,
    effective_from TIMESTAMP NOT NULL DEFAULT NOW(),
    effective_to TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 13. INDEXES
CREATE INDEX idx_datasets_source_id ON datasets(source_id);
CREATE INDEX idx_dataset_series_dataset_id ON dataset_series(dataset_id);
CREATE INDEX idx_metrics_domain_id ON metrics(domain_id);
CREATE INDEX idx_raw_observations_series_date ON raw_observations(dataset_series_id, raw_date);
CREATE INDEX idx_standardized_metric_date_current ON standardized_observations(metric_id, observation_date) WHERE observation_status = 'CURRENT';
CREATE INDEX idx_standardized_metric_approval ON standardized_observations(metric_id, approval_status);
CREATE INDEX idx_derived_metric_date_current ON derived_observations(metric_id, observation_date) WHERE observation_status = 'CURRENT';
CREATE INDEX idx_missing_metric_date ON missing_data_records(metric_id, observation_date);
CREATE INDEX idx_historical_events_date ON historical_events(event_date);
CREATE INDEX idx_sources_name_trgm ON sources USING gin (name gin_trgm_ops);
CREATE INDEX idx_metrics_name_trgm ON metrics USING gin (name gin_trgm_ops);

-- 14. VIEWS
CREATE VIEW current_standardized_observations_v AS
SELECT * FROM standardized_observations
WHERE observation_status = 'CURRENT' AND approval_status = 'APPROVED';

CREATE VIEW current_derived_observations_v AS
SELECT * FROM derived_observations
WHERE observation_status = 'CURRENT';

CREATE VIEW metric_availability_v AS
SELECT
    m.metric_id,
    m.slug AS metric_slug,
    MIN(cso.observation_date) AS first_published_date,
    MAX(cso.observation_date) AS last_published_date,
    COUNT(*) AS observation_count
FROM metrics m
LEFT JOIN current_standardized_observations_v cso ON m.metric_id = cso.metric_id
GROUP BY m.metric_id, m.slug;

-- 15. TRIGGERS (updated_at maintenance)
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_domains_updated_at BEFORE UPDATE ON domains
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_sources_updated_at BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_datasets_updated_at BEFORE UPDATE ON datasets
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_dataset_series_updated_at BEFORE UPDATE ON dataset_series
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_metrics_updated_at BEFORE UPDATE ON metrics
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_historical_events_updated_at BEFORE UPDATE ON historical_events
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 16. SEED DATA — 10 domains
INSERT INTO domains (slug, name, display_order) VALUES
    ('demographics', 'Demographics', 1),
    ('employment', 'Employment', 2),
    ('economy', 'Economy', 3),
    ('inflation-cost-of-living', 'Inflation & Cost of Living', 4),
    ('healthcare', 'Healthcare', 5),
    ('education', 'Education', 6),
    ('politics-government', 'Politics & Government', 7),
    ('immigration', 'Immigration', 8),
    ('agriculture-farming', 'Agriculture & Farming', 9),
    ('historical-events-legislation', 'Historical Events & Legislation', 10);

-- 16b. SEED DATA — 7 confidence tiers
INSERT INTO confidence_tier_definitions (confidence_tier, display_name, description, display_order, color_token) VALUES
    ('OFFICIAL_MEASUREMENT', 'Official Measurement', 'Direct measurement by authoritative government agency', 1, 'tier-official'),
    ('ADMINISTRATIVE_RECORD', 'Administrative Record', 'Derived from government administrative processes', 2, 'tier-admin'),
    ('SURVEY_ESTIMATE', 'Survey Estimate', 'Sampled government survey', 3, 'tier-survey'),
    ('HISTORICAL_RECONSTRUCTION', 'Historical Reconstruction', 'Reconstructed from historical documents', 4, 'tier-historical'),
    ('ACADEMIC_ESTIMATE', 'Academic Estimate', 'Published peer-reviewed research', 5, 'tier-academic'),
    ('MODELED_DERIVED', 'Modeled/Derived', 'Calculated from other tracked observations', 6, 'tier-modeled'),
    ('UNKNOWN', 'Unknown', 'Confidence classification cannot be determined', 7, 'tier-unknown');

-- 16c. SEED DATA — licenses
INSERT INTO licenses (name, short_code, url, is_open) VALUES
    ('Public Domain', 'public_domain', 'https://www.usa.gov/public-domain', true),
    ('Creative Commons Attribution 4.0 International', 'cc_by', 'https://creativecommons.org/licenses/by/4.0/', true),
    ('MIT License', 'mit', 'https://opensource.org/licenses/MIT', true);