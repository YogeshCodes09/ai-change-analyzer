from pydantic import BaseModel


class TestRecommendation(BaseModel):
    title: str
    scenario: str
    expected_result: str
    related_risks: list[str]


class TestRecommendations(BaseModel):
    tests: list[TestRecommendation]