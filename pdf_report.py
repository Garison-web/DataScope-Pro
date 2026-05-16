import io
from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)

# ── Palette ───────────────────────────────────────────────────────────────────
ACCENT  = HexColor("#06b6d4")
ACCENT2 = HexColor("#3b82f6")
TEXT    = HexColor("#1e293b")
MUTED   = HexColor("#64748b")
BORDER  = HexColor("#cbd5e1")
BG_ROW1 = HexColor("#f8fafc")
BG_ROW2 = HexColor("#e2e8f0")

PALETTE = ["#06b6d4","#3b82f6","#8b5cf6","#ec4899","#f59e0b","#10b981",
           "#ef4444","#14b8a6","#f97316","#a855f7"]

# ── Styles ────────────────────────────────────────────────────────────────────
def _styles():
    base = getSampleStyleSheet()
    return {
        "title":     ParagraphStyle("title", parent=base["Title"],
                        fontName="Helvetica-Bold", fontSize=26,
                        textColor=TEXT, leading=30, alignment=TA_LEFT),
        "subtitle":  ParagraphStyle("subtitle", parent=base["Normal"],
                        fontName="Helvetica", fontSize=11,
                        textColor=MUTED, leading=14),
        "h2":        ParagraphStyle("h2", parent=base["Heading2"],
                        fontName="Helvetica-Bold", fontSize=14,
                        textColor=TEXT, leading=18, spaceBefore=10, spaceAfter=6),
        "body":      ParagraphStyle("body", parent=base["Normal"],
                        fontName="Helvetica", fontSize=10,
                        textColor=TEXT, leading=15),
        "muted":     ParagraphStyle("muted", parent=base["Normal"],
                        fontName="Helvetica", fontSize=9,
                        textColor=MUTED, leading=12),
        "kpi_label": ParagraphStyle("kl", parent=base["Normal"],
                        fontName="Helvetica", fontSize=9,
                        textColor=MUTED, alignment=TA_CENTER),
        "kpi_value": ParagraphStyle("kv", parent=base["Normal"],
                        fontName="Helvetica-Bold", fontSize=18,
                        textColor=TEXT, alignment=TA_CENTER, leading=22),
    }


# ── Matplotlib helpers ────────────────────────────────────────────────────────
def _fig_to_flowable(fig, width_cm=16, height_cm=7):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=width_cm * cm, height=height_cm * cm)


def _bar_chart(labels, values, title, xlabel="", ylabel="Revenue ($)",
               horizontal=False, width_cm=16, height_cm=7):
    fig, ax = plt.subplots(figsize=(width_cm * 0.393701, height_cm * 0.393701))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]
    if horizontal:
        bars = ax.barh(labels, values, color=colors, edgecolor="none", height=0.6)
        ax.set_xlabel(ylabel, fontsize=9, color="#475569")
        for bar, val in zip(bars, values):
            ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
                    f"${val:,.0f}", va="center", fontsize=8, color="#334155")
    else:
        bars = ax.bar(labels, values, color=colors, edgecolor="none", width=0.6)
        ax.set_ylabel(ylabel, fontsize=9, color="#475569")
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.01,
                    f"${val:,.0f}", ha="center", fontsize=7.5, color="#334155")
        plt.xticks(rotation=20, ha="right", fontsize=8)
    ax.set_title(title, fontsize=12, fontweight="bold", color="#0f172a", pad=10)
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color("#cbd5e1")
    ax.tick_params(colors="#64748b", labelsize=8)
    ax.set_facecolor("#f8fafc")
    fig.patch.set_facecolor("white")
    plt.tight_layout()
    return _fig_to_flowable(fig, width_cm, height_cm)


def _donut_chart(labels, values, title, width_cm=13, height_cm=7):
    fig, ax = plt.subplots(figsize=(width_cm * 0.393701, height_cm * 0.393701))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]
    wedges, texts, autotexts = ax.pie(
        values, labels=None, colors=colors,
        autopct="%1.1f%%", startangle=140,
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
        pctdistance=0.75
    )
    for t in autotexts:
        t.set_fontsize(8)
        t.set_color("white")
        t.set_fontweight("bold")
    ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0.5),
              fontsize=8, frameon=False)
    ax.set_title(title, fontsize=12, fontweight="bold", color="#0f172a", pad=10)
    fig.patch.set_facecolor("white")
    plt.tight_layout()
    return _fig_to_flowable(fig, width_cm, height_cm)


def _line_chart(x, y, title, width_cm=16, height_cm=7):
    fig, ax = plt.subplots(figsize=(width_cm * 0.393701, height_cm * 0.393701))
    ax.fill_between(x, y, alpha=0.12, color="#06b6d4")
    ax.plot(x, y, color="#06b6d4", linewidth=2.2, solid_capstyle="round")
    ax.set_title(title, fontsize=12, fontweight="bold", color="#0f172a", pad=10)
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color("#cbd5e1")
    ax.tick_params(colors="#64748b", labelsize=8)
    ax.set_facecolor("#f8fafc")
    fig.patch.set_facecolor("white")
    step = max(1, len(x) // 8)
    ax.set_xticks(range(0, len(x), step))
    ax.set_xticklabels([str(x[i])[:10] for i in range(0, len(x), step)],
                       rotation=20, ha="right", fontsize=7.5)
    plt.tight_layout()
    return _fig_to_flowable(fig, width_cm, height_cm)


# ── KPI table ─────────────────────────────────────────────────────────────────
def _kpi_table(df, styles):
    cells = []
    if "Revenue" in df.columns:
        cells.append(("TOTAL REVENUE", f"${df['Revenue'].sum():,.2f}"))
    cells.append(("TOTAL RECORDS", f"{len(df):,}"))
    if "Quantity" in df.columns:
        cells.append(("ITEMS SOLD", f"{df['Quantity'].sum():,.0f}"))
    if "Revenue" in df.columns:
        denom = df["Order_ID"].nunique() if "Order_ID" in df.columns else len(df)
        avg   = df["Revenue"].sum() / denom if denom > 0 else 0
        cells.append(("AVG ORDER VALUE", f"${avg:,.2f}"))
    cells = cells[:4]
    while len(cells) < 4:
        cells.append((" ", " "))

    row_labels = [Paragraph(c[0], styles["kpi_label"]) for c in cells]
    row_values = [Paragraph(c[1], styles["kpi_value"]) for c in cells]
    tbl = Table([row_labels, row_values],
                colWidths=[4.1 * cm] * 4, rowHeights=[0.75 * cm, 1.2 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), HexColor("#f1f5f9")),
        ("LINEABOVE",    (0, 0), (-1, 0),  2, ACCENT),
        ("BOX",          (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID",    (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    return tbl


# ── Main builder ──────────────────────────────────────────────────────────────
def build_pdf(filtered_df: pd.DataFrame, filter_col, datetime_cols,
              ai_insights: str = "") -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.6*cm, rightMargin=1.6*cm,
        topMargin=1.6*cm, bottomMargin=1.6*cm,
        title="DataScope Pro Report",
    )
    styles = _styles()
    story  = []

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph("DataScope Pro", styles["title"]))
    story.append(Paragraph(
        f"Analytics Report &nbsp;·&nbsp; "
        f"Generated {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        styles["subtitle"]))
    story.append(Spacer(1, 0.25*cm))
    story.append(Paragraph(
        f"<b>{len(filtered_df):,}</b> rows &nbsp;·&nbsp; "
        f"<b>{len(filtered_df.columns)}</b> columns &nbsp;·&nbsp; "
        f"Grouped by: <b>{filter_col or 'n/a'}</b>",
        styles["muted"]))
    story.append(Spacer(1, 0.5*cm))

    # ── KPIs ────────────────────────────────────────────────────────────────
    story.append(Paragraph("Key Performance Indicators", styles["h2"]))
    story.append(_kpi_table(filtered_df, styles))
    story.append(Spacer(1, 0.6*cm))

    # ── Revenue by Category (bar) ────────────────────────────────────────────
    if filter_col and "Revenue" in filtered_df.columns:
        grp = (filtered_df.groupby(filter_col)["Revenue"]
               .sum().sort_values(ascending=False))
        story.append(Paragraph(f"Revenue by {filter_col}", styles["h2"]))
        story.append(_bar_chart(list(grp.index), list(grp.values),
                                f"Revenue by {filter_col}"))
        story.append(Spacer(1, 0.4*cm))

        story.append(Paragraph(f"Revenue Share by {filter_col}", styles["h2"]))
        story.append(_donut_chart(list(grp.index), list(grp.values),
                                  f"Revenue Share — {filter_col}"))

    # ── Revenue Over Time ────────────────────────────────────────────────────
    if datetime_cols and "Revenue" in filtered_df.columns:
        story.append(PageBreak())
        dc = datetime_cols[0]
        td = (filtered_df.groupby(dc)["Revenue"].sum()
              .reset_index().sort_values(dc))
        x_vals = [str(v)[:10] for v in td[dc].tolist()]
        y_vals = td["Revenue"].tolist()
        story.append(Paragraph("Revenue Trend Over Time", styles["h2"]))
        story.append(_line_chart(x_vals, y_vals, "Revenue Over Time"))
        story.append(Spacer(1, 0.4*cm))

    # ── Numeric Summary table ────────────────────────────────────────────────
    num_df = filtered_df.select_dtypes(include=["float64","int64"])
    if len(num_df.columns):
        story.append(PageBreak())
        story.append(Paragraph("Numeric Summary", styles["h2"]))
        desc = num_df.describe().round(2).reset_index().rename(columns={"index":"stat"})
        data = [list(desc.columns)] + desc.astype(str).values.tolist()
        n_cols = len(desc.columns)
        col_w  = [2.0*cm] + [(16.8 - 2.0) / max(n_cols - 1, 1) * cm] * (n_cols - 1)
        tbl = Table(data, colWidths=col_w, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0),  ACCENT2),
            ("TEXTCOLOR",     (0,0), (-1,0),  HexColor("#ffffff")),
            ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 8.5),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [BG_ROW1, BG_ROW2]),
            ("GRID",          (0,0), (-1,-1), 0.3, BORDER),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ("ALIGN",         (1,1), (-1,-1), "RIGHT"),
            ("LEFTPADDING",   (0,0), (-1,-1), 5),
            ("RIGHTPADDING",  (0,0), (-1,-1), 5),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.5*cm))

    # ── AI Insights ──────────────────────────────────────────────────────────
    if ai_insights and ai_insights.strip():
        story.append(PageBreak())
        story.append(Paragraph("AI Insights", styles["h2"]))
        for line in ai_insights.split("\n"):
            line = line.strip()
            if not line:
                story.append(Spacer(1, 0.12*cm))
                continue
            line = line.replace("**", "<b>").replace("**", "</b>")
            if line.startswith(("- ", "* ", "• ")):
                line = "• " + line[2:]
            story.append(Paragraph(line, styles["body"]))

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.8*cm))
    story.append(Paragraph(
        "Generated by DataScope Pro &nbsp;·&nbsp; "
        "Built with Flask, Plotly, ReportLab &amp; Gemini AI",
        styles["muted"]))

    doc.build(story)
    return buf.getvalue()
