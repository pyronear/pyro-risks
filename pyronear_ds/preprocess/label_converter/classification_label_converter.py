from pandas import DataFrame

from pyronear_ds.preprocess.label_converter.label_converter import LabelConverter


class ClassificationLabelConverter(LabelConverter):
    """
    Classification Label Converter which uses an given column to
    assign 0 if no fire and 1 is fire.
    """

    def __init__(self, label_column):
        self.label_column = label_column

    def get_labels(self, data: DataFrame) -> DataFrame:
        where_no_fire = data[self.label_column].isna()
        data.loc[where_no_fire, self.label_column] = 0
        data.loc[~where_no_fire, self.label_column] = 1
        data[self.label_column] = data[self.label_column].astype(int)
        return data
