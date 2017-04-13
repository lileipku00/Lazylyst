# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(839, 573)
        self.mainLayout = QtGui.QWidget(MainWindow)
        self.mainLayout.setEnabled(True)
        self.mainLayout.setObjectName(_fromUtf8("mainLayout"))
        self.verticalLayout = QtGui.QVBoxLayout(self.mainLayout)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.traceSplitter = QtGui.QSplitter(self.mainLayout)
        self.traceSplitter.setFrameShape(QtGui.QFrame.NoFrame)
        self.traceSplitter.setLineWidth(0)
        self.traceSplitter.setOrientation(QtCore.Qt.Vertical)
        self.traceSplitter.setHandleWidth(1)
        self.traceSplitter.setChildrenCollapsible(True)
        self.traceSplitter.setObjectName(_fromUtf8("traceSplitter"))
        self.verticalLayoutWidget = QtGui.QWidget(self.traceSplitter)
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.timeImageLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.timeImageLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.timeImageLayout.setSpacing(1)
        self.timeImageLayout.setObjectName(_fromUtf8("timeImageLayout"))
        self.timeWidget = TimeWidget(self.verticalLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timeWidget.sizePolicy().hasHeightForWidth())
        self.timeWidget.setSizePolicy(sizePolicy)
        self.timeWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.timeWidget.setMaximumSize(QtCore.QSize(16777215, 50))
        self.timeWidget.setBaseSize(QtCore.QSize(0, 0))
        self.timeWidget.setFrameShape(QtGui.QFrame.NoFrame)
        self.timeWidget.setObjectName(_fromUtf8("timeWidget"))
        self.timeImageLayout.addWidget(self.timeWidget)
        self.imageWidget = ImageWidget(self.verticalLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageWidget.sizePolicy().hasHeightForWidth())
        self.imageWidget.setSizePolicy(sizePolicy)
        self.imageWidget.setMinimumSize(QtCore.QSize(0, 1))
        self.imageWidget.setObjectName(_fromUtf8("imageWidget"))
        self.timeImageLayout.addWidget(self.imageWidget)
        self.verticalLayoutWidget_2 = QtGui.QWidget(self.traceSplitter)
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.traceLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.traceLayout.setSpacing(1)
        self.traceLayout.setObjectName(_fromUtf8("traceLayout"))
        self.verticalLayout.addWidget(self.traceSplitter)
        MainWindow.setCentralWidget(self.mainLayout)
        self.textOutDock = QtGui.QDockWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textOutDock.sizePolicy().hasHeightForWidth())
        self.textOutDock.setSizePolicy(sizePolicy)
        self.textOutDock.setMinimumSize(QtCore.QSize(290, 179))
        self.textOutDock.setMaximumSize(QtCore.QSize(524287, 52487))
        self.textOutDock.setFeatures(QtGui.QDockWidget.DockWidgetFloatable|QtGui.QDockWidget.DockWidgetMovable)
        self.textOutDock.setObjectName(_fromUtf8("textOutDock"))
        self.textOutLayout = QtGui.QWidget()
        self.textOutLayout.setObjectName(_fromUtf8("textOutLayout"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.textOutLayout)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.textOutBrowser = QtGui.QTextBrowser(self.textOutLayout)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textOutBrowser.sizePolicy().hasHeightForWidth())
        self.textOutBrowser.setSizePolicy(sizePolicy)
        self.textOutBrowser.setObjectName(_fromUtf8("textOutBrowser"))
        self.verticalLayout_2.addWidget(self.textOutBrowser)
        self.textOutGridLayout = QtGui.QGridLayout()
        self.textOutGridLayout.setObjectName(_fromUtf8("textOutGridLayout"))
        self.strollingLabel = QtGui.QLabel(self.textOutLayout)
        self.strollingLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.strollingLabel.setObjectName(_fromUtf8("strollingLabel"))
        self.textOutGridLayout.addWidget(self.strollingLabel, 0, 0, 1, 1)
        self.strollComboBox = QtGui.QComboBox(self.textOutLayout)
        self.strollComboBox.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.strollComboBox.setObjectName(_fromUtf8("strollComboBox"))
        self.textOutGridLayout.addWidget(self.strollComboBox, 1, 0, 1, 1)
        self.schemingLabel = QtGui.QLabel(self.textOutLayout)
        self.schemingLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.schemingLabel.setObjectName(_fromUtf8("schemingLabel"))
        self.textOutGridLayout.addWidget(self.schemingLabel, 0, 1, 1, 1)
        self.schemeComboBox = QtGui.QComboBox(self.textOutLayout)
        self.schemeComboBox.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.schemeComboBox.setObjectName(_fromUtf8("schemeComboBox"))
        self.textOutGridLayout.addWidget(self.schemeComboBox, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.textOutGridLayout)
        self.textOutDock.setWidget(self.textOutLayout)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.textOutDock)
        self.archiveDock = QtGui.QDockWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.archiveDock.sizePolicy().hasHeightForWidth())
        self.archiveDock.setSizePolicy(sizePolicy)
        self.archiveDock.setMinimumSize(QtCore.QSize(373, 125))
        self.archiveDock.setMaximumSize(QtCore.QSize(524287, 150))
        self.archiveDock.setFeatures(QtGui.QDockWidget.DockWidgetFloatable|QtGui.QDockWidget.DockWidgetMovable)
        self.archiveDock.setObjectName(_fromUtf8("archiveDock"))
        self.archiveLayout = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.archiveLayout.sizePolicy().hasHeightForWidth())
        self.archiveLayout.setSizePolicy(sizePolicy)
        self.archiveLayout.setMaximumSize(QtCore.QSize(16777215, 125))
        self.archiveLayout.setObjectName(_fromUtf8("archiveLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.archiveLayout)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setSpacing(1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.archiveLeftLayout = QtGui.QVBoxLayout()
        self.archiveLeftLayout.setObjectName(_fromUtf8("archiveLeftLayout"))
        self.archiveList = ArchiveListWidget(self.archiveLayout)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.archiveList.sizePolicy().hasHeightForWidth())
        self.archiveList.setSizePolicy(sizePolicy)
        self.archiveList.setMinimumSize(QtCore.QSize(290, 80))
        self.archiveList.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.archiveList.setObjectName(_fromUtf8("archiveList"))
        self.archiveLeftLayout.addWidget(self.archiveList)
        self.horizontalLayout.addLayout(self.archiveLeftLayout)
        self.archiveRightLayout = QtGui.QVBoxLayout()
        self.archiveRightLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.archiveRightLayout.setSpacing(1)
        self.archiveRightLayout.setObjectName(_fromUtf8("archiveRightLayout"))
        self.archiveSpan = ArchiveSpanWidget(self.archiveLayout)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.archiveSpan.sizePolicy().hasHeightForWidth())
        self.archiveSpan.setSizePolicy(sizePolicy)
        self.archiveSpan.setMinimumSize(QtCore.QSize(0, 50))
        self.archiveSpan.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.archiveSpan.setObjectName(_fromUtf8("archiveSpan"))
        self.archiveRightLayout.addWidget(self.archiveSpan)
        self.archiveEvent = ArchiveEventWidget(self.archiveLayout)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.archiveEvent.sizePolicy().hasHeightForWidth())
        self.archiveEvent.setSizePolicy(sizePolicy)
        self.archiveEvent.setMinimumSize(QtCore.QSize(0, 30))
        self.archiveEvent.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.archiveEvent.setObjectName(_fromUtf8("archiveEvent"))
        self.archiveRightLayout.addWidget(self.archiveEvent)
        self.archiveTextLayout = QtGui.QHBoxLayout()
        self.archiveTextLayout.setSpacing(0)
        self.archiveTextLayout.setObjectName(_fromUtf8("archiveTextLayout"))
        self.archiveSpanT0Label = DblClickLabelWidget(self.archiveLayout)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.archiveSpanT0Label.sizePolicy().hasHeightForWidth())
        self.archiveSpanT0Label.setSizePolicy(sizePolicy)
        self.archiveSpanT0Label.setMinimumSize(QtCore.QSize(0, 0))
        self.archiveSpanT0Label.setMaximumSize(QtCore.QSize(16777215, 14))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.archiveSpanT0Label.setFont(font)
        self.archiveSpanT0Label.setText(_fromUtf8(""))
        self.archiveSpanT0Label.setObjectName(_fromUtf8("archiveSpanT0Label"))
        self.archiveTextLayout.addWidget(self.archiveSpanT0Label)
        self.archiveSpanT1Label = DblClickLabelWidget(self.archiveLayout)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.archiveSpanT1Label.sizePolicy().hasHeightForWidth())
        self.archiveSpanT1Label.setSizePolicy(sizePolicy)
        self.archiveSpanT1Label.setMinimumSize(QtCore.QSize(0, 0))
        self.archiveSpanT1Label.setMaximumSize(QtCore.QSize(16777215, 14))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.archiveSpanT1Label.setFont(font)
        self.archiveSpanT1Label.setText(_fromUtf8(""))
        self.archiveSpanT1Label.setObjectName(_fromUtf8("archiveSpanT1Label"))
        self.archiveTextLayout.addWidget(self.archiveSpanT1Label)
        spacerItem = QtGui.QSpacerItem(0, 14, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.archiveTextLayout.addItem(spacerItem)
        self.archiveRightLayout.addLayout(self.archiveTextLayout)
        self.archiveRightLayout.setStretch(0, 8)
        self.archiveRightLayout.setStretch(1, 4)
        self.archiveRightLayout.setStretch(2, 1)
        self.horizontalLayout.addLayout(self.archiveRightLayout)
        self.archiveDock.setWidget(self.archiveLayout)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(4), self.archiveDock)
        self.mapDock = QtGui.QDockWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mapDock.sizePolicy().hasHeightForWidth())
        self.mapDock.setSizePolicy(sizePolicy)
        self.mapDock.setMinimumSize(QtCore.QSize(290, 125))
        self.mapDock.setMaximumSize(QtCore.QSize(524287, 52487))
        self.mapDock.setFeatures(QtGui.QDockWidget.DockWidgetFloatable|QtGui.QDockWidget.DockWidgetMovable)
        self.mapDock.setObjectName(_fromUtf8("mapDock"))
        self.mayLayout = QtGui.QWidget()
        self.mayLayout.setObjectName(_fromUtf8("mayLayout"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.mayLayout)
        self.verticalLayout_6.setMargin(0)
        self.verticalLayout_6.setSpacing(1)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.mapWidget = MapWidget(self.mayLayout)
        self.mapWidget.setObjectName(_fromUtf8("mapWidget"))
        self.verticalLayout_6.addWidget(self.mapWidget)
        self.mapDock.setWidget(self.mayLayout)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.mapDock)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Lazylyst", None))
        self.textOutDock.setWindowTitle(_translate("MainWindow", "Standard Out", None))
        self.strollingLabel.setText(_translate("MainWindow", "Strolling (0)", None))
        self.schemingLabel.setText(_translate("MainWindow", "Scheming (0)", None))
        self.archiveDock.setWindowTitle(_translate("MainWindow", "Archive", None))
        self.mapDock.setWindowTitle(_translate("MainWindow", "Map View", None))

from CustomWidgets import ArchiveEventWidget, ArchiveListWidget, ArchiveSpanWidget, DblClickLabelWidget, ImageWidget, MapWidget, TimeWidget
