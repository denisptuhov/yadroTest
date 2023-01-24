import csv
import sys
import re
import os


def printTable():
    for i in table:
        for j in range(len(i)):
            end = ','
            if j == len(i) - 1:
                end = '\n'
            print(i[j], end=end)


def checkCLArgs(args):
    return not (len(args) != 2 or not os.path.isfile(args[1]))


def isFloat(element):
    try:
        float(element)
        return True
    except ValueError:
        return False


def checkReResult(result):
    if not result:
        return False

    for name in result.group(1, 4):
        if name not in columnNames:
            return False

    for n in result.group(2, 5):
        if n not in rowNums:
            return False

    return True


def checkPrevExpressions(curColumnName, curRowNum, prevExpList):
    expAddress = curColumnName + curRowNum
    return expAddress in prevExpList


def calculateExpression(firstArg, secondArg, op, curExpAddress):
    curExpJ, curExpI = curExpAddress[0], curExpAddress[1]

    if op == '+':
        table[curExpI][curExpJ] = str(float(firstArg) + float(secondArg))
    elif op == '-':
        table[curExpI][curExpJ] = str(float(firstArg) - float(secondArg))
    elif op == '*':
        table[curExpI][curExpJ] = str(float(firstArg) * float(secondArg))
    else:
        table[curExpI][curExpJ] = str(float(firstArg) / float(secondArg))


def parseExpression(columnName_, rowNum_, prevExpList):
    curExpJ, curExpI = columnNames.index(columnName_), rowNums.index(rowNum_)
    exp = table[curExpI][curExpJ]

    reResult = re.match(r'=([A-Za-z]+)(\d+)([+\-*/])([A-Za-z]+)(\d+)', exp)

    checkRes = checkReResult(reResult)
    if not checkRes:
        return False

    prevExpList.append(columnName_ + rowNum_)

    firstArgI, firstArgJ = rowNums.index(reResult.group(2)), columnNames.index(reResult.group(1))
    secondArgI, secondArgJ = rowNums.index(reResult.group(5)), columnNames.index(reResult.group(4))

    if checkPrevExpressions(columnNames[firstArgJ], rowNums[firstArgI], prevExpList):
        return False

    if checkPrevExpressions(columnNames[secondArgJ], rowNums[secondArgI], prevExpList):
        return False

    firstArg = table[firstArgI][firstArgJ]
    if not isFloat(firstArg):
        calcResult_ = parseExpression(columnNames[firstArgJ], rowNums[firstArgI], prevExpList)
        if not calcResult_:
            return False

    secondArg = table[secondArgI][secondArgJ]
    if not isFloat(secondArg):
        calcResult_ = parseExpression(columnNames[secondArgJ], rowNums[secondArgI], prevExpList)
        if not calcResult_:
            return False

    firstArg = table[firstArgI][firstArgJ]
    secondArg = table[secondArgI][secondArgJ]
    op = reResult.group(3)

    if op == '/' and secondArg == '0':
        return False

    calculateExpression(firstArg, secondArg, op, [curExpJ, curExpI])

    return True


if __name__ == "__main__":
    clCheckResult = checkCLArgs(sys.argv)
    if not clCheckResult:
        print("Bad command line arguments")
        exit(0)

    with open(sys.argv[1], newline='') as f:
        reader = csv.reader(f)
        table = []

        for row in reader:
            table.append(row)

        if len(table) == 1:
            print("Bad table")
            exit(0)

        rowNums = [row[0] for row in table]
        columnNames = table[0]

        for i in range(1, len(table)):
            for j in range(1, len(table[i])):
                cur_elem = table[i][j]

                if cur_elem[0] == '=':
                    calcResult = parseExpression(columnNames[j], rowNums[i], [])
                    if not calcResult:
                        print(f"Bad expression")
                        exit(0)
                elif not isFloat(cur_elem):
                    print(f"Bad number({cur_elem}) in {i} row, {j} column")
                    exit(0)

        printTable()
