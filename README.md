## Pathology extractor from radiology reports

### Useful modules

In order of execution:

- `crosswalks2csv.py`

This module merges all the files of the SDR into a single CSV file to ease the loading process.

- `loader.py`

This module contains functions to load various data: labels, reports, reports with and without impression, radlex 
synonyms (work in progress).  

For example, the function `load_reports` returns a list of 
Report objects (a helper class that contains the report text and the rest of the information on the report).

- `save_impressions.py`

This is a helper module to create the input files for the Label Studio (the annotation tool)
so that medical experts can choose a label for each report.

- `main.py`

For now, this module holds all the code to do string analysis (exact matching and fuzzy matching) on the reports and 
extract a label from them.

It also contains functions to help with negation detection and counting the number of predicted pathologies.


**This repo is a work in progress.**

This repository contains the code to extract a pathology from a radiology report.

This tool is part of the AI 4 Resident Education project.
