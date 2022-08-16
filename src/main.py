from pathlib import Path
import pandas as pd
import spacy
from tqdm import tqdm
from collections import Counter
from rapidfuzz import fuzz

from report_manager import Report
from body_sections import BodySection


spacy.prefer_gpu()


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


def load_reports(data_path: str | Path, body_section: str | None = None) -> tuple[list[Report], list[Report]]:
    """Loads the reports and cleans them.

    Only reports of a specific body section can be returned.

    Args:
        data_path: Path to the CSV file with all the reports merged together
        body_section: If given, only the reports of the given body section will be loaded.

    Returns:
        A tuple of two lists, one with reports containing impression and one with reports not containing it.

    """
    # TODO: break this function into two: load and clean
    csv_path = Path(data_path).resolve()
    df = pd.read_csv(csv_path)

    if body_section is not None:
        print(f"Getting only reports of section {body_section}")
        df = df[df["file"].str.contains(body_section)]

    # Ignore cases where the report doesn't seem to contain impressions
    print(f"Total number of reports: {df.shape}")
    valid_idx = df["Report"].str.contains("impress", case=False)
    impress_df = df[valid_idx]
    non_impress_df = df[~valid_idx]
    print(f"Number of reports after removing reports without 'Impressions': {impress_df.shape}")
    print(f"Number of reports removed: {non_impress_df.shape[0]}")

    # TODO: potentially return generators if possible
    # Load reports with impression as Report objects
    impress_reports = []
    for rep in impress_df["Report"].tolist():
        impress_reports.append(Report(rep))

    # Load reports without impression as Report objects
    non_impress_reports = []
    for rep in non_impress_df["Report"].tolist():
        non_impress_reports.append(Report(rep))

    return impress_reports, non_impress_reports


labels = load_pathology_labels("./data/pathology_labels/pathology_labels.csv")
reports, non_impression_reports = load_reports("./data/merged_crosswalks_csv/sdr_crosswalks.csv", body_section=BodySection.MSK)


# Exact match
def exact_match(reports: list[Report], look_in: str = "impression") -> list[str]:
    """Finds the pathology of each report using exact match.

    This function changes the report object in-place by adding the predicted pathology to the 'pred_pathology' field.

    Args:
        reports: Reports to label.
        look_in: Text to look in. Either "impression" to look only in the impression section or "report" to look in
            the whole report.

    Returns:
        A list with the predicted pathologies.

    """
    preds = []
    for report in tqdm(reports):
        if look_in == "impression":
            text = report.get_impression()
        elif look_in == "report":
            text = report.text
        else:
            raise ValueError(f"look_in must be 'impression' or 'report'")

        # This variable is needed to check that no pathology was assigned
        found_path = False
        for label in labels:
            # We only accept a match if the whole n-gram of the label is in the impression
            if label in text:
                preds.append(label)
                report.pred_pathology = label
                found_path = True
                break

        # No pathology was found
        if not found_path:
            preds.append("NO PATHOLOGY")
            report.pred_pathology = "NO PATHOLOGY"

    return preds


# Fuzzy match
def fuzzy_match(reports: list[Report], look_in: str = "impression", threshold: float = 80.0) -> list[str]:
    """Finds the pathology of each report using fuzzy match.

    This function changes the report object in-place by adding the predicted pathology to the 'pred_pathology' field.

    Args:
        reports: Reports to label.
        look_in: Text to look in. Either "impression" to look only in the impression section or "report" to look in
            the whole report.
        threshold: Threshold for the fuzzy match.

    Returns:
        A list with the predicted pathologies.

    """
    preds = []
    for report in tqdm(reports):
        if look_in == "impression":
            text = report.get_impression()
        elif look_in == "report":
            text = report.text
        else:
            raise ValueError(f"look_in must be 'impression' or 'report'")

        # This variable is needed to check that no pathology was assigned
        found_path = False
        for label in labels:
            # We only accept a match if the whole n-gram of the label is in the impression

            if fuzz.partial_token_ratio(label, text) > threshold:
                preds.append(label)
                report.pred_pathology = label
                found_path = True
                # TODO: don't break if multiple matches are found but get the max instead
                break

        # No pathology was found
        if not found_path:
            preds.append("NO PATHOLOGY")
            report.pred_pathology = "NO PATHOLOGY"

    return preds


# Exact match
preds_exact_impression = exact_match(reports, "impression")
c_exat_impression = Counter(preds_exact_impression)
print(f"Number of unlabeled reports with exact matching in the impression: {c_exat_impression['NO PATHOLOGY']}")

preds_exact_whole_report = exact_match(reports, "report")
c_exact_whole_report = Counter(preds_exact_whole_report)
print(f"Number of unlabeled reports with exact matching in the whole report: {c_exact_whole_report['NO PATHOLOGY']}")

# Fuzzy match
preds_fuzzy_impression = fuzzy_match(reports, "impression")
c_fuzzy_impression = Counter(preds_fuzzy_impression)
print(f"Number of unlabeled reports with fuzzy matching in the impression: {c_fuzzy_impression['NO PATHOLOGY']}")

preds_fuzzy_whole_report = fuzzy_match(reports, "report")
c_fuzzy_whole_report = Counter(preds_fuzzy_whole_report)
print(f"Number of unlabeled reports with fuzzy matching in the whole report: {c_fuzzy_whole_report['NO PATHOLOGY']}")


for report in reports:
    print(f"{report.text} -> {report.pred_pathology}")
    break



# if __name__ == '__main__':
#     labels = load_pathology_labels("./data/pathology_labels/pathology_labels.csv")
#     reports = load_reports("./data/merged_crosswalks_csv/sdr_crosswalks.csv")


# report_text = df[(df["Exam Description"] == "XR FOOT AP LATERAL AND OBLIQUE LEFT") & (df["Modality"] == "CR") & (df["Reason/Diagnosis/History/Findings"] == "ankle pain")]["Report"][3323]
# pprint(report_text)
#
# report = Report(report_text)
# report.get_impression()



