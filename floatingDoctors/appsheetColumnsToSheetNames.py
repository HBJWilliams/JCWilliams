import pandas as pd


def appsheetColumnsToSheetNames(df: pd.DataFrame) -> dict:
    """After inputing a pandas dataframe, creates a dictionary where keys  are the original column names of the dataframe and the values the column names that actually work as sheet names in an excel file"""
    ## create dictionary of column names that are of
    columnNames = df.columns.tolist()
    columnNames = dict(zip(columnNames, columnNames))

    ## create a list of disallowed character sets for excel sheets
    disallowedCharactersForSheetNames = ["/", "\\", "?", "*", ":", "[", "]"]

    ## make keys of the dictionary the original column names and the values the column names that actually work as sheet names in an excel file
    for originalName, sheetName in columnNames.items():
        columnNames[originalName] = (
            sheetName.replace(disallowedCharactersForSheetNames[0], "_")
            .replace(disallowedCharactersForSheetNames[1], "_")
            .replace(disallowedCharactersForSheetNames[2], "_")
            .replace(disallowedCharactersForSheetNames[3], "_")
            .replace(disallowedCharactersForSheetNames[4], "_")
            .replace(disallowedCharactersForSheetNames[5], "_")
            .replace(disallowedCharactersForSheetNames[6], "_")[0:31]
        )
    return columnNames
