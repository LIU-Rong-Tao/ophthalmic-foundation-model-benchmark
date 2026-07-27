"""Streamlit dashboard; reads only pre-built, sanitized JSON files."""

from __future__ import annotations

import json
from pathlib import Path


def run_dashboard(results: Path) -> None:
    try:
        import plotly.express as px
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError("Dashboard requires ophbench[dashboard]: streamlit and plotly") from exc
    required = ("releases.json", "leaderboard.json", "insights.json", "model_details.json")
    missing = [name for name in required if not (results / name).is_file()]
    if missing:
        raise RuntimeError(f"Generated result files are missing: {', '.join(missing)}")
    data = {name: json.loads((results / name).read_text(encoding="utf-8")) for name in required}
    st.set_page_config(page_title="OphBench", layout="wide")
    st.title("OphBench")
    release = data["releases.json"][0] if data["releases.json"] else {}
    st.caption("冻结特征基准展示：仅使用已生成的脱敏聚合结果。")
    if release.get("limitations"):
        st.warning("；".join(release["limitations"]))
    leaderboard = data["leaderboard.json"]
    overview, board, insights, details = st.tabs(["Overview", "Leaderboard", "Insights", "Details"])
    with overview:
        columns = st.columns(3)
        columns[0].metric("Release", release.get("release_id", "—"))
        columns[1].metric("Models", len(leaderboard))
        columns[2].metric("Tasks", len({run.get("task_id") for run in leaderboard}))
    with board:
        query = st.text_input("搜索模型", placeholder="输入模型 ID")
        shown = [run for run in leaderboard if query.lower() in run.get("model_id", "").lower()]
        st.dataframe([{"Model": run["model_id"], **run.get("metrics", {}), **run.get("cost", {})} for run in shown], use_container_width=True, hide_index=True)
    with insights:
        rows = data["insights.json"].get("metric_comparison", [])
        if rows:
            metrics = [name for name in ("Macro-F1", "Balanced Accuracy", "Accuracy", "Macro-AUROC") if name in rows[0]]
            st.plotly_chart(px.bar(rows, x="model_id", y=metrics, barmode="group"), use_container_width=True)
            cost = [row for row in rows if row.get("throughput") is not None]
            if cost:
                st.plotly_chart(px.scatter(cost, x="throughput", y="Macro-F1", hover_name="model_id"), use_container_width=True)
        else:
            st.info("当前 Release 没有可视化的聚合指标。")
    with details:
        choices = {run["model_id"]: run for run in leaderboard}
        if choices:
            run = choices[st.selectbox("模型", list(choices))]
            st.json({key: run.get(key) for key in ("checkpoint_id", "adapter_version", "metrics", "cost", "limitations")})
            st.dataframe(run.get("per_class", []), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    import sys

    run_dashboard(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("benchmark/generated"))
