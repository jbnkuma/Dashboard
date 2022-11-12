#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8
from __future__ import unicode_literals

import datetime
import os
import sys

import gdata.gauth
import gdata.service
import gdata.spreadsheet
import gdata.spreadsheet.service
import gdata.spreadsheets.client
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from novell_libraries import dashboard_utils
from novell_libraries.config import SQLALCHEMY_DATABASE_URI
from novell_libraries.dashboard_utils import Logs
from novell_libraries.models import Base, changes

"""
    :author: Jesus Becerril Navarrete
    :organization: 
    :contact: jesus.becerril@protonmail.com
"""


class GoogleChangeRegister:
    def __init__(self):
        file_log = dashboard_utils.FileConfig().google_file()
        self.log = Logs(file_log)
        try:
            self.log.info_log("Iniciando aplicación")
            self.log.info_log("Leyendo datos del archivo de configuración")
            utils = dashboard_utils.FileConfig()
            data = utils.google_data()
            self.spreadsheet_id = data[0]
            file_key = data[1]
            file_cred = data[2]
            #os.environ['http_proxy'] = data[3]
            #os.environ['https_proxy'] = data[3]
            self.log.info_log("Se han obtenido los datos del archivo de configuración")
            self.log.info_log("Creando conexión con la base de datos")
            engine = create_engine(SQLALCHEMY_DATABASE_URI)
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            self.session = Session()
            self.log.info_log("La conexión con la base de datos esta lista")
            self.log.info_log("Iniciando la conexión con google spreadsheets")
            storage = Storage(file_cred)
            credentials = storage.get()
            if credentials is None or credentials.invalid:

                credentials = run_flow(
                    flow_from_clientsecrets(file_key, scope=["https://spreadsheets.google.com/feeds"]),
                                  storage)
            if credentials.access_token_expired:
                credentials.refresh(httplib2.Http())

            self.gd_client = gdata.spreadsheet.service.SpreadsheetsService(
                additional_headers={'Authorization': 'Bearer %s' % credentials.access_token})
            self.log.info_log("La conexión con google spreadsheets se a establecido")
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.log.error_log("Se presento el error: %s %s %s0" % (exc_type, exc_value, exc_traceback))

    def getRows(self, ListFeed):
        try:
            self.log.info_log("Obteniendo los datos de las columnas del tablero de cambios")
            rows = []
            for entry in ListFeed.entry:
                d = {}
                for key in entry.custom.keys():
                    d[key] = entry.custom[key].text
                rows.append(d)
            return rows
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.log.error_log("Se presento el error: %s %s %s0" % (exc_type, exc_value, exc_traceback))

    def storage_google_info(self):
        try:
            self.log.info_log("Se inicia la obtencion de la información del tablero de cambios")
            dic_rows = self.getRows(self.gd_client.GetListFeed(self.spreadsheet_id))
            self.log.info_log("La información se a obtenido comenzando a procesar la información")

            for google_info in dic_rows:
                elist = []
                date_ini = ""
                time_ini = ""
                time_end = ""

                date_cab = google_info[u'fechasesióncab']
                d1 = datetime.datetime.strptime(date_cab, "%d/%m/%Y")
                date_standard = datetime.datetime.strptime("22/06/2015", "%d/%m/%Y")
                if d1 > date_standard:
                    self.log.info_log("Se ha validado que no es un cambio anterior al 22/06/2015")
                    try:
                        self.log.info_log(
                            "Validando si el cambio con rfc: %s ya esta en la base de datos" % google_info[
                                'foliorfcsat'])
                        q = self.session.query(changes).filter(changes.reference == google_info['foliorfcsat']).one()
                        self.log.info_log(
                            "El cambio con rfc: %s ya esta en la base de datos" % google_info['foliorfcsat'])
                    except NoResultFound:
                        self.log.info_log(
                            "El cambio %s no se encontro en la bd iniciando proceso para almacenarlo" % google_info[
                                'foliorfcsat'])

                        date_time_tmp = google_info[u'fechayhorainicialdeimplementación'].split(' ')
                        date_ini = date_time_tmp[0]
                        time_tmp = date_time_tmp[1].split(':')
                        time_ini = time_tmp[0] + ":" + time_tmp[1]
                        date_time_tmp = google_info[u'fechayhorafinaldeimplementación'].split(' ')
                        date_end = date_time_tmp[0]
                        time_tmp = date_time_tmp[1].split(':')
                        time_end = time_tmp[0] + ":" + time_tmp[1]
                        listing = google_info[u'ambientenombredeequipoippuertoaplicaci\xf3n']

                        ltmp = listing.splitlines()
                        for i in ltmp:
                            try:
                                d = i.strip().split("/")[1].strip()

                                if d[0] != "t":
                                    pass
                                else:
                                    elist.append(d)
                            except IndexError:
                                pass

                        if google_info[u'descripci\xf3ndelcambio'] != None:
                            descrp = google_info[u'descripci\xf3ndelcambio']
                        else:
                            descrp = "none"

                        if google_info['solicitantedelcambio'] != None:
                            charge = google_info['solicitantedelcambio']
                        else:
                            charge = "none"

                        if google_info['ejecutordelcambio'] != None:
                            ej = google_info['ejecutordelcambio']
                        else:
                            ej = "none"

                        if google_info['notas'] != None:
                            note = google_info['notas']
                        else:
                            note = "none"
                        if google_info['grupodesoporte'] != None:
                            group = google_info['grupodesoporte']
                        else:
                            group = "none"

                        if google_info['prioridad'] != None:
                            priority = google_info['prioridad']
                        else:
                            priority = "none"

                        change = changes(date_now=datetime.datetime.now().strftime("%d-%m-%Y-%H:%M"),
                                         datecab=google_info[u'fechasesi\xf3ncab'],
                                         reference=google_info['foliorfcsat'],
                                         change_name=google_info['nombredelcambio'],
                                         category=google_info[u'categoría'],
                                         environment=google_info['ambiente'], platform=google_info['plataforma'],
                                         description=descrp, in_charge=charge, applicant=ej,
                                         listing=str(elist), date_ini=date_ini, time_ini=time_ini,
                                         date_end=str(date_end),
                                         time_end=time_end,
                                         vobo=google_info['vo.bo.gobierno'], notes=note, support=group,
                                         priority=priority)
                        self.session.add(change)
                        self.session.commit()
                        self.log.info_log("El cambio %s se  almacenado correctamente" % google_info['foliorfcsat'])
                else:
                    self.log.info_log(
                        "El cambio %s es anterior al 22/06/2015 no sera almacenado" % google_info['foliorfcsat'])

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.log.error_log("Se presento el error: %s %s %s0" % (exc_type, exc_value, exc_traceback))


obj = GoogleChangeRegister()
obj.storage_google_info()
