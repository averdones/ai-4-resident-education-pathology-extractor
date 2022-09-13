from pathlib import Path
import pandas as pd
import numpy as np

from src.report_manager import Report


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

    impress_reports = []
    non_impress_reports = []
    for i, text in enumerate(df["Report"].values):
        rep = Report(text)
        if rep.has_impression():
            impress_reports.append(rep)
        else:
            non_impress_reports.append(rep)

    print(f"Total number of reports: {len(impress_reports) + len(non_impress_reports)}")
    print(f"Number of reports with impression: {len(impress_reports)}")
    print(f"Number of reports without impression: {len(non_impress_reports)}")

    return impress_reports, non_impress_reports


def load_radlex_synonyms(data_path: str | Path):
    """Loads the synonyms from the RadLex (Radiology Lexicon) file.

    Args:
        data_path: Path to the XLS file with the RadLex file.

    Returns:

    """
    df = pd.read_excel(data_path, usecols=["Preferred Label", "Synonyms"])

    labels = df["Preferred Label"].str.lower().tolist()
    synonyms = df["Synonyms"].str.split("|").tolist()
    synonyms = [x if x is not np.nan else [] for x in synonyms]

    return dict(zip(labels, synonyms))


if __name__ == '__main__':
    import numpy as np
    radlex_path = "/home/antonio/NYU/AI_4_Resident_Education/ai-4-resident-education-pathology-extractor/src/data_preparation/data/radlex/radlex.xls"
    d = load_radlex_synonyms(radlex_path)
