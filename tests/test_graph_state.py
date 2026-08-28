from ai_change_analyzer.graph.state import ChangeAnalysisState


def test_change_analysis_state() -> None:
    state: ChangeAnalysisState = {
        "original_change": {
            "change_id": "CHG006",
            "title": "Database retry change",
        }
    }

    assert state["original_change"]["change_id"] == "CHG006"