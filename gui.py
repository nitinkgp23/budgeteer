import sys
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

from PyQt5 import QtCore


class WidgetGallery(QDialog):
    def __init__(self, parent=None, transactions=None, categories=None, accounts=None):
        super(WidgetGallery, self).__init__(parent)

        self.groupBoxRows = []
        self.transactions = transactions
        self.categories = categories
        self.accounts = accounts
        for i, transaction in enumerate(self.transactions):
            self.createGroupBox(i, transaction)

        mainLayout = QGridLayout()
        for i, groupBox in enumerate(self.groupBoxRows):
            mainLayout.addWidget(groupBox, i+1, 0)

        pybutton = QPushButton('OK')
        pybutton.clicked.connect(self.clickMethod)
        mainLayout.addWidget(pybutton)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Budgeteer")
        QApplication.setStyle(QStyleFactory.create('macintosh'))

    def clickMethod(self):

        for i, groupBox in enumerate(self.groupBoxRows):
            if not groupBox.isChecked():
                self.transactions[i].isValid = False
                continue

            self.transactions[i].desc = groupBox.layout().itemAt(1).widget().text()
            self.transactions[i].category = str(groupBox.layout().itemAt(2).widget().currentText())
            self.transactions[i].account = str(groupBox.layout().itemAt(3).widget().currentText())
            self.transactions[i].amount = groupBox.layout().itemAt(4).widget().text()

        self.close()

    @staticmethod
    def convert_date(date):
        """
        Takes in date time object, returns string in format %m/%d/%Y

        becaue google sheets takes in this format
        """
        return date.strftime('%d-%B-%Y')

    def createGroupBox(self, i, transaction):

        groupBox = QGroupBox("Transaction {}".format(i+1))
        groupBox.setCheckable(True)
        groupBox.setChecked(True)
        date = QLineEdit(self.convert_date(transaction.date))
        desc = QLineEdit(transaction.desc)
        category = QComboBox()
        account = QComboBox()
        amount = QLineEdit(transaction.amount)

        date.setFixedWidth(100)
        desc.setFixedWidth(150)
        amount.setFixedWidth(50)

        category.addItems(self.categories)
        account.addItems(self.accounts)

        category.setCurrentIndex(category.findText(transaction.category, QtCore.Qt.MatchFixedString))
        account.setCurrentIndex(account.findText(transaction.account, QtCore.Qt.MatchFixedString))

        layout = QGridLayout()
        layout.addWidget(date, 0, 0)
        layout.addWidget(desc, 0, 1)
        layout.addWidget(category, 0, 2)
        layout.addWidget(account, 0, 3)
        layout.addWidget(amount, 0, 4)

        groupBox.setLayout(layout)

        self.groupBoxRows.append(groupBox)


class Driver(object):
    def __init__(self, transactions=None, categories=None, accounts=None):
        self.transactions = transactions
        self.categories = categories
        self.accounts = accounts
        self.take_user_input()

    def take_user_input(self):

        app = QApplication(sys.argv)
        gallery = WidgetGallery(transactions=self.transactions, categories=self.categories, accounts=self.accounts)
        gallery.show()
        self.transactions = gallery.transactions
        app.exec_()


def update_transactions_via_gui(transactions, categories, accounts):
    d = Driver(transactions=transactions, categories=categories, accounts=accounts)
    return d.transactions
