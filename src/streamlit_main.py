"""Unfinished module"""

import streamlit as st
import pandas as pd

from main import load_pathology_labels, load_reports, fuzzy_match
from src.const.body_sections import BodySection

labels = load_pathology_labels("./data/pathology_labels/pathology_labels.csv")
reports, non_impression_reports = load_reports("./data/merged_crosswalks_csv/sdr_crosswalks.csv", body_section=BodySection.MSK)
preds_fuzzy_impression = fuzzy_match(reports, "impression")

df = pd.DataFrame({"Report": [rep.text for rep in reports], "Predicted pathology": preds_fuzzy_impression})

st.title("Predicted reports labels")

st.write(df)
