"""
Script to preprocess output_reviews text data to use for topic modeling
"""
# imports
from datetime import datetime
import os
import sys
import pandas as pd
import spacy
import logging
from rich.logging import RichHandler

class PreprocessTextSimple:
    """
    simple method of using spacy to preprocess text.
    - gets pandas dataframe as input
    - saves csv of cleaned text as output (Return none)
    """
    def __init__(self):
        self.file_dir = os.path.dirname(__file__)
        self.logger = self.__init__logger()

    def __init__logger(self):
        logger = logging.getLogger(__file__)

        # handlers
        shell_handler = RichHandler()
        file_handler = logging.FileHandler(os.path.join(self.file_dir,f"../logs/preprocess_text/{datetime.now().strftime('%Y%m%d-%H-%M-%S')}_simple.log"))

        # formatters
        shell_formatter = logging.Formatter('%(message)s')
        file_formatter = logging.Formatter(
            '%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s')

        # set formatters
        shell_handler.setFormatter(shell_formatter)
        file_handler.setFormatter(file_formatter)

        # set levels
        logger.setLevel(logging.DEBUG)
        shell_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.DEBUG)

        # add handlers to logger
        logger.addHandler(shell_handler)
        logger.addHandler(file_handler)

        return logger


    # read text
    def _read_text_df(self,file_name,text_col_name='text'):
        input_path = os.path.join(self.file_dir, f"review_scraper/output_reviews/{file_name}")
        self.logger.info(f"Started reading text from {input_path}")
        try:
            df = pd.read_json(input_path)
            self.logger.info(f"Imported input file with {len(df)} reviews")
            return df[text_col_name]
        except BaseException as e:
            self.logger.error(f"Cannot read file due to following error: {e}")
            sys.exit(1)

    def preprocess_text(self,spacy_object,text,lemm=True,lower=True,stopwords=True,punctuations=False,numbers=False):
        # create spacy doc
        doc = spacy_object(text)

        # clean text based on rules
        if lemm and lower:
            clean_token_list = [token.lemma_.lower() for token in doc if (token.is_stop == stopwords and token.is_punct == punctuations and token.is_digit == numbers)]
        elif lemm:
            clean_token_list = [token.lemma_ for token in doc if (token.is_stop == stopwords and token.is_punct == punctuations and token.is_digit == numbers)]
        elif lower:
            clean_token_list = [token.lower() for token in doc if (token.is_stop == stopwords and token.is_punct == punctuations and token.is_digit == numbers)]
        else:
            clean_token_list = [token for token in doc if (token.is_stop == stopwords and token.is_punct == punctuations and token.is_digit == numbers)]

        return ' '.join(clean_token_list)

    def save_preprocessed_texts(self,file_name):
        text_df = self._read_text_df(file_name)
        # create spacy doc
        nlp = spacy.load("en_core_web_sm")

        # cleaning method
        clean_method = {
            'lemm': True,
            'lower': True,
            'stopwords': True,
            'punctuations': False,
            'numbers': False
        }
        self.logger.info(f"Cleaning input text with following cleaning methods: f{clean_method}")

        # preprocess all texts
        preprocessed = []
        self.logger.info(f"Started cleaning texts")
        error_counter = 0
        for i, text in enumerate(text_df):
            try:
                cleaned_text = self.preprocess_text(nlp, text)
            except BaseException as e:
                self.logger.warning(f"Could not process text index {i} with following error, and will add empty string instead: {e}")
                cleaned_text = ''
                error_counter += 1
            preprocessed.append(cleaned_text)
            if error_counter == 10:
                self.logger.error(f"Running into too many errors, shutting down.")
                sys.exit(1)
        self.logger.debug(f"Completed preprocessing texts")

        # save list of string as csv
        try:
            output_path = os.path.join(self.file_dir,f'input_topicmodel/preprocessed_simple_{datetime.now().strftime("%Y%m%d%H%M")}.csv')
            pd.Series(preprocessed).to_csv(output_path)
            self.logger.info(f"Preprocessed text saved in directory: {output_path}")
        except BaseException as e:
            self.logger.error(f"Failed to save cleaned file with the following error: {e}")
            sys.exit(1)

# this for testing
def main():
    sc = PreprocessTextSimple()
    sc.save_preprocessed_texts(file_name="all_reviews.json")

if __name__ == '__main__':
    main()
