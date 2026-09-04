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
