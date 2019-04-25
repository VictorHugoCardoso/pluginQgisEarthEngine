# -*- coding: utf-8 -*-
"""
/***************************************************************************
 earthengine3
                                 A QGIS plugin
 teste earthengine3
                             -------------------
        begin                : 2019-03-19
        copyright            : (C) 2019 by victor
        email                : victor_mendes00@hotmail.com
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load earthengine3 class from file earthengine3.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .earthengine import earthengine3
    return earthengine3(iface)
