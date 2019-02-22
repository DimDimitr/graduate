# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 16:36:26 2019

@author: dmitry.efremov
"""
import random
import math
from DatBaseConnector import datBaseConnector 
from DatBaseConnector import Operation

#Класс описывающий среднее свремя по категориям для отдельного типа обращения
class BaseTime():
    def __init__(self, timeObject):
        self.usualPerson = timeObject[0]  
        self.oldPerson = timeObject[1]
        self.invalidPerson = timeObject[2]
        self.timeList = timeObject
    def getUsualPerson(self):
        return self.usualPerson
    def getOldPerson(self):
        return self.oldPerson
    def getInvalidPerson(self):
        return self.invalidPerson
    def getByNumber(self, number):
        return self.timeList[number - 1] 

#класс, хранящий словарь из типов операций и соответствующих им классов BaseTime
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
def randZeroToOne():
    return random.random()
       
class InputQueueEngine():
    def __init__(self, limitModelingTime):
        self.limitModelingTime = limitModelingTime
        self.__initParameters()
        self.__initCommingQueue(10)
    
    def __initParameters(self):
        self.timeBr = BaseTimeInfo()
        self.connect = datBaseConnector()
        self.uniqeOperations = self.connect.selectUniqeDescriptions()
        for element in self.connect.selectOperationTypes():
            operations = self.connect.selectByType(element[0])
            if operations != None:
                self.timeBr.addNewCalc(operations)
                
    def __initCommingQueue(self, middleTime):
        self.commingQueue = []
        tempTime = 0
        while tempTime < self.limitModelingTime:
            randomTimeComming = int(random.gauss(10, 3))
            self.commingQueue.append((self.__genRandomOparation(), randomTimeComming))
            tempTime += randomTimeComming
        for tempRow in self.commingQueue:
            print('gen time:' + str(tempRow[1]) + ' gen value:' + str(tempRow[0].toString()))
    
    def __getRandomConcession(self):
        return random.randint(1, 3)
        
    def __genRandomOparation(self):
        randDescr = random.choice(list(self.uniqeOperations.keys()))
        randomOperType = self.uniqeOperations[randDescr]
        randConcession = self.__getRandomConcession()
        randomMidTime = self.timeBr.times[randomOperType].getByNumber(randConcession)
        if(randomMidTime == 0):
            randomMidTime = self.timeBr.times[randomOperType].getByNumber(1)
        return Operation([1,
                          randDescr,
                          randomOperType,
                          int(random.gauss(randomMidTime, 3)),
                          randConcession])


inputQueueEngine = InputQueueEngine(100)