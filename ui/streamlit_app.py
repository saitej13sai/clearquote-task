import os
import json
import requests
import streamlit as st


st.set_page_config(page_title="ClearQuote NL→SQL", layout="wide")

st.title("ClearQuote NL→SQL → Answer")


def _default_api_url() -> str:
    # Priority:
    # 1) STREAMLIT_API_URL env var
    # 2) local
    return os.getenv("STREAMLIT_API_URL", "http://127.0.0.1:8000/query")


def _post_query(api_url: str, question: str, timeout_s: int = 120) -> dict:
    r = requests.post(api_url, json={"question": question}, timeout=timeout_s)

    # Helpful errors for Codespaces public URL (401 if not authenticated)
    if r.status_code in (401, 403):
        raise RuntimeError(
            f"API returned {r.status_code}. If you're calling the public Codespaces URL, "
            f"open it in the browser once and ensure it's set to Public, or pass auth headers."
        )

    if r.status_code >= 400:
        # Try to parse FastAPI detail
        try:
            data = r.json()
            raise RuntimeError(f"API error {r.status_code}: {data}")
        except Exception:
            raise RuntimeError(f"API error {r.status_code}: {r.text}")

    try:
        return r.json()
    except Exception:
        raise RuntimeError(f"API returned non-JSON: {r.text[:3000]}")


with st.sidebar:
    st.header("Settings")
    api_url = st.text_input("API URL", value=_default_api_url(), help="FastAPI endpoint, e.g. http://127.0.0.1:8000/query")
    timeout_s = st.number_input("Request timeout (seconds)", min_value=10, max_value=600, value=120, step=10)
    st.caption("Tip: In Codespaces, you can use the forwarded port URL + /query.")

st.subheader("Ask a question")
question = st.text_area(
    "Natural language query",
    value="What is the average repair cost for rear bumper damages in last 30 days?",
    height=100,
)

colA, colB = st.columns([1, 3])
with colA:
    run_btn = st.button("Run", type="primary")

if "last_response" not in st.session_state:
    st.session_state["last_response"] = None

if run_btn:
    if not question.strip():
        st.warning("Enter a question.")
    else:
        with st.spinner("Querying..."):
            try:
                data = _post_query(api_url, question.strip(), timeout_s=int(timeout_s))
                st.session_state["last_response"] = data
            except Exception as e:
                st.error(str(e))
                st.session_state["last_response"] = None


data = st.session_state.get("last_response")

if data:
    needs_clar = data.get("needs_clarification", False)

    if needs_clar:
        st.warning("Needs clarification")
        st.write(data.get("clarification_question") or "Please clarify your question.")

        # Show debug info
        with st.expander("Debug details"):
            st.json(data)

    else:
        st.success("Answer")
        st.markdown(f"### {data.get('answer', '')}")

        meta1, meta2, meta3 = st.columns(3)
        meta1.metric("Rows returned", data.get("rows_returned") or 0)
        meta2.metric("Clarification", "No")
        meta3.metric("Status", "OK")

        if data.get("notes"):
            st.info("Notes")
            for n in data["notes"]:
                st.write(f"- {n}")

        with st.expander("SQL"):
            st.code(data.get("sql") or "", language="sql")

        with st.expander("Raw JSON"):
            st.json(data)
else:
    st.caption("Run a query to see results here.")
