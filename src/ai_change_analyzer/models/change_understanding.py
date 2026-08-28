from pydantic import BaseModel, Field


class SearchQueries(BaseModel):
    incident: str = Field(
        description="Query for searching relevant historical incidents."
    )
    change: str = Field(
        description="Query for searching similar historical changes."
    )
    sop: str = Field(
        description="Query for searching relevant SOP requirements."
    )
    product: str = Field(
        description="Query for searching architecture, components, and dependencies."
    )


class ChangeUnderstanding(BaseModel):
    change_summary: str
    affected_components: list[str]
    search_queries: SearchQueries