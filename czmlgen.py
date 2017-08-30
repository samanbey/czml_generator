# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CZMLGenerator
                                 A QGIS plugin
 CZML Generator
                             -------------------
        begin                : 2016-01-06
        copyright            : (C) 2016 by Mátyás Gede
        email                : saman@map.elte.hu
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import resources

from prism_map_dialog import PrismMapDialog
from prism_map_time_dialog import PrismMapTimeDialog
from range_legend_dialog import RangeLegendDialog
from scaled_models_dialog import ScaledModelsDialog
from connector_lines_dialog import ConnectorLinesDialog

class CZMLGenerator:
    """CZML Generator QGIS plugin"""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # save reference to the QGIS interface
        self.iface = iface

    def initGui(self):
        """Create the menu entries inside the QGIS GUI."""
        # create actions that will start plugin configuration
        self.actions=[]
        # Prism Map
        a=QAction(QIcon(":/plugins/czml_generator/prism.png"), "Prism Map", self.iface.mainWindow())
        a.triggered.connect(self.runPrismMap)
        self.actions.append(a)
        # Prism Map with time
        a=QAction(QIcon(":/plugins/czml_generator/prism.png"), "Prism Map with time", self.iface.mainWindow())
        a.triggered.connect(self.runPrismMapTime)
        self.actions.append(a)
        # Scaled models with time
        a=QAction(QIcon(":/plugins/czml_generator/prism.png"), "Scaled models with time", self.iface.mainWindow())
        a.triggered.connect(self.runScaledModels)
        self.actions.append(a)
        # Raised connector lines
        a=QAction(QIcon(":/plugins/czml_generator/prism.png"), "Raised connector lines", self.iface.mainWindow())
        a.triggered.connect(self.runConnectorLines)
        self.actions.append(a)
        
        # create dialogs
        self.PMDlg=PrismMapDialog()
        self.PMTDlg=PrismMapTimeDialog()
        self.RLDlg=RangeLegendDialog()
        self.PMDlg.RLDlg=self.RLDlg
        self.PMTDlg.RLDlg=self.RLDlg
        self.SMDlg=ScaledModelsDialog()
        self.CLDlg=ConnectorLinesDialog()
        
        for a in self.actions:
            # add menu item
            self.iface.addPluginToWebMenu("&CZML Generator", a)
        
    def unload(self):
        """Removes the plugin menu item from QGIS GUI."""
        for a in self.actions:
            # remove the plugin menu item and icon
            self.iface.removePluginWebMenu("&CZML Generator", a)
        
    def runPrismMap(self):
        """Creates and launches prism map dialog"""
        self.PMDlg.runThis(self.iface)
        
    def runPrismMapTime(self):
        """Creates and launches prism map with time dialog"""
        self.PMTDlg.runThis(self.iface)

    def runScaledModels(self):
        """Creates and launches prism map with time dialog"""
        self.SMDlg.runThis(self.iface)

    def runConnectorLines(self):
        """Creates and launches raised connector lines dialog"""
        self.CLDlg.runThis(self.iface)
        