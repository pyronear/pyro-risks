import pandas as pd


class Reader:
    def read(self) -> pd.DataFrame:
        raise NotImplementedError
