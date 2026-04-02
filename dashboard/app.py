import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
from datetime import datetime

import pandas as pd
import streamlit as st

from app.services.crm import get_lead_stats, get_leads

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lead Automation Dashboard",
    page_icon="🎯",
    layout="wide",
)

# ── Auto-refresh every 30 seconds ────────────────────────────────────────────
REFRESH_INTERVAL = 30  # seconds

# ── Helper ────────────────────────────────────────────────────────────────────
LABEL_COLORS = {"hot": "#ef4444", "warm": "#f59e0b", "cold": "#6b7280"}
STATUS_COLORS = {
    "new": "#3b82f6",
    "contacted": "#10b981",
    "follow_up_scheduled": "#f59e0b",
    "converted": "#22c55e",
    "lost": "#ef4444",
}


@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data():
    records = get_leads()
    stats = get_lead_stats()
    rows = []
    for r in records:
        f = r.get("fields", {})
        rows.append({
            "ID": r["id"],
            "Name": f.get("Name", ""),
            "Email": f.get("Email", ""),
            "Company": f.get("Company", ""),
            "Sector": f.get("Sector", ""),
            "Score": f.get("Score", 0),
            "Label": f.get("Label", ""),
            "Status": f.get("Status", ""),
            "Source": f.get("Source", ""),
            "FollowUpCount": f.get("FollowUpCount", 0),
            "Message": f.get("Message", ""),
            "Reason": f.get("Reason", ""),
            "SuggestedResponse": f.get("SuggestedResponse", ""),
            "CreatedAt": f.get("Created time", f.get("CreatedAt", "")),
        })
    df = pd.DataFrame(rows)
    return df, stats


# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎯 Lead Automation Dashboard")
st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  •  Auto-refreshes every {REFRESH_INTERVAL}s")

# Manual refresh button
col_refresh, col_empty = st.columns([1, 9])
with col_refresh:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

st.divider()

# ── Load data ─────────────────────────────────────────────────────────────────
try:
    df, stats = load_data()
except Exception as e:
    st.error(f"Could not load data from Airtable: {e}")
    st.stop()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("📊 Total Leads", stats["total"])
with k2:
    hot = stats["by_label"].get("hot", 0)
    st.metric("🔥 Hot Leads", hot)
with k3:
    warm = stats["by_label"].get("warm", 0)
    st.metric("✨ Warm Leads", warm)
with k4:
    cold = stats["by_label"].get("cold", 0)
    st.metric("❄️ Cold Leads", cold)

st.divider()

# ── Charts row ────────────────────────────────────────────────────────────────
chart1, chart2 = st.columns(2)

with chart1:
    st.subheader("Lead Distribution by Label")
    if not df.empty and "Label" in df.columns:
        label_counts = df["Label"].value_counts()
        chart_df = pd.DataFrame({
            "Label": label_counts.index,
            "Count": label_counts.values,
        })
        st.bar_chart(chart_df.set_index("Label"))
    else:
        st.info("No data yet.")

with chart2:
    st.subheader("Lead Pipeline by Status")
    if not df.empty and "Status" in df.columns:
        status_counts = df["Status"].value_counts()
        chart_df = pd.DataFrame({
            "Status": status_counts.index,
            "Count": status_counts.values,
        })
        st.bar_chart(chart_df.set_index("Status"))
    else:
        st.info("No data yet.")

# ── Score Distribution ────────────────────────────────────────────────────────
if not df.empty and "Score" in df.columns and df["Score"].sum() > 0:
    st.subheader("Score Distribution")
    score_df = df[["Name", "Score"]].sort_values("Score", ascending=False)
    st.bar_chart(score_df.set_index("Name")["Score"])

st.divider()

# ── Recent Leads Table ────────────────────────────────────────────────────────
st.subheader("📋 All Leads")

if df.empty:
    st.info("No leads yet. Submit a lead via the web form to get started.")
else:
    # Filter controls
    f1, f2, f3 = st.columns(3)
    with f1:
        label_filter = st.selectbox("Filter by Label", ["All", "hot", "warm", "cold"])
    with f2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "new", "contacted", "follow_up_scheduled", "converted", "lost"],
        )
    with f3:
        source_filter = st.selectbox("Filter by Source", ["All", "web_form", "whatsapp", "email"])

    filtered = df.copy()
    if label_filter != "All":
        filtered = filtered[filtered["Label"] == label_filter]
    if status_filter != "All":
        filtered = filtered[filtered["Status"] == status_filter]
    if source_filter != "All":
        filtered = filtered[filtered["Source"] == source_filter]

    # Display table
    display_cols = ["Name", "Email", "Company", "Sector", "Score", "Label", "Status", "Source", "FollowUpCount"]
    available_cols = [c for c in display_cols if c in filtered.columns]
    st.dataframe(
        filtered[available_cols],
        use_container_width=True,
        hide_index=True,
    )
    st.caption(f"Showing {len(filtered)} of {len(df)} leads")

st.divider()

# ── Lead Detail View ──────────────────────────────────────────────────────────
st.subheader("🔍 Lead Detail")

if not df.empty:
    lead_names = df["Name"].tolist()
    selected_name = st.selectbox("Select a lead to view details", ["— select —"] + lead_names)

    if selected_name != "— select —":
        row = df[df["Name"] == selected_name].iloc[0]

        d1, d2 = st.columns(2)
        with d1:
            st.markdown(f"**Name:** {row['Name']}")
            st.markdown(f"**Email:** {row['Email']}")
            st.markdown(f"**Company:** {row.get('Company') or '—'}")
            st.markdown(f"**Sector:** {row.get('Sector') or '—'}")
            st.markdown(f"**Source:** {row.get('Source') or '—'}")
            st.markdown(f"**Follow-up Count:** {row.get('FollowUpCount', 0)}")

        with d2:
            label = row.get("Label", "")
            color = LABEL_COLORS.get(label, "#6b7280")
            st.markdown(
                f"**Score:** <span style='font-size:24px; font-weight:bold; color:{color}'>"
                f"{row.get('Score', 0)}</span>  "
                f"<span style='background:{color}; color:white; padding:2px 10px; border-radius:999px; font-size:12px'>"
                f"{label.upper()}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Status:** {row.get('Status') or '—'}")
            st.markdown(f"**Airtable ID:** `{row['ID']}`")

        st.markdown("**Message:**")
        st.info(row.get("Message") or "—")

        st.markdown("**AI Qualification Reason:**")
        st.info(row.get("Reason") or "—")

        st.markdown("**AI Suggested Response:**")
        st.success(row.get("SuggestedResponse") or "—")

# ── Auto-refresh via meta tag ─────────────────────────────────────────────────
st.markdown(
    f"""<meta http-equiv="refresh" content="{REFRESH_INTERVAL}">""",
    unsafe_allow_html=True,
)
