import io
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)


BG = HexColor("#0f172a")
PANEL = HexColor("#1e293b")
ACCENT = HexColor("#06b6d4")
ACCENT2 = HexColor("#3b82f6")
TEXT = HexColor("#f1f5f9")
MUTED = HexColor("#94a3b8")
BORDER = HexColor("#334155")


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"],
            fontName="Helvetica-Bold", fontSize=26, textColor=TEXT, leading=30, alignment=TA_LEFT),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"],
            fontName="Helvetica", fontSize=11, textColor=MUTED, leading=14),
        "h2": ParagraphStyle("h2", parent=base["Heading2"],
            fontName="Helvetica-Bold", fontSize=15, textColor=TEXT, leading=18, spaceBefore=10, spaceAfter=8),
        "body": ParagraphStyle("body", parent=base["Normal"],
            fontName="Helvetica", fontSize=10, textColor=TEXT, leading=14),
        "muted": ParagraphStyle("muted", parent=base["Normal"],
            fontName="Helvetica", fontSize=9, textColor=MUTED, leading=12),
        "kpi_label": ParagraphStyle("kl", parent=base["Normal"],
            fontName="Helvetica", fontSize=9, textColor=MUTED, alignment=TA_CENTER),
        "kpi_value": ParagraphStyle("kv", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=18, textColor=TEXT, alignment=TA_CENTER, leading=22),
    }


def _styled_fig(fig):
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Helvetica", color="#1e293b", size=11),
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def _fig_to_image_flowable(fig, width_cm=16, height_cm=8):
    buf = io.BytesIO()
    img_bytes = fig.to_image(format="png", width=1100, height=int(1100 * height_cm / width_cm), scale=2)
    buf.write(img_bytes)
    buf.seek(0)
    return Image(buf, width=width_cm * cm, height=height_cm * cm)


def _kpi_table(filtered_df, styles):
    cells = []
    if "Revenue" in filtered_df.columns:
        cells.append(("Total Revenue", f"${filtered_df['Revenue'].sum():,.2f}"))
    cells.append(("Total Records", f"{len(filtered_df):,}"))
    if "Quantity" in filtered_df.columns:
        cells.append(("Items Sold", f"{filtered_df['Quantity'].sum():,.0f}"))
    elif "Order_ID" in filtered_df.columns:
        cells.append(("Total Orders", f"{filtered_df['Order_ID'].nunique():,}"))
    else:
        cells.append(("Total Columns", f"{len(filtered_df.columns)}"))
    if "Revenue" in filtered_df.columns and ("Quantity" in filtered_df.columns or "Order_ID" in filtered_df.columns):
        orders = filtered_df["Order_ID"].nunique() if "Order_ID" in filtered_df.columns else filtered_df["Quantity"].sum()
        avg = filtered_df["Revenue"].sum() / orders if orders > 0 else 0
        cells.append(("Avg Order Value", f"${avg:,.2f}"))
    cells = cells[:4]
    while len(cells) < 4:
        cells.append((" ", " "))

    row1 = [Paragraph(c[0].upper(), styles["kpi_label"]) for c in cells]
    row2 = [Paragraph(c[1], styles["kpi_value"]) for c in cells]
    tbl = Table([row1, row2], colWidths=[4.2 * cm] * 4, rowHeights=[0.7 * cm, 1.1 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#f1f5f9")),
        ("LINEABOVE", (0, 0), (-1, 0), 2, ACCENT),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return tbl


def build_pdf(filtered_df: pd.DataFrame, filter_col, datetime_cols, ai_insights: str = "") -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.6 * cm, rightMargin=1.6 * cm,
        topMargin=1.6 * cm, bottomMargin=1.6 * cm,
        title="DataScope Pro Report",
    )
    styles = _styles()
    story = []

    # Header
    story.append(Paragraph("DataScope Pro", styles["title"]))
    story.append(Paragraph(
        f"Analytics Report &nbsp;·&nbsp; Generated {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        styles["subtitle"]))
    story.append(Spacer(1, 0.3 * cm))

    # Summary line
    story.append(Paragraph(
        f"<b>{len(filtered_df):,}</b> rows &nbsp;·&nbsp; "
        f"<b>{len(filtered_df.columns)}</b> columns &nbsp;·&nbsp; "
        f"Filter column: <b>{filter_col or 'n/a'}</b>",
        styles["muted"]))
    story.append(Spacer(1, 0.5 * cm))

    # KPI cards
    story.append(Paragraph("Key Performance Indicators", styles["h2"]))
    story.append(_kpi_table(filtered_df, styles))
    story.append(Spacer(1, 0.6 * cm))

    # Charts
    color_seq = ["#06b6d4", "#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981"]

    if filter_col and "Revenue" in filtered_df.columns:
        story.append(Paragraph(f"Revenue by {filter_col}", styles["h2"]))
        bar_data = filtered_df.groupby(filter_col)["Revenue"].sum().reset_index().sort_values("Revenue", ascending=False)
        fig = px.bar(bar_data, x=filter_col, y="Revenue",
                     color_discrete_sequence=[ACCENT.hexval()[:7].replace("0x", "#")])
        fig.update_traces(marker_color="#06b6d4")
        story.append(_fig_to_image_flowable(_styled_fig(fig), width_cm=16, height_cm=7))
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph(f"Revenue Share by {filter_col}", styles["h2"]))
        pie = px.pie(filtered_df, names=filter_col, values="Revenue", hole=0.5,
                     color_discrete_sequence=color_seq)
        pie.update_traces(textposition="inside", textinfo="percent+label")
        story.append(_fig_to_image_flowable(_styled_fig(pie), width_cm=14, height_cm=7))
    elif filter_col:
        story.append(Paragraph(f"Distribution by {filter_col}", styles["h2"]))
        bar_data = filtered_df[filter_col].value_counts().reset_index()
        bar_data.columns = [filter_col, "Count"]
        fig = px.bar(bar_data, x=filter_col, y="Count", color_discrete_sequence=["#06b6d4"])
        story.append(_fig_to_image_flowable(_styled_fig(fig), width_cm=16, height_cm=7))

    if len(datetime_cols) > 0 and "Revenue" in filtered_df.columns:
        story.append(PageBreak())
        story.append(Paragraph("Revenue Trend Over Time", styles["h2"]))
        date_col = datetime_cols[0]
        time_data = filtered_df.groupby(date_col)["Revenue"].sum().reset_index()
        line = px.area(time_data, x=date_col, y="Revenue", color_discrete_sequence=["#06b6d4"])
        line.update_traces(line=dict(color="#06b6d4", width=2.5), fillcolor="rgba(6,182,212,0.18)")
        story.append(_fig_to_image_flowable(_styled_fig(line), width_cm=16, height_cm=7))
        story.append(Spacer(1, 0.4 * cm))

    # Numeric summary
    num_df = filtered_df.select_dtypes(include=["float64", "int64"])
    if len(num_df.columns) > 0:
        story.append(PageBreak())
        story.append(Paragraph("Numeric Summary", styles["h2"]))
        desc = num_df.describe().round(2).reset_index().rename(columns={"index": "stat"})
        data = [list(desc.columns)] + desc.astype(str).values.tolist()
        col_widths = [2.2 * cm] + [(16.8 - 2.2) / max(len(desc.columns) - 1, 1) * cm] * (len(desc.columns) - 1)
        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT2),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#f8fafc"), HexColor("#e2e8f0")]),
            ("GRID", (0, 0), (-1, -1), 0.3, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.5 * cm))

    # AI insights
    if ai_insights:
        story.append(PageBreak())
        story.append(Paragraph("AI Insights", styles["h2"]))
        for para in ai_insights.split("\n"):
            line = para.strip()
            if not line:
                story.append(Spacer(1, 0.15 * cm))
                continue
            line = line.replace("**", "")
            if line.startswith(("- ", "* ", "• ")):
                line = "• " + line[2:]
            story.append(Paragraph(line, styles["body"]))

    # Footer
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph(
        "Generated by DataScope Pro · Modern analytics built with Streamlit, Plotly, ReportLab & Gemini AI",
        styles["muted"]))

    doc.build(story)
    return buf.getvalue()
