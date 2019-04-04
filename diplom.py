# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 16:36:26 2019

@author: dmitry.efremov
"""
import random
import math
import statistics
from DatBaseConnector import datBaseConnector 
from DatBaseConnector import Operation
incomeMidTime = 1
separateValue = 2

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
        operationTimes = [[], [], []]
        for operation in listOfOperations:
            operationTimes[operation.getConcession_grade() - 1].append(operation.getOperation_time())
        def getMedian(timesList):
            if(len(timesList) > 0):
                return statistics.median(timesList)
            return 1
        
        self.times[listOfOperations[0].getOperation_type()] = BaseTime(
                [getMedian(operationTimes[0]),
                getMedian(operationTimes[1]),
                getMedian(operationTimes[2])])
    
#работа только с объектом типа Операция
def randZeroToOne():
    return random.random()

#описывает элемент очереди - операция и время выполнения 
class QueueUnit():
    def __init__(self, operation, unitTime):
        self.operation = operation
        self.unitTime = unitTime
    def getOperation(self):
        return self.operation
    def getUnitTime(self):
        return self.unitTime
    def increaseTime(self):
        self.unitTime -= 1
        if self.unitTime == 0:
            return self.operation 
        return None   
        
#Ксласс, описывающий заполнение входной очереди, на вход принимает время моделирования в минутах      
class InputQueueEngine():
    def __init__(self, limitModelingTime):
        self.limitModelingTime = limitModelingTime
        self.__initParameters()
        self.commingQueue = []
        self.__initCommingQueue(incomeMidTime)
        
#    устанавливает исходные параметры
    def __initParameters(self):
#        хранит в себе словарь из типа операции и времени для различных типов посетителей
        self.timeBr = BaseTimeInfo()
#        коннектор бд
        self.connect = datBaseConnector()
#        все уникальные операции, по которым есть информация в базе
        self.uniqeOperations = self.connect.selectUniqeDescriptions()
        self.__fillTimeBr()
        
#    заполняет словарь средних по времени для каждой операции
    def __fillTimeBr(self):
        for element in self.connect.selectOperationTypes():
            operations = self.connect.selectByType(element[0])
            if operations != None:
                self.timeBr.addNewCalc(operations)
           
#   заполняет очередь через случайные заявки и случайных людей
    def __initCommingQueue(self, middleTime):
        tempTime = 0
        while tempTime < self.limitModelingTime:
            randomTimeComming = self.__getRandomCommingTime(middleTime)
            self.commingQueue.append(QueueUnit(self.__genRandomOperation(), randomTimeComming))
            tempTime += randomTimeComming
    
    def __getRandomCommingTime(self, middleTime):
        randomTimeComming = int(random.gauss(middleTime, 1))
        while randomTimeComming <= 0:
            randomTimeComming = int(random.gauss(middleTime, 1))
        return randomTimeComming
#   Возвращает случайный тип посетителя
    def __getRandomConcession(self):
        return random.randint(1, 3)
    
#    Возвращает случайно определенную операцию    
    def __genRandomOperation(self):
        randDescr = random.choice(list(self.uniqeOperations.keys()))
        randomOperType = self.uniqeOperations[randDescr]
        randConcession = self.__getRandomConcession()
        randomMidTime = self.timeBr.times[randomOperType].getByNumber(randConcession)
        while(randomMidTime < 1):
            randomMidTime = self.timeBr.times[randomOperType].getByNumber(1)
        print('randomMidTime: ' + str(randomMidTime))
        randomOperTime = int(random.gauss(randomMidTime, 3))
        while(randomOperTime < 1):
            randomOperTime = int(random.gauss(randomMidTime, 3))
        return Operation([1,
                          randDescr,
                          randomOperType,
                          randomOperTime,
                          randConcession])
    
    def tryToPopFromQueue(self):
        if(self.inputQueueGet()):
            return self.commingQueue.pop(0)
    
#    Вернет операцию, если человек пришел, None если нет
    def inputQueueGet(self):
#        print("в очереди на приход - " + str(len(self.commingQueue)))
        if(len(self.commingQueue) > 0):
            return self.commingQueue[0].increaseTime()
        
    def printStat(self):
        for unit in self.commingQueue:
            print("элемент очереди " + unit.getOperation().toString())
            print("имеет время прихода = " + str(unit.getUnitTime()))
                
#Класс описывающий кассу    
class Till():
    def __init__(self, tillNumber, serviceTime = 0):
        self.tillNumber = tillNumber
        self.isVacant = True
        self.serviceTime = serviceTime
        self.serviceCount = 0
    def getTillNumber(self):
        return self.tillNumber
    def getIsVacant(self):
        return self.isVacant
    def getServiceCount(self):
        return self.serviceCount
    def getServiceTime(self):
        return self.serviceTime
    def initNewTime(self, operation):
        self.serviceTime = operation.getOperation_time()
        self.changeStatus()
    def __increaseServiceCount(self):
        self.serviceCount += 1
    def changeStatus(self):
#        print("Till isVacant was and become " + str(self.isVacant) + str(not self.isVacant))
        self.isVacant = not self.isVacant
        return self.isVacant
    
    def increaseServiceTime(self):
        if(self.isVacant):
            return True
        else:
            if(self.serviceTime > 0):
                self.serviceTime -= 1
            else:
                self.changeStatus()
                self.__increaseServiceCount()
                
    def toString(self):
        print(str(self.tillNumber) + str(self.isVacant))
        
    def getStat(self):
        print("Статистика для " + str(self.tillNumber) + " кассы:")
        print("Обслужано: " + str(self.serviceCount))
    
#Класс реализующий работу касс, инициализируется количеством касс
class TillEngine():
    def __init__(self, tillCount):
        self.tillCount = tillCount
        self.listOfTills = [Till(x) for x in range(tillCount)]
#    попытка операции попасть к оператору, результат - успешно/нет
    def callFromTill(self, operation):
        for till in self.listOfTills:
            if(till.getIsVacant()):
                till.initNewTime(operation)
                return True
        return False
#    во всех точках обслуживания уменьшается время на 1
    def increaseTimeAllTills(self):
        for till in self.listOfTills:
            till.increaseServiceTime()
            
    def getStat(self):
        for till in self.listOfTills:
            till.getStat()

class QueueObject():
    def __init__(self, queueUnit):
        self.waitingTime = 0
        self.queueUnit = queueUnit
     
    def increaseTime(self):
        self.waitingTime += 1       
    
#основная модель очереди
class GeneralStandartQueue():
    def __init__(self, separation):
        self.generalQueue = []
        self.separation = separation
        self.waitingTimeArray = []
    
    def addOperationIntoQueue(self, queueUnit):
        if(len(self.generalQueue) == 0):
            listOp = []
            listOp.append(QueueObject(queueUnit))
            self.generalQueue.append(listOp)
        else:
            tempOp = self.generalQueue[len(self.generalQueue) - 1]
            if(len(tempOp) == self.separation):
                listOp = []
                listOp.append(QueueObject(queueUnit))
                self.generalQueue.append(listOp)
            else:
                tempOp.append(QueueObject(queueUnit))
            self.sortInQueuePart(self.generalQueue[len(self.generalQueue) - 1])
#        print("after add" + str(self.generalQueue))
    
    def popOperationFromQueue(self):
        popOper = None
        if(len(self.generalQueue) > 0):
            popOper = self.generalQueue[0].pop(0)
            if(len(self.generalQueue[0]) == 0):
                self.generalQueue.pop()
        self.waitingTimeArray.append(popOper.waitingTime)
        return popOper.queueUnit
    
    def increaseAllTimes(self):
        for arr in self.generalQueue:
            for queueObject in arr:
                queueObject.increaseTime()
                
    def sortInQueuePart(self, queuePart):
        tempTr = []
        for party in queuePart:
            tempTr.append(party.queueUnit.operation.getOperation_time())
        print('before')
        print(tempTr)
        queuePart = sorted(queuePart, key=lambda queueUnit: queueUnit.queueUnit.operation.getOperation_time())
        tempTr = []
        for party in queuePart:
            tempTr.append(party.queueUnit.operation.getOperation_time())
        print('after')
        print(tempTr)
    
    def getWaitingTimes(self):
        return self.waitingTimeArray
        
    def getFirstOperation(self):
        if(len(self.generalQueue) > 0):
            if(len(self.generalQueue[0]) > 0):
                return self.generalQueue[0][0].queueUnit
        return None
    
    def getStat(self):
        print("Количество людей в очереди GeneralStandartQueue = " + str(len(self.generalQueue)))

# главный класс-модель работы почты
class PostModel():
    def __init__(self, initTime, tillCount):
        self.initTime = initTime
        self.inputQueueEngine = InputQueueEngine(initTime)
        self.inputQueueEngine.printStat()
        self.tillEngine = TillEngine(tillCount)
        self.genQueue = GeneralStandartQueue(separateValue)
        
    def start(self):
        tempTime = 0
        while(tempTime < self.initTime):
#            print("time now = " + str(tempTime))
#           попытка добавить операцию в очередь, проверка очереди прихода
            tempOper = self.inputQueueEngine.tryToPopFromQueue()
#            self.genQueue.getStat()
            if(tempOper != None):
                self.genQueue.addOperationIntoQueue(tempOper)

#           попыка достать операцию и отправить на обслуживание
            tempOper = self.genQueue.getFirstOperation()
            if(tempOper):
                if(self.tillEngine.callFromTill(tempOper.getOperation())):
                    self.genQueue.popOperationFromQueue()
                    
#            уменьшает все время на кассах
            self.tillEngine.increaseTimeAllTills()
#            добавляет время ожидания всем в очереди
            self.genQueue.increaseAllTimes()
            tempTime += 1
            
        self.inputQueueEngine.printStat()
        
    def getTillsStat(self):
        self.tillEngine.getStat()
        
    def getUserStat(self):
        print(self.genQueue.getWaitingTimes())

#создание модели для почты, параметры - время, количество точек обслуживания                 
posMod = PostModel(80, 2)
posMod.start()          
posMod.getUserStat()  
posMod.getTillsStat()