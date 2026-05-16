"""
DataScope Pro — Flask backend
Run locally:  python server.py
Vercel:       configured via vercel.json
"""

import io
import os
import json
import time
import hashlib
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=".")
CORS(app)

# ── Helpers ──────────────────────────────────────────────────────────────────

def _parse_df(csv_string: str) -> pd.DataFrame:
    """Parse a CSV string into a DataFrame with type inference."""
    if not csv_string:
        return pd.DataFrame()
    df = pd.read_csv(io.StringIO(csv_string))
    # Detect date columns
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass
    # Auto-derive Revenue
    if "Revenue" not in df.columns:
        if "Price" in df.columns and "Quantity" in df.columns:
            df["Revenue"] = (
                pd.to_numeric(df["Price"], errors="coerce")
                * pd.to_numeric(df["Quantity"], errors="coerce")
            )
    return df


def _dataset_context(df: pd.DataFrame, max_rows: int = 30) -> str:
    buf = io.StringIO()
    buf.write(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns\n\n")
    buf.write("Columns & dtypes:\n")
    for col, dtype in df.dtypes.items():
        buf.write(f"  {col}: {dtype}\n")
    num_df = df.select_dtypes(include=["float64", "int64"])
    if len(num_df.columns):
        buf.write("\nNumeric summary:\n")
        buf.write(num_df.describe().round(2).to_string())
        buf.write("\n")
    cat_df = df.select_dtypes(include=["object", "string"])
    if len(cat_df.columns):
        buf.write("\nTop values per categorical column:\n")
        for col in cat_df.columns[:6]:
            top = cat_df[col].value_counts().head(5)
            buf.write(f"  {col}: {dict(top)}\n")
    buf.write(f"\nFirst {min(max_rows, len(df))} rows (CSV):\n")
    buf.write(df.head(max_rows).to_csv(index=False))
    return buf.getvalue()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/dataset.csv")
def demo_csv():
    return send_from_directory(".", "dataset.csv")


@app.route("/api/chat", methods=["POST"])
def chat():
    body     = request.get_json(force=True, silent=True) or {}
    question = body.get("question", "").strip()
    history  = body.get("history", [])          # [{role, content}, ...]
    csv_data = body.get("csvData", "")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    df = _parse_df(csv_data)
    context = _dataset_context(df)

    # Build conversation history string
    history_str = ""
    if history:
        history_str = "\n\n=== CONVERSATION HISTORY ===\n"
        for msg in history[-6:]:
            role = "User" if msg.get("role") == "user" else "Assistant"
            history_str += f"{role}: {str(msg.get('content',''))[:300]}\n"

    system = (
        "You are DataScope AI, a sharp data analyst embedded in a web dashboard. "
        "Answer using ONLY the dataset summary below. "
        "Be concise (3-6 sentences). Use bullet points and bold key numbers. "
        "Cite specific columns/categories from the data. "
        "If the dataset doesn't contain the answer, say so. "
        "Do not invent data."
    )
    prompt = (
        f"{system}\n\n=== DATASET ===\n{context}"
        f"{history_str}\n\n=== QUESTION ===\n{question}"
    )

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return jsonify({
            "answer": "⚠️ GEMINI_API_KEY not set. Add it as an environment variable to enable AI features."
        })

    try:
        from google import genai
        MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]
        client = genai.Client(api_key=api_key)
        last_err = None
        for model in MODELS:
            for attempt in range(2):
                try:
                    resp = client.models.generate_content(model=model, contents=prompt)
                    return jsonify({"answer": resp.text or "No response generated."})
                except Exception as e:
                    last_err = e
                    msg = str(e)
                    if any(x in msg for x in ("503", "UNAVAILABLE", "overloaded", "429", "EXHAUSTED")):
                        time.sleep(1.5 * (attempt + 1))
                        continue
                    break
        return jsonify({"answer": f"⚠️ AI temporarily unavailable. ({last_err})"})
    except ImportError:
        return jsonify({"answer": "⚠️ google-genai package not installed. Run: pip install google-genai"})
    except Exception as e:
        return jsonify({"answer": f"⚠️ Error: {e}"})


@app.route("/api/pdf", methods=["POST"])
def generate_pdf():
    body     = request.get_json(force=True, silent=True) or {}
    csv_data = body.get("csvData", "")
    ai_text  = body.get("aiInsights", "")

    df = _parse_df(csv_data)
    if df.empty:
        return jsonify({"error": "No data provided"}), 400

    datetime_cols = [c for c in df.columns if hasattr(df[c], "dt")]
    cat_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    filter_col = cat_cols[0] if cat_cols else None

    try:
        import pdf_report
        pdf_bytes = pdf_report.build_pdf(df, filter_col, datetime_cols, ai_text)
        from flask import Response
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": "attachment; filename=datascope_report.pdf"},
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print(f"\n  DataScope Pro running at  http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=True)
