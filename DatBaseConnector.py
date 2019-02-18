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
        
    def createTestData(self):
        1
#        self.execute("delete from human_resources")
#        #имя, позывной, инфо, отряд
#        departaments = ['Тверь', 'Ржев', 'Кимры', 'Конаково']
#        for dapart in departaments:
#            i = 0
#            while i < 10:
#                self.insertNewVolunteer(['Имя' + dapart + str(i), dapart + str(i), 'info ' + str(i), dapart])
#                i += 1
#        
#    def selectAllVolunteeres(self): 
#        stringToExec = "select full_Name from human_resources"
#        return self.execute(stringToExec, returnMode = 'strCostr')
#    
#    def insertNewVolunteer(self, insertData):
#        stringToExec = "insert into human_resources values(NULL,?,?,?,?)"
#        self.execute(stringToExec, insertData)
#        
#    def isertNick(self, nick):
#        stringToExec = "insert into empty_callsign values(NULL, '" + nick + "')"
#        self.execute(stringToExec)
#            
#    def emptyNick(self, checkNickState):
#        stringToExec = "select * from empty_callsign where callsign = '" + checkNickState + "'"
#        return self.execute(stringToExec, returnMode = 'fetchOne')
#    
#    def deleteNick(self, nick):
#        stringToExec = "delete from empty_callsign where callsign = '" + nick + "'"
#        self.execute(stringToExec)
#    
#    def selectAllUniqDepartaments(self):
#        stringToExec = "select distinct departament from human_resources"
#        return self.execute(stringToExec, returnMode = 'strCostr')
    
    def selectByType(self, operationType): 
        stringToExec = "select * from time_records where operation_type = " + str(operationType)
        return self.execute(stringToExec,  returnMode = 'operstions')
    
    def selectOperationTypes(self):
        stringToExec = "select * from operation_types"
        return self.execute(stringToExec,  returnMode = 'types')
    
#    def updateVolunteer(self, sovaVolont):
#        stringToExec = "update human_resources set full_name = '"  + sovaVolont.getName() + "', "
#        stringToExec += "callsign = '"  + sovaVolont.getNick() + "', "
#        stringToExec += "additional_information = '"  + sovaVolont.getInfo() + "', "
#        stringToExec += "departament = '"  + sovaVolont.getDepartament() + "' "
#        stringToExec += "where id = " + sovaVolont.getId()
#        self.execute(stringToExec)
#    
#    def existNickInNickTable(self, sovaVolontCall):
#        stringToExec = "select * from empty_callsign where upper(callsign) = upper('"
#        stringToExec +=  sovaVolontCall + "') limit 1"
#        return self.execute(stringToExec, returnMode = 'fetchOne') != None
#    
#    def existNickInPeopleTable(self, sovaVolontCall):
#        stringToExec = "select * from human_resources where upper(callsign) = upper('"
#        stringToExec +=  sovaVolontCall + "') limit 1"
#        return self.execute(stringToExec, returnMode = 'fetchOne') != None
#    
#    def selectVolunteerById(self, idDB):
#        stringToExec = "select * from human_resources where id = " + str(idDB)
#        getStr = str(self.execute(stringToExec, returnMode = 'fetchOne'))
#        getStr = getStr.replace("(", "")
#        getStr = getStr.replace(")", "")
#        getStr = getStr.replace("'", "")
#        arr = getStr.split(', ')
#        return Volunteer(arr)
#    
#    def selectByDepartament(self, departament): 
#        stringToExec = "select * from human_resources where departament = '" + departament + "' order by full_name asc"
#        return self.execute(stringToExec, returnMode = 'fetchAll')
#    
#    def deletFromVolunteeres(self, id):
#        stringToExec = "delete from human_resources where id = " + str(id)
#        self.execute(stringToExec)
#    
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