# -*- coding: UTF-8 -*-

'''
@Author: t-zhel
@Date: 2019-07-09 13:48:38
@LastEditor: t-zhel
@LastEditTime: 2019-07-13 16:57:08
@Description: Implement the GUI of iCSHD
'''

import sys
import pyodbc
import numpy as np
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import (QWidget, QPushButton, QScrollArea, QTextEdit, QLabel,
                             QHBoxLayout, QVBoxLayout, QMainWindow, QApplication)

class CaseButton(QPushButton):
    def __init__(self, parent=None, **kwargs):
        super().__init__(kwargs.get('buttonText', ""), parent)

        self.SLA = kwargs.get('SLA', 'default SLA')
        self.FDR = kwargs.get('FDR', 'default FDR')
        self.labor = kwargs.get('labor', 123)
        self.owner = kwargs.get('owner', "")
        self.caseAge = kwargs.get('caseAge', 0)
        self.idleTime = kwargs.get('idleTime', 0)
        self.recentCPE = kwargs.get('recentCPE', 0)
        self.isResolved = kwargs.get('isResolved', 0)
        self.ongoingCases = kwargs.get('ongoingCases', 3)
        self.estimatedScore = kwargs.get('estimatedScore', 5)
        self.productSupported = kwargs.get('productSupported', "")
        self.customerSentimental = kwargs.get('customerSentimental', 0)

class CustomerInfo(QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)

        TAM = kwargs.get('TAM', "default TAM")
        name = kwargs.get('name', "")
        email = kwargs.get('email', "")
        company = kwargs.get('company', "")
        relatedCases = kwargs.get('relatedCases', [])
        engineerAlias = kwargs.get('engineerAlias', "")
        estimatedScore = kwargs.get('estimatedScore', 5)
        surveyProbability = kwargs.get('surveyProbability', 0)

        # Initialize parameters
        custBtnWidth  = 400
        custBtnHeight = 200
        caseBtnWidth  = 200
        caseBtnHeight = 50
        suggestEditorWidth  = 400
        suggestEditorHeight = 200
        commentEditorWidth  = 400
        commentEditorHeight = 200

        hbox = QHBoxLayout()
        vbox = QVBoxLayout()

        # TODO: Customize the shape of the button
        # TODO: Show long company name
        # Cutomer button
        buttonText = ("Customer: %s\nEmail: %s\nCompany: %s\nTAM: %s\n"
                    + "Survey Probability: %s%%\nEstimated score: %s") \
                    % (name, email, company, TAM, surveyProbability, estimatedScore)
        custBtn = QPushButton(buttonText, self)
        custBtn.setFixedSize(custBtnWidth, custBtnHeight)
        hbox.addWidget(custBtn)

        # Case buttons
        for case in relatedCases:
            # Take the first five characters of CaseID as the name of the CaseButton
            caseBtn = CaseButton(self,
                                 buttonText="CaseID: %s" % case[0][0:5],
                                 caseAge=case[1],
                                 idleTime=case[2],
                                 customerSentimental=case[3],
                                 productSupported=case[4],
                                 recentCPE=case[5],
                                 isResolved=case[6],
                                 owner=case[7])

            # if the case hase been resolved
            if caseBtn.isResolved == 1:
                # if the case belong to current engineer
                if caseBtn.owner == engineerAlias:
                    caseBtn.setStyleSheet("color: green; border: 2px groove blue;")
                else:
                    caseBtn.setStyleSheet("color: green")
            else:
                if caseBtn.owner == engineerAlias:
                    caseBtn.setStyleSheet("color: red; border: 2px groove blue;")
                else:
                    caseBtn.setStyleSheet("color: red")

            caseBtn.setToolTip(case[0])
            caseBtn.setFixedSize(caseBtnWidth, caseBtnHeight)
            caseBtn.clicked.connect(self.showGraph)
            vbox.addWidget(caseBtn)
        hbox.addLayout(vbox)

        # Suggest editor
        suggestEditor = QTextEdit(self)
        suggestEditor.setPlaceholderText("Enter your suggestion here")
        suggestEditor.setFixedSize(suggestEditorWidth, suggestEditorHeight)
        hbox.addWidget(suggestEditor)

        # Comment editor
        commentEditor = QTextEdit(self)
        commentEditor.setPlaceholderText("Enter your comment here")
        commentEditor.setFixedSize(commentEditorWidth, commentEditorHeight)
        hbox.addWidget(commentEditor)

        self.setLayout(hbox)

    def showGraph(self):
        # TODO: why must import pyplot here
        import matplotlib.pyplot as plt

        caseBtn = self.sender()

        # Turn on the interactive mode. plt.show() is not needed in interactive mode.
        plt.ion()

        data = np.array([caseBtn.caseAge, caseBtn.idleTime, caseBtn.labor, caseBtn.customerSentimental,
                         caseBtn.recentCPE, caseBtn.ongoingCases])
        labels = [str(i) for i in data]
        data = np.concatenate((data, [data[0]]))
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))

        fig = plt.figure(figsize=(18, 6))

        ax1 = fig.add_subplot(121, polar=True)
        ax1.plot(angles, data, 'ro-', linewidth=2)
        ax1.set_thetagrids(angles * 180 / np.pi, labels)
        ax1.set_title("Customer Analysis", va='bottom')
        ax1.grid(True)

        # TODO: Hidden the row label
        ax2 = fig.add_subplot(122)
        plt.axis("off")
        colLabels = ['Information']
        rowLabels = ['Owner','Product','SLA', 'FDR', 'IsResolved', 'EstimatedScore']
        cellText = [[caseBtn.owner], [caseBtn.productSupported], [caseBtn.SLA],
                    [caseBtn.FDR], [caseBtn.isResolved], [caseBtn.estimatedScore]]
        ax2.table(cellText=cellText, rowLabels=rowLabels,
                  colLabels=colLabels, cellLoc='center', loc='center')

        # Turn off the interactive mode
        plt.ioff()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the connection to SQL Server
        self.initSqlServer()

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
        cur = self.conn.cursor()

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
        cur = self.conn.cursor()

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
        self.conn = pyodbc.connect(driver=driver,
                                   server=server,
                                   user=user,
                                   password=password,
                                   database=database)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
