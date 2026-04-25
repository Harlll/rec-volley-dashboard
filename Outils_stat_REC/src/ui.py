import streamlit as st
from src.config import (
    PRIMARY_BG,
    SECONDARY_BG,
    ACCENT_GOLD,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    CARD_BG,
    BORDER,
)


def apply_global_style():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                linear-gradient(135deg, rgba(198,168,91,0.05) 0%, rgba(198,168,91,0.00) 18%),
                repeating-linear-gradient(
                    -45deg,
                    rgba(198,168,91,0.035) 0px,
                    rgba(198,168,91,0.035) 2px,
                    transparent 2px,
                    transparent 28px
                ),
                {PRIMARY_BG};
            color: {TEXT_PRIMARY};
        }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: {TEXT_PRIMARY} !important;
            font-weight: 700;
        }}

        p, label, div, span {{
            color: {TEXT_PRIMARY};
        }}

        section[data-testid="stSidebar"] {{
            background-color: {SECONDARY_BG};
            border-right: 1px solid {BORDER};
        }}

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            color: {TEXT_PRIMARY};
        }}

        .stSelectbox label,
        .stMultiSelect label {{
            color: {TEXT_SECONDARY} !important;
            font-weight: 600;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}

        .stTabs [data-baseweb="tab"] {{
            background-color: {CARD_BG};
            border-radius: 10px 10px 0 0;
            padding: 10px 16px;
            border: 1px solid {BORDER};
            color: {TEXT_PRIMARY};
        }}

        .stTabs [aria-selected="true"] {{
            background-color: {ACCENT_GOLD} !important;
            color: black !important;
        }}

        .kpi-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.18);
        }}

        .kpi-title {{
            font-size: 0.95rem;
            color: {TEXT_SECONDARY};
            margin-bottom: 8px;
        }}

        .kpi-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: {ACCENT_GOLD};
        }}

        .section-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 16px;
        }}

        .header-bar {{
            background: linear-gradient(90deg, #C6A85B 0%, #D9C58B 100%);
            padding: 18px 28px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.35);
        }}

        .header-title {{
            font-size: 1.9rem;
            font-weight: 800;
            color: black;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: rgba(198,168,91,0.10);
            border: 1px solid rgba(198,168,91,0.35) !important;
            border-radius: 14px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )