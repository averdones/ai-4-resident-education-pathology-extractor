import numpy as np
import spacy
from rapidfuzz import fuzz


##############################################################################
# Extracting impression sentences
# Load model
# nlp = spacy.load("en_core_sci_scibert")   # Limited to 512 tokens
nlp = spacy.load("en_core_sci_lg", disable=["attribute_ruler", "tagger", "ner"])   # Full model

docs = []
for i, report in enumerate(reports):
    if i % 1000 == 0:
        print(f"Case number: {i}")

    # Temporary
    if i == 10:
        break

    doc = nlp(report)
    docs.append(doc)


tokens = []
for token in nlp("dog dogg cat banana afskfsd"):
    tokens.append(token)

a = list(doc.sents)
print(len(a))

tokens = nlp(" ".join(labels))
for token in tokens:
    # print(token.text, token.has_vector, token.vector_norm, token.is_oov)
    if token.is_oov:
        print(token.text)

# Clean reports
clean_docs = []
for doc in docs:
    lemma_list = []
    for token in doc:
        lemma_list.append(token.lemma_)

    normalized_tokens = []
    for word in lemma_list:
        lexeme = nlp.vocab[word]
        if not lexeme.is_stop and not lexeme.is_punct and not lexeme.like_num:
            normalized_tokens.append(word)

    # Join tokens into a string
    # text_tokens = " ".join(normalized_tokens)
    clean_docs.append(normalized_tokens)

for doc in clean_docs:
    scores_ratio_dict = {}
    for label in labels:
        scores_ratio = np.array([])
        for token in doc:
            scores_ratio = np.append(scores_ratio, fuzz.ratio(token, label))

        scores_ratio_dict[label] = scores_ratio.max()




fuzz.ratio(report, "lipoma")
fuzz.partial_ratio(report, "lipoma")
fuzz.token_sort_ratio(report, "lipoma")
fuzz.token_set_ratio(report, "lipoma")
fuzz.partial_ratio_alignment(report, "lipoma")
fuzz.partial_token_ratio(report, "lipoma")
fuzz.partial_token_set_ratio(report, "lipoma")
fuzz.partial_token_sort_ratio(report, "lipoma")
fuzz.QRatio(report, "lipoma")
fuzz.WRatio(report, "lipoma")
