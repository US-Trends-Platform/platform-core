import enum

from sqlalchemy import Enum as SAEnum


class ConfidenceClassification(str, enum.Enum):
    """Plan §18 — every observation gets exactly one."""
    OFFICIAL_MEASUREMENT = "official_measurement"
    ADMINISTRATIVE_RECORD = "administrative_record"
    SURVEY_ESTIMATE = "survey_estimate"
    HISTORICAL_RECONSTRUCTION = "historical_reconstruction"
    ACADEMIC_ESTIMATE = "academic_estimate"
    MODELED_DERIVED = "modeled_derived"
    UNKNOWN = "unknown"


# Single shared instance — reuse this exact object in every model that has a
# confidence column. Declaring SAEnum(ConfidenceClassification, name=...) fresh
# in each model file creates duplicate CREATE TYPE statements on Postgres.
confidence_classification_type = SAEnum(
    ConfidenceClassification, name="confidence_classification"
)


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
