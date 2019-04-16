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
import matplotlib.pyplot as plt

from tkinter import tix as tk
from tkinter import *
from tkinter import ttk

repeatCount = 20
incomeMidTime = 7

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
        self.queueMaxLen = 1
    
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
            actualLength = self.getLengthCode()
            if (self.queueMaxLen < actualLength):
                    self.queueMaxLen = actualLength
            self.sortInQueuePart(self.generalQueue[len(self.generalQueue) - 1])
    
    def getLengthCode(self):
        if ((self.generalQueue) == None):
            return 0
        lentemp = 0
        for queueObjectList in self.generalQueue:
            lentemp += len(queueObjectList)
        return lentemp
        
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
        queuePart = sorted(queuePart, key=lambda queueUnit: queueUnit.queueUnit.operation.getOperation_time())
        tempTr = []
        for party in queuePart:
            tempTr.append(party.queueUnit.operation.getOperation_time())
    
    def getWaitingTimes(self):
        return self.waitingTimeArray
    
    def getMaxQueueLen(self):
        return self.queueMaxLen
    
    def getFinalLenState(self):
        return len(self.generalQueue)
        
    def getFirstOperation(self):
        if(len(self.generalQueue) > 0):
            if(len(self.generalQueue[0]) > 0):
                return self.generalQueue[0][0].queueUnit
        return None
    
    def getStat(self):
        print("Количество людей в очереди GeneralStandartQueue = " + str(len(self.generalQueue)))

# главный класс-модель работы почты
class PostModel():
    def __init__(self, initTime, tillCount, separateValue):
        self.initTime = initTime
        self.inputQueueEngine = InputQueueEngine(initTime)
        self.tillCount = tillCount
        self.separateValue = separateValue
        self.tillEngine = TillEngine(tillCount)
        self.genQueue = GeneralStandartQueue(separateValue)
        
    def start(self):
        tempTime = 0
        while(tempTime < self.initTime):
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
        
    def getTillsStat(self):
        self.tillEngine.getStat()
        
    def getStatDict(self):
        waitingTimes = self.genQueue.getWaitingTimes()
#        print(waitingTimes)
        return {'tillCount'      : self.tillCount,
                'separateValue'  : self.separateValue,
                'maxWaitingTime' : max(waitingTimes),
                'minWaitingTime' : min(waitingTimes),
                'maxQueueLen'    : self.genQueue.getMaxQueueLen(),
                'countIgnored'   : self.genQueue.getFinalLenState(),
                'serviceMidTime' : sum(waitingTimes) / len(waitingTimes)}
        
    def getUserStat(self):
        stat = self.getStatDict()
        print("Максимальное время ожмдания = " + str(stat['maxWaitingTime']))
        print("Минимальное время ожмдания = " + str(stat['minWaitingTime']))
        print("Максимальная длина очереди = " + str(stat['maxQueueLen']))
        print("Не успели обслужиться - " + str(stat['countIgnored']))
        print("Среднее время ожидания = " + str(stat['serviceMidTime']))

#создание модели для почты, параметры - время, количество точек обслуживания   
generalTimeToModel = 80

class OptimalParameters():
    def __init__(self, modelTime, tillCountMax, separateValueMax):    
        self.modelTime = modelTime
        self.tillCountMax = tillCountMax
        self.separateValueMax = separateValueMax
        self.listOfStat = []
        
    def tryToOptimise(self): 
        tillCount = 1
        while(tillCount <= self.tillCountMax):
            separateValue = 1
            while(separateValue <= self.separateValueMax):
                objTemp = MultipleTesting(self.modelTime, tillCount, separateValue)
                self.listOfStat.append(objTemp.getStat())
                separateValue += 1
            tillCount += 1              

    def drawPlotByName(self, namePar):
        listToDraw = []
        lableList = []
        for oneStat in self.listOfStat:
            listToDraw.append(oneStat[namePar])
            lableList.append("t" + str(oneStat['tillCount']) + 's' + str(oneStat['separateValue']))
        plt.plot(lableList, listToDraw)
        plt.title(namePar)
        plt.show()
                
        
    def getOptimalParameters(self, optimalType):
        self.tryToOptimise()
        theMostOptimal = None
        if(len(self.listOfStat) > 0):
            theMostOptimal = self.listOfStat[0]
            for statObj in self.listOfStat:
                if(statObj[optimalType] < theMostOptimal[optimalType]):
                    theMostOptimal = statObj
        return theMostOptimal
        

class MultipleTesting():
    def __init__(self, modelTime, tillCount, separateValue):
        self.modelTime = modelTime
        self.tillCount = tillCount
        self.separateValue = separateValue
        self.resultArray = self.calculate(self.modelTime, self.tillCount, self.separateValue)
    
    def calculate(self, modelTime, tillCount, separateValue):
        resultArray = []
        tempI = 0
        while(tempI < repeatCount):
            tempPosMod = PostModel(modelTime, tillCount, separateValue)
            tempPosMod.start()
            resultArray.append(tempPosMod.getStatDict())
            tempI += 1
        return resultArray
            
    def getStat(self):
        maxWaitingTime = 0
        minWaitingTime = 0
        maxQueueLen = 0
        countIgnored = 0
        serviceMidTime = 0
        for singleStat in self.resultArray:
            maxWaitingTime += singleStat['maxWaitingTime']
            minWaitingTime += singleStat['minWaitingTime']
            maxQueueLen += singleStat['maxQueueLen']
            countIgnored += singleStat['countIgnored']
            serviceMidTime += singleStat['serviceMidTime']
        statsLen = len(self.resultArray)
        return {'tillCount'      : self.tillCount,
                'separateValue'  : self.separateValue,
                'maxWaitingTime' : maxWaitingTime / statsLen,
                'minWaitingTime' : minWaitingTime / statsLen,
                'maxQueueLen'    : maxQueueLen / statsLen,
                'countIgnored'   : countIgnored / statsLen,
                'serviceMidTime' : serviceMidTime / statsLen}


class GeneralFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.modelTime = StringVar()
        self.tillCount = StringVar()
        self.separateValue = StringVar()
        self.initUI()
        
    def initUI(self):
        self.parent.title("SovaVolunteer")          
        self.pack(fill=BOTH, expand=1)
        frame = Frame(self)
        frame.pack()
        
        labelName = Label(frame, text = 'Количество касс').grid(row = 0, column = 0, padx=5, pady=5)
        POSField = Entry(frame, font='Arial 10', textvariable=self.tillCount)
        POSField.grid(row = 0, column = 1, columnspan = 1,  padx=5, pady=5)
        
        labelName = Label(frame, text = 'Количество в контейнере').grid(row = 1, column = 0, padx=5, pady=5)
        containerField = Entry(frame, font='Arial 10', textvariable=self.separateValue)
        containerField.grid(row = 1, column = 1, columnspan = 1,  padx=5, pady=5)
        
        labelName = Label(frame, text = 'Время для моделирования').grid(row = 2, column = 0, padx=5, pady=5)
        timeField = Entry(frame, font='Arial 10', textvariable=self.modelTime)
        timeField.grid(row = 2, column = 1, columnspan = 1,  padx=5, pady=5)

        button_calc = Button(frame, text = 'Рассчитать', command = self.calculateFunc)
        button_calc.config(background="#96cafb")
        button_calc.grid(row = 3, column = 0, columnspan = 1,  padx=5, pady=5)
        
        button_optim = Button(frame, text = 'Оптимизировать', command = self.optimise)
        button_optim.config(background="#96cafb")
        button_optim.grid(row = 3, column = 1, columnspan = 1,  padx=5, pady=5)
        
        
        frame.mainloop()
        
    def optimise(self):
        tillCount = int(self.tillCount.get())
        separateValue = int(self.separateValue.get())
        modelTime = int(self.modelTime.get())
        optimPar = OptimalParameters(modelTime, tillCount, separateValue)
        self.formReportFrame(optimPar.getOptimalParameters('maxWaitingTime'), 1)
        optimPar.drawPlotByName('maxWaitingTime')
        
    def calculateFunc(self):
        tillCount = int(self.tillCount.get())
        separateValue = int(self.separateValue.get())
        modelTime = int(self.modelTime.get())       
        objTemp = MultipleTesting(modelTime, tillCount, separateValue)
        self.formReportFrame(objTemp.getStat())
        
    def formReportFrame(self, result, optimMode = None):
        resFrame = Toplevel()
        resFrame.title("Результат")
        if(optimMode):
            labelTableName = Label(resFrame, text="В резульате оптимазации найдены наименьшие значения:")
        else:
            labelTableName = Label(resFrame, text="Для указанных параметров получены результаты:")
        widthFrame = 170
        if(labelTableName.winfo_reqwidth() + 10 > widthFrame):
            widthFrame = labelTableName.winfo_reqwidth() + 10
        resFrame.geometry(str(widthFrame) + "x200")
        labelTableName.grid(row = 0, column = 0, columnspan = 3, padx=5, pady=5)
        textToLable = "Количество точек обслужвания = " + str(result['tillCount'])
        textToLable += "\nСегментация очереди = " + str(result['separateValue'])
        textToLable += "\nМаксимальное время ожидания = " + str(result['maxWaitingTime'])
        textToLable += "\nМинимальное время ожмдания = " + str(result['minWaitingTime'])
        textToLable += "\nМаксимальная длина очереди = " + str(result['maxQueueLen'])
        textToLable += "\nНе успели обслужиться - " + str(result['countIgnored'])
        textToLable += "\nСреднее время ожидания = " + str(result['serviceMidTime'])
        labelStat = Label(resFrame, text = textToLable).grid(row = 1, column = 0, rowspan = 6, columnspan = 3, padx=5, pady=5)

        def okay():
            resFrame.destroy()
        button_decine = Button(resFrame, text = '   Ок   ', command = okay)
        button_decine.grid(row = 10, column = 1, padx=5, pady=5) 
        
root=Tk()
var = StringVar()
root.geometry("350x300")
style = ttk.Style(root)
GeneralFrame(root)    
root.mainloop()



