from pydantic import BaseModel, Field


class RiskFinding(BaseModel):
    title: str
    description: str
    evidence: list[str]
    reasoning: str
    severity: str = Field(
        description="Potential consequence severity: LOW, MEDIUM, or HIGH."
    )


class RiskAnalysis(BaseModel):
    risks: list[RiskFinding]
    missing_information: list[str] = Field(default_factory=list)