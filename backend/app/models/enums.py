import enum

from sqlalchemy import Enum as SAEnum


class ConfidenceTier(str, enum.Enum):
    """Canonical confidence values used by the live Postgres schema."""

    OFFICIAL_MEASUREMENT = "OFFICIAL_MEASUREMENT"
    ADMINISTRATIVE_RECORD = "ADMINISTRATIVE_RECORD"
    SURVEY_ESTIMATE = "SURVEY_ESTIMATE"
    HISTORICAL_RECONSTRUCTION = "HISTORICAL_RECONSTRUCTION"
    ACADEMIC_ESTIMATE = "ACADEMIC_ESTIMATE"
    MODELED_DERIVED = "MODELED_DERIVED"
    UNKNOWN = "UNKNOWN"


# Backward compatibility for legacy imports that still use the older naming.
ConfidenceClassification = ConfidenceTier


# Reuse one shared enum instance so SQLAlchemy does not try to create a second
# Postgres enum type with the same name.
confidence_tier_type = SAEnum(ConfidenceTier, name="confidence_tier", create_type=False)
confidence_classification_type = confidence_tier_type


class ObservationStatus(str, enum.Enum):
    """Postgres enum `observation_status` (ADR-002 revision handling)."""

    CURRENT = "CURRENT"
    SUPERSEDED = "SUPERSEDED"


class MissingDataReason(str, enum.Enum):
    """Postgres enum `missing_data_reason` (ADR-005, PRD FR-7)."""

    NO_AUTHORITATIVE_DATASET = "NO_AUTHORITATIVE_DATASET"
    NOT_YET_PUBLISHED = "NOT_YET_PUBLISHED"
    HISTORICAL_DATA_UNAVAILABLE = "HISTORICAL_DATA_UNAVAILABLE"
    METHODOLOGICAL_BREAK = "METHODOLOGICAL_BREAK"
    SOURCE_DISCONTINUED = "SOURCE_DISCONTINUED"
    DATA_SUPPRESSION = "DATA_SUPPRESSION"
    COLLECTION_NOT_STARTED = "COLLECTION_NOT_STARTED"
    PENDING_RETRIEVAL = "PENDING_RETRIEVAL"
    UNKNOWN_REASON = "UNKNOWN_REASON"


class CadenceType(str, enum.Enum):
    """Postgres enum `cadence_type`."""

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUAL = "ANNUAL"
    BIENNIAL = "BIENNIAL"
    TRIENNIAL = "TRIENNIAL"
    QUINQUENNIAL = "QUINQUENNIAL"
    DECENNIAL = "DECENNIAL"
    IRREGULAR = "IRREGULAR"
    EVENT_BASED = "EVENT_BASED"


# These four columns are Postgres ENUM types in the live schema, not VARCHAR.
# Declaring them as String made reads appear to work while any comparison
# failed at runtime with "operator does not exist: <enum> = character varying".
observation_status_type = SAEnum(ObservationStatus, name="observation_status", create_type=False)
missing_data_reason_type = SAEnum(MissingDataReason, name="missing_data_reason", create_type=False)
cadence_type = SAEnum(CadenceType, name="cadence_type", create_type=False)


class DatasetLifecycleStatus(str, enum.Enum):
    """Plan §21."""
    IDENTIFIED = "identified"
    REGISTERED = "registered"
    RETRIEVED = "retrieved"
    VALIDATED = "validated"
    STANDARDIZED = "standardized"
    APPROVED = "approved"
    PUBLISHED = "published"
    REVISED = "revised"
    DEPRECATED = "deprecated"


class SourcePriorityTier(int, enum.Enum):
    """Plan §44."""
    US_GOVERNMENT_AGENCY = 1
    INDEPENDENT_PUBLIC_INSTITUTION = 2
    PEER_REVIEWED_ACADEMIC = 3
    INTERNATIONAL_ORGANIZATION = 4
    DOCUMENTED_HISTORICAL_RECONSTRUCTION = 5
