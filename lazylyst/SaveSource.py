# Author: Andrew.M.G.Reynen
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from ChangeSource import Ui_CsDialog
import os

# Saved sources class, for reading in old (or adding new) archive/pick/station information
class SaveSource(object):
    def __init__(self,tag=None,archDir=None,
                 pickDir=None,staFile=None):
        self.tag=tag
        self.archDir=archDir
        self.pickDir=pickDir
        self.staFile=staFile
    
    # A check to see if all files can be read
    def pathExist(self):
        allPathsExist=True
        for txt,path in [['archive directory',self.archDir],
                         ['pick directory',self.pickDir],
                         ['station file',self.staFile]]:
            if not os.path.exists(path):
                print('The '+txt+' does not exist at: '+path)
                allPathsExist=False
        return allPathsExist

# Change source dialog
class CsDialog(QtWidgets.QDialog, Ui_CsDialog):
    def __init__(self,hotVar,savedSources,parent=None):
        QtWidgets.QDialog.__init__(self,parent)
        self.setupUi(self)
        self.hotVar=hotVar
        self.saveSource=savedSources
        # Give the dialog some functionaly
        self.setFunctionality()
        # Load in the text of the current source
        self.fillDialog()
        # Show the list of previous saved sources
        self.csSaveSourceList.addItems(sorted([key for key in self.saveSource.keys()]))
        
    # Set up some functionality to the configuration dialog
    def setFunctionality(self):
        self.csSaveSourceList.itemDoubleClicked.connect(self.loadSaveSource)
        self.csSaveSourceList.keyPressedSignal.connect(self.delSaveSource)
        self.csSaveSourceButton.clicked.connect(self.addSavedSource)
        # Allow double click on paths to open up dialogs to extract path names
        self.csArchiveLineEdit.doubleClicked.connect(lambda: self.getPathName('arch'))
        self.csPickLineEdit.doubleClicked.connect(lambda: self.getPathName('pick'))
        self.csStationLineEdit.doubleClicked.connect(self.getFileName)
        
    # Fill the dialog with info relating current source
    def fillDialog(self):
        # Fill line edits with current source
        self.csTagLineEdit.setText(self.hotVar['sourceTag'].val)
        self.csArchiveLineEdit.setText(self.hotVar['archDir'].val)
        self.csPickLineEdit.setText(self.hotVar['pickDir'].val)
        self.csStationLineEdit.setText(self.hotVar['staFile'].val)
        
    # Put the saved source into the saved source list and dictionary
    def loadSaveSource(self):
        source=self.saveSource[self.csSaveSourceList.currentItem().text()]
        self.csTagLineEdit.setText(source.tag)
        self.csArchiveLineEdit.setText(source.archDir)
        self.csPickLineEdit.setText(source.pickDir)
        self.csStationLineEdit.setText(source.staFile)
    
    # Delete the selected saved source
    def delSaveSource(self):
        if self.csSaveSourceList.key != Qt.Key_Delete or self.csSaveSourceList.currentItem()==None:
            return
        tag=self.csSaveSourceList.currentItem().text()
        # Remove from the saved sources dictionary...
        self.saveSource.pop(tag)
        # ...and the gui list
        self.csSaveSourceList.takeItem(self.csSaveSourceList.currentRow())
    
    # Using the current text
    def addSavedSource(self):
        source=self.curSource()
        for text in [source.tag,source.archDir,source.pickDir,source.staFile]:
            if text.replace(' ','')=='':
                print('Fill in the source information to save')
                return
        # Add this to the saved sources list
        if source.tag not in [key for key in self.saveSource.keys()]:
            self.csSaveSourceList.addItem(source.tag)
        self.saveSource[source.tag]=source
        
    # Function to open a dialog and get the path name
    def getPathName(self,thisLineEdit):
        # Check which line was clicked
        if thisLineEdit=='arch':
            line=self.csArchiveLineEdit
        else:
            line=self.csPickLineEdit
        # If the value is already set, start from there
        if os.path.isdir(line.text()):
            startFolder=line.text()
        else:
            startFolder=os.path.dirname(os.path.realpath(__file__))
        name=str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder",startFolder))
        name=name.replace('\\','/')
        # If a folder was selected, update the line edit
        if name!='' and os.path.isdir(name):
            line.setText(name)
            
    # Function to open a dialog and get the file name
    def getFileName(self):
        # Start the dialog from the previously selected file (if it exists)
        if os.path.isfile(self.csStationLineEdit.text()):
            startFolder=os.path.dirname(os.path.realpath(self.csStationLineEdit.text()))
        else:
            startFolder=os.path.dirname(os.path.realpath(__file__))
        name=str(QtWidgets.QFileDialog.getOpenFileName(self, "Select File",startFolder)[0])
        # If a folder was selected, update the line edit
        if name!='' and os.path.isfile(name):
            self.csStationLineEdit.setText(name)
        
    # Create a source object from the line edit
    def curSource(self):
        source=SaveSource(tag=self.csTagLineEdit.text(),
                          archDir=self.csArchiveLineEdit.text(),
                          pickDir=self.csPickLineEdit.text(),
                          staFile=self.csStationLineEdit.text())
        return source
        
    # Upon close, return the source currently in the line edits
    def returnSource(self):
        return self.curSource()