"""Streamlit dashboard for pre-built, sanitized OphBench benchmark results.

The interface uses an independent, data-dense benchmark design: a scalable
leaderboard, capability matrices, and an auditable model evidence ledger.  It
reads only OphBench generated JSON and imports no OphAgent code or data.
"""

from __future__ import annotations

import json
import os
from html import escape
from pathlib import Path
from typing import Any

TOKENS = {
    "ink": "#152238",
    "muted": "#667085",
    "line": "#DCE3EC",
    "canvas": "#F7F9FC",
    "surface": "#FFFFFF",
    "nav": "#101828",
    "nav_hover": "#1D2939",
    "teal": "#2855D9",
    "teal_soft": "#EDF2FF",
    "amber": "#D97706",
    "amber_soft": "#FFF7E8",
}


def _inject_css(st: Any) -> None:
    """Apply OphBench's independent, data-dense benchmark design system."""

    st.markdown(
        f"""
        <style>
        :root {{
          --ob-ink: {TOKENS["ink"]}; --ob-muted: {TOKENS["muted"]};
          --ob-line: {TOKENS["line"]}; --ob-canvas: {TOKENS["canvas"]};
          --ob-surface: {TOKENS["surface"]}; --ob-nav: {TOKENS["nav"]};
          --ob-teal: {TOKENS["teal"]}; --ob-teal-soft: {TOKENS["teal_soft"]};
          --ob-amber: {TOKENS["amber"]}; --ob-amber-soft: {TOKENS["amber_soft"]};
        }}
        .stApp, [data-testid="stAppViewContainer"] {{
          background: var(--ob-canvas); color: var(--ob-ink);
          font-family: Inter, "Noto Sans SC", "Microsoft YaHei", sans-serif;
        }}
        .main .block-container {{ max-width: 1480px; padding: .8rem 2.1rem 3rem; }}
        header[data-testid="stHeader"] {{ background:transparent; height:0; }}
        #MainMenu, footer, [data-testid="stToolbar"] {{ visibility:hidden; }}
        .ob-brand-mark {{
          width:1.85rem; height:1.85rem; display:inline-grid; place-items:center;
          background:var(--ob-nav); border-radius:7px;
          color:#FFFFFF; font-size:.68rem; font-weight:850; letter-spacing:-.02em;
        }}
        .ob-page-head {{
          display:flex; align-items:flex-end; justify-content:space-between; gap:1.2rem;
          padding:1rem 0 .75rem; margin-bottom:.1rem;
        }}
        .ob-eyebrow {{ color:var(--ob-teal); font-size:.64rem; font-weight:800;
          letter-spacing:.12em; text-transform:uppercase; margin-bottom:.55rem; }}
        .ob-page-title {{ color:var(--ob-ink); font-size:1.7rem; font-weight:800;
          line-height:1.12; margin:0; letter-spacing:-.035em; }}
        .ob-page-copy {{ color:var(--ob-muted); font-size:.86rem; line-height:1.55;
          margin-top:.65rem; max-width:760px; }}
        .ob-page-context {{ white-space:nowrap; color:#344054; font-size:.7rem; font-weight:700;
          background:var(--ob-teal-soft); border:1px solid #C7E7E2; border-radius:999px;
          padding:.42rem .7rem; }}
        .ob-boundary {{
          display:flex; gap:.6rem; align-items:flex-start; background:var(--ob-amber-soft);
          border:1px solid #EAD7AA; border-left:4px solid var(--ob-amber); padding:.65rem .8rem;
          color:#624D1D; line-height:1.5; font-size:.78rem; margin:0 0 1rem; }}
        .ob-metric {{ background:#FFFFFF;
          border:1px solid var(--ob-line); border-radius:7px;
          padding:1rem 1.05rem; min-height:112px; position:relative; overflow:hidden;
          box-shadow:none; }}
        .ob-metric:before {{ content:""; position:absolute; left:0; top:0; right:0;
          height:2px; background:var(--accent,var(--ob-teal)); }}
        .ob-metric span {{
          display:block; color:var(--ob-muted); font-size:.72rem; font-weight:700;
        }}
        .ob-metric b {{ display:block; color:var(--ob-ink); font-size:1.55rem; line-height:1.2;
          margin:.25rem 0; font-variant-numeric:tabular-nums; overflow-wrap:anywhere; }}
        .ob-metric small {{ display:block; color:#7C8797; font-size:.7rem; line-height:1.35; }}
        .ob-section {{ margin:1.5rem 0 .72rem; }}
        .ob-section h3 {{ font-size:1.05rem; color:var(--ob-ink); margin:0 0 .25rem; }}
        .ob-section p {{ font-size:.76rem; color:var(--ob-muted); margin:0; line-height:1.5; }}
        .ob-panel {{ background:var(--ob-surface); border:1px solid var(--ob-line);
          border-radius:8px; padding:1.15rem; box-shadow:none; }}
        [data-testid="stDataFrame"] {{ border:1px solid var(--ob-line); border-radius:4px;
          overflow:hidden; background:var(--ob-surface); }}
        [data-testid="stTabs"] [data-baseweb="tab-list"] {{
          gap:1.15rem; border-bottom:1px solid var(--ob-line);
        }}
        [data-testid="stTabs"] [data-baseweb="tab"] {{ padding:.65rem .05rem; border-radius:0;
          color:#607085; font-weight:600; }}
        [data-testid="stTabs"] [aria-selected="true"] {{ color:var(--ob-teal); font-weight:750; }}
        [data-testid="stTabs"] [data-baseweb="tab-highlight"] {{ background:var(--ob-teal); }}
        [data-testid="stRadio"] [role="radiogroup"] {{ gap:1.75rem;
          border-bottom:1px solid var(--ob-line); padding-bottom:.15rem; }}
        [data-testid="stRadio"] label {{ padding:.55rem 0 .72rem; color:#66758a;
          font-weight:650; transition:color .18s ease; }}
        [data-testid="stRadio"] label:has(input:checked) {{ color:var(--ob-teal);
          border-bottom:2px solid var(--ob-teal); }}
        [data-testid="stRadio"] input {{ display:none; }}
        [data-testid="stRadio"] label > div > div > div:first-child {{ display:none; }}
        .ob-rank-table {{ width:100%; border-collapse:separate; border-spacing:0; overflow:hidden;
          border:1px solid var(--ob-line); border-radius:12px; background:#fff; font-size:.82rem;
          box-shadow:0 7px 24px rgba(31,50,73,.04); }}
        .ob-rank-table th {{ background:#f7f9fc; color:#68778a; text-align:left; font-size:.68rem;
          letter-spacing:.03em; text-transform:uppercase; padding:.72rem .8rem;
          border-bottom:1px solid var(--ob-line); }}
        .ob-rank-table td {{ padding:.92rem .8rem; border-bottom:1px solid #edf1f5;
          color:var(--ob-ink); }}
        .ob-rank-table tr:last-child td {{ border-bottom:0; }}
        .ob-rank-table tbody tr:hover {{ background:#f2faf8; }}
        .ob-rank-table .rank {{ color:var(--ob-teal); font-weight:800; width:52px; }}
        .ob-rank-table .model {{ font-weight:780; }}
        .ob-rank-table .score {{ font-variant-numeric:tabular-nums; font-weight:750; }}
        .ob-rank-table .best {{ background:var(--ob-teal-soft); color:#173E9A; }}
        .ob-rank-table .rank-note {{ display:block; color:#7A8798; font-size:.62rem;
          font-weight:600; margin-top:.12rem; }}
        .ob-rank-table .muted {{ color:#8a97a8; }}
        .ob-taskbar {{ display:flex; align-items:center; gap:.45rem; flex-wrap:wrap;
          margin:.35rem 0 .9rem; color:var(--ob-muted); font-size:.7rem; }}
        .ob-pill {{ display:inline-flex; align-items:center; border:1px solid var(--ob-line);
          border-radius:999px; padding:.3rem .58rem; background:#fff; color:#506176;
          font-weight:650; }}
        .ob-rank-list {{ display:grid; gap:0; border:1px solid var(--ob-line);
          border-radius:8px; overflow:hidden; background:#fff; }}
        .ob-rank-row {{ background:#fff; border:0; border-bottom:1px solid #EDF0F4;
          border-radius:0; box-shadow:none; overflow:hidden;
          transition:background .15s ease; }}
        .ob-rank-row:last-child {{ border-bottom:0; }}
        .ob-rank-row:hover {{ background:#F8FAFC; }}
        .ob-rank-row summary {{ cursor:pointer; list-style:none; display:grid;
          grid-template-columns:54px minmax(190px,1.35fr) repeat(5,minmax(92px,.72fr)) 24px;
          align-items:center; gap:.65rem; padding:.82rem .9rem; }}
        .ob-rank-list[data-metrics="4"] .ob-rank-row summary {{
          grid-template-columns:54px minmax(190px,1.35fr) repeat(4,minmax(92px,.72fr)) 24px;
        }}
        .ob-rank-list[data-metrics="3"] .ob-rank-row summary {{
          grid-template-columns:54px minmax(190px,1.35fr) repeat(3,minmax(92px,.72fr)) 24px;
        }}
        .ob-rank-row summary::-webkit-details-marker {{ display:none; }}
        .ob-rank-number {{ width:32px; height:32px; border-radius:0; display:grid;
          place-items:center; background:transparent; color:#98A2B3;
          font-size:.76rem; font-weight:850; font-variant-numeric:tabular-nums; }}
        .ob-rank-model b {{ display:block; color:var(--ob-ink); font-size:.86rem; }}
        .ob-rank-model small {{ display:block; color:var(--ob-muted); font-size:.66rem;
          margin-top:.16rem; overflow-wrap:anywhere; }}
        .ob-rank-score span {{ display:block; color:#7A8798; font-size:.58rem;
          text-transform:uppercase; letter-spacing:.035em; }}
        .ob-rank-score b {{ display:block; color:var(--ob-ink); font-size:.84rem;
          margin-top:.13rem; font-variant-numeric:tabular-nums; }}
        .ob-chevron {{ color:var(--ob-teal); font-size:.9rem; transition:transform .18s ease; }}
        .ob-rank-row[open] .ob-chevron {{ transform:rotate(180deg); }}
        .ob-rank-detail {{ border-top:1px solid #EDF1F5; background:#FAFCFD;
          padding:.75rem .9rem .9rem 4.25rem; display:grid;
          grid-template-columns:repeat(4,minmax(0,1fr)); gap:.65rem; }}
        .ob-rank-detail div {{ color:var(--ob-muted); font-size:.68rem; line-height:1.45; }}
        .ob-rank-detail b {{ display:block; color:#41536A; font-size:.62rem;
          text-transform:uppercase; letter-spacing:.04em; margin-bottom:.15rem; }}
        .ob-winner {{ display:inline-flex; align-items:center; border-radius:999px;
          background:#FFF5DA; color:#8B5A04; border:1px solid #F0D79B;
          padding:.12rem .4rem; font-size:.58rem; font-weight:800; margin-left:.35rem; }}
        [data-testid="stExpander"] {{ border-color:var(--ob-line); border-radius:5px;
          background:var(--ob-surface); }}
        .ob-topnav-brand {{ display:flex; align-items:center; gap:.65rem; color:var(--ob-ink);
          font-size:1.02rem; font-weight:800; letter-spacing:-.02em; }}
        .ob-topnav-copy {{ display:block; color:#8190A3; font-size:.64rem; font-weight:650;
          letter-spacing:.06em; text-transform:uppercase; margin-top:.12rem; }}
        .ob-summary {{ background:var(--ob-surface); border:1px solid var(--ob-line);
          border-radius:12px;
          padding:1rem; min-height:116px; box-shadow:0 5px 18px rgba(31,50,73,.035); }}
        .ob-summary b {{ display:block; color:var(--ob-ink); font-size:.88rem;
          margin-bottom:.35rem; }}
        .ob-summary p {{ margin:0; color:var(--ob-muted); font-size:.73rem; line-height:1.5; }}
        .ob-footer {{ margin-top:2.1rem; padding-top:.9rem; border-top:1px solid var(--ob-line);
          color:var(--ob-muted); font-size:.72rem; line-height:1.55; }}
        .ob-model-hero {{ background:#FFFFFF; border:1px solid var(--ob-line);
          border-radius:8px; padding:1.15rem 1.25rem; color:var(--ob-ink); margin:.5rem 0 1rem;
          box-shadow:none; }}
        .ob-model-hero small {{ color:#667085; text-transform:uppercase; letter-spacing:.09em;
          font-weight:750; font-size:.66rem; }}
        .ob-model-hero h2 {{ margin:.35rem 0 .25rem; font-size:1.55rem; }}
        .ob-model-hero p {{ margin:0; color:#667085; font-size:.78rem; }}
        .ob-evidence-table {{ width:100%; border-collapse:collapse; margin:.75rem 0 1rem;
          background:#fff; border:1px solid var(--ob-line); font-size:.76rem; }}
        .ob-evidence-table th {{ background:#F8FAFC; color:#667085; font-size:.64rem;
          text-transform:uppercase; letter-spacing:.04em; padding:.65rem; text-align:left;
          border-bottom:1px solid var(--ob-line); }}
        .ob-evidence-table td {{ padding:.7rem .65rem; border-bottom:1px solid #EDF0F4;
          vertical-align:top; }}
        .ob-evidence-table tr:last-child td {{ border-bottom:0; }}
        .ob-status-ok {{ color:#067647; font-weight:750; }}
        .ob-status-muted {{ color:#98A2B3; }}
        .ob-info-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.75rem; }}
        .ob-info {{ background:#fff; border:1px solid var(--ob-line);
          border-radius:10px; padding:.85rem; }}
        .ob-info span {{ display:block; color:var(--ob-muted); font-size:.68rem; font-weight:700; }}
        .ob-info b {{ display:block; margin-top:.28rem; color:var(--ob-ink);
          font-size:.88rem; overflow-wrap:anywhere; }}
        .ob-note {{ background:#F8FAFC; border:1px solid var(--ob-line); border-radius:10px;
          padding:.9rem 1rem; color:var(--ob-muted); font-size:.77rem; line-height:1.55; }}
        .ob-note b {{ color:var(--ob-ink); }}
        .ob-chart-title {{ font-size:.92rem; font-weight:800; color:var(--ob-ink);
          margin-bottom:.2rem; }}
        .ob-chart-copy {{ font-size:.72rem; color:var(--ob-muted); margin-bottom:.5rem; }}
        .ob-class-panel {{ background:#fff; border:1px solid var(--ob-line);
          border-radius:8px; padding:.85rem; min-height:390px; }}
        .ob-class-panel h4 {{ margin:0; color:var(--ob-ink); font-size:.92rem; }}
        .ob-class-panel > small {{ display:block; color:var(--ob-muted); font-size:.65rem;
          margin:.18rem 0 .7rem; }}
        .ob-class-row {{ display:grid; grid-template-columns:24px minmax(92px,1fr) 70px 42px;
          align-items:center; gap:.45rem; min-height:34px; border-top:1px solid #EEF2F6;
          font-size:.68rem; }}
        .ob-class-row .rank {{ color:#98A2B3; font-weight:800; }}
        .ob-class-row b {{ color:#344054; overflow:hidden; text-overflow:ellipsis;
          white-space:nowrap; }}
        .ob-class-row strong {{ color:var(--ob-ink); text-align:right;
          font-variant-numeric:tabular-nums; }}
        .ob-class-bar {{ height:5px; background:#E9EFF8; border-radius:999px; overflow:hidden; }}
        .ob-class-bar i {{ display:block; height:100%; background:var(--ob-teal);
          border-radius:999px; }}
        .ob-class-row.winner {{ background:#FFFBEB; }}
        .ob-class-row.winner .ob-class-bar i {{ background:var(--ob-amber); }}
        .ob-class-row.winner strong {{ color:#9A5A04; }}
        div[data-testid="stPlotlyChart"] {{ background:#fff; border:1px solid var(--ob-line);
          border-radius:8px; overflow:hidden; box-shadow:none; }}
        [data-baseweb="input"] > div, [data-baseweb="select"] > div {{
          border-color:var(--ob-line) !important; border-radius:9px !important;
          background:#fff !important;
        }}
        @media (prefers-reduced-motion: reduce) {{
          * {{ transition:none !important; animation:none !important; }}
        }}
        @media (max-width: 760px) {{
          .main .block-container {{ padding:1.15rem .9rem 3rem; }}
          .ob-page-head {{ align-items:flex-start; flex-direction:column; }}
          .ob-page-context {{ white-space:normal; }}
          .ob-page-title {{ font-size:1.55rem; }}
          .ob-info-grid {{ grid-template-columns:1fr; }}
          .ob-class-row {{ grid-template-columns:22px minmax(80px,1fr) 54px 38px; }}
          .ob-rank-table {{ display:block; overflow-x:auto; }}
          .ob-rank-row summary {{ grid-template-columns:42px 1fr 72px 20px; }}
          .ob-rank-row .ob-rank-score:nth-of-type(n+3) {{ display:none; }}
          .ob-rank-detail {{ padding-left:.9rem; grid-template-columns:1fr 1fr; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _metric_card(label: str, value: str | int, note: str, *, accent: str = "#0F766E") -> str:
    return (
        f'<div class="ob-metric" style="--accent:{accent}"><span>{label}</span>'
        f"<b>{value}</b><small>{note}</small></div>"
    )


def _section(title: str, description: str) -> str:
    return f'<div class="ob-section"><h3>{title}</h3><p>{description}</p></div>'


def _configure_figures(px: Any, go: Any | None = None) -> None:
    template = {
        "layout": {
            "paper_bgcolor": "#FFFFFF",
            "plot_bgcolor": "#FFFFFF",
            "font": {"color": TOKENS["ink"], "family": "Inter, Noto Sans SC, sans-serif"},
            "colorway": ["#0F766E", "#245F9E", "#B7791F", "#7C3AED", "#B42318"],
            "xaxis": {"gridcolor": "#E6EDF5", "linecolor": "#DCE3EB"},
            "yaxis": {"gridcolor": "#E6EDF5", "linecolor": "#DCE3EB"},
        }
    }
    px.defaults.template = template
    if go is not None:
        go.layout.Template(template)


def _render_header(st: Any, task: dict[str, Any]) -> None:
    task_name = escape(str(task.get("display_name") or task.get("task_id") or "Benchmark"))
    st.markdown(
        '<div class="ob-page-head"><div>'
        '<div class="ob-eyebrow">OphBench · Foundation Model Benchmark</div>'
        '<h1 class="ob-page-title">Fundus Foundation Model Benchmark</h1>'
        f'<div class="ob-page-copy">{task_name} · 统一冻结特征协议下的模型迁移能力比较；'
        "页面不读取原始图像、病例身份信息或实验目录。</div></div>"
        '<div class="ob-page-context">只读 Benchmark</div></div>',
        unsafe_allow_html=True,
    )


def _render_topnav(st: Any, release_ids: list[str]) -> str:
    left, center, right = st.columns((3, 5, 2), vertical_alignment="center")
    left.markdown(
        '<div class="ob-topnav-brand"><span class="ob-brand-mark">OB</span><span>OphBench'
        '<small class="ob-topnav-copy">Foundation model benchmark</small></span></div>',
        unsafe_allow_html=True,
    )
    center.markdown("", unsafe_allow_html=True)
    return right.selectbox("Release", release_ids, label_visibility="collapsed")


def _render_task_switcher(
    st: Any,
    tasks: list[dict[str, Any]],
    default_task_id: str,
) -> str:
    task_ids = [str(item.get("task_id")) for item in tasks if item.get("task_id")]
    if not task_ids:
        return ""
    default_index = task_ids.index(default_task_id) if default_task_id in task_ids else 0
    labels = {
        str(item["task_id"]): str(item.get("display_name") or item["task_id"])
        for item in tasks
        if item.get("task_id")
    }
    selector, metadata = st.columns((1.35, 2.65), gap="small", vertical_alignment="bottom")
    selected = selector.selectbox(
        "Benchmark task",
        task_ids,
        index=default_index,
        format_func=lambda task_id: labels.get(task_id, task_id),
        key="benchmark_task",
    )
    task = _task_for_id(tasks, selected)
    evidence_status = str(task.get("evidence_status") or "")
    evidence_pills = ""
    if evidence_status == "diagnostic_only":
        evidence_pills = (
            '<span class="ob-pill"><b>仅数据诊断</b></span>'
            '<span class="ob-pill"><b>高采集捷径风险</b></span>'
        )
    metadata.markdown(
        '<div class="ob-taskbar">'
        f'<span class="ob-pill">{escape(_task_type_label(task.get("task_type")))}</span>'
        f'<span class="ob-pill">{escape(_text_or_dash(task.get("class_count")))} classes</span>'
        f'<span class="ob-pill">{escape(_text_or_dash(task.get("sample_count")))} samples</span>'
        '<span class="ob-pill">Frozen features</span>'
        f"{evidence_pills}"
        "</div>",
        unsafe_allow_html=True,
    )
    return selected


def _release_for_id(releases: list[dict[str, Any]], release_id: str) -> dict[str, Any]:
    return next((item for item in releases if item.get("release_id") == release_id), {})


def _dashboard_rows(
    data: dict[str, Any],
    release_id: str,
    task_id: str,
) -> list[dict[str, Any]]:
    return [
        run
        for run in data["leaderboard.json"]
        if run.get("release_id") == release_id and run.get("task_id") == task_id
    ]


def _task_for_id(tasks: list[dict[str, Any]], task_id: str) -> dict[str, Any]:
    return next(
        (item for item in tasks if str(item.get("task_id")) == task_id),
        {"task_id": task_id, "display_name": task_id},
    )


def _task_insights(insights: dict[str, Any], task_id: str) -> dict[str, Any]:
    return insights.get("by_task", {}).get(task_id, insights)


def _metric_value(run: dict[str, Any], name: str) -> float | None:
    value = run.get("metrics", {}).get(name)
    return float(value) if isinstance(value, (float, int)) else None


def _metric_display(run: dict[str, Any], name: str) -> str:
    value = _metric_value(run, name)
    return "—" if value is None else f"{value:.3f}"


METRIC_SPECS = (
    ("Macro-F1", "Macro-F1"),
    ("Balanced Accuracy", "BAcc"),
    ("Accuracy", "Accuracy"),
    ("Top-3 Accuracy", "Top-3"),
    ("Macro-AUROC", "AUROC"),
)


def _available_metric_specs(runs: list[dict[str, Any]]) -> list[tuple[str, str]]:
    return [
        spec
        for spec in METRIC_SPECS
        if any(_metric_value(run, spec[0]) is not None for run in runs)
    ]


def _class_count(leaderboard: list[dict[str, Any]]) -> int:
    return len(
        {
            str(row.get("class_id") or row.get("class_name"))
            for run in leaderboard
            for row in run.get("per_class", [])
        }
    )


def _model_label(model_id: str) -> str:
    return {
        "retfound-green": "RETFound-Green",
        "retfound": "RETFound CFP",
        "eyeclip": "EyeCLIP",
        "flair": "FLAIR",
        "keepfit": "KeepFIT",
        "ret-clip": "RET-CLIP",
        "retizero": "RetiZero",
        "urfound": "UrFound",
        "vilref": "ViLReF",
    }.get(model_id, model_id)


def _text_or_dash(value: Any) -> str:
    if value is None:
        return "—"
    text = str(value).strip()
    return "—" if not text or text.lower() in {"unknown", "none", "null", "nan"} else text


def _task_type_label(value: Any) -> str:
    return {
        "single_label_multiclass_classification": "单标签多分类",
        "ordinal_classification": "有序多分类",
        "observed_directory_multilabel_probe": "观测多标签探针",
    }.get(str(value), _text_or_dash(value))


def _leaderboard_rows(
    runs: list[dict[str, Any]],
    *,
    leader_badge: str = "LEADER",
) -> str:
    metrics = _available_metric_specs(runs)
    rows = []
    for rank, run in enumerate(runs, start=1):
        model_id = str(run.get("model_id") or "unknown")
        model_name = escape(_model_label(model_id))
        checkpoint = escape(_text_or_dash(run.get("checkpoint_id")))
        winner = (
            f'<span class="ob-winner">{escape(leader_badge)}</span>' if rank == 1 else ""
        )
        score_cells = "".join(
            '<div class="ob-rank-score">'
            f"<span>{escape(short)}</span><b>{escape(_metric_display(run, metric))}</b>"
            "</div>"
            for metric, short in metrics
        )
        cost = run.get("cost") or {}
        limitations = run.get("limitations") or []
        limitation_text = (
            "；".join(escape(str(item)) for item in limitations[:2])
            if limitations
            else "未提供额外限制说明"
        )
        rows.append(
            '<details class="ob-rank-row">'
            f'<summary aria-label="展开 {model_name} 详情">'
            f'<span class="ob-rank-number">{rank:02d}</span>'
            f'<span class="ob-rank-model"><b>{model_name}{winner}</b>'
            f"<small>{checkpoint}</small></span>"
            f'{score_cells}<span class="ob-chevron">⌄</span></summary>'
            '<div class="ob-rank-detail">'
            f"<div><b>Adapter</b>{escape(_text_or_dash(run.get('adapter_version')))}</div>"
            f"<div><b>Feature dim</b>{escape(_text_or_dash(cost.get('feature_dim')))}</div>"
            f"<div><b>Qualification</b>{escape(_text_or_dash(run.get('qualification_status')))}</div>"
            f"<div><b>Limitations</b>{limitation_text}</div>"
            "</div></details>"
        )
    return (
        f'<div class="ob-rank-list" data-metrics="{len(metrics)}">'
        + "".join(rows)
        + "</div>"
    )


def _release_table(leaderboard: list[dict[str, Any]]) -> str:
    body = "".join(
        "<tr>"
        f"<td class='model'>{escape(_model_label(str(run.get('model_id', '—'))))}</td>"
        f"<td class='score'>{escape(_metric_display(run, 'Macro-F1'))}</td>"
        f"<td>{escape(_metric_display(run, 'Balanced Accuracy'))}</td>"
        f"<td>{escape(_metric_display(run, 'Accuracy'))}</td>"
        "</tr>"
        for run in sorted(
            leaderboard,
            key=lambda item: _metric_value(item, "Macro-F1") or float("-inf"),
            reverse=True,
        )
    )
    return (
        "<table class='ob-rank-table'><thead><tr><th>Model</th><th>Macro-F1</th>"
        f"<th>Balanced Accuracy</th><th>Accuracy</th></tr></thead><tbody>{body}</tbody></table>"
    )


def _metric_rank_table(rows: list[dict[str, Any]]) -> str:
    metric_specs = [
        spec
        for spec in METRIC_SPECS
        if any(isinstance(row.get(spec[0]), (int, float)) for row in rows)
    ]
    rankings: dict[str, dict[str, int]] = {}
    best_values: dict[str, float] = {}
    for metric, _ in metric_specs:
        available = sorted(
            {
                float(row[metric])
                for row in rows
                if isinstance(row.get(metric), (int, float))
            },
            reverse=True,
        )
        rankings[metric] = {str(value): rank for rank, value in enumerate(available, start=1)}
        if available:
            best_values[metric] = available[0]

    body = []
    for row in sorted(
        rows,
        key=lambda item: float(item.get("Macro-F1") or float("-inf")),
        reverse=True,
    ):
        cells = []
        for metric, _ in metric_specs:
            value = row.get(metric)
            if not isinstance(value, (int, float)):
                cells.append("<td class='muted'>—</td>")
                continue
            numeric = float(value)
            rank = rankings[metric][str(numeric)]
            delta = numeric - best_values[metric]
            note = f"#{rank}" if rank == 1 else f"#{rank} · {delta:+.3f}"
            css_class = "score best" if rank == 1 else "score"
            cells.append(
                f"<td class='{css_class}'>{numeric:.3f}"
                f"<span class='rank-note'>{escape(note)}</span></td>"
            )
        body.append(
            "<tr>"
            f"<td class='model'>{escape(_model_label(str(row.get('model_id') or '—')))}</td>"
            + "".join(cells)
            + "</tr>"
        )
    headers = "".join(f"<th>{escape(label)}</th>" for _, label in metric_specs)
    return (
        "<table class='ob-rank-table'><thead><tr><th>Model</th>"
        + headers
        + "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table>"
    )


def _per_class_table(rows: list[dict[str, Any]]) -> str:
    def pick(row: dict[str, Any], *names: str) -> Any:
        for name in names:
            if name in row:
                return row[name]
        return None

    def metric(row: dict[str, Any], *names: str) -> str:
        value = pick(row, *names)
        return f"{float(value):.3f}" if isinstance(value, (int, float)) else "—"

    ordered = sorted(rows, key=lambda row: int(pick(row, "class_id", "\ufeffclass_id") or 0))
    rendered_rows = []
    for row in ordered:
        class_id = escape(_text_or_dash(pick(row, "class_id", "\ufeffclass_id")))
        class_name = escape(_text_or_dash(pick(row, "class_name", "Class Name")))
        support = escape(_text_or_dash(pick(row, "Support", "support")))
        rendered_rows.append(
            "<tr>"
            f"<td class='rank'>{class_id}</td>"
            f"<td class='model'>{class_name}</td>"
            f"<td class='score'>{metric(row, 'F1')}</td>"
            f"<td>{metric(row, 'Precision')}</td>"
            f"<td>{metric(row, 'Recall', 'Sensitivity')}</td>"
            f"<td>{metric(row, 'Specificity')}</td>"
            f"<td>{metric(row, 'AUROC')}</td>"
            f"<td>{metric(row, 'AUPRC', 'AP')}</td>"
            f"<td>{support}</td>"
            "</tr>"
        )
    body = "".join(rendered_rows)
    return (
        "<table class='ob-rank-table'><thead><tr><th>ID</th><th>Class</th><th>F1</th>"
        "<th>Precision</th><th>Recall</th><th>Specificity</th><th>AUROC</th><th>AUPRC</th>"
        f"<th>Support</th></tr></thead><tbody>{body}</tbody></table>"
    )


def _render_overview(
    st: Any,
    release: dict[str, Any],
    task: dict[str, Any],
    leaderboard: list[dict[str, Any]],
) -> None:
    columns = st.columns(3, gap="small")
    cards = [
        _metric_card(
            "当前 Release", release.get("release_id", "—"), "冻结的评测版本", accent="#245F9E"
        ),
        _metric_card("已纳入模型", len(leaderboard), "具有脱敏聚合结果", accent="#0F766E"),
        _metric_card(
            "当前任务类别",
            task.get("class_count", _class_count(leaderboard)) or "—",
            str(task.get("display_name") or task.get("task_id") or "当前任务"),
            accent="#B7791F",
        ),
    ]
    for column, card in zip(columns, cards, strict=True):
        column.markdown(card, unsafe_allow_html=True)
    st.markdown(
        '<div class="ob-boundary"><strong>结果解释边界</strong><span>该页面用于冻结特征与轻量探针'
        "的研究比较；数据标签与患者层面泛化限制以各模型详情中的说明为准。</span></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        _section("方法与数据契约", "所有页面严格读取同一份冻结 Release，不扫描实验目录。"),
        unsafe_allow_html=True,
    )
    details = st.columns(3, gap="small")
    details[0].markdown(
        '<div class="ob-summary"><b>评测协议</b><p>冻结视觉编码器特征，'
        "使用统一的轻量探针协议比较迁移能力。</p></div>",
        unsafe_allow_html=True,
    )
    details[1].markdown(
        '<div class="ob-summary"><b>标签语义</b><p>观测目录标签并非完整多标签真值；'
        "结果仅用于探索性比较。</p></div>",
        unsafe_allow_html=True,
    )
    details[2].markdown(
        '<div class="ob-summary"><b>隐私边界</b><p>Dashboard 仅读取脱敏聚合指标，'
        "不读取原始图像或病例标识。</p></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        _section("当前 Release", "已导入模型与核心指标；缺失项保持为空。"), unsafe_allow_html=True
    )
    if leaderboard:
        st.markdown(_release_table(leaderboard), unsafe_allow_html=True)
    else:
        st.info("当前 Release 没有可展示的模型结果。")


def _render_leaderboard(
    st: Any,
    task: dict[str, Any],
    leaderboard: list[dict[str, Any]],
    insights: dict[str, Any],
) -> None:
    st.markdown(
        _section("Leaderboard", "按 Macro-F1 默认降序；筛选只改变展示，不改变冻结的基准结果。"),
        unsafe_allow_html=True,
    )
    available = [
        value for run in leaderboard if (value := _metric_value(run, "Macro-F1")) is not None
    ]
    class_count = int(task.get("class_count") or _class_count(leaderboard) or 0)
    f1_winners = insights.get("stable_class_winners", {}).get("F1", {})
    stable_class_count = int(insights.get("stable_class_count") or 0)
    winner_text = (
        "—"
        if not f1_winners
        else f"{max(f1_winners.values())}/{stable_class_count or class_count}"
    )
    best_score = f"{max(available):.3f}" if available else "—"
    st.markdown(
        '<div class="ob-taskbar">'
        f'<span class="ob-pill"><b>{len(leaderboard)}</b>&nbsp; benchmarked models</span>'
        f'<span class="ob-pill"><b>{class_count or "—"}</b>&nbsp; classes</span>'
        f'<span class="ob-pill">Best Macro-F1&nbsp;<b>{best_score}</b></span>'
        f'<span class="ob-pill">最多稳定类别冠军&nbsp;<b>{winner_text}</b></span>'
        '<span class="ob-pill">support ≥ 5</span>'
        "</div>",
        unsafe_allow_html=True,
    )
    filter_left, filter_right = st.columns((2, 1), gap="small")
    query = filter_left.text_input("搜索模型", placeholder="输入模型 ID 或名称")
    choices = sorted({str(run.get("checkpoint_id", "—")) for run in leaderboard})
    checkpoint = filter_right.selectbox("Checkpoint", ["全部", *choices])
    shown = [
        run
        for run in leaderboard
        if query.lower() in str(run.get("model_id", "")).lower()
        and (checkpoint == "全部" or run.get("checkpoint_id") == checkpoint)
    ]
    shown.sort(key=lambda run: _metric_value(run, "Macro-F1") or float("-inf"), reverse=True)
    diagnostic_only = str(task.get("evidence_status") or "") == "diagnostic_only"
    st.markdown(
        _leaderboard_rows(
            shown,
            leader_badge="本任务最高" if diagnostic_only else "LEADER",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        _section("摘要", "仅展示已导入的证据；缺失指标不会估算或补写。"), unsafe_allow_html=True
    )
    summary_columns = st.columns(3, gap="small")
    winner_lines = (
        "<br>".join(
            f"{escape(_model_label(str(model)))}：{count}"
            for model, count in sorted(
                f1_winners.items(), key=lambda item: (-item[1], str(item[0]))
            )
        )
        or "—"
    )
    summary_columns[0].markdown(
        '<div class="ob-summary"><b>'
        f"{stable_class_count or class_count}个稳定疾病类别中的 F1 冠军数"
        f"</b><p>{winner_lines}<br>support ≥ 5；完全同分时并列模型均计为冠军。</p></div>",
        unsafe_allow_html=True,
    )
    stability_lines = []
    for run in leaderboard:
        stability = run.get("stability") or {}
        mean = stability.get("macro_f1_mean")
        std = stability.get("macro_f1_std")
        if isinstance(mean, (int, float)) and isinstance(std, (int, float)):
            stability_lines.append(
                f"{escape(_model_label(str(run['model_id'])))}：{mean:.3f} ± {std:.3f}"
            )
    stability_text = "<br>".join(stability_lines) or "—<br>当前任务未导入五种子汇总。"
    summary_columns[1].markdown(
        f'<div class="ob-summary"><b>五种子稳定性</b><p>{stability_text}</p></div>',
        unsafe_allow_html=True,
    )
    summary_columns[2].markdown(
        '<div class="ob-summary"><b>评测限制</b><p>观测目录标签并非完整多标签真值；'
        "患者级泛化尚未建立。</p></div>",
        unsafe_allow_html=True,
    )


def _render_insights(
    st: Any,
    insights: dict[str, Any],
    leaderboard: list[dict[str, Any]],
    px: Any,
    go: Any,
) -> None:
    st.markdown(
        _section(
            "Insights",
            "整体指标按列排名；逐类别图根据任务类别数自动切换为小面板或热图。",
        ),
        unsafe_allow_html=True,
    )
    rows = insights.get("metric_comparison", [])
    if not rows:
        st.info("当前 Release 没有可视化的聚合指标。")
        return
    st.markdown(
        '<div class="ob-chart-title">整体指标对照</div>'
        '<div class="ob-chart-copy">'
        "每列独立排名；#1 为该指标最高值，后续单元格同时显示名次及与最高值的差距。"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(_metric_rank_table(rows), unsafe_allow_html=True)

    per_class_metrics = ("F1", "Recall", "Specificity", "AUROC", "AUPRC")
    selected_metric = st.selectbox(
        "逐类矩阵指标",
        per_class_metrics,
        index=0,
        key="insights_class_metric",
    )
    class_ids = sorted(
        {
            int(row.get("class_id"))
            for run in leaderboard
            for row in run.get("per_class", [])
            if isinstance(row.get("class_id"), (int, float))
        }
    )
    if class_ids:
        class_labels = []
        class_matrix = []
        hover_text = []
        for class_id in class_ids:
            representative = next(
                (
                    item
                    for run in leaderboard
                    for item in run.get("per_class", [])
                    if int(item.get("class_id", -1)) == class_id
                ),
                {},
            )
            class_labels.append(str(representative.get("class_name") or class_id))
        for run in leaderboard:
            by_id = {
                int(item["class_id"]): item
                for item in run.get("per_class", [])
                if isinstance(item.get("class_id"), (int, float))
            }
            values = []
            labels = []
            for class_id, class_name in zip(class_ids, class_labels, strict=True):
                item = by_id.get(class_id, {})
                value = item.get(selected_metric)
                values.append(float(value) if isinstance(value, (int, float)) else None)
                support = _text_or_dash(item.get("Support"))
                display = "—" if value is None else f"{float(value):.3f}"
                labels.append(
                    f"{class_name}<br>{selected_metric}: {display}<br>Support: {support}"
                )
            class_matrix.append(values)
            hover_text.append(labels)
        if len(class_ids) <= 5:
            st.markdown(
                '<div class="ob-chart-title">逐类别模型对比</div>'
                '<div class="ob-chart-copy">类别较少时不使用大块热图；每个面板对应一个类别，'
                f"模型按 {escape(selected_metric)} 从高到低排列，金色行表示该类别最高值。</div>",
                unsafe_allow_html=True,
            )
            panels = st.columns(len(class_ids), gap="small")
            for class_index, (column, class_name) in enumerate(
                zip(panels, class_labels, strict=True)
            ):
                ranked = sorted(
                    (
                        (
                            _model_label(str(run["model_id"])),
                            model_values[class_index],
                        )
                        for run, model_values in zip(
                            leaderboard, class_matrix, strict=True
                        )
                        if isinstance(model_values[class_index], (int, float))
                    ),
                    key=lambda item: item[1],
                    reverse=True,
                )
                best = ranked[0][1] if ranked else None
                representative = next(
                    (
                        item
                        for item in leaderboard[0].get("per_class", [])
                        if int(item.get("class_id", -1)) == class_ids[class_index]
                    ),
                    {},
                )
                support = _text_or_dash(representative.get("Support"))
                rendered = []
                displayed_rank = 0
                previous_value: float | None = None
                for position, (model_name, value) in enumerate(ranked, start=1):
                    if previous_value is None or abs(value - previous_value) > 1e-12:
                        displayed_rank = position
                    previous_value = value
                    winner = best is not None and abs(value - best) <= 1e-12
                    rendered.append(
                        f'<div class="ob-class-row{" winner" if winner else ""}">'
                        f'<span class="rank">{displayed_rank:02d}</span>'
                        f"<b>{escape(model_name)}</b>"
                        '<span class="ob-class-bar">'
                        f'<i style="width:{value * 100:.1f}%"></i></span>'
                        f"<strong>{value:.3f}</strong></div>"
                    )
                column.markdown(
                    f'<div class="ob-class-panel"><h4>{escape(class_name)}</h4>'
                    f"<small>{escape(selected_metric)} · Test support {escape(support)}</small>"
                    + "".join(rendered)
                    + "</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="ob-chart-title">模型 × 疾病类别表现热图</div>'
                '<div class="ob-chart-copy">每行是一个模型、每列是一种疾病；颜色越深表示当前'
                f"选择的 {escape(selected_metric)} 越高。support &lt; 5 的类别仍展示，"
                "但不计入稳定类别冠军。</div>",
                unsafe_allow_html=True,
            )
            chart = go.Figure(
                data=go.Heatmap(
                    z=class_matrix,
                    x=class_labels,
                    y=[_model_label(str(run["model_id"])) for run in leaderboard],
                    zmin=0,
                    zmax=1,
                    colorscale=[
                        [0.0, "#F8FAFC"],
                        [0.35, "#DBEAFE"],
                        [0.7, "#7DB4F2"],
                        [1.0, "#174EA6"],
                    ],
                    text=hover_text,
                    hovertemplate="%{text}<extra></extra>",
                    colorbar={"title": selected_metric, "thickness": 12},
                    xgap=1,
                    ygap=2,
                )
            )
            chart.update_layout(
                height=max(330, 110 + 48 * len(leaderboard)),
                margin={"l": 120, "r": 35, "t": 18, "b": 100},
                xaxis={"tickangle": -55, "automargin": True},
            )
            st.plotly_chart(chart, width="stretch", config={"displayModeBar": True})

    cost = [row for row in rows if row.get("throughput") is not None]
    if cost and all(row.get("Macro-F1") is not None for row in cost):
        chart = px.scatter(cost, x="throughput", y="Macro-F1", hover_name="model_id")
        chart.update_layout(height=320, margin={"l": 42, "r": 24, "t": 24, "b": 42})
        st.plotly_chart(chart, width="stretch", config={"displayModeBar": False})
    winners = insights.get("stable_class_winners", {}).get("F1", {})
    stable_class_count = int(insights.get("stable_class_count") or 0)
    if winners and stable_class_count > 5:
        st.markdown(
            f'<div class="ob-chart-title">{stable_class_count}个稳定疾病类别中的 '
            "F1 冠军数</div>"
            '<div class="ob-chart-copy">每个疾病类别比较所有模型的 F1；最高者计1次。'
            "仅统计 support ≥ 5 的类别，完全同分时并列模型均计为冠军。</div>",
            unsafe_allow_html=True,
        )
        ordered_winners = sorted(winners.items(), key=lambda item: item[1], reverse=True)
        winner_names = [_model_label(str(item[0])) for item in ordered_winners]
        winner_values = [item[1] for item in ordered_winners]
        chart = go.Figure(
            go.Scatter(
                x=winner_values,
                y=winner_names,
                mode="markers+text",
                text=winner_values,
                textposition="middle right",
                marker={"size": 13, "color": "#2855D9"},
                hovertemplate="%{y}: %{x} 个稳定疾病类别冠军<extra></extra>",
            )
        )
        for name, value in zip(winner_names, winner_values, strict=True):
            chart.add_shape(
                type="line",
                x0=0,
                x1=value,
                y0=name,
                y1=name,
                line={"color": "#C7D7F5", "width": 2},
                layer="below",
            )
        chart.update_layout(
            height=max(260, 90 + 52 * len(winner_names)),
            margin={"l": 120, "r": 50, "t": 20, "b": 42},
            showlegend=False,
        )
        chart.update_xaxes(
            range=[0, max(winner_values) * 1.18],
            title="稳定疾病类别 F1 冠军数",
        )
        st.plotly_chart(chart, width="stretch", config={"displayModeBar": False})
    ranking = insights.get("cost_ranking", [])
    if ranking:
        st.markdown(
            _section("成本排名", "仅纳入有成本或吞吐量记录的模型。"), unsafe_allow_html=True
        )
        rows = [{"Model": run["model_id"], **run.get("cost", {})} for run in ranking]
        st.dataframe(rows, hide_index=True, width="stretch")
    stability_rows = []
    for run in leaderboard:
        stability = run.get("stability") or {}
        mean = stability.get("macro_f1_mean")
        std = stability.get("macro_f1_std")
        if isinstance(mean, (int, float)) and isinstance(std, (int, float)):
            stability_rows.append(
                {
                    "Model": _model_label(str(run["model_id"])),
                    "Mean Macro-F1": mean,
                    "Std": std,
                }
            )
    if stability_rows:
        st.markdown(
            '<div class="ob-chart-title">五种子稳定性</div>'
            '<div class="ob-chart-copy">误差线为五个预注册随机种子的样本标准差。</div>',
            unsafe_allow_html=True,
        )
        chart = go.Figure(
            go.Scatter(
                x=[row["Mean Macro-F1"] for row in stability_rows],
                y=[row["Model"] for row in stability_rows],
                mode="markers+text",
                text=[f'{row["Mean Macro-F1"]:.3f}' for row in stability_rows],
                textposition="middle right",
                marker={"size": 12, "color": "#2855D9"},
                error_x={
                    "type": "data",
                    "array": [row["Std"] for row in stability_rows],
                    "visible": True,
                    "color": "#7DA2E8",
                    "thickness": 2,
                },
                hovertemplate="%{y}<br>Macro-F1: %{x:.3f}<extra></extra>",
            )
        )
        chart.update_layout(
            height=max(260, 95 + 48 * len(stability_rows)),
            margin={"l": 120, "r": 50, "t": 20, "b": 42},
            showlegend=False,
        )
        st.plotly_chart(chart, width="stretch", config={"displayModeBar": False})

    radar_rows = insights.get("radar") or []
    radar_axes = [
        axis
        for axis in (
            "Macro-F1",
            "Balanced Accuracy",
            "Accuracy",
            "Macro-AUROC",
            "Stability",
            "Efficiency",
        )
        if sum(isinstance(row.get(axis), (int, float)) for row in radar_rows) >= 2
    ]
    if len(radar_axes) >= 3 and radar_rows:
        st.markdown(
            '<div class="ob-chart-title">归一化能力雷达</div>'
            '<div class="ob-chart-copy">最多对比三个模型；仅使用已导入指标，'
            "精确数值仍以排行榜与明细表为准。</div>",
            unsafe_allow_html=True,
        )
        radar_choices = {
            _model_label(str(row["model_id"])): row for row in radar_rows
        }
        selected_radar = st.multiselect(
            "雷达图模型（最多3个）",
            list(radar_choices),
            default=list(radar_choices)[:3],
            max_selections=3,
            key="insights_radar_models",
        )
        radar = go.Figure()
        for label in selected_radar:
            row = radar_choices[label]
            values = [row.get(axis) for axis in radar_axes]
            if all(isinstance(value, (int, float)) for value in values):
                radar.add_trace(
                    go.Scatterpolar(
                        r=[*values, values[0]],
                        theta=[*radar_axes, radar_axes[0]],
                        fill="toself",
                        name=label,
                    )
                )
        radar.update_layout(
            height=430,
            margin={"l": 50, "r": 50, "t": 30, "b": 30},
            polar={"radialaxis": {"visible": True, "range": [0, 1]}},
            legend={"orientation": "h", "y": -0.08},
        )
        st.plotly_chart(radar, width="stretch", config={"displayModeBar": False})

    notes = st.columns(2, gap="small")
    notes[0].markdown(
        '<div class="ob-summary"><b>五种子稳定性</b><p>'
        + (
            f"已导入 {len(stability_rows)} 个模型的五种子结果。"
            if stability_rows
            else "—<br>当前任务未导入五种子汇总。"
        )
        + "</p></div>",
        unsafe_allow_html=True,
    )
    notes[1].markdown(
        '<div class="ob-summary"><b>质量—成本</b><p>'
        + (
            f"已纳入 {len(cost)} 个具有吞吐量记录的模型。"
            if cost
            else "—<br>当前任务没有可用成本指标。"
        )
        + "</p></div>",
        unsafe_allow_html=True,
    )


def _render_details(st: Any, leaderboard: list[dict[str, Any]], px: Any) -> None:
    st.markdown(
        _section("Model Details", "查看单个模型的完整指标、逐类表现、混淆矩阵和稳定性信息。"),
        unsafe_allow_html=True,
    )
    if not leaderboard:
        st.info("当前 Release 没有可查看的模型详情。")
        return
    choices = {str(run["model_id"]): run for run in leaderboard}
    run = choices[st.selectbox("选择模型", list(choices), key="details_model")]
    model_name = escape(_model_label(str(run.get("model_id", "—"))))
    st.markdown(
        f'<div class="ob-model-hero"><small>Selected model</small><h2>{model_name}</h2>'
        f"<p>Macro-F1 {_metric_display(run, 'Macro-F1')} · Balanced Accuracy "
        f"{_metric_display(run, 'Balanced Accuracy')} · Accuracy "
        f"{_metric_display(run, 'Accuracy')}</p></div>",
        unsafe_allow_html=True,
    )
    cost = run.get("cost") or {}
    evidence_rows = (
        ("Checkpoint", _text_or_dash(run.get("checkpoint_id"))),
        ("Adapter version", _text_or_dash(run.get("adapter_version"))),
        ("Feature dimension", _text_or_dash(cost.get("feature_dim"))),
        ("Qualification", _text_or_dash(run.get("qualification_status"))),
        ("Per-class records", str(len(run.get("per_class", [])))),
    )
    st.markdown(
        '<table class="ob-evidence-table"><thead><tr><th>Evidence item</th>'
        "<th>Imported value</th><th>Status</th></tr></thead><tbody>"
        + "".join(
            "<tr>"
            f"<td>{escape(label)}</td><td>{escape(value)}</td>"
            f'<td class="{"ob-status-ok" if value != "—" else "ob-status-muted"}">'
            f'{"Available" if value != "—" else "Not provided"}</td></tr>'
            for label, value in evidence_rows
        )
        + "</tbody></table>",
        unsafe_allow_html=True,
    )
    limitations = run.get("limitations") or ["当前 Release 未提供额外限制说明。"]
    st.markdown(
        '<div class="ob-note"><b>实验限制</b><br>'
        + "<br>".join(f"• {escape(str(item))}" for item in limitations)
        + "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        _section("逐类表现", "Support < 5 的类别指标具有较高不稳定性；AUPRC 仅在已导入时展示。"),
        unsafe_allow_html=True,
    )
    st.markdown(_per_class_table(run.get("per_class", [])), unsafe_allow_html=True)
    if run.get("confusion_matrix"):
        chart = px.imshow(run["confusion_matrix"], title="混淆矩阵")
        chart.update_layout(height=520)
        st.plotly_chart(chart, width="stretch", config={"displayModeBar": False})
    if run.get("stability"):
        st.markdown(
            f'<div class="ob-note"><b>五种子稳定性</b><br>{escape(str(run["stability"]))}</div>',
            unsafe_allow_html=True,
        )


def run_dashboard(results: Path) -> None:
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError("Dashboard requires ophbench[dashboard]: streamlit and plotly") from exc
    required = (
        "releases.json",
        "tasks.json",
        "leaderboard.json",
        "insights.json",
        "model_details.json",
    )
    missing = [name for name in required if not (results / name).is_file()]
    if missing:
        raise RuntimeError(f"Generated result files are missing: {', '.join(missing)}")
    data = {name: json.loads((results / name).read_text(encoding="utf-8")) for name in required}
    st.set_page_config(
        page_title="OphBench",
        page_icon="OB",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    _inject_css(st)
    _configure_figures(px, go)
    releases = data["releases.json"]
    release_ids = [str(item.get("release_id", "unknown")) for item in releases]
    if not release_ids:
        st.error("未找到可用的 Release。")
        return
    selected_release = _render_topnav(st, release_ids)
    release = _release_for_id(releases, selected_release)
    release_task_ids = {str(task_id) for task_id in release.get("task_ids", []) if task_id}
    tasks = [
        task
        for task in data["tasks.json"]
        if not release_task_ids or str(task.get("task_id")) in release_task_ids
    ]
    default_task_id = str(
        release.get("default_task_id")
        or data["insights.json"].get("default_task_id")
        or (tasks[0].get("task_id") if tasks else "")
    )
    active_task_id = str(st.session_state.get("benchmark_task", default_task_id))
    task = _task_for_id(tasks, active_task_id)
    _render_header(st, task)
    selected_task_id = _render_task_switcher(st, tasks, default_task_id)
    task = _task_for_id(tasks, selected_task_id)
    task_limitations = task.get("limitations") or []
    if task_limitations:
        st.markdown(
            '<div class="ob-boundary"><strong>任务证据边界</strong><span>'
            + "；".join(escape(str(item)) for item in task_limitations)
            + "</span></div>",
            unsafe_allow_html=True,
        )
    leaderboard = _dashboard_rows(data, selected_release, selected_task_id)
    insights = _task_insights(data["insights.json"], selected_task_id)
    view = st.radio(
        "页面导航",
        ["Leaderboard", "Models", "Insights", "Methodology"],
        horizontal=True,
        label_visibility="collapsed",
    )
    if view == "Leaderboard":
        _render_leaderboard(st, task, leaderboard, insights)
    elif view == "Insights":
        _render_insights(st, insights, leaderboard, px, go)
    elif view == "Models":
        _render_details(st, leaderboard, px)
    else:
        _render_overview(st, release, task, leaderboard)
    release_date = escape(_text_or_dash(release.get("release_date")))
    st.markdown(
        '<div class="ob-footer">协议版本：当前 Release 元数据 · 数据语义：观测目录标签 · '
        f"更新时间：{release_date} · "
        "GitHub：LIU-Rong-Tao/ophthalmic-foundation-model-benchmark</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    results = os.environ.get("OPHBENCH_DASHBOARD_RESULTS")
    run_dashboard(Path(results) if results else Path("benchmark/generated"))
