#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8
from __future__ import unicode_literals
import logging
import os
import subprocess
import sys
from multiprocessing import get_logger
from progress.bar import Bar
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from novell_libraries import dashboard_utils
from novell_libraries.config import SQLALCHEMY_DATABASE_URI
from novell_libraries.dashboard_utils import months
from novell_libraries.models import Base, servers

"""
    :author: Jesus Becerril Navarrete
    :organization: 
    :contact: jesusbn5@protonmail.com
"""
__docformat__ = "restructuredtext"


class Logs:
    '''Clase destinada a los objetos que manipulan los archivos de texto o logs de esta aplicacion'''

    def __init__(self, file_log):
        """
        Funcion que inicializa la clase es muy similar a un constructor da de alta los objetos de clase logger para
        poder usarlos para escribir los mensajes en los archivos de log
        :param file_log: Archivo donde se escriran los mensajes de log.
        """
        self.logger = None
        if None is self.logger:
            self.logger = get_logger()
            self.hdlr = logging.FileHandler(file_log)
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
            self.hdlr.setFormatter(formatter)
            self.logger.addHandler(self.hdlr)
            self.logger.setLevel(logging.DEBUG)

    def info_log(self, message):
        """
        Funcion usada para crear el log con el nivel de prioridades de nivel 6  o mensajes informativos
        :param message: string que contiene el mensaje a escribir en el log
        """
        self.logger.info(message)

    #        self.logger.removeHandler(self.hdlr)

    def error_log(self, message):
        """
        Funcion usada para crear el log con el nivel de prioridades de nivel 3  o mensajes de error
        :param message: string que contiene el mensaje a escribir en el log
        """
        self.logger.error(message)


class Reports:
    def __init__(self):
        file_log = dashboard_utils.FileConfig().local_receiver_file()
        self.log = dashboard_utils.Logs(file_log)
        try:
            self.log.info_log(u"Iniciando la aplicación")
            self.log.info_log(u"Iniciando la conexion con la base de datos")
            engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
            Base.metadata.create_all(engine)
            Session_factory = sessionmaker(bind=engine)
            self.Session = Session_factory

            self.log.info_log(u"La conexión con la bd fue exitosa")
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.log.error_log(u"Se presento el error: %s %s %s0" % (exc_type, exc_value, exc_traceback))

    def create_report(self, dir_txt=None, date_start=None, date_stop=None, environment=None):
        #        try:
        session = self.Session()
        self.log.info_log(u"Obteniendo los datos de los servidores operativos")
        q = session.query(servers)
        q = q.filter(and_(or_(servers.status == "operativo", servers.status == "alta"),
                          servers.environment == environment))
        server = q.order_by(servers.id.asc()).all()
        self.log.info_log(u"Los datos de los servidores se han consultado exitosamente")
        dir_md5 = "/var/md5_files/"
        if os.path.exists(dir_md5):
            md5_file = "md5sum." + environment + "-" + str(months[int(date_start.split("-")[1])]) + str(
                date_start.split("-")[2]) + ".txt"
            if os.path.exists(dir_md5 + md5_file):
                os.remove(dir_md5 + md5_file)
        else:
            os.makedirs(dir_md5)
            md5_file = "md5sum." + environment + "-" + str(months[int(date_start.split("-")[1])]) + str(
                date_start.split("-")[2]) + ".txt"

        toolbar_width = int(len(server))
        bar = Bar('Procesando las bitacoras de los servidores de:  ' + environment, max=toolbar_width)
        for i in server:
            aux = date_start.split("-")
            year = aux[2]
            month = aux[1]
            month_range = date_stop.split("-")[0]
            cmd = "~/RubymineProjects/file_processing/logbook_processing.rb -Y " + str(year) + str(" -M ") + str(
                month) + " -D " + str(month_range) + " -H " + str(i.hostname) + " -d " + str(dir_txt) + " -I " + str(
                i.id)
            output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out = output.communicate()
            bar.next()
        bar.finish()
        session.close()


if __name__ == "__main__":

    if len(sys.argv) == 5:

        dir_txt = sys.argv[1]
        ini = sys.argv[2]
        fin = sys.argv[3]
        environment = sys.argv[4]
        log = Logs("/var/log/reports_local_" + str(environment) + ".log")
        r = Reports()
        log.info_log("El reporte se realizara de la fecha %s a la fecha %s" % (ini, fin))
        r.create_report(dir_txt, ini, fin, environment)
    else:
        print ("Se debe indicar el periodo de tiempo del cual se realizara el reporte")
        sys.exit(1)
