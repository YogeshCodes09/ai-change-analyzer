import json
from html import escape
from pathlib import Path

import streamlit as st

from ai_change_analyzer.graph.workflow import build_graph

SAMPLE_CHANGE_PATH = Path("data/changes/new_change.json")

st.set_page_config(
    page_title="AI Change Analyzer",
    page_icon="⚡",
    layout="wide",
)


def apply_styles() -> None:
    st.html(
        """
        <style>
        .block-container {
            max-width: 1250px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        .hero {
            padding: 2.2rem 2.5rem;
            border-radius: 24px;
            background: linear-gradient(135deg, #454fb0, #7342ad);
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 14px 40px rgba(0, 0, 0, 0.15);
        }

        .hero-title {
            font-size: 2.6rem;
            font-weight: 800;
            margin-bottom: 0.7rem;
        }

        .hero-subtitle {
            font-size: 1.05rem;
            line-height: 1.7;
            opacity: 0.9;
            max-width: 900px;
        }

        .summary-card {
            padding: 1.3rem 1.5rem;
            border-radius: 16px;
            border: 1px solid rgba(128, 128, 128, 0.2);
            background: rgba(128, 128, 128, 0.05);
            line-height: 1.6;
        }

        .risk-badge {
            display: inline-block;
            padding: 0.45rem 0.9rem;
            border-radius: 999px;
            font-weight: 800;
        }

        .risk-HIGH {
            background: rgba(220, 50, 50, 0.13);
            color: #ff5252;
        }

        .risk-MEDIUM {
            background: rgba(240, 165, 30, 0.13);
            color: #f2a72f;
        }

        .risk-LOW {
            background: rgba(45, 180, 100, 0.13);
            color: #42c878;
        }

        div[data-testid="stMetric"] {
            border: 1px solid rgba(128, 128, 128, 0.18);
            padding: 1rem 1.2rem;
            border-radius: 16px;
        }

        .footer {
            text-align: center;
            opacity: 0.55;
            padding-top: 3rem;
        }
        </style>
        """
    )


@st.cache_resource
def get_graph():
    return build_graph()


def load_sample_change() -> dict:
    with SAMPLE_CHANGE_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def run_analysis(change: dict) -> dict:
    return get_graph().invoke({"original_change": change})


def render_hero() -> None:
    st.html(
        """
        <div class="hero">
            <div class="hero-title">⚡ AI Change Analyzer</div>
            <div class="hero-subtitle">
                Analyze a proposed production change against historical incidents,
                SOP requirements, previous changes and architecture evidence.
                LangGraph orchestrates the workflow while deterministic scoring
                produces the final risk classification.
            </div>
        </div>
        """
    )


def render_risk_badge(risk: str) -> None:
    safe_risk = escape(risk)
    st.html(
        f'<span class="risk-badge risk-{safe_risk}">'
        f"{safe_risk} RISK"
        "</span>"
    )


def render_score_breakdown(report: dict) -> None:
    st.subheader("Risk Score Breakdown")

    for factor in report["risk_breakdown"]:
        score = factor["score"]
        maximum = factor["max_score"]

        st.markdown(
            f"**{factor['factor']} — {score}/{maximum}**"
        )
        st.progress(score / maximum if maximum else 0)
        st.caption(factor["reason"])


def render_overview(report: dict) -> None:
    left, right = st.columns(2)

    with left:
        st.subheader("Affected Components")
        for component in report["affected_components"]:
            st.write(f"• {component}")

    with right:
        st.subheader("Related Historical Incidents")
        for incident in report["related_incidents"]:
            st.code(incident)

    st.subheader("Missing Information")

    if report["missing_information"]:
        for item in report["missing_information"]:
            st.warning(item)
    else:
        st.success("No significant missing information identified.")

    st.subheader("Recommendation")

    message = report["recommendation"]
    risk = report["overall_risk"]

    if risk == "HIGH":
        st.error(message)
    elif risk == "MEDIUM":
        st.warning(message)
    else:
        st.success(message)


def render_risks(report: dict) -> None:
    risks = report["identified_risks"]

    if not risks:
        st.info("No evidence-backed risks were identified.")
        return

    for index, risk in enumerate(risks, start=1):
        title = (
            f"{index}. [{risk['severity']}] "
            f"{risk['title']}"
        )

        with st.expander(title, expanded=index == 1):
            st.markdown("#### Description")
            st.write(risk["description"])

            st.markdown("#### Evidence")
            for evidence in risk["evidence"]:
                st.write(f"• {evidence}")

            st.markdown("#### Reasoning")
            st.write(risk["reasoning"])


def render_tests(report: dict) -> None:
    tests = report["recommended_tests"]

    if not tests:
        st.info("No regression tests were generated.")
        return

    for index, test in enumerate(tests, start=1):
        with st.expander(
            f"{index}. {test['title']}",
            expanded=index == 1,
        ):
            st.markdown("#### Scenario")
            st.write(test["scenario"])

            st.markdown("#### Expected Result")
            st.write(test["expected_result"])

            st.markdown("#### Related Risks")
            for risk in test["related_risks"]:
                st.write(f"• {risk}")


def render_report(report: dict) -> None:
    st.divider()

    change_column, score_column, incident_column = st.columns(
        [1.5, 1, 1]
    )

    with change_column:
        st.caption("CHANGE")
        st.subheader(report["change_id"])
        render_risk_badge(report["overall_risk"])

    with score_column:
        st.metric(
            "Risk Score",
            f"{report['risk_score']}/100",
        )

    with incident_column:
        st.metric(
            "Related Incidents",
            len(report["related_incidents"]),
        )

    st.markdown("### Change Summary")
    st.html(
        f'<div class="summary-card">'
        f'{escape(report["change_summary"])}'
        "</div>"
    )

    overview, risks, tests, scoring = st.tabs(
        [
            "Overview",
            "Risks",
            "Regression Tests",
            "Evidence & Scoring",
        ]
    )

    with overview:
        render_overview(report)

    with risks:
        render_risks(report)

    with tests:
        render_tests(report)

    with scoring:
        render_score_breakdown(report)


def get_change_input() -> dict | None:
    source = st.radio(
        "Change input",
        ["Use sample change", "Upload JSON change"],
        horizontal=True,
    )

    if source == "Use sample change":
        change = load_sample_change()

        with st.expander("Preview sample change"):
            st.json(change)

        return change

    uploaded_file = st.file_uploader(
        "Upload proposed change",
        type=["json"],
    )

    if uploaded_file is None:
        return None

    try:
        change = json.load(uploaded_file)
    except json.JSONDecodeError:
        st.error("The uploaded file is not valid JSON.")
        return None

    with st.expander("Preview uploaded change"):
        st.json(change)

    return change


def main() -> None:
    apply_styles()
    render_hero()

    st.markdown("## Analyze Production Change")

    change = get_change_input()

    if st.button(
        "⚡ Analyze Change",
        type="primary",
        use_container_width=True,
        disabled=change is None,
    ):
        with st.spinner(
            "Retrieving evidence and analyzing change..."
        ):
            try:
                st.session_state["analysis_result"] = run_analysis(
                    change
                )
            except Exception as exc:  # noqa: BLE001
                st.error("Change analysis failed.")
                st.exception(exc)
                return

    result = st.session_state.get("analysis_result")

    if result:
        report = result.get("final_report")

        if report:
            render_report(report)
        else:
            st.warning(
                "Detailed analysis stopped because sufficient "
                "SOP and architecture evidence was unavailable."
            )

            for item in result.get("missing_information", []):
                st.warning(item)

    st.html(
        """
        <div class="footer">
            AI Change Analyzer · LangGraph · ChromaDB · Gemini
        </div>
        """
    )


if __name__ == "__main__":
    main()