# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ConnectorLinesDialog
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
 
 A dialog for creating raised connector lines
"""
from PyQt4 import QtGui, uic
from PyQt4.QtGui import QMessageBox, QFileDialog, QTableWidgetItem
from qgis.core import QGis, QgsCoordinateReferenceSystem, QgsCoordinateTransform
import os
import codecs
import math
from math import *
import qgis
import sys
sys.modules['qgscolorbutton']=qgis.gui # a workaround to make setupUi know QGSColorButton

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'connector_lines.ui'))
    
class ConnectorLinesDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ConnectorLinesDialog, self).__init__(parent)
        self.setupUi(self)       
        # event handlers
        self.pbOK.clicked.connect(self.confirmOK) # OK Button
        self.pbCancel.clicked.connect(self.reject) # Cancel button
        self.pbBrowse.clicked.connect(self.browseFile) # open file dialog on clicking the browse button
        self.layerList.currentIndexChanged.connect(self.getAttrList) # get attribute list when a layer is selected
        #self.pbAdd.clicked.connect(self.addAttr) # Add button
        #self.pbRemove.clicked.connect(self.removeAttr) # Remove button
        #self.twTimesAttrs.itemSelectionChanged.connect(self.enableDisableRemove) # Enable/disable remove button
        #self.rbLin.toggled.connect(self.showMinMax) # update min/max when scale type is changed
        #self.rbSqrt.toggled.connect(self.showMinMax) # update min/max when scale type is changed
        #self.rbLog.toggled.connect(self.showMinMax) # update min/max when scale type is changed
        #self.scaleFactor.textEdited.connect(self.showMinMax) # update min/max when scale factor is changed
                
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
        self.strAttrList.clear()
        for fld in alayer.pendingFields():
            if (fld.typeName()=='String'):
                self.strAttrList.addItem(fld.name()) # an attribute can be used as name if it is a string

    
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
        """This is called when user clicks on "CZML Raised Connector Lines"

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # store iface
        self.iface=iface
        
        # clear lists
        self.layerList.clear()
        #self.twTimesAttrs.clear()
        #self.twTimesAttrs.setRowCount(0)
        
        # place to store legend settings
        self.legendSamples=None
        
        # collect currently loaded vector layers to "layerList" comboBox
        layers=iface.legendInterface().layers()
        ll=[] 
        for layer in layers:
            # check if it is a vector layer
            if (layer.type()==layer.VectorLayer and layer.geometryType()==QGis.Line):
                ll.append(layer.name())
        self.layerList.addItems(ll)
        # die if no suitable layers found
        if (len(ll)==0):
            QMessageBox.warning(self,"Error","No suitable layers found.\n(Need vector layers With lines)")
            return
        # show dialog
        self.show()
        if self.exec_():
            # OK clicked, let's create the CZML file
            # get filename
            filename=self.leFileName.text()
            # set html legend filename
            #htmlFn=filename+".legend.html"
            # find layer by chosen name
            name=self.layerList.currentText()
            for layer in layers:
                if (layer.name()==name):
                    alayer=layer
                    break
            # get chosen attribute name
            #aName=self.attrList.currentText()
            
            # TODO: get these values from dialog
            segments=20;
            RAD=pi/180;
            # create projection transformer object
            crsDest = QgsCoordinateReferenceSystem(4326) # WGS 84
            crsSrc = alayer.crs()
            xform = QgsCoordinateTransform(crsSrc, crsDest)
            # open output file
            ofile=codecs.open(filename,'w','utf-8')
            # leading [ and document packet
            ofile.write('[\n{"id":"document","version":"1.0"}')
            # get renderer (todo: get line color from renderer)
            # rend=alayer.rendererV2()
            # get symbol color for current polyline
            symColor=self.cb.color()
            symR=symColor.red()
            symG=symColor.green()
            symB=symColor.blue()
            symA=symColor.alpha()
            rgba=str(symR)+','+str(symG)+','+str(symB)+','+str(symA)
            # iterate over feaures
            lineN=0
            for f in alayer.getFeatures():
                px=-1000
                py=-1000
                availString="" # TODO: later add availability...
                if (self.cbAddName.isChecked()):
                    nameString=',\n\t"name":"'+f[self.strAttrList.currentText()]+'"'
                else:
                    nameString=''
                for p in f.geometry().asPolyline():
                    p1=xform.transform(p)
                    x=p1.x()
                    y=p1.y()
                    if (px>-1000):
                        # create line segment
                        # calculate distance and azimuth
                        d=acos(sin(py*RAD)*sin(y*RAD)+cos(py*RAD)*cos(y*RAD)*cos((x-px)*RAD))/RAD
                        cosaz=(sin(y*RAD)-sin(py*RAD)*cos(d*RAD))/cos(py*RAD)/sin(d*RAD)
                        if (cosaz>1):
                            cosaz=1
                        if (cosaz<-1):
                            cosaz=1
                        az=acos(cosaz)/RAD
                        if (sin((x-px)*RAD)<0):
                            az=-az
                        maxh=d*40000
                        # create arc segments
                        coords=""
                        for i in range(0,segments+1):
                            gamma=i*pi/segments
                            dd=d*(.5-.5*cos(gamma))
                            h=sin(gamma)*maxh
                            lat2=asin(sin(py*RAD)*cos(dd*RAD)+cos(py*RAD)*sin(dd*RAD)*cos((az)*RAD))/RAD
                            cosl2=(cos(dd*RAD)-sin(py*RAD)*sin(lat2*RAD))/cos(py*RAD)/cos(lat2*RAD)
                            if (cosl2>1):
                                cosl2=1
                            if (cosl2<-1):
                                cosl2=-1
                            lon2=acos(cosl2)/RAD
                            if (sin(az*RAD)<0):
                                lon2=-lon2
                            lon2=lon2+px
                            if (coords!=""):
                                coords=coords+","
                            coords=coords+'\n\t\t\t\t'+str(lon2)+","+str(lat2)+","+str(h)
                        packetString='{\n\t"id":"line'+str(lineN)+'"'+nameString+availString+',\n\t"polyline":{\n\t\t"material":{"solidColor":{"color":{"rgba":['+rgba+']}}},\n\t\t"positions":{\n\t\t\t"cartographicDegrees":['+coords+']},\n\t\t"width":5}}'
                        ofile.write(",\n"+packetString);
                        lineN=lineN+1
                    else:
                        # this is the first node of the polyline
                        px=x
                        py=y                    
            # trailing ] and close flie
            ofile.write('\n]')
            ofile.close()
            # farewell message
            msg="CZML file ("+filename+")"
            msg=msg+" successfully created."
            QMessageBox.information(self,"Information",msg)
            

