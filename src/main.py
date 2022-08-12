from pathlib import Path
import numpy as np
import pandas as pd
import spacy
from tqdm import tqdm
from collections import Counter

from src.report_manager import Report


spacy.require_gpu()


def load_pathology_labels(data_path: str | Path) -> list[str]:
    """Loads the pathology labels.

    Args:
        data_path: Path to the CSV file with all the pathology labels.

    Returns:
        A list of pathologies.

    """
    csv_path = Path(data_path).resolve()
    df = pd.read_csv(csv_path)

    return df["labels"].str.lower().tolist()


def load_reports(data_path: str | Path) -> list[Report]:
    """Loads the reports and cleans them.

    Args:
        data_path: Path to the CSV file with all the reports merged together

    Returns:
        A list with the cleaned reports.

    """
    csv_path = Path(data_path).resolve()
    df = pd.read_csv(csv_path)

    # Ignore cases where the report doesn't seem to contain impressions
    print(f"Shape of df: {df.shape}")
    clean_df = df[df["Report"].str.contains("impress", case=False)]
    print(f"Shape of df after removing rows without 'Impressions': {clean_df.shape}")
    print(f"Number of rows removed: {df.shape[0] - clean_df.shape[0]}")

    # Load reports as Report objects
    reports = []
    for rep in clean_df["Report"].tolist():
        reports.append(Report(rep))

    return reports


labels = load_pathology_labels("./data/pathology_labels/pathology_labels.csv")
reports = load_reports("./data/merged_crosswalks_csv/sdr_crosswalks.csv")


# Exact match
def exact_match(reports):
    preds = []
    for report in tqdm(reports):
        # impression = report.get_impression()
        impression = report.text

        if "there is a minimally displaced fracture of the left medial malleolus" in impression:
            print()

        # This variable is needed to check that no pathology was assigned
        found_path = False
        for label in labels:
            # We only accept a match if the whole n-gram of the label is in the impression
            if label in impression:
                preds.append(label)
                report.pred_pathology = label
                found_path = True
                break

        # No pathology was found
        if not found_path:
            preds.append("NO PATHOLOGY")
            report.pred_pathology = "NO PATHOLOGY"

    return preds

preds = exact_match(reports)
Counter(preds)

np.where(np.array(preds) == "Aneurysmal bone cyst")
print(reports[2].text)











# if __name__ == '__main__':
#     labels = load_pathology_labels("./data/pathology_labels/pathology_labels.csv")
#     reports = load_reports("./data/merged_crosswalks_csv/sdr_crosswalks.csv")


report_text = df[(df["Exam Description"] == "XR FOOT AP LATERAL AND OBLIQUE LEFT") & (df["Modality"] == "CR") & (df["Reason/Diagnosis/History/Findings"] == "ankle pain")]["Report"][3323]
pprint(report_text)

report = Report(report_text)
report.get_impression()



