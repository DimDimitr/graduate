import logging
import sqlite3

# add filemode="w" to overwrite

logging.basicConfig(filename="diplom.log", level=logging.INFO, format = "%(asctime)s %(levelname)s - %(message)s") 

#logging.debug("")
#logging.info("")
#logging.error("")

def stopLogging():
    logging.shutdown()
    
class Operation():
    def __init__(self, stringFromDB):
        self.id = stringFromDB[0]  
        self.operation_name = stringFromDB[1]
        self.operation_type = stringFromDB[2]
        self.operation_time = stringFromDB[3]
        self.concession_grade = stringFromDB[4]
    
    def getId(self):
        return self.id       
    def getOperation_name(self):
        return self.operation_name
    def getOperation_type(self):
        return int(self.operation_type)
    def getOperation_time(self):
        return int(self.operation_time)
    def getConcession_grade(self):
        return int(self.concession_grade)   
    def toString(self):
        resStr = "id:" + str(self.id) + "; "
        resStr +=  "operation_name:" + str(self.operation_name) + "; "
        resStr +=  "operation_type:" + str(self.operation_type) + "; "
        resStr +=  "operation_time:" + str(self.operation_time) + "; "
        resStr +=  "concession_grade:" + str(self.concession_grade)
        return resStr

class datBaseConnector():
    def __init__(self): 
        logging.info("init connection")
        self.conn = sqlite3.connect('SovaVolunteeres.sqlite', timeout=100)
        self.cursor = self.conn.cursor()
        self.creator()      
    
    #returnMode:
    #fetchOne
    #fetchAll
    #strCostr
    def execute(self, query, param = None, returnMode = ''):
        logging.info(query + " " + (str(param)))
        self.conn = sqlite3.connect('diplom.sqlite', timeout=100)
        self.cursor = self.conn.cursor()
        try:
            if param == None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, param)
            self.conn.commit()
        except Exception as err:
            logging.error('execute failed: %s : %s' % (query, str(err)))
        result = None
        if(returnMode == 'fetchOne'):
            result = self.cursor.fetchone()
        elif(returnMode == 'fetchAll'):
            result = self.cursor.fetchall()
        elif(returnMode == 'operstions'):
            result = self.getListOfOperations(self.cursor)
        elif(returnMode == 'types'):
            result = self.getTypes(self.cursor)
        elif(returnMode == 'oper_descr'):
            result = self.getDictionaryOfOperationsAndDescriptions(self.cursor)
        self.closeConnect()
        return result
        
    def creator(self):
        self.execute("""CREATE TABLE `time_records` (
                        `	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        `operation_name`	TEXT NOT NULL,
                        `operation_type`	INTEGER NOT NULL,
                        `operation_time`	BLOB NOT NULL,
                        `concession_grade`	INTEGER NOT NULL DEFAULT 0
                        );""") 
        self.execute("""CREATE TABLE `operation_types` (
                        `operation_number`	INTEGER UNIQUE,
                        `operation_name`	TEXT NOT NULL UNIQUE,
                        PRIMARY KEY(`operation_number`)
                        );""")
        self.execute("""CREATE TABLE `concession_grades` (
                        `concession_grade`	INTEGER NOT NULL UNIQUE,
                        `concession_name`	TEXT NOT NULL UNIQUE,
                        PRIMARY KEY(`concession_grade`)
                        ); """)
        
    def selectByType(self, operationType): 
        stringToExec = "select * from time_records where operation_type = " + str(operationType)
        return self.execute(stringToExec,  returnMode = 'operstions')
    
    def selectOperationTypes(self):
        stringToExec = "select * from operation_types"
        return self.execute(stringToExec,  returnMode = 'types')
    
    def selectUniqeDescriptions(self):
        stringToExec = "select distinct * from time_records"
        return self.execute(stringToExec,  returnMode = 'oper_descr')
     
    def getListOfOperations(self, cursor):
        operations = []
        firstDat = cursor.fetchone()
        if firstDat == None:
            return None
        operations.append(Operation(firstDat))
        while firstDat is not None:
            operations.append(Operation(firstDat))
            firstDat = cursor.fetchone()
        return operations
    
    def getDictionaryOfOperationsAndDescriptions(self, cursor):
        operationsAndDescriptions = {}
        firstDat = cursor.fetchone()
        if firstDat == None:
            return None
#        print(firstDat)
        operation = Operation(firstDat)
#        print('types? ' + str(operation.getOperation_type()) + ' ' + str(operation.getOperation_name()))
        operationsAndDescriptions[operation.getOperation_name()] = operation.getOperation_type()
        while firstDat is not None:
            operation = Operation(firstDat)
#            print('types? ' + str(operation.getOperation_type()) + ' ' + str(operation.getOperation_name()))
            operationsAndDescriptions[operation.getOperation_name()] = operation.getOperation_type()
            firstDat = cursor.fetchone()
        
        return operationsAndDescriptions
    
    def getTypes(self, cursor):
        types = []
        firstDat = cursor.fetchone()
        types.append(firstDat)
        while firstDat is not None:
            types.append(firstDat)
            firstDat = cursor.fetchone()
        return types
    
    
    def closeConnect(self):
        logging.info("closeConnect")
        self.conn.close()