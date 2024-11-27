import pandas as pd
from typing import Literal
from datetime import datetime
import os


# newFile
# oldFile
def floatingDoctorsDifferenceCheck(
    oldFile: str, newFile: str, writeToExcel: bool = False
) -> pd.DataFrame:
    PATIENT: Literal["1_PatientDemographics"] = "1_PatientDemographics"
    VISIT: Literal["1_MedicalVisit"] = "1_MedicalVisit"
    SHEET_NAMES = [PATIENT, VISIT]
    NEW = "new"
    OLD = "old"
    KEY_ID = "Key ID"
    dfDict = dict()
    dfDict[NEW] = pd.read_excel(newFile, sheet_name=SHEET_NAMES)
    dfDict[OLD] = pd.read_excel(oldFile, sheet_name=SHEET_NAMES)

    dfPatientOld: pd.DataFrame = dfDict[OLD][PATIENT].copy()
    dfPatientNew: pd.DataFrame = dfDict[NEW][PATIENT].copy()
    dfVisitOld: pd.DataFrame = dfDict[OLD][VISIT].copy()
    dfVisitNew: pd.DataFrame = dfDict[NEW][VISIT].copy()

    dfPatientMerged = dfPatientNew.merge(
        dfPatientOld, left_on=KEY_ID, right_on=KEY_ID, how="outer", indicator=True
    )
    dfVisitMerged = dfVisitNew.merge(
        dfVisitOld, left_on=KEY_ID, right_on=KEY_ID, how="outer", indicator=True
    )

    def processFile(dataframe):
        dataframeFilt = ~dataframe["_merge"].isin({"both", "left_only"})
        dataframe = dataframe[dataframeFilt].reset_index(drop=True)
        dataframe = dataframe.rename(columns={"_merge": "merge"})

        mapDict: dict[str, str] = {
            "left_only": oldFile.split("\\")[-1].replace(".xlsx", ""),
            "right_only": newFile.split("\\")[-1].replace(".xlsx", ""),
            "both": "both",
        }

        dataframe["sourceFile"] = dataframe["merge"].map(mapDict)
        return dataframe

    dfPatientMerged = processFile(dfPatientMerged)
    dfVisitMerged = processFile(dfVisitMerged)

    dfDict: dict[str, pd.DataFrame] = {
        "dfPatientMerged": dfPatientMerged,
        "dfVisitMerged": dfVisitMerged,
    }

    if writeToExcel:
        date = datetime.now().strftime("%Y%m%d_%H%M%S_FloatingDoctorsComparison.xlsx")
        writer: pd.ExcelWriter = pd.ExcelWriter(date)
        for sheetName, frame in dfDict.items():
            frame.to_excel(writer, sheet_name=sheetName, index=False)

    return dfDict


def renameFiles(directory, filePathList, renameFiles=False):

    monthToNumDict: dict[str, str] = {
        "01-": "January ",
        "02-": "February ",
        "03-": "March ",
        "04-": "April ",
        "05-": "May ",
        "06-": "June ",
        "07-": "July ",
        "08-": "August ",
        "09-": "September ",
        "10-": "October ",
        "11-": "November ",
        "12-": "December ",
    }

    newNames: list[str] = [
        string.split("\\")[-1].replace(month, num).replace("Appointments - ", "2024-")
        for string in filePathList
        for num, month in monthToNumDict.items()
        if string.split("\\")[-1].replace(month, num) != string.split("\\")[-1]
    ]
    newNames = [directory + "\\" + string for string in newNames]

    if renameFiles == True:
        for oldFileName, newFileName in zip(filePathList, newNames):
            os.rename(oldFileName, newFileName)
    return newNames
