from pandas import DataFrame


class LabelConverter:
    """
    This class takes in a final merged DataFrame and apply necessary operations
    in order to get a labeled DataFrame which can then be used for modeling purposes.
    """

    def get_labels(self, data: DataFrame) -> DataFrame:
        raise NotImplementedError
