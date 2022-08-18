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

        # Add column to identify the origin file and the row index in the file
        df.insert(0, "file", f.stem)
        df.insert(1, "row_index", df.index)

        # Drop rows with all nans due to excel bad formatting
        df = df.dropna(how="all")

        # Drop rows where Report is nan
        df = df.dropna(subset="Report")

        # Clean column names
        df.columns = [x.strip() for x in df.columns]
        if "ExamDescription" in df.columns:
            df = df.rename(columns={"ExamDescription": "Exam Description"})

        # Drop invalid and unwanted columns
        for name in df.columns:
            if "unnamed" in name.lower() or "anonymized accession" in name.lower():
                df = df.drop(columns=[name])
        # df = df.dropna(axis=1, how="all")

        ###############
        # We don't need this code anymore because we simply drop the columns with anonymized accessions
        # Merge columns with anonymized accessions into one
        # merged_data_list = []
        # for name in df.columns:
        #     if "anonymized accession" in name.lower():
        #         # Save values in the columns
        #         merged_data_list.append(np.expand_dims(df[name].astype(str), axis=1))
        #
        #         # Remove the column
        #         df = df.drop(columns=[name])

        # Add the new column
        # hor_stacked_list = list(np.hstack(merged_data_list))
        # for i in range(len(hor_stacked_list)):
        #     hor_stacked_list[i] = ";".join(hor_stacked_list[i])
        # df["Anonymized Accessions"] = hor_stacked_list
        ###############

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
