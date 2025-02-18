from datetime import datetime
from typing import Literal
from numpy import nan
import pandas as pd


def create_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


def create_merged_dataframe(excelFilePath: str = "Appointments.xlsx") -> pd.DataFrame:
    # load in sheets from excel
    dfDict = pd.read_excel(
        excelFilePath, sheet_name=["1_PatientDemographics", "1_MedicalVisit"]
    )

    # define variables of the tables I actually need
    dfPatients, dfVisit = dfDict["1_PatientDemographics"], dfDict["1_MedicalVisit"]

    # perform a left join on data.
    dfMerged: pd.DataFrame = dfVisit.merge(
        dfPatients, left_on="Patient Linked", right_on="Key ID"
    )
    return dfMerged


def keep_needed_columns_and_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    # create a list of columns that I actually need for this analysis.
    columns: list[str] = [
        "Key ID_x",
        "Patient Linked",
        "Date",  # requires datetime type specification
        "Location of Visit",  # required cleaning (not done yet 2025-02-09)
        "Visit Type",
        "Glucose (Urine)",  # required cleaning
        "Patient Fasting?",
        "Glucose mg/dL (fasting)",  # required cleaning
        "Glucose mg/dL (NOT fasting)",  # required cleaning
        "Date Time Created",  # requires datetime type specification
        "Patient Consent",
        # "Date of Birth",  # specified as date
        "Sex",  # specified as enum type
        "Age",
        "Chronic Medication",  # No cleaning needed
    ]
    # create a dataframe with columns I actually need. Filter data by age >= 35.
    dataframe = (
        dataframe[columns].query("`Age`>=35").rename(columns={"Key ID_x": "Key ID"})
    )
    return dataframe


def clean_data_and_specify_data_types(dataframe: pd.DataFrame) -> pd.DataFrame:
    typeDict: dict = {
        "Patient Fasting?": bool,
        "Patient Consent": bool,
        "Visit Type": pd.CategoricalDtype(),
        "Sex": pd.CategoricalDtype(),
        # "Location of Visit": pd.CategoricalDtype(), # categorical type setting done later to avoid errors and FutureWarnings. Not yet a categorical variable, but it will
        "Patient Linked": pd.CategoricalDtype(),
        "Chronic Medication": pd.CategoricalDtype(),
    }
    dataframe = dataframe.astype(typeDict)
    dateTimeColumns: list[str] = [
        "Date",
        "Date Time Created",
        # "Date of Birth",
    ]
    # specify date time columns
    for column in dateTimeColumns:
        dataframe[column] = pd.to_datetime(dataframe[column])
    glucoseSubstitutionDict: dict[str, float] = {
        "110&115": nan,
        "189,,.": nan,
        "262,216": nan,
        "5002": nan,
        "96=>6": nan,
        "122,74": nan,
        "133,128": nan,
        ">600": nan,
        "539,570": nan,
    }
    glucoseList: list[str] = ["Glucose mg/dL (fasting)", "Glucose mg/dL (NOT fasting)"]
    for col in glucoseList:
        dataframe[col] = pd.to_numeric(
            dataframe[col]
            .replace(to_replace="[a-z|A-Z|/| |()+|[am]|>]", regex=True, value="")
            .replace(to_replace=glucoseSubstitutionDict),
            errors="raise",
            downcast="float",
        )

        locationNameCorrectionDict: dict[str, str] = {
            "Bahia Grande": "Bahia Grande",
            "Baja Cedro": "Bajo Cedro",
            "Bajo Cedro": "Bajo Cedro",
            "Bajo la Esperanza": "Bajo la Esperanza",
            "Base camp": "Base",
            "Base Clinic": "Base",
            "Base clinic": "Base",
            "Bisira": "Bisira",
            "Buena Esperanza": "Buena Esperanza",
            "Cayo de Agua": "Cayo de Agua",
            "Cayo De Agua": "Cayo de Agua",
            "Cero Brujo": "Cerro Brujo",
            "Cerro Brujo": "Cerro Brujo",
            "Ensanada": "Ensenada",
            "Ensenada": "Ensenada",
            "Isla Tigre": "Isla Tigre",
            "La Sabana": "La Sabana",
            "Loma Partida": "Loma Partida",
            "Nance de Risco": "Nance de Risco",
            "Nance De Risco": "Nance de Risco",
            "Norteno": "Norteno",
            "Playa Lorenzo": "Playa Lorenzo",
            "Playa Verde": "Playa Verde",
            "Popa I": "Popa I",
            "Popa II": "Popa II",
            "Pueblo Nuevo": "Pueblo Nuevo",
            "Quebrada Sal": "Quebrada Sal",
            "Rio Cana": "Rio Cana",
            "Rio Caña": "Rio Cana",
            "Rio Oeste": "Rio Oeste",
            "Salt Creek": "Salt Creek",
            "San Cristobal": "San Cristobal",
            "San Cristóbal": "San Cristobal",
            "Shark Hole": "Shark Hole",
            "Tierra Oscura": "Tierra Oscura",
            "Tobobe": "Tobobe",
            "Valle Escondido": "Valle Escondido",
        }
    # the pandas series method ser.cat.rename_categories is used in to future data cleaning step that
    # reduces the number of categories (i.e. Baho Cedro  & Baja Cedro --> Baho Cedro)
    # to avoid any FutureWarning depracation warnings and to ensure compatability with future versions of Pandas.
    if set(dataframe["Location of Visit"].dropna()) == set(
        locationNameCorrectionDict.keys()
    ):
        # map will turn elements not in the keys of the dict into na values, which is why this check takes place
        dataframe["Location of Visit"] = dataframe["Location of Visit"].map(
            locationNameCorrectionDict
        )
    else:
        raise ValueError(
            "There are some missing values found in the location of visit column that are not mapped in the correction dictionary"
        )
    return dataframe


def substitute_columns_with_dummy_index(
    dataframe: pd.DataFrame, columnName: str
) -> pd.DataFrame:
    def make_mapping_dict(dataframe: pd.DataFrame, columnName: str) -> dict[str, int]:
        sourceDict: dict[int, str] = (
            dataframe[columnName]
            .reset_index(drop=True)
            .reset_index()[[columnName, "index"]]
            .to_dict()[columnName]
        )
        dictionary: dict[str, int] = {v: k for k, v in sourceDict.items()}
        return dictionary

    dictionary: dict[str, int] = make_mapping_dict(dataframe, columnName)
    dataframe[columnName] = dataframe[columnName].map(dictionary)
    return dataframe


def dataframe_for_floating_doctors_request(excelFilePath: str) -> pd.DataFrame:
    dfMerged = create_merged_dataframe(excelFilePath)
    dataframe = keep_needed_columns_and_rows(dfMerged)
    dataframe = clean_data_and_specify_data_types(dataframe)
    dataframe = substitute_columns_with_dummy_index(dataframe, "Key ID")
    dataframe = substitute_columns_with_dummy_index(dataframe, "Patient Linked")
    return dataframe


if __name__ == "__main__":
    # Assumes that the excel file is in the same directory as the executable.
    excelFilePath: str = "Appointments.xlsx"
    dataframe: pd.DataFrame = dataframe_for_floating_doctors_request(excelFilePath)
    dataframe.to_excel(f"{create_timestamp()}.xlsx", index=False)
