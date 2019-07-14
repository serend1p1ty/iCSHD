# -*- coding: UTF-8 -*-

'''
@Author: t-zhel
@Date: 2019-07-09 13:48:38
@LastEditor: t-zhel
@LastEditTime: 2019-07-14 15:26:44
@Description: Implement the GUI of iCSHD
'''

import sys
import pyodbc
from CustomerInfo import CustomerInfo
from SearchCaseWin import SearchCaseWin
from PyQt5.QtWidgets import (QWidget, QScrollArea, QAction, QVBoxLayout,
                             QMainWindow, QApplication)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the connection to SQL Server
        self.initSqlServer()

        menubar = self.menuBar()
        toolMenu = menubar.addMenu('Tools')
        searchAct = QAction("Search Case", self)
        searchAct.setShortcut('Ctrl+F')
        toolMenu.addAction(searchAct)
        searchAct.triggered.connect(self.searchCase)

        # Current engineer
        self.alias = "ruiwzhan"

        # Get the information of all customers that current engineer serves
        relatedCustomers = self.getRelatedCustomer(self.alias)

        # TODO: Add prompt bar
        # TODO: Let scrollWidget be the same size with MainWindow
        scrollWidget = QWidget()
        vbox = QVBoxLayout()

        for customer in relatedCustomers:
            vbox.addWidget(CustomerInfo(scrollWidget,
                                        relatedCases=self.getRelatedCase(customer[0]),
                                        name=customer[1],
                                        email=customer[2],
                                        surveyProbability=customer[3],
                                        company=customer[4],
                                        engineerAlias=self.alias))

        scrollWidget.setLayout(vbox)
        scrollArea = QScrollArea()
        scrollArea.setWidget(scrollWidget)
        self.setCentralWidget(scrollArea)

        self.resize(1550, 1000)
        self.setWindowTitle('Current Engineer: %s' % self.alias)


    def getRelatedCustomer(self, engineerAlias):
        print('Getting the information of all related customers')
        cur = self.sqlcon.cursor()

        sql = '''
        select distinct iCSHD_Customer.CustomerId, iCSHD_Customer.Name,
                        Email, SurveyProbability, Company
        from iCSHD_Case, iCSHD_Customer, iCSHD_Engineer
        where iCSHD_Case.CustomerId = iCSHD_Customer.CustomerId
          and iCSHD_Case.EngineerId = iCSHD_Engineer.EngineerId
          and iCSHD_Engineer.Alias = '%s'
        ''' % engineerAlias

        cur.execute(sql)
        print('Done')
        return cur.fetchall()

    def getRelatedCase(self, customerID):
        print('Getting all related cases')
        cur = self.sqlcon.cursor()

        sql = '''
        select CaseId, CaseAge, IdleTime, CustomerSentimental,
               ProductSupported, RecentCPE, IsResolved, Alias
        from iCSHD_Case, iCSHD_Customer, iCSHD_Engineer
        where iCSHD_Case.CustomerId = iCSHD_Customer.CustomerId
          and iCSHD_Customer.CustomerId = '%s'
          and iCSHD_Case.EngineerId = iCSHD_Engineer.EngineerId
        ''' % customerID

        cur.execute(sql)
        print('Done')
        return cur.fetchall()

    def initSqlServer(self):
        driver = 'SQL Server Native Client 11.0'
        server = 'shmsdsql.database.windows.net'
        user = 'msdadmin'
        password = 'PasSw0rd01'
        database = 'SDCasesTEST'
        self.sqlcon = pyodbc.connect(driver=driver,
                                     server=server,
                                     user=user,
                                     password=password,
                                     database=database)
    
    def searchCase(self):
        self.searchWin = SearchCaseWin(self.sqlcon)
        self.searchWin.show()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()