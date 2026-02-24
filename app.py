import streamlit as st
import requests
import streamlit.components.v1 as components

# ---------------- CONFIG ----------------
API_URL = st.secrets["API_URL"]

st.set_page_config(
    page_title="Trademark Text Search",
    layout="wide"
)

# ---------------- HEADER ----------------
st.title("Trademark Text Search")
#st.caption("Search trademarks using text similarity")

# ---------------- INPUT ----------------
query = st.text_input("Enter Trademark Name", placeholder="Wordmark")
search_clicked = st.button("Search")

# ---------------- CARD RENDER FUNCTION ----------------
def render_card(item):
    score_percent = int(float(item.get("text_score", 0)) * 100)

    rows_html = ""

    label_map = {
    "tm_certificate_no": "Certificate No.",    
    "tmr_application_status": "Status"
    }

    for key, value in item.items():
        if key in ["image_url", "text_score"]:
            continue

        label = label_map.get(
        key,
        key.replace("_", " ").title()
    )
        display_value = value if value is not None else "None"

        rows_html += f"""
        <div style="margin-bottom:4px;">
            <b>{label}:</b> {display_value}
        </div>
        """

    html = f"""
    <div style="
        border:1px solid #e6e6e6;
        border-radius:14px;
        padding:14px;
        background:white;
        font-family: Arial, sans-serif;
    ">

        <!-- IMAGE -->
        <img src="{item.get('image_url','')}" style="
            width:100%;
            height:160px;
            object-fit:contain;
            border-radius:8px;
            margin-bottom:12px;
        " />

        <!-- ALL JSON FIELDS -->
        {rows_html}

        <!-- SCORE BAR -->
        <div style="
    background:#e0e0e0;
    border-radius:30px;
    height:26px;
    margin-top:14px;
">
    <div style="
        background:#d18b00;
        height:26px;
        width:{score_percent}%;
        border-radius:30px;
        text-align:center;
        color:white;
        font-size:13px;
        font-weight:700;
        line-height:26px;
    ">
        {score_percent} %
    </div>
        </div>
    </div>
    """

    components.html(html, height=680)


# ---------------- API CALL ----------------
if search_clicked and query.strip():

    with st.spinner("Searching trademarks..."):
        response = requests.get(
            API_URL,
            params={"query": query},
            timeout=15
        )

    if response.status_code != 200:
        st.error(f"API Error: {response.status_code}")
        st.code(response.text)
        st.stop()

    try:
        data = response.json()
    except Exception:
        st.error("API did not return valid JSON")
        st.code(response.text)
        st.stop()

    results = data.get("results", [])

    if not results:
        st.warning("No results found.")
    else:
        # -------- GRID LAYOUT (4 CARDS PER ROW) --------
        cols_per_row = 4
        rows = [
            results[i:i + cols_per_row]
            for i in range(0, len(results), cols_per_row)
        ]

        for row in rows:
            cols = st.columns(cols_per_row)
            for col, item in zip(cols, row):
                with col:
                    render_card(item)
