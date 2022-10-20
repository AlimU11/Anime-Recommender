import re

import nltk

from . import ITextProcessor


class TextProcessor(ITextProcessor):
    """ITextProcessor implementation."""

    def __init__(self, text: str):
        self.text = text

    def clean_text(self) -> str:
        self.text = re.sub(r'[^ \nA-Za-z0-9À-ÖØ-öø-ÿ/]+', ' ', self.text)
        self.text = re.sub(r'[\\/×\^\]\[÷]', ' ', self.text)
        return self.text

    def remove_html_tags(self) -> str:
        self.text = re.sub(r'<.*?>', '', self.text)
        return self.text

    def to_lower(self) -> str:
        self.text = self.text.lower()
        return self.text

    def apply_stopwords(self) -> str:
        nltk.download('stopwords', quiet=True)
        from nltk.corpus import stopwords

        stopwords_list = stopwords.words('english')
        text_tokens = self.text.replace('\n', ' ').replace('\t', ' ').split(' ')
        final_list = [word for word in text_tokens if word not in stopwords_list]
        self.text = ' '.join(final_list)
        return self.text

    def lemmatize(self) -> str:
        nltk.download('wordnet', quiet=True)
        from nltk import WordNetLemmatizer

        lemma = WordNetLemmatizer()
        self.text = ' '.join([lemma.lemmatize(i) for i in self.text.split()])
        return self.text

    def text_pipe(self) -> str:
        self.clean_text()
        self.to_lower()
        self.apply_stopwords()
        self.lemmatize()
        return self.text
