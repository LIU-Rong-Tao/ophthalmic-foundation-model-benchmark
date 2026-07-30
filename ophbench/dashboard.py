"""Streamlit dashboard for pre-built, sanitized OphBench benchmark results.

The visual tokens and page shell intentionally align with the generic Streamlit
design language in OphAgent's live Model Hub.  This module remains standalone:
it reads only OphBench's generated JSON and imports no OphAgent code or data.
"""

from __future__ import annotations

import json
import os
from html import escape
from pathlib import Path
from typing import Any

TOKENS = {
    "ink": "#132238",
    "muted": "#66758A",
    "line": "#DDE5ED",
    "canvas": "#F6F8FB",
    "surface": "#FFFFFF",
    "nav": "#132238",
    "nav_hover": "#1E3652",
    "teal": "#087F75",
    "teal_soft": "#EAF7F5",
    "amber": "#B86B08",
    "amber_soft": "#FFF7E8",
}


def _inject_css(st: Any) -> None:
    """Apply the reusable OphAgent-style research dashboard shell."""

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
        .main .block-container {{ max-width: 1380px; padding: 1rem 2rem 3rem; }}
        header[data-testid="stHeader"] {{ background:transparent; height:0; }}
        #MainMenu, footer, [data-testid="stToolbar"] {{ visibility:hidden; }}
        .ob-brand-mark {{
          width:2.25rem; height:2.25rem; display:inline-grid; place-items:center;
          background:linear-gradient(135deg,#163E68,#087F75); border-radius:10px;
          color:#FFFFFF; font-size:.78rem; font-weight:850; letter-spacing:-.02em;
          box-shadow:0 7px 18px rgba(8,127,117,.18);
        }}
        .ob-page-head {{
          display:flex; align-items:flex-end; justify-content:space-between; gap:1.2rem;
          padding:1.4rem 0 1rem; margin-bottom:.15rem;
        }}
        .ob-eyebrow {{ color:var(--ob-teal); font-size:.7rem; font-weight:800;
          letter-spacing:.12em; text-transform:uppercase; margin-bottom:.55rem; }}
        .ob-page-title {{ color:var(--ob-ink); font-size:1.85rem; font-weight:800;
          line-height:1.12; margin:0; letter-spacing:-.035em; }}
        .ob-page-copy {{ color:var(--ob-muted); font-size:.86rem; line-height:1.55;
          margin-top:.65rem; max-width:760px; }}
        .ob-page-context {{ white-space:nowrap; color:#426174; font-size:.72rem; font-weight:700;
          background:var(--ob-teal-soft); border:1px solid #C7E7E2; border-radius:999px;
          padding:.42rem .7rem; }}
        .ob-boundary {{
          display:flex; gap:.6rem; align-items:flex-start; background:var(--ob-amber-soft);
          border:1px solid #EAD7AA; border-left:4px solid var(--ob-amber); padding:.65rem .8rem;
          color:#624D1D; line-height:1.5; font-size:.78rem; margin:0 0 1rem; }}
        .ob-metric {{ background:linear-gradient(180deg,#FFFFFF 0%,#FBFCFE 100%);
          border:1px solid var(--ob-line); border-radius:12px;
          padding:1rem 1.05rem; min-height:112px; position:relative; overflow:hidden;
          box-shadow:0 5px 18px rgba(31,50,73,.045); }}
        .ob-metric:before {{ content:""; position:absolute; left:0; top:0; bottom:0;
          width:3px; background:var(--accent,var(--ob-teal)); }}
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
          border-radius:12px; padding:1.15rem; box-shadow:0 6px 20px rgba(31,50,73,.04); }}
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
        .ob-rank-table .muted {{ color:#8a97a8; }}
        .ob-taskbar {{ display:flex; align-items:center; gap:.45rem; flex-wrap:wrap;
          margin:.35rem 0 .9rem; color:var(--ob-muted); font-size:.7rem; }}
        .ob-pill {{ display:inline-flex; align-items:center; border:1px solid var(--ob-line);
          border-radius:999px; padding:.3rem .58rem; background:#fff; color:#506176;
          font-weight:650; }}
        .ob-rank-list {{ display:grid; gap:.55rem; }}
        .ob-rank-row {{ background:#fff; border:1px solid var(--ob-line); border-radius:12px;
          box-shadow:0 5px 18px rgba(31,50,73,.035); overflow:hidden;
          transition:border-color .18s ease, box-shadow .18s ease, transform .18s ease; }}
        .ob-rank-row:hover {{ border-color:#B9DAD5; box-shadow:0 9px 24px rgba(31,50,73,.07);
          transform:translateY(-1px); }}
        .ob-rank-row summary {{ cursor:pointer; list-style:none; display:grid;
          grid-template-columns:54px minmax(190px,1.35fr) repeat(5,minmax(92px,.72fr)) 24px;
          align-items:center; gap:.65rem; padding:.82rem .9rem; }}
        .ob-rank-row summary::-webkit-details-marker {{ display:none; }}
        .ob-rank-number {{ width:32px; height:32px; border-radius:9px; display:grid;
          place-items:center; background:var(--ob-teal-soft); color:var(--ob-teal);
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
        .ob-model-hero {{ background:linear-gradient(135deg,#102B49 0%,#0A6E69 100%);
          border-radius:14px; padding:1.35rem 1.5rem; color:#FFFFFF; margin:.5rem 0 1rem;
          box-shadow:0 10px 28px rgba(20,49,77,.15); }}
        .ob-model-hero small {{ color:#BFE2DF; text-transform:uppercase; letter-spacing:.09em;
          font-weight:750; font-size:.66rem; }}
        .ob-model-hero h2 {{ margin:.35rem 0 .25rem; font-size:1.55rem; }}
        .ob-model-hero p {{ margin:0; color:#D9E7EF; font-size:.78rem; }}
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
        div[data-testid="stPlotlyChart"] {{ background:#fff; border:1px solid var(--ob-line);
          border-radius:12px; overflow:hidden; box-shadow:0 6px 20px rgba(31,50,73,.04); }}
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
    metadata.markdown(
        '<div class="ob-taskbar">'
        f'<span class="ob-pill">{escape(_task_type_label(task.get("task_type")))}</span>'
        f'<span class="ob-pill">{escape(_text_or_dash(task.get("class_count")))} classes</span>'
        f'<span class="ob-pill">{escape(_text_or_dash(task.get("sample_count")))} samples</span>'
        '<span class="ob-pill">Frozen features</span>'
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
    }.get(model_id, model_id)


def _text_or_dash(value: Any) -> str:
    text = str(value or "").strip()
    return "—" if not text or text.lower() in {"unknown", "none", "null", "nan"} else text


def _task_type_label(value: Any) -> str:
    return {
        "single_label_multiclass_classification": "单标签多分类",
        "observed_directory_multilabel_probe": "观测多标签探针",
    }.get(str(value), _text_or_dash(value))


def _leaderboard_rows(runs: list[dict[str, Any]]) -> str:
    metrics = (
        ("Macro-F1", "Macro-F1"),
        ("Balanced Accuracy", "BAcc"),
        ("Accuracy", "Accuracy"),
        ("Top-3 Accuracy", "Top-3"),
        ("Macro-AUROC", "AUROC"),
    )
    rows = []
    for rank, run in enumerate(runs, start=1):
        model_id = str(run.get("model_id") or "unknown")
        model_name = escape(_model_label(model_id))
        checkpoint = escape(_text_or_dash(run.get("checkpoint_id")))
        winner = '<span class="ob-winner">LEADER</span>' if rank == 1 else ""
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
    return '<div class="ob-rank-list">' + "".join(rows) + "</div>"


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
    columns = st.columns(4, gap="small")
    class_count = int(task.get("class_count") or _class_count(leaderboard) or 0)
    f1_winners = insights.get("stable_class_winners", {}).get("F1", {})
    winner_text = "—" if not f1_winners else str(max(f1_winners.values()))
    cards = [
        _metric_card("Models", len(leaderboard), "当前 Release", accent="#245F9E"),
        _metric_card("Classes", class_count or "—", "逐类指标可用类别", accent="#0F766E"),
        _metric_card(
            "最高 Macro-F1",
            f"{max(available):.3f}" if available else "—",
            "当前 Release 的最高模型表现",
            accent="#0F766E",
        ),
        _metric_card(
            "最多逐类 F1 赢家",
            winner_text,
            "仅统计 support ≥ 5 的类别",
            accent="#B7791F",
        ),
    ]
    for column, card in zip(columns, cards, strict=True):
        column.markdown(card, unsafe_allow_html=True)
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
    st.markdown(_leaderboard_rows(shown), unsafe_allow_html=True)
    st.markdown(
        _section("摘要", "仅展示已导入的证据；缺失指标不会估算或补写。"), unsafe_allow_html=True
    )
    summary_columns = st.columns(3, gap="small")
    winner_lines = (
        "<br>".join(
            f"{escape(_model_label(str(model)))}：{count}"
            for model, count in sorted(f1_winners.items())
        )
        or "—"
    )
    summary_columns[0].markdown(
        f'<div class="ob-summary"><b>逐类赢家</b><p>{winner_lines}<br>F1，support ≥ 5。</p></div>',
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
        _section("Insights", "聚焦整体迁移表现与逐类优势；所有图表均来自预生成聚合指标。"),
        unsafe_allow_html=True,
    )
    rows = insights.get("metric_comparison", [])
    if not rows:
        st.info("当前 Release 没有可视化的聚合指标。")
        return
    metric_names = (
        "Macro-F1",
        "Balanced Accuracy",
        "Accuracy",
        "Top-3 Accuracy",
        "Macro-AUROC",
    )
    metric_rows = [
        {
            "Model": _model_label(str(row["model_id"])),
            "Metric": metric_name,
            "Score": float(row[metric_name]),
        }
        for row in rows
        for metric_name in metric_names
        if isinstance(row.get(metric_name), (int, float))
    ]
    if metric_rows:
        st.markdown(
            '<div class="ob-chart-title">核心指标比较</div>'
            '<div class="ob-chart-copy">仅展示已导入的真实指标；缺失项不会估算或补值。</div>',
            unsafe_allow_html=True,
        )
        chart = px.bar(
            metric_rows,
            x="Model",
            y="Score",
            color="Metric",
            barmode="group",
            category_orders={"Metric": list(metric_names)},
        )
        chart.update_layout(
            height=360,
            margin={"l": 42, "r": 24, "t": 24, "b": 42},
            legend={"orientation": "h", "y": 1.08, "x": 0},
            bargap=0.28,
        )
        chart.update_yaxes(range=[0, 1], tickformat=".1f")
        st.plotly_chart(chart, width="stretch", config={"displayModeBar": False})
    cost = [row for row in rows if row.get("throughput") is not None]
    if cost and all(row.get("Macro-F1") is not None for row in cost):
        chart = px.scatter(cost, x="throughput", y="Macro-F1", hover_name="model_id")
        chart.update_layout(height=320, margin={"l": 42, "r": 24, "t": 24, "b": 42})
        st.plotly_chart(chart, width="stretch", config={"displayModeBar": False})
    winners = insights.get("stable_class_winners", {}).get("F1", {})
    if winners:
        st.markdown(
            '<div class="ob-chart-title">逐类 F1 赢家</div>'
            '<div class="ob-chart-copy">仅统计 support ≥ 5 且具有F1证据的类别。</div>',
            unsafe_allow_html=True,
        )
        ordered_winners = sorted(winners.items(), key=lambda item: item[1], reverse=True)
        chart = px.bar(
            x=[_model_label(str(item[0])) for item in ordered_winners],
            y=[item[1] for item in ordered_winners],
            text=[item[1] for item in ordered_winners],
            labels={"x": "Model", "y": "Class wins"},
        )
        chart.update_traces(marker_color="#087F75", textposition="outside")
        chart.update_layout(
            height=300, margin={"l": 42, "r": 24, "t": 20, "b": 42}, showlegend=False
        )
        chart.update_yaxes(range=[0, max(winners.values()) * 1.18])
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
        chart = px.bar(
            stability_rows,
            x="Model",
            y="Mean Macro-F1",
            error_y="Std",
            text="Mean Macro-F1",
        )
        chart.update_traces(
            marker_color="#245F9E",
            texttemplate="%{text:.3f}",
            textposition="outside",
        )
        chart.update_layout(
            height=320,
            margin={"l": 42, "r": 24, "t": 20, "b": 42},
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
            '<div class="ob-chart-copy">仅使用已导入指标；精确数值仍以排行榜与明细表为准。</div>',
            unsafe_allow_html=True,
        )
        radar = go.Figure()
        for row in radar_rows:
            values = [row.get(axis) for axis in radar_axes]
            if all(isinstance(value, (int, float)) for value in values):
                radar.add_trace(
                    go.Scatterpolar(
                        r=[*values, values[0]],
                        theta=[*radar_axes, radar_axes[0]],
                        fill="toself",
                        name=_model_label(str(row["model_id"])),
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
    meta = (
        '<div class="ob-info-grid">'
        '<div class="ob-info"><span>Checkpoint</span><b>'
        f'{escape(_text_or_dash(run.get("checkpoint_id")))}</b></div>'
        '<div class="ob-info"><span>Adapter</span><b>'
        f'{escape(_text_or_dash(run.get("adapter_version")))}</b></div>'
        f'<div class="ob-info"><span>逐类记录</span><b>{len(run.get("per_class", []))}</b></div>'
        "</div>"
    )
    st.markdown(meta, unsafe_allow_html=True)
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
