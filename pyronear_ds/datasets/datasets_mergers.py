import pandas as pd


def merge_datasets_by_departements(
        dataframe1: pd.DataFrame,
        time_col1: str,
        geometry_col1: str,
        dataframe2: pd.DataFrame,
        time_col2: str,
        geometry_col2: str,
        how: str
) -> pd.DataFrame:
    """
    Merge two datasets containing some kind of geometry and date columns.
    The merge is down on [time_col1, time_col2] and [geometry_col1, geometry_col2].
    Here the geometry is based on French departements. Therefore the geometry columns
    should contains either the code on the departement or its geometry (should be
    consistent throughout both datasets).

    Finally the merge is done according to the `how` parameter. Keep me mind that
    this parameter must be so that the merged dataframe keeps similar dimensions to the
    weather dataframe. This is because if there is an inner join, we will keep only the days
    where wildfires were declared. Therefore if the weather dataframe is the left frame, then
    `how` must be left, if it is the right frame, `how` must be right.

    Args:
        dataframe1: pd.DataFrame
            First dataframe, containing a time column and a geometry one.
        time_col1: str
            Name of the time column of dataframe1 on which the merge will be done.
        geometry_col1: str
            Name of the geometry column of dataframe1 on which the merge will be done.
        dataframe2: pd.DataFrame
            Second dataframe, containing a time column and a geometry one.
        time_col2: str
            Name of the time column of dataframe2 on which the merge will be done.
        geometry_col2: str
            Name of the geometry column of dataframe2 on which the merge will be done.
        how:
            Parameter of the merge, should correspond to which of the left or right frame
            the weather dataframe is.

    Returns: pd.DataFrame
        Merged dataset on French departement.
    """
    merged_data = pd.merge(
        dataframe1,
        dataframe2,
        left_on=[dataframe1[time_col1], dataframe1[geometry_col1]],
        right_on=[dataframe2[time_col2], dataframe2[geometry_col2]],
        how=how
    )
    return merged_data
