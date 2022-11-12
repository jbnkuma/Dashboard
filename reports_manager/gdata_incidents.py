#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8
from __future__ import unicode_literals
import sys
import os
import datetime

import gdata.spreadsheet.service
import gdata.service
import gdata.spreadsheet
import gdata.spreadsheets.client
import gdata.gauth
import httplib2
from sqlalchemy.orm.exc import NoResultFound
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets

from oauth2client.tools import run_flow

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from sqlalchemy import and_

from novell_libraries import dashboard_utils
from novell_libraries.config import SQLALCHEMY_DATABASE_URI
from novell_libraries.models import Base, incidents
from novell_libraries.dashboard_utils import Logs

"""
    :author: Jesus Becerril Navarrete
    :organization: 
    :contact: jesusbn5@protonmail.com
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
            self.spreadsheet_id = data[4]
            file_key = data[1]
            file_cred = data[2]
            os.environ['http_proxy'] = data[3]
            os.environ['https_proxy'] = data[3]
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
                if google_info['componentedenovell'] != 'Ninguno':
                    tmp = google_info['fechadelincidente'].split(" ")
                    fecha_incidente = tmp[0]
                    hora_incidente = tmp[1]

                    elist = []

                    try:
                        self.log.info_log(
                            "Validando si el incidente con nombre: %s ya esta en la base de datos" % google_info[
                                ''])
                        q = self.session.query(incidents).filter(and_(incidents.datecab == fecha_incidente,
                                                                      incidents.incident_name == google_info[
                                                                          'componentedenovell'],
                                                                      incidents.time_ini == hora_incidente)).one()
                        self.log.info_log(
                            "El incidente con nombre: %s ya esta en la base de datos" % google_info[
                                ''])
                    except NoResultFound:
                        self.log.info_log(
                            "El incidente %s no se encontro en la bd iniciando proceso para almacenarlo" % google_info[
                                ''])

                        if google_info[u'comentarios'] != None:
                            notes = google_info[u'comentarios']
                        else:
                            notes = "none"

                        if google_info['gruporesponsable'] != None:
                            group = google_info['gruporesponsable']
                        else:
                            group = "none"

                        if google_info['numerodeincidente'] != None:
                            reference = google_info['numerodeincidente']
                        else:
                            reference = "none"

                        if google_info['sintoma'] != None:
                            description = google_info['sintoma']
                        else:
                            description = "none"

                        incident = incidents(date_now=datetime.datetime.now().strftime("%d-%m-%Y-%H:%M"),
                                             datecab=fecha_incidente,
                                             reference=reference,
                                             incident_name=google_info['componentedenovell'],
                                             environment=google_info['ambiente'], platform='none',
                                             description=description,
                                             listing=str(elist), time_ini=hora_incidente,
                                             time_end='none', notes=notes)

                        self.session.add(incident)
                        self.session.commit()
                        self.log.info_log(
                            "El incidente %s se  almacenado correctamente" % google_info['componentedenovell'])
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.log.error_log("Se presento el error: %s %s %s0" % (exc_type, exc_value, exc_traceback))


obj = GoogleChangeRegister()
obj.storage_google_info()
