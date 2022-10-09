from abc import ABCMeta, abstractmethod


class ITextProcessor(metaclass=ABCMeta):
    """A text processor interface."""

    @abstractmethod
    def clean_text(self) -> str:
        """Clean text from special characters and html tags."""

    @abstractmethod
    def remove_html_tags(self) -> str:
        """Remove html tags from text.

        While `clean_text` method is part of `text_pipe` pipeline, this method is used to
        preprocess text for further displaying.
        """

    @abstractmethod
    def to_lower(self) -> str:
        """Convert text to lower case."""

    @abstractmethod
    def apply_stopwords(self) -> str:
        """Remove stopwords from text."""

    @abstractmethod
    def lemmatize(self) -> str:
        """Lemmatize text."""

    @abstractmethod
    def text_pipe(self) -> str:
        """Apply all text processing methods to text in predefined order."""
