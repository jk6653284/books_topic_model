"""
Script to preprocess output_reviews text data to use for topic modeling
"""
# imports
from datetime import datetime
import os
import pandas as pd
import spacy

class PreprocessTextSimple:
    """
    simple method of using spacy to preprocess text.
    - gets pandas dataframe as input
    - saves csv of cleaned text as output (Return none)
    """
    def __init__(self):
        self.text_df = self.read_text_df(self.path)
        self.file_dir = os.path.dirname(__file__)

    # read text
    def read_text_df(self,file_name,text_col_name='text'):
        try:
            df = pd.read_json(os.path.join(self.file_dir,file_name))
            return df[[text_col_name]]
        except BaseException as e:
            print(f"Cannot open file with following error: {e}")

    def preprocess_text(spacy_object,text,lemm=True,lower=True,stopwords=True,punctuations=False,numbers=False):
        # create spacy doc
        doc = spacy_object(text)

        # clean text based on rules
        # test: if this logic works
        if lemm and lower:
            clean_token_list = [token.lemma_.lower() for token in doc if (token.is_stop == stopwords and token.is_punct == punctuations and token.is_numbers == numbers)]
        elif lemm:
            clean_token_list = [token.lemma_ for token in doc if (token.is_stop == stopwords and token.is_punct == punctuations and token.is_numbers == numbers)]
        elif lower:
            clean_token_list = [token.lower() for token in doc if (token.is_stop == stopwords and token.is_punct == punctuations and token.is_numbers == numbers)]
        else:
            clean_token_list = [token for token in doc if (token.is_stop == stopwords and token.is_punct == punctuations and token.is_numbers == numbers)]

        return ' '.join(clean_token_list)

    def save_preprocessed_texts(self):
        # create spacy doc
        nlp = spacy.load("en_core_web_sm")

        # preprocess all texts
        # test: if length of text_df and preprocessed list is the same
        preprocessed = []
        for i, text in enumerate(self.text_df):
            try:
                cleaned_text = self.preprocess_text(nlp, text)
            except BaseException as e:
                print(f"Could not process text {i} with following error: {e}")
                print(f"Added empty string instead")
                cleaned_text = ''
            preprocessed.append(cleaned_text)

        # save list of string as csv
        output_path = os.path.join(self.file_dir,f'input_topicmodel/preprocessed_simple_{datetime.now().strftime("%Y%m%d%H%M")}.csv')
        pd.Series(preprocessed).to_csv(output_path)

