"""
This module saves the impression sections of the reports in separates files, one per body section.
These files will be used as inputs to the annotation tool.
"""
import pandas as pd

from src.const.body_sections import BodySection
from src.data_preparation.loaders import load_reports_with_impression

from src.report_manager import Report


def create_impression(report: Report) -> list[str | float]:
    """Creates a dict with only the impression section of a report and the accession numbers.

    Accession numbers will be used to re-identify the report in the SDR files.

    Args:
        report: Report object.

    Returns:
        A dict with the impression section and the accession numbers.

    """
    return [report.get_impression(), report.orig_acc, report.anon_acc, report.anon_acc_1, report.anon_acc_2]


def create_impressions(reports: list[Report]) -> pd.DataFrame:
    """Creates a Dataframe with only the impressions from a list of reports.

    Returns:
        Dataframe of Impressions and their corresponding accession numbers to keep track of them.

    """
    impressions = []
    for rep in reports:
        impressions.append(create_impression(rep))

    return pd.DataFrame(impressions, columns=["impression", "orig_acc", "anon_acc", "anon_acc_1", "anon_acc_2"])


def save_impressions(body_section: str) -> None:
    """Saves the impression sections of the reports in a CSV files.

    Args:
        body_section: Body section to save the impressions from.

    """
    reports, _ = load_reports_with_impression("src/data_preparation/data/merged_crosswalks_csv/sdr_crosswalks.csv",
                                              body_section=body_section)

    impressions_df = create_impressions(reports)

    # Save to file
    impressions_df.to_csv(f"src/data_preparation/data/impressions/impressions_{body_section.lower()}.csv", index=False)


def main():
    body_sections = [
        BodySection.BODY,
        BodySection.CARDIAC,
        BodySection.CHEST,
        BodySection.MAMMO,
        BodySection.MSK,
        BodySection.NEURO,
        BodySection.NUCMED,
        BodySection.PET,
        BodySection.PEDS,
    ]

    for body_section in body_sections:
        save_impressions(body_section)


if __name__ == '__main__':
    main()
