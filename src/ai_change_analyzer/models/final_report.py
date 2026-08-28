from typing import Any

from pydantic import BaseModel


class FinalChangeReport(BaseModel):
    change_id: str
    change_summary: str

    overall_risk: str
    risk_score: int

    affected_components: list[str]
    related_incidents: list[str]

    identified_risks: list[dict[str, Any]]
    recommended_tests: list[dict[str, Any]]

    missing_information: list[str]
    risk_breakdown: list[dict[str, Any]]

    recommendation: str