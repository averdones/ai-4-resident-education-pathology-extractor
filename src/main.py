import spacy
from tqdm import tqdm
from copy import deepcopy
from collections import Counter
from rapidfuzz import fuzz

from src.report_manager import Report
from src.const.body_sections import BodySection
from src.const.pathologies import Pathology
from src.data_preparation.loaders import load_pathology_labels, load_reports, load_radlex_synonyms


spacy.prefer_gpu()


labels = load_pathology_labels("src/data_preparation/data/pathology_labels/pathology_labels.csv")
reports, non_impression_reports = load_reports("src/data_preparation/data/merged_crosswalks_csv/sdr_crosswalks.csv",
                                               body_section=BodySection.MSK)
synonyms_dict = load_radlex_synonyms("src/data_preparation/data/radlex/radlex.xls")


# Exact match
def exact_match(reports: list[Report], look_in: str = "impression", check_synonyms: bool = False) -> list[Report]:
    """Finds the pathology of each report using exact match.

    Args:
        reports: Reports to label.
        look_in: Text to look in. Either "impression" to look only in the impression section or "report" to look in
            the whole report.
        check_synonyms: If True, the synonyms of the pathology will be checked as well.

    Returns:
        A list of Report objects with the predicted pathologies.

    """
    reports_copy = deepcopy(reports)

    for report in tqdm(reports_copy):
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
                report.pred_pathology = label
                found_path = True
                break

            # TODO: break into different function and have more advance matching
            # Check for synonyms of pathologies
            # WARNING: no synonyms help
            if label in synonyms_dict:
                for synonym in synonyms_dict[label]:
                    if synonym in text:
                        report.pred_pathology = label
                        found_path = True
                        break

        # No pathology was found
        if not found_path:
            report.pred_pathology = Pathology.unknown

    return reports_copy


# Fuzzy match
def fuzzy_match(reports: list[Report], look_in: str = "impression", threshold: float = 80.0) -> list[Report]:
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
    reports_copy = deepcopy(reports)

    preds = []
    for report in tqdm(reports_copy):
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

            if fuzz.partial_ratio(label, text) > threshold:
                preds.append(label)
                report.pred_pathology = label
                found_path = True
                # TODO: don't break if multiple matches are found but get the max instead
                break

        # No pathology was found
        if not found_path:
            preds.append(Pathology.unknown)
            report.pred_pathology = Pathology.unknown

    return reports_copy


def count_pred_path(reports: list[Report], possible_labels: list[str]) -> dict:
    """Counts the number of pathologies predicted for each pathology in all reports.

    Args:
        reports: Reports.
        possible_labels: Possible pathology labels.

    Returns:
        A dictionary with the number of predicted pathologies for each pathology.

    """
    possible_labels.append(Pathology.unknown)
    
    # Initialize counter
    counter = {x:0 for x in possible_labels}
    for report in reports:
        counter[report.pred_pathology] += 1

    return counter


# Exact match
preds_exact_impression = exact_match(reports, "impression")
c_exat_impression = count_pred_path(preds_exact_impression, labels)
print(f"Number of unlabeled reports with exact matching in the impression: {c_exat_impression[Pathology.unknown]}")

preds_exact_whole_report = exact_match(reports, "report")
c_exact_whole_report = count_pred_path(preds_exact_whole_report, labels)
print(f"Number of unlabeled reports with exact matching in the whole report: {c_exact_whole_report[Pathology.unknown]}")

# Fuzzy match
preds_fuzzy_impression = fuzzy_match(reports, "impression", threshold=70)
c_fuzzy_impression = count_pred_path(preds_fuzzy_impression, labels)
print(f"Number of unlabeled reports with fuzzy matching in the impression: {c_fuzzy_impression[Pathology.unknown]}")

preds_fuzzy_whole_report = fuzzy_match(reports, "report", threshold=70)
c_fuzzy_whole_report = count_pred_path(preds_fuzzy_whole_report, labels)
print(f"Number of unlabeled reports with fuzzy matching in the whole report: {c_fuzzy_whole_report[Pathology.unknown]}")


## Check with synonyms
preds_exact_impression_synonyms = exact_match(reports, "impression", check_synonyms=True)
c_exat_impression_synonyms = count_pred_path(preds_exact_impression_synonyms, labels)
print(f"Number of unlabeled reports with exact matching in the impression with synonyms: {c_exat_impression_synonyms[Pathology.unknown]}")

preds_exact_whole_report_synonyms = exact_match(reports, "report", check_synonyms=True)
c_exact_whole_report_synonyms = count_pred_path(preds_exact_whole_report_synonyms, labels)
print(f"Number of unlabeled reports with exact matching in the whole report with synonyms: {c_exact_whole_report_synonyms[Pathology.unknown]}")




