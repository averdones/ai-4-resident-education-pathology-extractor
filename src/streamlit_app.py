"""Unfinished module"""
import sys
import os
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.abspath('.'))

from main import load_pathology_labels, load_reports, exact_match, fuzzy_match
from const.body_sections import BodySection

st.set_page_config(page_title="AI 4 Resident Education", layout="wide")


labels = load_pathology_labels("src/data_preparation/data/pathology_labels/pathology_labels.csv")
reports, non_impression_reports = load_reports("src/data_preparation/data/merged_crosswalks_csv/sdr_crosswalks.csv",
                                               body_section=BodySection.MSK)


st.title("AI 4 Resident Education")

st.header("Predicted pathologies - Exact Matching")

preds_exact_impression = exact_match(reports, labels, "impression")
df_exact = pd.DataFrame({"Report": [rep.text for rep in preds_exact_impression],
                         "Predicted pathology": [rep.pred_pathology for rep in preds_exact_impression]})
st.dataframe(df_exact)


st.header("Predicted pathologies - Fuzzy Matching")

thresh = st.slider("Select a threshold for the fuzzy match", 0, 100, 85)
preds_fuzzy_impression = fuzzy_match(reports, labels, "impression", threshold=thresh)

df_fuzzy = pd.DataFrame({"Report": [rep.text for rep in preds_fuzzy_impression],
                         "Predicted pathology": [rep.pred_pathology for rep in preds_fuzzy_impression]})

st.dataframe(df_fuzzy, height=800)
