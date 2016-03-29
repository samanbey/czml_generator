# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ScaledModelsDialog
                                 A QGIS plugin
 CZML Generator
                             -------------------
        begin                : 2016-01-06
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Gede Mátyás
        email                : saman@map.elte.hu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 
 A dialog for creating maps full of scaled models with temporal animation
"""
from PyQt4 import QtGui, uic
from PyQt4.QtGui import QMessageBox, QFileDialog, QTableWidgetItem
from qgis.core import QGis, QgsCoordinateReferenceSystem, QgsCoordinateTransform
import os
import codecs
import math
import qgis
import sys
sys.modules['qgscolorbutton']=qgis.gui # a workaround to make setupUi know QGSColorButton

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'scaled_models.ui'))
    
class ScaledModelsDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ScaledModelsDialog, self).__init__(parent)
        self.setupUi(self)       
        # event handlers
        self.pbOK.clicked.connect(self.confirmOK) # OK Button
        self.pbCancel.clicked.connect(self.reject) # Cancel button
        self.pbBrowse.clicked.connect(self.browseFile) # open file dialog on clicking the browse button
        self.layerList.currentIndexChanged.connect(self.getAttrList) # get attribute list when a layer is selected
        self.pbAdd.clicked.connect(self.addAttr) # Add button
        self.pbRemove.clicked.connect(self.removeAttr) # Remove button
        self.twTimesAttrs.itemSelectionChanged.connect(self.enableDisableRemove) # Enable/disable remove button
        self.rbLin.toggled.connect(self.showMinMax) # update min/max when scale type is changed
        self.rbSqrt.toggled.connect(self.showMinMax) # update min/max when scale type is changed
        self.rbLog.toggled.connect(self.showMinMax) # update min/max when scale type is changed
        self.scaleFactor.textEdited.connect(self.showMinMax) # update min/max when scale factor is changed
                
    def browseFile(self):
        """Opens a file save as dialog to get the file name"""
        fn=QFileDialog.getSaveFileName(self,"Save file as...","","CZML flies (*.czml)")
        if (fn!=""):
            self.leFileName.setText(fn)
            
    def confirmOK(self):
        """Checks if a filename was specified before accepting the dialog"""
        if (self.leFileName.text()==''):
            QMessageBox.warning(self,"Warning","You must specify a filename!")
        else:
            self.accept()

    def getAttrList(self):
        """Loads the attribute names of the selected layer into attrList and strAttrList comboboxes"""
        # find layer by chosen name
        name=self.layerList.currentText()
        alayer=None
        for layer in self.iface.legendInterface().layers():
            if (layer.name()==name):
                alayer=layer
                break
        if alayer==None:
            return
        # get attr list
        al=[]
        self.strAttrList.clear()
        for fld in alayer.pendingFields():
            if (fld.typeName() in ['Integer','Real']): # TODO: add other numeric types
                al.append(fld.name()) # a mappable attribute if numeric
            elif (fld.typeName()=='String'):
                self.strAttrList.addItem(fld.name()) # an attribute can be used as name if it is a string
        # dictionaries for min/max attribute values
        self.amin={}
        self.amax={}
        # get and min/max attribute values
        for i,f in enumerate(alayer.getFeatures()):
            for a in al:
                if (f[a]):
                    if (not a in self.amin): # when it is the first feature, simply set the min/max valuse for the attrs
                        self.amin[a]=f[a]
                        self.amax[a]=f[a]
                    else: # otherwise change min/max if neccessary
                        if (f[a]<self.amin[a]):
                            self.amin[a]=f[a]
                        if (f[a]>self.amax[a]):
                            self.amax[a]=f[a]
        # set attr list
        self.attrList.clear()
        self.attrList.addItems(al)

    def showMinMax(self):
        """Displays the min/max values for the chosen attribute set"""
        # if nothing is selected, empty the text field and return
        if self.twTimesAttrs.rowCount()==0:
            self.lblRange.setText('')
            return
        # iterate over selected attributes and find absolute min and max
        self.minV=None
        self.maxV=None
        for row in range(self.twTimesAttrs.rowCount()):
            aName=self.twTimesAttrs.item(row,1).text()
            if self.minV==None or self.minV>self.amin[aName]:
                self.minV=self.amin[aName]
            if self.maxV==None or self.maxV<self.amax[aName]:
                self.maxV=self.amax[aName]
        # min/max values using currently selected scale function and factor
        if (self.rbLin.isChecked()):
            mn=self.minV
            mx=self.maxV
        elif (self.rbSqrt.isChecked()):
            if (self.minV<0 or self.maxV<0):
                # use sqrt only for non-negative values
                QMessageBox.warning(self,"Warning","Square root is not applicable for negative values!")
                self.rbLin.toggle()
                return
            mn=math.sqrt(self.minV)
            mx=math.sqrt(self.maxV)
        else:
            if (self.minV<=0 or self.maxV<=0):
                # use log only for positive values
                QMessageBox.warning(self,"Warning","Logarithm is not applicable for non-positive values!")
                self.rbLin.toggle()
                return
            mn=math.log(self.minV)
            mx=math.log(self.maxV)
        # failsafe string-float conversion
        try:
            sf=float(self.scaleFactor.text())
        except ValueError:
            sf=0
        # modify min/max by scale
        mn=mn*sf
        mx=mx*sf
        self.sf=sf
        self.lblRange.setText(str(mn)+" - "+str(mx))
    
    def addAttr(self):
        """Add selected attribute and time to time/attribute list"""
        # current attr name
        aname=self.attrList.currentText()
        if (aname==""):
            return
        time=self.dteTime.dateTime().toString(1)+"Z" # ISO datetime
        # add new row
        row=self.twTimesAttrs.rowCount()+1
        self.twTimesAttrs.setRowCount(row)
        # put datetime and attribute name to table
        self.twTimesAttrs.setItem(row-1,0,QTableWidgetItem(time,0))
        self.twTimesAttrs.setItem(row-1,1,QTableWidgetItem(aname,0))
        self.twTimesAttrs.sortItems(0);
        # update min/max information
        self.showMinMax()
    
    def enableDisableRemove(self):
        """Enable/disable remove button"""
        # Remove button is enabled if there is something selected
        self.pbRemove.setEnabled(len(self.twTimesAttrs.selectedItems())>0)

    def removeAttr(self):
        """Add selected attribute and time to time/attribute list"""
        # remove selected row
        self.twTimesAttrs.removeRow(self.twTimesAttrs.selectedItems()[0].row())
        # disable remove button
        self.pbRemove.setEnabled(False)
        # update min/max information
        self.showMinMax()
    
    def runThis(self,iface):
        """This is called when user clicks on "CZML Scaled models with time"

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # store iface
        self.iface=iface
        
        # clear lists
        self.layerList.clear()
        self.twTimesAttrs.clear()
        self.twTimesAttrs.setRowCount(0)
        
        # place to store legend settings
        self.legendSamples=None
        
        # collect currently loaded vector layers to "layerList" comboBox
        layers=iface.legendInterface().layers()
        ll=[] 
        for layer in layers:
            # check if it is a vector layer
            if (layer.type()==layer.VectorLayer):
                ll.append(layer.name())
        self.layerList.addItems(ll)
        # die if no suitable layers found
        if (len(ll)==0):
            QMessageBox.warning(self,"Error","No suitable layers found.")
            return
        # show dialog
        self.show()
        if self.exec_():
            # OK clicked, let's create the CZML file
            
            # get filename
            filename=self.leFileName.text()
            # set html legend filename
            htmlFn=filename+".legend.html"
            # find layer by chosen name
            name=self.layerList.currentText()
            for layer in layers:
                if (layer.name()==name):
                    alayer=layer
                    break
            # get chosen attribute name
            aName=self.attrList.currentText()
            # create projection transformer object
            crsDest = QgsCoordinateReferenceSystem(4326) # WGS 84
            crsSrc = alayer.crs()
            xform = QgsCoordinateTransform(crsSrc, crsDest)
            # find minimum/maximum time and attribute value
            self.minT=None
            self.maxT=None
            usedAttrs=[]
            for row in range(self.twTimesAttrs.rowCount()):
                t=self.twTimesAttrs.item(row,0).text()
                usedAttrs.append(self.twTimesAttrs.item(row,1).text())
                if self.minT==None or self.minT>t:
                    self.minT=t
                if self.maxT==None or self.maxT<t:
                    self.maxT=t
            self.minV=None
            self.maxV=None
            for aName in usedAttrs:
                if self.minV==None or self.minV>self.amin[aName]:
                    self.minV=self.amin[aName]
                if self.maxV==None or self.maxV<self.amax[aName]:
                    self.maxV=self.amax[aName]
            # get model url
            modelURL=self.leModelURL.text()
            # open output file
            ofile=codecs.open(filename,'w','utf-8')
            # leading [ and document packet
            ofile.write('[\n{"id":"document","version":"1.0"}')
            # iterate over feaures
            polyN=0
            for f in alayer.getFeatures():
                # calculate animated value (scale) if there is more than one timestamp
                scales=[]
                for row in range(self.twTimesAttrs.rowCount()):
                    aTime=self.twTimesAttrs.item(row,0).text()
                    aName=self.twTimesAttrs.item(row,1).text()
                    # calculate height
                    value=f[aName]
                    if (not value):
                        value=0
                    if (self.rbLin.isChecked()):
                        h=value
                    elif (self.rbSqrt.isChecked()):
                        h=math.sqrt(value)
                    else:
                        h=math.log(value)
                    h=h*self.sf
                    if (self.minT==self.maxT):
                        scales.append(str(h))
                    else:
                        scales.append('"'+aTime+'",'+str(h))
                # get centroid in WGS84
                cent=xform.transform(f.geometry().centroid().asPoint())
                coords=str(cent.x())+","+str(cent.y())+",0"
                # add element name if checked
                if (self.cbAddName.isChecked()):
                    nameString=',\n\t"name":"'+f[self.strAttrList.currentText()]+'"'
                else:
                    nameString=''
                # create availability and scale series only if more than 1 attribute
                if (self.minT==self.maxT):
                    availString=''
                    scaleString=scales[0]
                else:
                    availString=',"availability":"'+self.minT+'/'+self.maxT+'"'
                    scaleString='['+(','.join(scales))+']'
                packetString='{\n\t"id":"point'+str(polyN)+'"'+nameString+availString+',\n\t"position":{\n\t\t"cartographicDegrees":['+coords+']},\n\t"model":{\n\t\t"gltf":"'+modelURL+'",\n\t\t"scale":{"number":'+scaleString+'}}}'
                ofile.write(",\n"+packetString);
                polyN=polyN+1
            # trailing ] and close flie
            ofile.write('\n]')
            ofile.close()
            # farewell message
            msg="CZML file ("+filename+")"
            msg=msg+" successfully created."
            QMessageBox.information(self,"Information",msg)
            

