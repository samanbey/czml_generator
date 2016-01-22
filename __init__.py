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
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    """Load CZMLGenerator class from file czmlgen.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from czmlgen import CZMLGenerator
    return CZMLGenerator(iface)
