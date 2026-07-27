"""Streamlit dashboard; reads only pre-built, sanitized JSON files."""

from __future__ import annotations

import json
import os
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
    releases = data["releases.json"]
    release_ids = [item.get("release_id", "unknown") for item in releases]
    selected_release = st.selectbox("Release", release_ids) if release_ids else "unknown"
    release = next((item for item in releases if item.get("release_id") == selected_release), {})
    st.caption("冻结特征基准展示：仅使用已生成的脱敏聚合结果。")
    if release.get("limitations"):
        st.warning("；".join(release["limitations"]))
    leaderboard = [run for run in data["leaderboard.json"] if run.get("release_id") == selected_release]
    overview, board, insights, details = st.tabs(["Overview", "Leaderboard", "Insights", "Details"])
    with overview:
        columns = st.columns(3)
        columns[0].metric("Release", release.get("release_id", "—"))
        columns[1].metric("Models", len(leaderboard))
        columns[2].metric("Tasks", len({run.get("task_id") for run in leaderboard}))
    with board:
        query = st.text_input("搜索模型", placeholder="输入模型 ID")
        choices = sorted({run.get("checkpoint_id") for run in leaderboard})
        checkpoint = st.selectbox("Checkpoint 筛选", ["全部", *choices])
        shown = [run for run in leaderboard if query.lower() in run.get("model_id", "").lower() and (checkpoint == "全部" or run.get("checkpoint_id") == checkpoint)]
        rows = [{"Model": run["model_id"], "Checkpoint": run.get("checkpoint_id"), **run.get("metrics", {}), **run.get("cost", {})} for run in shown]
        st.dataframe(rows, use_container_width=True, hide_index=True)
        if shown:
            expanded = {run["model_id"]: run for run in shown}
            run = expanded[st.selectbox("展开模型详情", list(expanded))]
            st.json({key: run.get(key) for key in ("checkpoint_id", "adapter_version", "cost", "limitations")})
            st.dataframe(run.get("per_class", []), use_container_width=True, hide_index=True)
    with insights:
        rows = data["insights.json"].get("metric_comparison", [])
        if rows:
            metrics = [name for name in ("Macro-F1", "Balanced Accuracy", "Accuracy", "Macro-AUROC") if name in rows[0]]
            st.plotly_chart(px.bar(rows, x="model_id", y=metrics, barmode="group"), use_container_width=True)
            cost = [row for row in rows if row.get("throughput") is not None]
            if cost:
                st.plotly_chart(px.scatter(cost, x="throughput", y="Macro-F1", hover_name="model_id"), use_container_width=True)
            winners = data["insights.json"].get("stable_class_winners", {}).get("F1", {})
            if winners:
                st.plotly_chart(px.bar(x=list(winners), y=list(winners.values()), labels={"x": "Model", "y": "稳定类别赢家数"}), use_container_width=True)
            ranking = data["insights.json"].get("cost_ranking", [])
            if ranking:
                st.subheader("成本排名")
                st.dataframe([{"Model": run["model_id"], **run.get("cost", {})} for run in ranking], hide_index=True, use_container_width=True)
            radar = data["insights.json"].get("radar", [])
            if radar:
                import plotly.graph_objects as go

                dimensions = ["Macro-F1", "Balanced Accuracy", "Accuracy", "Macro-AUROC", "Stability", "Efficiency"]
                figure = go.Figure()
                for row in radar:
                    values = [row.get(key) or 0 for key in dimensions]
                    figure.add_trace(go.Scatterpolar(r=values + values[:1], theta=dimensions + dimensions[:1], fill="toself", name=row["model_id"]))
                st.plotly_chart(figure, use_container_width=True)
        else:
            st.info("当前 Release 没有可视化的聚合指标。")
    with details:
        choices = {run["model_id"]: run for run in leaderboard}
        if choices:
            run = choices[st.selectbox("模型", list(choices))]
            st.json({key: run.get(key) for key in ("checkpoint_id", "adapter_version", "metrics", "cost", "limitations")})
            per_class = run.get("per_class", [])
            st.dataframe(per_class, use_container_width=True, hide_index=True)
            if run.get("confusion_matrix"):
                st.plotly_chart(px.imshow(run["confusion_matrix"], title="混淆矩阵"), use_container_width=True)
            if run.get("stability"):
                st.json({"five_seed_stability": run["stability"]})


if __name__ == "__main__":
    import sys

    results = os.environ.get("OPHBENCH_DASHBOARD_RESULTS")
    run_dashboard(Path(results) if results else Path("benchmark/generated"))
