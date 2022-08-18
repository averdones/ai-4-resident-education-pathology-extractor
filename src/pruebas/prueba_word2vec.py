# Word2vec match
def word2vec_match(reports: list[Report], look_in: str = "impression", threshold: float = 0.5) -> list[str]:
    """Finds the pathology of each report using word2vec match.

    This function changes the report object in-place by adding the predicted pathology to the 'pred_pathology' field.

    Args:
        reports: Reports to label.
        look_in: Text to look in. Either "impression" to look only in the impression section or "report" to look in
            the whole report.
        threshold: Threshold for the cosine similarity.

    Returns:
        A list with the predicted pathologies.

    """
    nlp = spacy.load("en_core_sci_lg", disable=["attribute_ruler", "tagger", "ner"])  # Full model

    # Calculate nlp model of reports
    report_docs = []
    for i, report in enumerate(tqdm(reports)):
        if look_in == "impression":
            text = report.get_impression()
        elif look_in == "report":
            text = report.text
        else:
            raise ValueError(f"look_in must be 'impression' or 'report'")

        # Temporary
        # if i % 10 == 0 and i != 0:
        #     break

        doc = nlp(text)
        report_docs.append(doc)

    # Calculate nlp model of labels
    label_docs = []
    for i, label in enumerate(labels):
        doc = nlp(label)
        label_docs.append(doc)


    preds = []
    for i, rep_doc in enumerate(tqdm(report_docs)):
        scores = []
        for lab_doc in label_docs:
            scores.append(rep_doc.similarity(lab_doc))

        max_score = max(scores)
        if max_score > threshold:
            preds.append(lab_doc.text)
            reports[i].pred_pathology = "NO PATHOLOGY"
        else:
            preds.append("NO PATHOLOGY")
            reports[i].pred_pathology = "NO PATHOLOGY"

    return preds


preds_word2vec_impression = word2vec_match(reports, "impression", threshold=0.5)
