from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC

###############################################################################
# Tf-idf classifier

# Split train test
X = clean_docs_reports
y = clean_docs_diagnosis

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=123)

vectorizer = TfidfVectorizer()
X_train_tf = vectorizer.fit_transform(X_train)
X_test_tf = vectorizer.transform(X_test)

# SVM classifier
clf = SVC()
clf.fit(X_train_tf, y_train)

clf.score(X_train_tf, y_train)
clf.score(X_test_tf, y_test)
