Database Schema
Project:U.S. Socioeconomic, Political & Agricultural Trends Platform
Version:1.0.0
Date:2026-08-06
Status:Draft for Team Review
________________________________________
1. Schema Objectives
The schema must support:
immutable raw data preservation;
complete provenance and lineage;
strict separation of raw, standardized, and derived data;
dataset lifecycle governance;
revision history without overwrite;
explicit missing-data representation;
confidence-tier labeling on every observation;
historical events as contextual entities;
reproducible transformations;
extensibility for future geographic expansion without redesign.
________________________________________
2. Design Assumptions
Assumption
Status
Phase 1 geography is national/federal only
Approved scope
State/county support will come later
Deferred, but schema must be expandable
Raw files may be stored on disk/object storage while metadata lives in PostgreSQL
Assumption for maintainability
Observation granularity may vary by dataset (annual, quarterly, monthly, decennial, event-date)
Authoritative-source driven
Some metrics will have no observation for some years
Required by policy; never backfilled artificially
A metric may map to multiple datasets/series across eras
Required for historical continuity without blending
________________________________________
3. Core Modeling Principles
Raw is immutable
Standardized is append-only versioned
Derived is separate
Missing data is explicit
Confidence tier is mandatory
Every displayed value must trace through provenance tables
Methodological distinctions remain structurally visible
No assumption that one metric = one dataset forever
________________________________________
4. High-Level Entity Model
text
sources
  └─< datasets
        └─< dataset_versions
              └─< ingestion_events
                    └─< raw_artifacts
                           └─< raw_observations
                                 └─< standardized_observations
                                       └─< derived_observation_inputs >─ derived_observations


domains
  └─< metrics
        └─< metric_series_links >─ datasets / series definitions


metrics
  └─< missing_data_records


transformation_scripts
  └─< transformation_runs
        └─< standardized_observations
        └─< derived_observations


historical_events
event_metric_links
event_domain_links
event_source_links


citations
licenses
dataset_lifecycle_status
confidence_tier_definitions
missing_data_reason_definitions
________________________________________
5. Logical ERD
mermaid
________________________________________
6. PostgreSQL Extensions & DDL Statements
-- PostgreSQL DDL Statements for US Trends Platform Phase A

-- IMMUTABLE RAW OBSERVATION LAYER

CREATE TABLE IF NOT EXISTS raw_observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    observation_key VARCHAR(512) NOT NULL,
    dataset_id UUID,
    dataset_version_id UUID,
    observation_time TIMESTAMP WITH TIME ZONE NOT NULL,
    observation_value JSONB NOT NULL,
    unit VARCHAR(64),
    source_id UUID NOT NULL,
    source_metadata JSONB,
    raw_artifact_id UUID,
    raw_text TEXT,
    ingestion_event_id UUID NOT NULL,
    location_id UUID,
    tags JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(128),
    CONSTRAINT fk_raw_observations_source FOREIGN KEY (source_id) REFERENCES sources(id),
    CONSTRAINT fk_raw_observations_dataset FOREIGN KEY (dataset_id) REFERENCES datasets(id),
    CONSTRAINT fk_raw_observations_dataset_version FOREIGN KEY (dataset_version_id) REFERENCES dataset_versions(id),
    CONSTRAINT fk_raw_observations_ingestion_event FOREIGN KEY (ingestion_event_id) REFERENCES ingestion_events(id),
    CONSTRAINT fk_raw_observations_raw_artifact FOREIGN KEY (raw_artifact_id) REFERENCES raw_artifacts(id)
);

CREATE INDEX idx_raw_observations_time ON raw_observations(observation_time);
CREATE INDEX idx_raw_observations_dataset ON raw_observations(dataset_id);
CREATE INDEX idx_raw_observations_source ON raw_observations(source_id);
CREATE INDEX idx_raw_observations_key ON raw_observations(observation_key);
CREATE INDEX idx_raw_observations_ingestion ON raw_observations(ingestion_event_id);

CREATE TABLE IF NOT EXISTS raw_artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    artifact_key VARCHAR(512) NOT NULL UNIQUE,
    dataset_id UUID,
    dataset_version_id UUID,
    artifact_time TIMESTAMP WITH TIME ZONE NOT NULL,
    artifact_type VARCHAR(64) NOT NULL,
    raw_contents BYTEA,
    raw_text TEXT,
    source_id UUID NOT NULL,
    source_metadata JSONB,
    ingestion_event_id UUID NOT NULL,
    content_hash VARCHAR(128),
    content_size_bytes INTEGER,
    tags JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(128),
    CONSTRAINT fk_raw_artifacts_source FOREIGN KEY (source_id) REFERENCES sources(id),
    CONSTRAINT fk_raw_artifacts_dataset FOREIGN KEY (dataset_id) REFERENCES datasets(id),
    CONSTRAINT fk_raw_artifacts_dataset_version FOREIGN KEY (dataset_version_id) REFERENCES dataset_versions(id),
    CONSTRAINT fk_raw_artifacts_ingestion_event FOREIGN KEY (ingestion_event_id) REFERENCES ingestion_events(id)
);

-- STANDARDIZED LAYER

CREATE TABLE IF NOT EXISTS standardized_observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    raw_observation_id UUID NOT NULL,
    observation_key VARCHAR(512) NOT NULL,
    dataset_id UUID,
    dataset_version_id UUID,
    observation_time TIMESTAMP WITH TIME ZONE NOT NULL,
    observation_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(64) NOT NULL,
    standardized_unit VARCHAR(64) NOT NULL,
    multiplier DOUBLE PRECISION DEFAULT 1.0,
    source_id UUID NOT NULL,
    metadata JSONB,
    transformation_script_id UUID,
    transformation_run_id UUID,
    location_id UUID,
    tags JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(128),
    CONSTRAINT fk_standardized_observations_raw FOREIGN KEY (raw_observation_id) REFERENCES raw_observations(id),
    CONSTRAINT fk_standardized_observations_source FOREIGN KEY (source_id) REFERENCES sources(id),
    CONSTRAINT fk_standardized_observations_dataset FOREIGN KEY (dataset_id) REFERENCES datasets(id),
    CONSTRAINT fk_standardized_observations_dataset_version FOREIGN KEY (dataset_version_id) REFERENCES dataset_versions(id),
    CONSTRAINT fk_standardized_observations_transformation_script FOREIGN KEY (transformation_script_id) REFERENCES transformation_scripts(id),
    CONSTRAINT fk_standardized_observations_transformation_run FOREIGN KEY (transformation_run_id) REFERENCES transformation_runs(id)
);

CREATE INDEX idx_standardized_observations_time ON standardized_observations(observation_time);
CREATE INDEX idx_standardized_observations_dataset ON standardized_observations(dataset_id);
CREATE INDEX idx_standardized_observations_key ON standardized_observations(observation_key);
CREATE INDEX idx_standardized_observations_source ON standardized_observations(source_id);
CREATE INDEX idx_standardized_observations_raw ON standardized_observations(raw_observation_id);

-- DERIVED LAYER

CREATE TABLE IF NOT EXISTS derived_observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    derived_key VARCHAR(512) NOT NULL UNIQUE,
    dataset_id UUID,
    dataset_version_id UUID,
    observation_time TIMESTAMP WITH TIME ZONE NOT NULL,
    observation_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(64) NOT NULL,
    calculation_formula TEXT,
    source_ids UUID[],
    input_observation_ids UUID[],
    transformation_script_id UUID,
    transformation_run_id UUID,
    confidence_score DOUBLE PRECISION,
    metadata JSONB,
    tags JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(128),
    CONSTRAINT fk_derived_observations_dataset FOREIGN KEY (dataset_id) REFERENCES datasets(id),
    CONSTRAINT fk_derived_observations_dataset_version FOREIGN KEY (dataset_version_id) REFERENCES dataset_versions(id),
    CONSTRAINT fk_derived_observations_transformation_script FOREIGN KEY (transformation_script_id) REFERENCES transformation_scripts(id),
    CONSTRAINT fk_derived_observations_transformation_run FOREIGN KEY (transformation_run_id) REFERENCES transformation_runs(id)
);

CREATE INDEX idx_derived_observations_time ON derived_observations(observation_time);
CREATE INDEX idx_derived_observations_dataset ON derived_observations(dataset_id);
CREATE INDEX idx_derived_observations_key ON derived_observations(derived_key);

CREATE TABLE IF NOT EXISTS derived_observation_inputs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    derived_observation_id UUID NOT NULL,
    input_observation_id UUID NOT NULL,
    input_type VARCHAR(32) NOT NULL,
    weight DOUBLE PRECISION DEFAULT 1.0,
    lag_period_days INTEGER,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(128),
    CONSTRAINT fk_derived_observation_inputs_derived FOREIGN KEY (derived_observation_id) REFERENCES derived_observations(id),
    CONSTRAINT fk_derived_observation_inputs_input FOREIGN KEY (input_observation_id) REFERENCES standardized_observations(id)
);

-- SUPPORTING TABLES

CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_key VARCHAR(128) NOT NULL UNIQUE,
    source_name VARCHAR(256) NOT NULL,
    source_type VARCHAR(64) NOT NULL,
    source_url TEXT,
    license_id UUID,
    update_frequency VARCHAR(32),
    reliability_score DOUBLE PRECISION DEFAULT 1.0,
    metadata JSONB,
    tags JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(128),
    CONSTRAINT fk_sources_license FOREIGN KEY (license_id) REFERENCES licenses(id)
);

CREATE TABLE IF NOT EXISTS datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_key VARCHAR(128) NOT NULL UNIQUE,
    dataset_name VARCHAR(256) NOT NULL,
    dataset_description TEXT,
    unit VARCHAR(64),
    domain_id UUID,
    source_id UUID NOT NULL,
    update_frequency VARCHAR(32),
    confidence_score DOUBLE PRECISION DEFAULT 1.0,
    metadata JSONB,
    tags JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(128),
    CONSTRAINT fk_datasets_source FOREIGN KEY (source_id) REFERENCES sources(id),
    CONSTRAINT fk_datasets_domain FOREIGN KEY (domain_id) REFERENCES domains(id)
);

-- PostgreSQL Extensions

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

Why:
uuid-ossp: stable UUID generation
pg_trgm: future search support
btree_gin: mixed indexing support
________________________________________
7. Enumerations
sql
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
    'IDENTIFIED',
    'REGISTERED',
    'RETRIEVED',
    'VALIDATED',
    'STANDARDIZED',
    'APPROVED',
    'PUBLISHED',
    'REVISED',
    'DEPRECATED'
);


CREATE TYPE retrieval_method AS ENUM (
    'API',
    'CSV_DOWNLOAD',
    'JSON_DOWNLOAD',
    'XLSX_DOWNLOAD',
    'PDF_EXTRACTION',
    'FTP',
    'MANUAL_ENTRY',
    'MANUAL_IMPORT'
);


CREATE TYPE artifact_storage_type AS ENUM (
    'LOCAL_FILE',
    'PARQUET_FILE',
    'OBJECT_STORAGE',
    'INLINE_JSON'
);


CREATE TYPE transformation_run_type AS ENUM (
    'STANDARDIZATION',
    'DERIVATION',
    'VALIDATION_REPROCESS',
    'BACKFILL_NORMALIZATION'
);


CREATE TYPE missing_data_reason AS ENUM (
    'NO_AUTHORITATIVE_DATASET',
    'NOT_YET_PUBLISHED',
    'HISTORICAL_DATA_UNAVAILABLE',
    'METHODOLOGICAL_BREAK',
    'SOURCE_DISCONTINUED',
    'DATA_SUPPRESSION',
    'COLLECTION_NOT_STARTED',
    'PENDING_RETRIEVAL',
    'UNKNOWN_REASON'
);


CREATE TYPE cadence_type AS ENUM (
    'DAILY',
    'WEEKLY',
    'MONTHLY',
    'QUARTERLY',
    'ANNUAL',
    'BIENNIAL',
    'TRIENNIAL',
    'QUINQUENNIAL',
    'DECENNIAL',
    'IRREGULAR',
    'EVENT_BASED'
);


CREATE TYPE observation_status AS ENUM (
    'CURRENT',
    'SUPERSEDED'
);
________________________________________
8. Core Reference Tables
8.1 domains
sql
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
Seed values:
demographics
employment
economy
inflation-cost-of-living
healthcare
education
politics-government
immigration
agriculture-farming
historical-events-legislation
________________________________________
8.2 licenses
sql
CREATE TABLE licenses (
    license_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(128) NOT NULL UNIQUE,
    short_code VARCHAR(64) NOT NULL UNIQUE,
    url TEXT,
    notes TEXT,
    is_open BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
________________________________________
8.3 confidence_tier_definitions
sql
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
________________________________________
8.4 missing_data_reason_definitions
sql
CREATE TABLE missing_data_reason_definitions (
    missing_data_reason missing_data_reason PRIMARY KEY,
    display_name VARCHAR(128) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
________________________________________
9. Source Registry Tables
9.1 sources
sql
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
9.2 datasets
sql
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
9.3 dataset_versions
sql
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
9.4 dataset_series
sql
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
________________________________________
10. Metric Registry Tables
10.1 metrics
sql
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
10.2 metric_series_links
Maps a platform metric to one or more dataset series without forcing merge/blend.
sql
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
Use cases:
unemployment metric linked to different authoritative series across eras
farm count metric linked separately to Census of Agriculture and annual NASS estimate tracks
legal immigration metric linked to distinct visa/program series
________________________________________
11. Ingestion & Raw Data Tables
11.1 ingestion_events
sql
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
11.2 raw_artifacts
Represents files/blobs exactly as retrieved.
sql
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
11.3 raw_observations
sql
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
Policy:
no updates allowed in application layer
immutable by convention + restricted DB permissions
________________________________________
12. Validation & Transformation Tables
12.1 validation_rules
sql
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
12.2 validation_runs
sql
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
12.3 validation_issues
sql
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
12.4 transformation_scripts
sql
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
12.5 transformation_runs
sql
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
________________________________________
13. Published Observation Tables
13.1 standardized_observations
sql
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
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
Constraints:
sql
ALTER TABLE standardized_observations
ADD CONSTRAINT chk_standardized_validity
CHECK (
    (observation_status = 'CURRENT' AND valid_to IS NULL)
    OR
    (observation_status = 'SUPERSEDED' AND valid_to IS NOT NULL)
);


ALTER TABLE standardized_observations
ADD CONSTRAINT chk_standardized_value_presence
CHECK (
    standardized_value IS NOT NULL OR standardized_value_text IS NOT NULL
);
13.2 derived_observations
sql
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
13.3 derived_observation_inputs
sql
CREATE TABLE derived_observation_inputs (
    derived_observation_input_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    derived_observation_id UUID NOT NULL REFERENCES derived_observations(derived_observation_id),
    standardized_observation_id UUID NOT NULL REFERENCES standardized_observations(standardized_observation_id),
    input_role VARCHAR(64) NOT NULL DEFAULT 'SOURCE',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_derived_input UNIQUE (derived_observation_id, standardized_observation_id, input_role)
);
________________________________________
14. Missing Data Tables
14.1 missing_data_records
sql
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
________________________________________
15. Governance & Publication Tables
15.1 dataset_governance
sql
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
15.2 publication_releases
sql
CREATE TABLE publication_releases (
    publication_release_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    release_version VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    released_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(128) NOT NULL
);
15.3 publication_release_items
sql
CREATE TABLE publication_release_items (
    publication_release_item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    publication_release_id UUID NOT NULL REFERENCES publication_releases(publication_release_id),
    dataset_id UUID REFERENCES datasets(dataset_id),
    metric_id UUID REFERENCES metrics(metric_id),
    notes TEXT
);
________________________________________
16. Historical Context Tables
16.1 historical_events
sql
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
16.2 event_domain_links
sql
CREATE TABLE event_domain_links (
    event_domain_link_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    historical_event_id UUID NOT NULL REFERENCES historical_events(historical_event_id),
    domain_id UUID NOT NULL REFERENCES domains(domain_id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_event_domain UNIQUE (historical_event_id, domain_id)
);
16.3 event_metric_links
sql
CREATE TABLE event_metric_links (
    event_metric_link_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    historical_event_id UUID NOT NULL REFERENCES historical_events(historical_event_id),
    metric_id UUID NOT NULL REFERENCES metrics(metric_id),
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_event_metric UNIQUE (historical_event_id, metric_id)
);
16.4 event_source_links
sql
CREATE TABLE event_source_links (
    event_source_link_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    historical_event_id UUID NOT NULL REFERENCES historical_events(historical_event_id),
    source_id UUID NOT NULL REFERENCES sources(source_id),
    citation_note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_event_source UNIQUE (historical_event_id, source_id)
);
________________________________________
17. Citation & Metadata Tables
17.1 citations
sql
CREATE TABLE citations (
    citation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID REFERENCES datasets(dataset_id),
    metric_id UUID REFERENCES metrics(metric_id),
    citation_format VARCHAR(32) NOT NULL,
    citation_text TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    generated_by VARCHAR(128) NOT NULL DEFAULT 'system'
);
17.2 metric_metadata_snapshots
Preserves versioned metadata over time.
sql
CREATE TABLE metric_metadata_snapshots (
    metric_metadata_snapshot_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_id UUID NOT NULL REFERENCES metrics(metric_id),
    metadata_json JSONB NOT NULL,
    effective_from TIMESTAMP NOT NULL DEFAULT NOW(),
    effective_to TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
________________________________________
18. Indexing Strategy
sql
CREATE INDEX idx_datasets_source_id ON datasets(source_id);
CREATE INDEX idx_dataset_series_dataset_id ON dataset_series(dataset_id);
CREATE INDEX idx_metrics_domain_id ON metrics(domain_id);


CREATE INDEX idx_raw_observations_series_date
    ON raw_observations(dataset_series_id, raw_date);


CREATE INDEX idx_standardized_metric_date_current
    ON standardized_observations(metric_id, observation_date)
    WHERE observation_status = 'CURRENT';


CREATE INDEX idx_standardized_metric_approval
    ON standardized_observations(metric_id, approval_status);


CREATE INDEX idx_derived_metric_date_current
    ON derived_observations(metric_id, observation_date)
    WHERE observation_status = 'CURRENT';


CREATE INDEX idx_missing_metric_date
    ON missing_data_records(metric_id, observation_date);


CREATE INDEX idx_historical_events_date
    ON historical_events(event_date);


CREATE INDEX idx_sources_name_trgm
    ON sources USING gin (name gin_trgm_ops);


CREATE INDEX idx_metrics_name_trgm
    ON metrics USING gin (name gin_trgm_ops);
________________________________________
19. Recommended Views
19.1 current_standardized_observations_v
sql
CREATE VIEW current_standardized_observations_v AS
SELECT *
FROM standardized_observations
WHERE observation_status = 'CURRENT'
  AND approval_status = 'APPROVED';
19.2 current_derived_observations_v
sql
CREATE VIEW current_derived_observations_v AS
SELECT *
FROM derived_observations
WHERE observation_status = 'CURRENT';
19.3 metric_availability_v
sql
CREATE VIEW metric_availability_v AS
SELECT
    m.metric_id,
    m.slug AS metric_slug,
    MIN(cso.observation_date) AS first_published_date,
    MAX(cso.observation_date) AS last_published_date,
    COUNT(*) AS observation_count
FROM metrics m
LEFT JOIN current_standardized_observations_v cso
    ON m.metric_id = cso.metric_id
GROUP BY m.metric_id, m.slug;
________________________________________
20. Trigger Recommendations
20.1 updated_at maintenance
sql
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;
Apply to:
domains
sources
datasets
dataset_series
metrics
historical_events
20.2 single current dataset version
Application-enforced preferred initially.
DB constraint can be added later if needed.
Assumption: simplest maintainable MVP favors app-level enforcement here.
________________________________________
21. Raw Immutability Policy
Application rules:
no update/delete endpoints for raw_observations or raw_artifacts
inserts only via ingestion pipeline
DB role for app user should deny update/delete on raw tables in production
Recommended DB grants:
sql
REVOKE UPDATE, DELETE ON raw_artifacts FROM app_user;
REVOKE UPDATE, DELETE ON raw_observations FROM app_user;
________________________________________
22. Revision Model
Revisions do not overwrite rows.
Pattern:
old row becomes SUPERSEDED
valid_topopulated
replacement row inserted with new valid_from
provenance preserved through new raw artifact + ingestion + transformation run
This supports:
BLS benchmark revisions
USDA revised annual estimates
methodology changes across historical reconstruction updates
________________________________________
23. Metric Metadata Coverage
This schema supports required metadata:
Requirement
Storage
Definition
metrics.definition
Units
metrics.units, observation units
Currency basis
metrics.currency_code
Inflation basis year
metrics.inflation_basis_year, observations
Methodology
metrics.methodology
Coverage start/end
metrics.first_available_date, last_available_date, datasets
Geographic scope
metrics.geographic_scope, datasets
Update frequency
datasets.cadence
Source agency
sources.agency_name
Series ID
dataset_series.series_code
Dataset
datasets.name
Confidence tier
observations
Last retrieved
ingestion_events.retrieved_at
Revision history
superseded rows + governance + versions
Known limitations
metrics.known_limitations
License
licenses, linked to sources/datasets
Citation format
citations
________________________________________
24. Future Geographic Expansion Compatibility
Phase G may add state/county data.
Planned extension path:
add geographies table
add geography_id FK to raw/standardized/derived observations
retain US_NATIONAL default seed row
no redesign required for current core tables if null/default policy used carefully
Assumption: defer actual implementation to avoid premature complexity.
________________________________________
25. Initial Seed Data
domains
10 required domains.
confidence_tier_definitions
7 required tiers.
missing_data_reason_definitions
9 required reasons.
licenses
At minimum:
Public Domain
CC BY 4.0
MIT
Apache-2.0
Custom / Source-Specific
________________________________________
26. Initial Alembic Migration Order
extensions
enums
reference tables
source registry tables
metric registry tables
ingestion/raw tables
validation/transformation tables
published observation tables
missing data tables
governance/publication tables
historical context tables
citation/metadata tables
indexes
views
triggers
________________________________________
27. Known Trade-offs
Decision
Benefit
Trade-off
Separate raw/standardized/derived tables
Strong integrity and reproducibility
More joins
Dataset/series/metric link abstraction
Historical continuity without blending
Slight schema complexity
Explicit missing-data table
Honest representation
More records to manage
Versioned transformations
Reproducibility
More governance overhead
App-level enforcement for some invariants
Simpler MVP
Stronger DB constraints may be added later
________________________________________
28. Approval Assessment
Requirement
Status
Immutable raw data
 
Derived separate from source
 
Confidence tiers mandatory
 
Missing data explicit
 
Provenance complete
 
Historical events modeled
 
Agriculture dual-track support
 
Immigration separate estimate track support
 
No forced blending
 
Extensible forward
 
________________________________________
29. Recommended Next Deliverable
Proceed to Source Registry.
Reason:
schema now defines where sources, datasets, series, cadence, licensing, and retrieval methods live
source registry populates the first authoritative operational catalog
data dictionary should follow source registry so metric definitions can reference actual dataset mappings
________________________________________
30. Summary
This schema provides:
a normalized authoritative-source registry;
immutable ingestion records;
versioned dataset retrieval;
explicit validation and transformation governance;
separate raw, standardized, and derived observation layers;
mandatory confidence labeling;
explicit missing-data records;
historical event contextualization;
publication and revision traceability;
future-ready extensibility without current scope expansion.