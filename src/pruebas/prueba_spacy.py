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



import spacy
from spacy.matcher import Matcher
from negspacy.negation import Negex
from negspacy.termsets import termset

ts = termset("en_clinical")
ts.add_patterns({
            "preceding_negations": ["no obvious"]
        })

nlp = spacy.load("en_core_sci_lg")
matcher = Matcher(nlp.vocab)


nlp.add_pipe(
    "negex",
    config={
        "neg_termset":ts.get_patterns()
    }
)

doc = nlp("signs of acute fracture. No obvious stress fracture")
for e in doc.ents:
    print(e.text, e._.negex)
    print("Done")



text = "impression: pelvis/left hip: mild bilateral hip joint osteoarthritis. no obvious acute fracture or stress fracture. further evaluation with mri can be obtained if clinically relevant. there is discogenic and facet joint degenerative disease of the lower lumbar spine. there are mild degenerative changes at both sacroiliac joints and symphysis pubis. history: rule out stress fracture technique: xr pelvis ap and frog left 3 views comparison: none electronic signature: i personally reviewed the images and agree with this report. final report: dictated by and signed by attending renata la rocca vieira md 12/18/2019 12:01 pm"
doc = nlp(text)
for e in doc.ents:
    print(e.text, e._.negex)
    print("Done")


pattern = [{"LOWER": "fracture"}, {"IS_PUNCT": True}, {"LOWER": "further"}]
matcher.add("HelloWorld", [pattern])

doc = nlp(text)
matches = matcher(doc)
for match_id, start, end in matches:
    string_id = nlp.vocab.strings[match_id]  # Get string representation
    span = doc[start:end]  # The matched span
    print(match_id, string_id, start, end, span.text)
