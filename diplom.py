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
    def getUsualPerson(self):
        return self.usualPerson
    def getOldPerson(self):
        return self.oldPerson
    def getInvalidPerson(self):
        return self.invalidPerson

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
       
class inputQueueEngine():
    def __init__(self, limitModelingTime):
        self.limitModelingTime = limitModelingTime
        self.initParameters()
        self.initCommingQueue(10)
    
    def initParameters(self):
        self.timeBr = BaseTimeInfo()
        connect = datBaseConnector()
        self.uniqeOperations = connect.selectUniqeDescriptions()
        for element in connect.selectOperationTypes():
            operations = connect.selectByType(element[0])
            if operations != None:
                self.timeBr.addNewCalc(operations)
                
    def initCommingQueue(self, middleTime):
        self.commingQueue = []
        tempTime = 0
        while tempTime < self.limitModelingTime:
            self.commingQueue.append((self.genRandomOparation(), self.randomGenTime(10)))
            tempTime += 10
            
    def randomGenTime(self, time):
        expFromLambda = math.exp(-time)
        key = True
        while key :
            rand_l = randZeroToOne()
            rand_r = rand_l * randZeroToOne()
            num = 0
            while not(rand_l >= expFromLambda and rand_r < expFromLambda):
                rand_l = rand_r
                rand_r *= randZeroToOne()
                num += 1
                if num > 1000:
                    return time
                if(num < 50 ):
                    key = False
        return num
    
    def genRandomOparation(self):
        randDescr = random.choice(list(self.uniqeOperations.keys()))
        randomOperType = self.uniqeOperations[randDescr]
        print('' + randDescr + ' ' + str(randomOperType))



