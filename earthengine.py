# -*- coding: utf-8 -*-
"""
/***************************************************************************
 earthengine3
                                 A QGIS plugin
 teste earthengine3
                              -------------------
        begin                : 2019-03-19
        git sha              : $Format:%H$
        copyright            : (C) 2019 by victor
        email                : victor_mendes00@hotmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources

# Import the code for the dialog
from earthengine_dialog import earthengine3Dialog
import os.path
import ee
import ee.mapclient
import time

from qgis.utils import *
from qgis.core import *


class earthengine3:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'earthengine3_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&earthengine3')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'earthengine3')
        self.toolbar.setObjectName(u'earthengine3')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('earthengine3', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = earthengine3Dialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/earthengine3/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'ee'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&earthengine3'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def scriptEE(self,parameters):

        print('Inicializando Conexao...')
        ee.Initialize();
        print('Conectado!');
        ee.data.setDeadline(0)

        sentinelTeste = ee.Image('COPERNICUS/S2/20180715T134211_20180715T134212_T21JYN').select(['B4','B3','B2'])
        
        dtInicio = str(parameters.anoInicial.year()) + "-" + str(parameters.anoInicial.month()) + "-" + "01";
        dtFim = str(parameters.anoFinal.year()) + "-" + str(parameters.anoFinal.month()) + "-" + "01";
        data = ee.DateRange(ee.Date(dtInicio),ee.Date(dtFim).advance(1,'month'));
    
        ocoi = ee.Feature(ee.FeatureCollection("users/odraitaipu/bracos/ocoi").union().first()).set('nome','Ocoí').geometry(); 

        def mapMacrofitas(image):
            ndvi = image.normalizedDifference().clip(ocoi);
            
            soma = ndvi.reproject(image.select('B4').projection()).reduceResolution(ee.Reducer.sum());
            porcentagem = soma.divide(ndvi).multiply(100).round();
            clippedNdvi = ndvi.updateMask(ndvi.where(porcentagem.lte(99),0));
        
            output = ee.Image(0).where(clippedNdvi.gte(0.2),1);
            
            result = output.updateMask(output).rename('macrofitas').reproject(image.select('B4').projection());
            return result

        def renderImage(imag):
            img = ee.Image(imag)
            '''
            rgb visualize
            minMax = img.reduceRegion(ee.Reducer.percentile([5,95]), ocoi, 100, None, None, True).values().sort()
            visualise = img.visualize(['B4','B3','B2'], None, None, minMax.get(0), minMax.get(-1))
            '''
            minMax = img.reduceRegion(ee.Reducer.minMax(), ocoi, 30, None, None, True);
            visualize = img.visualize(['macrofitas'], None, None, 1, minMax.get('macrofitas_max'), None, None, ['CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718','74A901', '66A000', '529400', '3E8601', '207401', '056201','004C00', '023B01', '012E01', '011D01', '011301']);

            mapa = visualize.getMapId()
            mapid = mapa.get('mapid')
            token = mapa.get('token')

            url='type=xyz&url=https://earthengine.googleapis.com/map/'+mapid+'/{z}/{x}/{y}'+'?token=' + token
            iface.addRasterLayer(url, 'macrofitas' , 'wms')
            print('Adicionado camada!')
            
        if parameters.collection == 'Landsat 8':

            collect = ee.ImageCollection('LANDSAT/LC08/C01/T1').filterDate(data).filterBounds(ocoi).sort('system:time_start').set('nomeColecao',parameters.collection,'satelite','LANDSAT/LC08/C01/T1_TOA').select(['B5','B4','B6'])
            collectMacrofitas = ee.ImageCollection(collect.map(mapMacrofitas));
            
            macrofitas = ee.Image(collectMacrofitas.sum())
            # renderImage(macrofitas)
            
            minMax = macrofitas.reduceRegion(ee.Reducer.minMax(), ocoi, 30, None, None, True);
            visualize = macrofitas.visualize(['macrofitas'], None, None, 1, minMax.get('macrofitas_max'), None, None, ['CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718','74A901', '66A000', '529400', '3E8601', '207401', '056201','004C00', '023B01', '012E01', '011D01', '011301']);
            url = visualize.getDownloadURL({'name': 'teste','scale': 30,'region': ee.String("[").cat(ee.List(ocoi.convexHull().coordinates().get(0)).join(",")).cat("]").getInfo()});

            print('Link: ')
            print(url)

            folder = "/home/laboratorio/.qgis2/python/plugins/earthengine3/downloads/"
            name = "teste"

            import requests
            r = requests.get(url)
            with open(folder+"teste.zip", "wb") as file:
                file.write(r.content)
            import zipfile
            with zipfile.ZipFile(folder+"teste.zip", "r") as z:
                z.extractall(folder)  

            iface.addRasterLayer(folder+"teste.vis-blue.tif", "macrofitasBlue")
            

            '''
            task = ee.batch.Export.image.toCloudStorage(visualize, 'teste', 'testeearthengine', None, None, ee.Feature(macrofitas).geometry().bounds().getInfo()['coordinates'], 30, None, None, 1e13)
            print('incicializando task');
            task.start()
            print('inicializada');
            '''
            
        
        # task = ee.batch.Export.map.toCloudStorage(imagem, 'teste1', 'testeearthengine', None, None, False, None, 30  )

    def run(self):
        
        print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n');
        print('*========================== START ==========================*');
    
        self.dlg.show()
        result = self.dlg.exec_()
        
        if result:
            pass
            print('OK Pressed!');

            maxNuv = self.dlg.maxNuv.text()
            minInter = self.dlg.minInter.text()        
            collection = self.dlg.collection.currentText()        

            anoInicial = self.dlg.anoInicial.date()
            anoFinal = self.dlg.anoFinal.date()

            p = parameters(maxNuv, minInter, collection, anoInicial, anoFinal)
            self.scriptEE(p)

        print('*========================== RIP   ==========================*');

class parameters:
    def __init__(self, maxNuv, minInter, collection, anoInicial, anoFinal):
        self.maxNuv = maxNuv
        self.minInter = minInter
        self.collection = collection
        self.anoInicial = anoInicial
        self.anoFinal = anoFinal

