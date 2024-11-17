def myPasswordGenerator(
    numberOfPasswordsGenerated: int,
    numberOfWordsInEachPassword: int,
    passwordType: str,
):
    from secrets import SystemRandom
    from typing import Literal

    EFF: Literal["EFF"] = "EFF"
    secretsGenerator = SystemRandom()
    if passwordType == EFF:
        filePath = "EFF_list.txt"
        listLength = 7776
    elif passwordType in ["2048", 2048]:
        filePath = "List2048.txt"
        listLength = 2048

    def generatePasswordList(filePath: str):
        with open(filePath, "r") as f:
            passwordList = f.read()
        passwordList = (
            passwordList.replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .replace(" ", "")
            .split(",")
        )
        return passwordList

    passwordList = generatePasswordList(filePath)
    myPasswordList = []
    for i in range(numberOfPasswordsGenerated):
        myRngList = [
            secretsGenerator.randint(0, listLength)
            for my in range(numberOfWordsInEachPassword)
        ]
        myPassword = "1!" + "".join([passwordList[my] for my in myRngList])
        myPasswordList.append(myPassword)
    return myPasswordList


if __name__ == "__main__":
    numberOfPasswordsGenerated = int(
        input("how many passwords do you want to generate: ")
    )
    numberOfWordsInEachPassword = int(input("how many words are in each password: "))
    passwordTypeQuestionText: str = """
            type "2048", or the number 2048 (without quotations) around it for a 2048 list 
            or "EFF" (again quotations not needed) for a 7776 list: 
            """

    passwordType = str(input(passwordTypeQuestionText))
    generatedFileName = str(
        input(
            "Name the file that you want to generate with the passwords (quotations not needed, but the file must end in .txt): "
        )
    )
    passwordList = myPasswordGenerator(
        numberOfPasswordsGenerated, numberOfWordsInEachPassword, passwordType
    )
    with open(generatedFileName, "w") as f:
        for password in passwordList:
            f.writelines(password)
            f.writelines("\n")
