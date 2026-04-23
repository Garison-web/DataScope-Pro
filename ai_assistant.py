import os
import io
import time
import hashlib
import pandas as pd
from google import genai
from google.genai import types

MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]

_CACHE: dict[str, str] = {}
_CACHE_ORDER: list[str] = []
_CACHE_MAX = 64


def _cache_key(question: str, df: pd.DataFrame) -> str:
    sig = f"{df.shape}-{list(df.columns)}-{int(pd.util.hash_pandas_object(df.head(50), index=False).sum())}"
    return hashlib.sha256(f"{question.strip().lower()}|{sig}".encode()).hexdigest()


def _cache_get(key: str):
    return _CACHE.get(key)


def _cache_set(key: str, value: str):
    if key in _CACHE:
        return
    _CACHE[key] = value
    _CACHE_ORDER.append(key)
    while len(_CACHE_ORDER) > _CACHE_MAX:
        old = _CACHE_ORDER.pop(0)
        _CACHE.pop(old, None)


def clear_cache():
    _CACHE.clear()
    _CACHE_ORDER.clear()


_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not configured")
        _client = genai.Client(api_key=api_key)
    return _client


def _dataset_context(df: pd.DataFrame, max_rows: int = 25) -> str:
    buf = io.StringIO()
    buf.write(f"Dataset shape: {df.shape[0]:,} rows x {df.shape[1]} columns\n\n")
    buf.write("Columns and dtypes:\n")
    for col, dtype in df.dtypes.items():
        buf.write(f"  - {col}: {dtype}\n")

    num_df = df.select_dtypes(include=["float64", "int64"])
    if len(num_df.columns) > 0:
        buf.write("\nNumeric summary:\n")
        buf.write(num_df.describe().round(2).to_string())
        buf.write("\n")

    cat_df = df.select_dtypes(include=["object", "string"])
    if len(cat_df.columns) > 0:
        buf.write("\nTop values per categorical column:\n")
        for col in cat_df.columns[:6]:
            top = cat_df[col].value_counts().head(5)
            buf.write(f"  {col}: {dict(top)}\n")

    buf.write(f"\nFirst {min(max_rows, len(df))} rows (CSV):\n")
    buf.write(df.head(max_rows).to_csv(index=False))
    return buf.getvalue()


def ask(question: str, df: pd.DataFrame, use_cache: bool = True) -> str:
    key = _cache_key(question, df)
    if use_cache:
        cached = _cache_get(key)
        if cached is not None:
            return cached + "\n\n_⚡ cached_"

    client = get_client()
    context = _dataset_context(df)

    system_prompt = (
        "You are DataScope AI, a sharp data analyst embedded in a dashboard. "
        "Answer the user's question using ONLY the dataset summary provided below. "
        "Be concise (3-6 sentences max). Use bullet points and bold key numbers when useful. "
        "Cite specific values, columns, or categories from the data. "
        "If the dataset doesn't contain the answer, say so clearly. "
        "Do not invent rows or columns that aren't shown."
    )

    prompt = f"{system_prompt}\n\n=== DATASET ===\n{context}\n\n=== QUESTION ===\n{question}"

    last_err = None
    for model in MODELS:
        for attempt in range(3):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                answer = response.text or "I couldn't generate a response. Please try rephrasing."
                _cache_set(key, answer)
                return answer
            except Exception as e:
                last_err = e
                msg = str(e)
                if "503" in msg or "UNAVAILABLE" in msg or "overloaded" in msg.lower():
                    time.sleep(1.5 * (attempt + 1))
                    continue
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                    time.sleep(2.0 * (attempt + 1))
                    continue
                break
    raise RuntimeError(
        "Gemini is temporarily overloaded across all fallback models. "
        f"Please try again in a moment. (Last error: {last_err})"
    )
