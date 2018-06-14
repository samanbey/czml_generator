# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RangeLegendDialog
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
 
 A dialog for setting range legends
"""
from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
#from qgis.core import QGis
import os
import codecs
import math
import qgis

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'range_legend.ui'))
    
class RangeLegendDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(RangeLegendDialog, self).__init__(parent)
        self.setupUi(self)
        # event handlers
        self.leNumberOfSamples.textEdited.connect(self.updateList) # number of samples changed
        self.pbUpdatePreview.clicked.connect(self.updatePreview) # update preview
        self.lwSampleValues.itemChanged.connect(self.checkValues) # check list values
               
    def checkValues(self):
        """Checks list values whether they are numbers or not"""
        for i in range(self.lwSampleValues.count()):
            try:
                value=float(self.lwSampleValues.item(i).text())
            except ValueError:
                QMessageBox.warning(self,"Error",'"'+self.lwSampleValues.item(i).text()+'" is not a valid number.')
                self.lwSampleValues.editItem(self.lwSampleValues.item(i))
                return            
        
    def updateList(self):
        """Update sample values list"""
        # get number of samples
        try:
            N=int(self.leNumberOfSamples.text())
        except ValueError:
            N=0
            return
        # re-generate sample list
        self.lwSampleValues.clear()
        for i in range(N):
            value=self.settings['minV']+(self.settings['maxV']-self.settings['minV'])*i/(N-1)
            self.lwSampleValues.addItem(str(value))
            self.lwSampleValues.item(i).setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        # store number of samples
        self.N=N
        # update preview
        self.updatePreview()
    
    def legendHtml(self):
        """Generates HTML markup for legend with the current settings"""
        # get color components from settings
        R1=self.settings['minColor'].red()
        G1=self.settings['minColor'].green()
        B1=self.settings['minColor'].blue()
        dR=self.settings['maxColor'].red()-R1
        dG=self.settings['maxColor'].green()-G1
        dB=self.settings['maxColor'].blue()-B1
        # create styles for color samples
        html='<style>\n.czmlLegendSample { width: 40px; height: 20px; border-radius:3px; border: solid thin black; display: inline-block; }\n'
        html+='h3.czmlLegend { margin:0; padding-bottom:10px; }\n'
        for i in range(self.N):
            try:
                value=float(self.lwSampleValues.item(i).text())
            except ValueError:
                value=0
                QMessageBox.warning(self,"Error",'"'+self.lwSampleValues.item(i).text()+'" is not a valid number.')
                self.lwSampleValues.editItem(self.lwSampleValues.item(i))
                return
            rv=(value-self.settings['minV'])/(self.settings['maxV']-self.settings['minV'])
            R=int(R1+dR*rv)
            G=int(G1+dG*rv)
            B=int(B1+dB*rv)
            if R>255:
                R=255
            if G>255:
                G=255
            if B>255:
                B=255
            html+='.czmlLegendSample'+str(i)+' { background: rgb('+str(R)+','+str(G)+','+str(B)+'); }\n'
        # add attribute name as heading
        html+='</style>\n<h3 class="czmlLegend">'+self.settings['attrName']+'</h3>'
        # create color samples
        for i in range(self.N):
            html+='<span class="czmlLegendSample czmlLegendSample'+str(i)+'"></span> '+self.lwSampleValues.item(i).text()+'<br/>'
        return html
    
    def updatePreview(self):
        """Update legend preview"""
        # view legend
        self.wvPreview.setHtml(self.legendHtml())
    
    def runThis(self,settings):
        """This is called when user clicks on "Legend settings"

        :param settings: A dictionary with settings
        :type settings: dictionary
        """
        self.settings=settings
        
        if self.settings['samples']==None:
            # set initial samples if no sample list provided
            self.updateList()
        else:
            # otherwise fill list with provided samples
            self.leNumberOfSamples.setText(str(len(self.settings['samples'])))
            self.lwSampleValues.clear()
            for s in self.settings['samples']:
                self.lwSampleValues.addItem(str(s))
            self.updatePreview()
            
        # show dialog
        self.show()
        if self.exec_():
            # OK clicked - return legend sample list
            l=[]
            for i in range(self.lwSampleValues.count()):
                l.append(float(self.lwSampleValues.item(i).text()))
            return l
        else:
            # Cancel clicked - return nothing
            return None
