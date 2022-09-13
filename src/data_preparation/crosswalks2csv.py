"""This module converts multiple Excel files as they are saved in the Sharepoint into a single CSV file
for convenience. These files are the "simulated daily readout" (SDR) created during the Covid pandemic to preserve
the education of radiology residents."""

from pathlib import Path
import pandas as pd


def crosswalks_to_csv(input_dir: Path, output_filename: Path) -> None:
    """Converts multiple Excel files into a CSV file.

    Args:
        input_dir: Path to the directory containing the Excel files.
        output_filename: Path to the output CSV file.

    """
    # Get all xlsx files from the input directory
    files = input_dir.glob("*.xlsx")

    # Load all excel files as dataframes into a list
    df_list = []
    for f in files:
        df = pd.read_excel(f)

        # Add column to identify the origin file
        df.insert(0, "file", f.stem)

        # Drop rows with all nans due to excel bad formatting
        df = df.dropna(how="all")

        # Drop rows where Report is nan
        df = df.dropna(subset="Report")

        # Clean column names
        df.columns = [x.strip() for x in df.columns]
        df.columns = df.columns.str.replace("Accession .1", "Accession.1", regex=False)
        df.columns = df.columns.str.replace("Accession .2", "Accession.2", regex=False)
        df.columns = df.columns.str.replace("ExamDescription", "Exam Description", regex=False)

        # Drop invalid columns
        for name in df.columns:
            if "unnamed" in name.lower():
                df = df.drop(columns=[name])

        # Append dataframe to list to concatenate
        df_list.append(df)

    # Concatenate list of dataframes
    all_df = pd.concat(df_list, axis=0, ignore_index=True)

    # Save CSV file
    all_df.to_csv(output_filename, index=False)


if __name__ == '__main__':
    input_dir_ = Path("data/original_crosswalks_excels").resolve()
    output_filename_ = Path("data/merged_crosswalks_csv/sdr_crosswalks.csv").resolve()

    crosswalks_to_csv(input_dir_, output_filename_)
