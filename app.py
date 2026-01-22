import streamlit as st
import pandas as pd
from pathlib import Path
from itsdangerous import URLSafeTimedSerializer, BadSignature

# ======================================================
# AUTH CONFIG (WEEKLY TOKEN)
# ======================================================
SECRET_KEY = "MY_SUPER_SECRET_KEY_2026"

TOKEN_EXPIRY_SECONDS = 7 * 24 * 60 * 60  # 7 days

serializer = URLSafeTimedSerializer(SECRET_KEY)

query_params = st.query_params
token = query_params.get("token")

if not token:
    st.error("Authentication required. Please request access.")
    st.stop()

try:
    serializer.loads(token, max_age=TOKEN_EXPIRY_SECONDS)
except BadSignature:
    st.error("Session expired or invalid. Please request a new link.")
    st.stop()

# ======================================================
# PAGE SETUP
# ======================================================
st.set_page_config(
    page_title="Site Photo Dashboard — FLM View",
    layout="wide"
)

st.title("📡 Site Photo Dashboard — FLM View")
st.caption("Operational view for rollout, audit & compliance teams")

# ======================================================
# CONFIDENTIALITY GATE (SINGLE)
# ======================================================
ack = st.checkbox(
    "🔒 I acknowledge these photos are confidential and must not be shared",
    key="confidential_ack"
)

if not ack:
    st.info("Please acknowledge confidentiality to continue.")
    st.stop()

st.success("Access granted. You may proceed.")

# ======================================================
# PATHS (CLOUD SAFE)
# ======================================================
BASE_DIR = Path(__file__).parent
EXCEL_PATH = BASE_DIR / "sites.xlsx"

# ======================================================
# LOAD EXCEL
# ======================================================
df = pd.read_excel(EXCEL_PATH)
df.columns = df.columns.str.strip()

df = df.rename(columns={
    "Site_id": "SiteID",
    "Has_Photos": "HasPhotos"
})

df["SiteID"] = df["SiteID"].astype(str).str.strip()
df["HasPhotos"] = df["HasPhotos"].astype(str).str.upper()

# ======================================================
# METRICS (LOCKED – FROM EXCEL ONLY)
# ======================================================
total_sites = len(df)
photos_ok = (df["HasPhotos"] == "YES").sum()
no_photos = total_sites - photos_ok

c1, c2, c3 = st.columns(3)
c1.metric("Total Sites", total_sites)
c2.metric("Photos OK", photos_ok)
c3.metric("No Photos", no_photos)

# ======================================================
# SIDEBAR FILTERS
# ======================================================
st.sidebar.markdown("### 🔍 Filters")

region = st.sidebar.selectbox(
    "Region", ["All"] + sorted(df["Region"].dropna().unique())
)

district_df = df if region == "All" else df[df["Region"] == region]

district = st.sidebar.selectbox(
    "District", ["All"] + sorted(district_df["District"].dropna().unique())
)

type_df = district_df if district == "All" else district_df[district_df["District"] == district]

site_type = st.sidebar.selectbox(
    "Type", ["All"] + sorted(type_df["Type"].dropna().unique())
)

site_search = st.sidebar.text_input("Site ID")

# ======================================================
# APPLY FILTERS
# ======================================================
filtered = df.copy()

if region != "All":
    filtered = filtered[filtered["Region"] == region]
if district != "All":
    filtered = filtered[filtered["District"] == district]
if site_type != "All":
    filtered = filtered[filtered["Type"] == site_type]
if site_search:
    filtered = filtered[filtered["SiteID"].str.contains(site_search, case=False)]

# ======================================================
# CSS (GREEN FLASH ON SEARCH)
# ======================================================
st.markdown("""
<style>
@keyframes flash {
  0% { box-shadow: 0 0 0px #22c55e; }
  50% { box-shadow: 0 0 20px #22c55e; }
  100% { box-shadow: 0 0 0px #22c55e; }
}
.flash {
  animation: flash 1.5s ease-in-out;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# SITE CARDS (NO PHOTO ACCESS – VIEW STATUS ONLY)
# ======================================================
for _, row in filtered.iterrows():
    site_id = row["SiteID"]
    has_images = row["HasPhotos"] == "YES"

    flash_class = "flash" if site_search == site_id and has_images else ""
    border_color = "#22c55e" if has_images else "#ef4444"
    status = "📸 Photos Available" if has_images else "No Photos"

    st.markdown(f"""
    <div class="{flash_class}" style="
        background:#0b1f3a;
        color:white;
        border-radius:14px;
        padding:16px 20px;
        margin-bottom:14px;
        border-left:6px solid {border_color};
    ">
        <div style="font-size:18px;font-weight:600;">
            Site {site_id} — {status}
        </div>
        <div style="font-size:14px;color:#cbd5e1;">
            Region: {row['Region']} |
            District: {row['District']} |
            Type: {row['Type']}
        </div>
    </div>
    """, unsafe_allow_html=True)

