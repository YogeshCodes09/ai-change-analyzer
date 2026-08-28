from pathlib import Path

import pandas as pd
from langchain_core.documents import Document


def load_changes(path: str | Path) -> list[Document]:
    df = pd.read_excel(path)

    documents = []

    for _, row in df.iterrows():
        content = (
            f"Change ID: {row['change_id']}\n"
            f"Title: {row['title']}\n"
            f"Description: {row['description']}\n"
            f"Implementation Plan: {row['implementation_plan']}\n"
            f"Rollback Plan: {row['rollback_plan']}\n"
            f"Testing Summary: {row['testing_summary']}\n"
            f"Result: {row['result']}"
        )

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source_type": "change",
                    "change_id": row["change_id"],
                    "application": row["affected_application"],
                    "result": row["result"],
                    "implementation_date": str(row["implementation_date"]),
                    "source": str(path),
                },
            )
        )

    return documents


def load_incidents(path: str | Path) -> list[Document]:
    df = pd.read_excel(path)

    documents = []

    for _, row in df.iterrows():
        content = (
            f"Incident ID: {row['incident_id']}\n"
            f"Title: {row['title']}\n"
            f"Description: {row['description']}\n"
            f"Root Cause: {row['root_cause']}\n"
            f"Resolution: {row['resolution']}"
        )

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source_type": "incident",
                    "incident_id": row["incident_id"],
                    "application": row["application"],
                    "severity": row["severity"],
                    "source": str(path),
                },
            )
        )

    return documents