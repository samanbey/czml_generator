# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PrismMapDialog
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
 
 A dialog for creating prism maps
"""
from PyQt4 import QtGui, uic
from PyQt4.QtGui import QMessageBox, QFileDialog
from qgis.core import QGis, QgsCoordinateReferenceSystem, QgsCoordinateTransform
import os
import codecs
import math
import qgis
import sys
sys.modules['qgscolorbutton']=qgis.gui # a workaround to make setupUi know QGSColorButton

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'prism_map.ui'))
    
class PrismMapDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(PrismMapDialog, self).__init__(parent)
        self.setupUi(self)
        
        # event handlers
        self.pbOK.clicked.connect(self.confirmOK) # OK Button
        self.pbCancel.clicked.connect(self.reject) # Cancel button
        self.pbBrowse.clicked.connect(self.browseFile) # open file dialog on clicking the browse button
        self.layerList.currentIndexChanged.connect(self.getAttrList) # get attribute list when a layer is selected
        self.attrList.currentIndexChanged.connect(self.attrChanged) # set legend attribute name when another attribute is selected and call showMinMax
        self.rbLin.toggled.connect(self.showMinMax) # update min/max when scale type is changed
        self.rbSqrt.toggled.connect(self.showMinMax) # update min/max when scale type is changed
        self.rbLog.toggled.connect(self.showMinMax) # update min/max when scale type is changed
        self.scaleFactor.textEdited.connect(self.showMinMax) # update min/max when scale factor is changed
        self.pbLegendSettings.clicked.connect(self.legendSettings) # Legend settings button
        
    def legendSettings(self):
        """Opens legend settings dialog"""
        # TODO: checking is there is a numeric attribute selected

        # current attr name
        aname=self.attrList.currentText()
        # dictionary with settings
        ls={}
        ls['minV']=self.amin[aname]
        ls['maxV']=self.amax[aname]
        ls['minColor']=self.cb1.color()
        ls['maxColor']=self.cb2.color()
        ls['attrName']=self.leLegendAttrName.text()
        ls['samples']=self.legendSamples
        l=self.RLDlg.runThis(ls)
        if l!=None:
            self.legendSamples=l
    
    def attrChanged(self):
        """Sets legend attribute name when another attribute is selected and calls showMinMax"""
        self.leLegendAttrName.setText(self.attrList.currentText())
        self.showMinMax()
    
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
        # update min/max information
        self.showMinMax()
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
                if (i==0): # when it is the first feature, simply set the min/max valuse for the attrs
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
        """Displays the min/max values for the chosen attribute"""
        # current attr name
        aname=self.attrList.currentText()
        if (aname==""):
            return
        # min/max values using currently selected scale function and factor
        if (self.rbLin.isChecked()):
            mn=self.amin[aname]
            mx=self.amax[aname]
        elif (self.rbSqrt.isChecked()):
            if (self.amin[aname]<0 or self.amax[aname]<0):
                # use sqrt only for non-negative values
                QMessageBox.warning(self,"Warning","Square root is not applicable for negative values!")
                self.rbLin.toggle()
                return
            mn=math.sqrt(self.amin[aname])
            mx=math.sqrt(self.amax[aname])
        else:
            if (self.amin[aname]<=0 or self.amax[aname]<=0):
                # use log only for positive values
                QMessageBox.warning(self,"Warning","Logarithm is not applicable for non-positive values!")
                self.rbLin.toggle()
                return
            mn=math.log(self.amin[aname])
            mx=math.log(self.amax[aname])
        try:
            sf=float(self.scaleFactor.text())
        except ValueError:
            sf=0
        mn=mn*sf
        mx=mx*sf
        self.sf=sf
        self.lblRange.setText(str(mn)+" - "+str(mx))
                
    def runThis(self,iface):
        """This is called when user clicks on "CZML Prism Map"

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # store iface
        self.iface=iface
        
        # place to store legend settings
        self.legendSamples=None
        
        # collect currently loaded polygon layers to "layerList" comboBox
        layers=iface.legendInterface().layers()
        ll=[] 
        for layer in layers:
            if (layer.type()==layer.VectorLayer and layer.geometryType()==QGis.Polygon):
                ll.append(layer.name())
        self.layerList.clear()
        self.layerList.addItems(ll)
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
            # get colors
            c1=self.cb1.color()
            c2=self.cb2.color()
            R1=c1.red()
            G1=c1.green()
            B1=c1.blue()
            A1=c1.alpha()
            dR=c2.red()-R1
            dG=c2.green()-G1
            dB=c2.blue()-B1
            dA=c2.alpha()-A1
            # open output file
            ofile=codecs.open(filename,'w','utf-8')
            # leading [ and document packet
            ofile.write('[\n{"id":"document","version":"1.0"}')
            # iterate over feaures
            polyN=0
            for f in alayer.getFeatures():
                # calculate height
                if (self.rbLin.isChecked()):
                    h=f[aName]
                elif (self.rbSqrt.isChecked()):
                    h=math.sqrt(f[aName])
                else:
                    h=math.log(f[aName])
                h=h*self.sf
                # calculate color
                rh=1.0*(f[aName]-self.amin[aName])/(self.amax[aName]-self.amin[aName])
                R=R1+dR*rh
                G=G1+dG*rh
                B=B1+dB*rh
                A=A1+dA*rh
                rgba=str(R)+','+str(G)+','+str(B)+','+str(A)
                coords=""
                # iterate over rings of the polygon
                for ring in f.geometry().asPolygon():
                    for p in ring:
                        p1=xform.transform(p)
                        if (coords!=""):
                            coords=coords+","
                        coords=coords+'\n\t\t\t\t'+str(p1.x())+","+str(p1.y())+",0"
                # add element name if checked
                if (self.cbAddName.isChecked()):
                    nameString=',\n\t"name":"'+f[self.strAttrList.currentText()]+'"'
                else:
                    nameString=''
                packetString='{\n\t"id":"poly'+str(polyN)+'",\n\t"description":"'+aName+': '+str(f[aName])+'"'+nameString+',\n\t"polygon":{\n\t\t"material":{"solidColor":{"color":{"rgba":['+rgba+']}}},\n\t\t"positions":{\n\t\t\t"cartographicDegrees":['+coords+']},\n\t\t"extrudedHeight":{"number":'+str(h)+'}}}'
                ofile.write(",\n"+packetString);
                polyN=polyN+1
            # trailing ] and close flie
            ofile.write('\n]')
            ofile.close()
            # create legend if checked
            if (self.cbCreateLegend.isChecked()):
                # open html legend file
                hfile=codecs.open(htmlFn,'w','utf-8')
                hfile.write('<style>\n.czmlLegendSample { width: 40px; height: 20px; border-radius:3px; border: solid thin black; display: inline-block; }\n')
                hfile.write('h3.czmlLegend { margin:0; padding-bottom:10px; }\n')
                if self.legendSamples!=None:
                    # we have custom settings for legend
                    for i in range(len(self.legendSamples)):
                        rv=(self.legendSamples[i]-self.amin[aName])/(self.amax[aName]-self.amin[aName])
                        R=int(R1+dR*rv)
                        G=int(G1+dG*rv)
                        B=int(B1+dB*rv)
                        hfile.write('.czmlLegendSample'+str(i)+' { background: rgb('+str(R)+','+str(G)+','+str(B)+'); }\n')
                else:
                    for i in range(4):
                        R=int(R1+dR*i/3.0)
                        G=int(G1+dG*i/3.0)
                        B=int(B1+dB*i/3.0)
                        hfile.write('.czmlLegendSample'+str(i)+' { background: rgb('+str(R)+','+str(G)+','+str(B)+'); }\n')
                hfile.write('</style>\n<h3 class="czmlLegend">'+self.leLegendAttrName.text()+'</h3>')
                if self.legendSamples!=None:
                    # we have custom settings for legend
                    for i in range(len(self.legendSamples)):
                        value=self.legendSamples[i]
                        hfile.write('<span class="czmlLegendSample czmlLegendSample'+str(i)+'"></span> '+str(value)+'<br/>')
                else:
                    for i in range(4):
                        value=int(self.amin[aName]+(self.amax[aName]-self.amin[aName])*i/3.0)
                        hfile.write('<span class="czmlLegendSample czmlLegendSample'+str(i)+'"></span> '+str(value)+'<br/>')
                    hfile.close()
            # farewell message
            msg="CZML file ("+filename+")"
            if (self.cbCreateLegend.isChecked()):
                msg=msg+" and legend ("+htmlFn+")"
            msg=msg+" successfully created."
            QMessageBox.information(self,"Information",msg)
            

