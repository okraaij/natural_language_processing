 # Text classification using several machine learning models
 
An implementation of various machine learning classifiers to classify text

## Overview

- This repository contains a Jupyter notebook with the implementation of several common text classification machine learning models that apply a binary classification to a Twitter dataset. 
- To use text in machine learning classifiers, it must be represented in a numerical form. Therefore, a bag-of-words approach is taken as default in which a word’s frequency is vectorized and used as a feature
to train the classifier (Jurafsky and Martin 2009). 
- Considering the size of the sample set, the set is split into a training (80%) and testing set (20%) and additionally, k-fold cross-validation is applied for k = [3,5,10]. 
- To explore other fold parameters, a random permutation cross-validator with five splits and test (30%) and training (70%) is included.
- As an alternative to the bag-of-words approach, a Term Frequency-Inverse
Document Frequency (TF-IDF)approach is also used. The TF-IDF can be seen as a weighted vectorizer that assesses the importance of a word in the text.
- The following machine learning models are provided in Python:
  - Multinomial Naive Bayes
  - Support Vector Machine with linear kernel
  - Random Forest (no hyperparameter tuning applied)
  - Logistic Regression with TF-IDF vectorizer
