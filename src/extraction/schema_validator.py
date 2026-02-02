"""Schema validation for RSP extractions using Pydantic models."""

from typing import Optional, Any
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class RiskDomainType(str, Enum):
    """Enumeration of recognized risk domains."""
    CBRN = "cbrn"
    CYBER = "cyber"
    AUTONOMY = "autonomy"
    PERSUASION = "persuasion"
    MODEL_AUTONOMY = "model_autonomy"
    AI_RD = "ai_rd"
    DECEPTION = "deception"
    BIOSECURITY = "biosecurity"
    CHEMICAL = "chemical"
    RADIOLOGICAL = "radiological"
    NUCLEAR = "nuclear"
    OTHER = "other"


class CoverageLevel(str, Enum):
    """Coverage levels for risk domains."""
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"


class SafeguardType(str, Enum):
    """Types of safeguards."""
    DEPLOYMENT = "deployment"
    SECURITY = "security"
    OPERATIONAL = "operational"
    GOVERNANCE = "governance"
    TECHNICAL = "technical"
    PROCEDURAL = "procedural"


class EvaluationType(str, Enum):
    """Types of evaluations."""
    INTERNAL = "internal"
    EXTERNAL = "external"
    RED_TEAM = "red_team"
    BENCHMARK = "benchmark"
    AUDIT = "audit"


class CommitmentType(str, Enum):
    """Types of commitments."""
    PAUSE = "pause"
    DISCLOSURE = "disclosure"
    COOPERATION = "cooperation"
    ASSESSMENT = "assessment"
    OTHER = "other"


class LabInfo(BaseModel):
    """Information about the AI lab and document."""
    name: str = Field(..., description="Name of the AI lab")
    document_name: Optional[str] = Field(None, description="Official document name")
    version: Optional[str] = Field(None, description="Version number")
    publication_date: Optional[str] = Field(None, description="Publication date")
    url: Optional[str] = Field(None, description="URL to official document")


class CapabilityTrigger(BaseModel):
    """A trigger condition for a capability threshold."""
    domain: Optional[str] = Field(None, description="Risk domain")
    capability: Optional[str] = Field(None, description="Specific capability")
    threshold: Optional[str] = Field(None, description="Threshold definition")


class CapabilityThreshold(BaseModel):
    """A capability/risk level defined in the framework."""
    level_name: str = Field(..., description="Human-readable level name")
    level_id: Optional[str] = Field(None, description="Standardized identifier")
    description: Optional[str] = Field(None, description="Level description")
    triggers: list[CapabilityTrigger] = Field(default_factory=list)
    required_safeguards: list[str] = Field(default_factory=list)


class DomainThreshold(BaseModel):
    """Threshold definition for a specific domain."""
    level: Optional[str] = None
    description: Optional[str] = None
    metrics: list[str] = Field(default_factory=list)


class RiskDomain(BaseModel):
    """A risk domain covered by the framework."""
    domain: str = Field(..., description="Domain name")
    coverage: Optional[str] = Field("partial", description="Coverage level")
    thresholds: list[DomainThreshold] = Field(default_factory=list)
    
    @field_validator("domain")
    @classmethod
    def normalize_domain(cls, v: str) -> str:
        """Normalize domain name to lowercase."""
        return v.lower().replace(" ", "_").replace("-", "_")


class Safeguard(BaseModel):
    """A safeguard defined in the framework."""
    type: Optional[str] = Field(None, description="Safeguard type")
    name: Optional[str] = Field(None, description="Safeguard name")
    description: Optional[str] = Field(None, description="Description")
    applicable_levels: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)


class EvaluationRequirement(BaseModel):
    """An evaluation or testing requirement."""
    name: Optional[str] = Field(None, description="Evaluation name")
    type: Optional[str] = Field(None, description="Evaluation type")
    frequency: Optional[str] = Field(None, description="How often required")
    description: Optional[str] = Field(None, description="Description")
    applicable_levels: list[str] = Field(default_factory=list)


class Commitment(BaseModel):
    """A commitment made in the framework."""
    type: Optional[str] = Field(None, description="Commitment type")
    description: Optional[str] = Field(None, description="Description")
    conditions: list[str] = Field(default_factory=list)


class ExtractionMetadata(BaseModel):
    """Metadata about the extraction process."""
    extraction_date: Optional[str] = None
    extraction_model: Optional[str] = None
    source: Optional[str] = None
    source_file: Optional[str] = None
    page_count: Optional[int] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)


class RSPExtractionModel(BaseModel):
    """Complete RSP extraction model for validation."""
    lab_info: LabInfo
    capability_thresholds: list[CapabilityThreshold] = Field(default_factory=list)
    risk_domains: list[RiskDomain] = Field(default_factory=list)
    safeguards: list[Safeguard] = Field(default_factory=list)
    evaluation_requirements: list[EvaluationRequirement] = Field(default_factory=list)
    commitments: list[Commitment] = Field(default_factory=list)
    metadata: Optional[ExtractionMetadata] = None


@dataclass
class ValidationResult:
    """Result of validation."""
    valid: bool
    errors: list[str]
    warnings: list[str]
    fixed_data: Optional[dict] = None


class RSPValidator:
    """Validator for RSP extraction data."""
    
    def validate(self, data: dict) -> ValidationResult:
        """Validate extraction data against the schema.
        
        Args:
            data: Extraction data dictionary
            
        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        errors = []
        warnings = []
        
        # Try to parse with Pydantic
        try:
            RSPExtractionModel(**data)
        except Exception as e:
            errors.append(f"Schema validation failed: {str(e)}")
        
        # Additional validation checks
        warnings.extend(self._check_completeness(data))
        warnings.extend(self._check_consistency(data))
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def fix_common_issues(self, data: dict) -> dict:
        """Attempt to fix common issues in extraction data.
        
        Args:
            data: Extraction data dictionary
            
        Returns:
            Fixed data dictionary
        """
        fixed = data.copy()
        
        # Ensure required structure exists
        if "lab_info" not in fixed or not fixed["lab_info"]:
            fixed["lab_info"] = {"name": "Unknown"}
        
        # Ensure lists exist
        for key in ["capability_thresholds", "risk_domains", "safeguards", 
                   "evaluation_requirements", "commitments"]:
            if key not in fixed or fixed[key] is None:
                fixed[key] = []
        
        # Fix capability thresholds
        fixed["capability_thresholds"] = [
            self._fix_threshold(t) for t in fixed["capability_thresholds"]
        ]
        
        # Fix risk domains
        fixed["risk_domains"] = [
            self._fix_domain(d) for d in fixed["risk_domains"]
        ]
        
        # Normalize domain names
        for domain in fixed["risk_domains"]:
            if "domain" in domain:
                domain["domain"] = domain["domain"].lower().replace(" ", "_")
        
        return fixed
    
    def _fix_threshold(self, threshold: dict) -> dict:
        """Fix common issues in a capability threshold."""
        fixed = threshold.copy()
        
        # Ensure level_name exists
        if "level_name" not in fixed:
            fixed["level_name"] = fixed.get("name", "Unknown Level")
        
        # Generate level_id if missing
        if "level_id" not in fixed:
            fixed["level_id"] = fixed["level_name"].lower().replace(" ", "_").replace("-", "_")
        
        # Ensure triggers is a list
        if "triggers" not in fixed or fixed["triggers"] is None:
            fixed["triggers"] = []
        
        # Ensure required_safeguards is a list
        if "required_safeguards" not in fixed or fixed["required_safeguards"] is None:
            fixed["required_safeguards"] = []
        
        return fixed
    
    def _fix_domain(self, domain: dict) -> dict:
        """Fix common issues in a risk domain."""
        fixed = domain.copy()
        
        # Ensure domain name exists
        if "domain" not in fixed:
            fixed["domain"] = "other"
        
        # Default coverage
        if "coverage" not in fixed:
            fixed["coverage"] = "partial"
        
        # Ensure thresholds is a list
        if "thresholds" not in fixed or fixed["thresholds"] is None:
            fixed["thresholds"] = []
        
        return fixed
    
    def _check_completeness(self, data: dict) -> list[str]:
        """Check for incomplete data."""
        warnings = []
        
        # Check for empty sections
        if not data.get("capability_thresholds"):
            warnings.append("No capability thresholds defined")
        
        if not data.get("risk_domains"):
            warnings.append("No risk domains defined")
        
        if not data.get("safeguards"):
            warnings.append("No safeguards defined")
        
        if not data.get("commitments"):
            warnings.append("No commitments defined")
        
        # Check for missing descriptions
        for i, threshold in enumerate(data.get("capability_thresholds", [])):
            if not threshold.get("description"):
                warnings.append(f"Threshold {i+1} missing description")
        
        return warnings
    
    def _check_consistency(self, data: dict) -> list[str]:
        """Check for consistency issues."""
        warnings = []
        
        # Get all referenced levels
        threshold_levels = {t.get("level_name") for t in data.get("capability_thresholds", [])}
        
        # Check safeguard level references
        for safeguard in data.get("safeguards", []):
            for level in safeguard.get("applicable_levels", []):
                if level not in threshold_levels and threshold_levels:
                    warnings.append(f"Safeguard references unknown level: {level}")
        
        # Check domain coverage
        covered_domains = {d.get("domain") for d in data.get("risk_domains", [])}
        
        # Check triggers reference valid domains
        for threshold in data.get("capability_thresholds", []):
            for trigger in threshold.get("triggers", []):
                domain = trigger.get("domain")
                if domain and domain.lower() not in covered_domains and domain.lower() != "any":
                    warnings.append(f"Trigger references domain not in risk_domains: {domain}")
        
        return warnings


def validate_extraction(data: dict) -> ValidationResult:
    """Convenience function to validate extraction data.
    
    Args:
        data: Extraction data dictionary
        
    Returns:
        ValidationResult
    """
    validator = RSPValidator()
    return validator.validate(data)


def validate_and_fix(data: dict) -> tuple[dict, ValidationResult]:
    """Validate and fix extraction data.
    
    Args:
        data: Extraction data dictionary
        
    Returns:
        Tuple of (fixed_data, validation_result)
    """
    validator = RSPValidator()
    
    # First try to fix common issues
    fixed = validator.fix_common_issues(data)
    
    # Then validate
    result = validator.validate(fixed)
    result.fixed_data = fixed
    
    return fixed, result
