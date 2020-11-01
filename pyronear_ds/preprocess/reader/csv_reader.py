import pandas as pd

from pyronear_ds.preprocess.reader.reader import Reader


class CsvReader(Reader):
    def __init__(self, file_path: str, separator: str):
        self.file_path = file_path
        self.separator = separator

    def read(self) -> pd.DataFrame:
        return pd.read_csv(self.file_path, sep=self.separator)
