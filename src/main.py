import spacy
from tqdm import tqdm
from copy import deepcopy
from rapidfuzz import fuzz
import numpy as np

from src.report_manager import Report
from src.const.body_sections import BodySection
from src.const.pathologies import Pathology
from src.data_preparation.loaders import load_pathology_labels, load_reports, load_radlex_synonyms


spacy.prefer_gpu()


# Exact match
def exact_match(reports: list[Report], labels: list[str], look_in: str = "impression",
                check_synonyms: bool = False) -> list[Report]:
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
            if check_synonyms:
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
def fuzzy_match(reports: list[Report], labels: list[str],  look_in: str = "impression",
                threshold: float = 80.0) -> list[Report]:
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

    for report in tqdm(reports_copy):
        if look_in == "impression":
            text = report.get_impression()
        elif look_in == "report":
            text = report.text
        else:
            raise ValueError(f"look_in must be 'impression' or 'report'")

        # This variable is needed to check that no pathology was assigned
        found_path = False
        fuzzy_scores = []
        for label in labels:
            # We calculate the fuzzy score for all pathologies and get the highest one that is above the threshold
            # In case of draw, we arbitrarily take the first one
            score = fuzz.partial_ratio(label, text)
            fuzzy_scores.append(score)

        # Only get the highest score that is above the threshold
        max_idx = np.argmax(fuzzy_scores)
        max_score = fuzzy_scores[max_idx]
        if max_score > threshold:
            report.pred_pathology = labels[max_idx]
            found_path = True

        # No pathology was found
        if not found_path:
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
    possible_labels_copy = possible_labels.copy()
    possible_labels_copy.append(Pathology.unknown)
    
    # Initialize counter
    counter = {x:0 for x in possible_labels_copy}
    for report in reports:
        counter[report.pred_pathology] += 1

    return counter


if __name__ == '__main__':
    labels = load_pathology_labels("src/data_preparation/data/pathology_labels/pathology_labels.csv")
    reports, non_impression_reports = load_reports("src/data_preparation/data/merged_crosswalks_csv/sdr_crosswalks.csv",
                                                   body_section=BodySection.MSK)
    synonyms_dict = load_radlex_synonyms("src/data_preparation/data/radlex/radlex.xls")

    # Exact match
    preds_exact_impression = exact_match(reports, labels, "impression")
    c_exat_impression = count_pred_path(preds_exact_impression, labels)
    print(f"Number of unlabeled reports with exact matching in the impression: {c_exat_impression[Pathology.unknown]}")

    preds_exact_whole_report = exact_match(reports, labels, "report")
    c_exact_whole_report = count_pred_path(preds_exact_whole_report, labels)
    print(f"Number of unlabeled reports with exact matching in the whole report: {c_exact_whole_report[Pathology.unknown]}")

    # Fuzzy match
    preds_fuzzy_impression = fuzzy_match(reports, labels, "impression", threshold=0)
    c_fuzzy_impression = count_pred_path(preds_fuzzy_impression, labels)
    print(f"Number of unlabeled reports with fuzzy matching in the impression: {c_fuzzy_impression[Pathology.unknown]}")

    preds_fuzzy_whole_report = fuzzy_match(reports, labels, "report", threshold=70)
    c_fuzzy_whole_report = count_pred_path(preds_fuzzy_whole_report, labels)
    print(f"Number of unlabeled reports with fuzzy matching in the whole report: {c_fuzzy_whole_report[Pathology.unknown]}")


    ## Check with synonyms
    preds_exact_impression_synonyms = exact_match(reports, labels, "impression", check_synonyms=True)
    c_exat_impression_synonyms = count_pred_path(preds_exact_impression_synonyms, labels)
    print(f"Number of unlabeled reports with exact matching in the impression with synonyms: {c_exat_impression_synonyms[Pathology.unknown]}")

    preds_exact_whole_report_synonyms = exact_match(reports, labels, "report", check_synonyms=True)
    c_exact_whole_report_synonyms = count_pred_path(preds_exact_whole_report_synonyms, labels)
    print(f"Number of unlabeled reports with exact matching in the whole report with synonyms: {c_exact_whole_report_synonyms[Pathology.unknown]}")
