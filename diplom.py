# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 16:36:26 2019

@author: dmitry.efremov
"""
from DatBaseConnector import datBaseConnector 
from DatBaseConnector import Operation

class BaseTime():
    def __init__(self, timeObject):
        self.usualPerson = timeObject[0]  
        self.oldPerson = timeObject[1]
        self.invalidPerson = timeObject[2]
    def getUsualPerson(self):
        return self.usualPerson
    def getOldPerson(self):
        return self.oldPerson
    def getInvalidPerson(self):
        return self.invalidPerson

class BaseTimeInfo():
    def __init__(self):
        self.times = {}
    def addNewCalc(self, listOfOperations):
        summOperations1 = 0
        count1 = 0
        summOperations2 = 0
        count2 = 0
        summOperations3 = 0
        count3 = 0
        for operation in listOfOperations:
            if(operation.getConcession_grade() == 1):
                summOperations1 += operation.getOperation_time()
            elif(operation.getConcession_grade() == 2):  
                summOperations2 += operation.getOperation_time()
            else:
                summOperations3 += operation.getOperation_time()
        if(count1 != 0):
           summOperations1 = summOperations1 /  count1
        if(count2 != 0):
           summOperations2 = summOperations2 /  count2
        if(count3 != 0):
           summOperations3 = summOperations3 /  count3
        self.times[listOfOperations[0].getOperation_type()] = BaseTime([summOperations1,
                                                                        summOperations2,
                                                                        summOperations3])
    
#работа только с объектом типа Операция
operation = Operation("12345")

timeBr = BaseTimeInfo()
connect = datBaseConnector()
for element in connect.selectOperationTypes():
    operations = connect.selectByType(element[0])
    if operations != None:
        timeBr.addNewCalc(operations)
#            print(op.toString())


