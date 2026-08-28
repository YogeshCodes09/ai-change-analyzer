from pydantic import BaseModel, Field


class ImpactFinding(BaseModel):
    component: str
    evidence: str
    inference: str
    source: str


class ImpactAnalysis(BaseModel):
    findings: list[ImpactFinding]
    missing_information: list[str] = Field(default_factory=list)