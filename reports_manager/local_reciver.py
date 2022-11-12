#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8
from __future__ import unicode_literals
import datetime
import sys

from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

import server_reports_local
from novell_libraries import dashboard_utils
from novell_libraries.models import Base, servers, services_status, logbook, ConnectionError
from novell_libraries.config import SQLALCHEMY_DATABASE_URI


class Receiver:
    def __init__(self):
        file_log = dashboard_utils.FileConfig().local_receiver_file()
        self.write_log = dashboard_utils.Logs(file_log)
        self.reports_local = server_reports_local.Reports(self.write_log)
        #        try:
        self.write_log.info_log(u"Iniciando la aplicación")
        self.write_log.info_log(u"Iniciando la conexion con la base de datos")
        engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.write_log.info_log(u"La conexión con la bd fue exitosa")
        #        except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        self.write_log.error_log(u"Se presento el error: %s %s %s0" % (exc_type, exc_value, exc_traceback))

    def receiver_info(self, logbook_dir, ini="", fin=""):
        self.write_log.info_log(u"Obteniendo los datos de los servidores operativos")
        q = self.session.query(servers)
        q = q.filter(or_(servers.status == "operativo", servers.status == "alta"))
        server = q.order_by(servers.id.asc()).all()
        self.write_log.info_log(u"Los datos de los servidores se han consultado exitosamente")
        for i in server:
            self.write_log.info_log(u"se inicia el procesamiento de bitacoras del server %s" % i.hostname)
            date_connection = datetime.datetime.now().strftime("%d-%m-%Y")
            #            data = (self.ssh.ssh_conn(i.ip_admin, self.write_log, ini, fin))
            data = self.reports_local.create_report(logbook_dir, ini, fin, i.ip_admin, i.hostname)
            #            print data
            self.write_log.info_log(u"Ordenando la información para almacenar en la bd")
            if data != "" and data != None:
                dict_data = data
                host = dict_data['Hostname']
                status = dict_data['Status']
                files_d = str(dict_data['down_files'])
                dict_files = dict_data['down_files']
                d_time = dict_data['Downtime_total']
                biometric = dict_data['Identity']
                ip = dict_data['Ip']

                for key in dict_files.keys():
                    try:
                        self.write_log.info_log(u"Validando si el md5 de las bitacoras de downtime ya estan en la bd")
                        md5 = dict_files[key]
                        if md5 != None or md5 != 'None':
                            print md5
                            self.session.query(logbook).filter(
                                and_(logbook.hash_md5 == md5, logbook.file_name == key)).one()
                            self.write_log.info_log(u"Este md5 ya esta almacenado en la bd")

                    except NoResultFound:
                        self.write_log.info_log(u"Guardando los md5 de las bitacoras de downtime")
                        md5 = dict_files[key]
                        if md5 != None or md5 != 'None':
                            log = logbook(file_name=key, hash_md5=md5)
                            self.session.add(log)
                            self.session.commit()
                        #                try:
                self.write_log.info_log(u"Continuando con el guardado de la información")
                hash_server = self.session.query(servers).filter(servers.biometric == biometric).one()
                id = hash_server.id
                host_server = hash_server.hostname
                try:
                    self.write_log.info_log(
                        u"Validando si hay una entrada en la bd con fecha %s " % datetime.datetime.now().strftime(
                            "%d-%m-%Y"))
                    time = self.session.query(services_status).filter(
                        services_status.date == datetime.datetime.now().strftime("%d-%m-%Y")).all()

                    q = self.session.query(services_status)
                    q = q.filter(
                        and_(services_status.servers_id == id,
                             services_status.date == datetime.datetime.now().strftime("%d-%m-%Y")))
                    self.write_log.info_log(
                        u"Existe la entrada con fecha %s, se actualiza el estatus" % datetime.datetime.now().strftime(
                            "%d-%m-%Y"))
                    record = q.one()
                    record.time_down = d_time
                    record.files_down = files_d
                    self.session.flush()
                    self.session.commit()
                    self.write_log.info_log(u"La actualización del estatus se realizo correctamente")
                except NoResultFound:
                    self.write_log.info_log(
                        u"La entrada con fecha %s no existe en la bd" % datetime.datetime.now().strftime(
                            "%d-%m-%Y"))
                    self.write_log.info_log(u"Almacenando la nueva información")
                    service_s = services_status(date=datetime.datetime.now().strftime("%d-%m-%Y"),
                                                time_down=d_time, files_down=files_d, servers_id=id,
                                                hostname=host_server)
                    self.session.add(service_s)
                    self.session.commit()
                    self.write_log.info_log(u"La información del estatus se almaceno correctamente")
                #                except NoResultFound:
                #                    exc_type, exc_value, exc_traceback = sys.exc_info()
                #                    self.write_log.error_log(u"Se presento el error: %s %s %s0" % (exc_type, exc_value, exc_traceback))
            else:

                try:
                    self.write_log.info_log(u"No se pudo obtener estatus del servidor %s" % i.hostname)
                    self.write_log.info_log(u"Validando  si ya esta en lista de espera para poder intentarlo mas tarde")
                    q = self.session.query(ConnectionError).filter(and_(ConnectionError.hostname == i.hostname,
                                                                        ConnectionError.date_insert == datetime.datetime.now().strftime(
                                                                            "%d-%m-%Y"))).one()
                    self.write_log.info_log(u"El servidor ya esta en lista de espera validando la fecha")
                    if q.date_connection == date_connection:
                        pass
                    else:
                        self.write_log.info_log(u"La fecha de lista de espera es distinta se procede a almacenar")

                        server_error = ConnectionError(date_insert=datetime.datetime.now().strftime("%d-%m-%Y"),
                                                       date_connection=date_connection, hostname=i.hostname,
                                                       ip=i.ip_admin)
                        self.session.add(server_error)
                        self.session.commit()
                        self.write_log.info_log(u"La información del server se guardo correctamente en la lista")
                except NoResultFound:
                    self.write_log.info_log(u"La información del server no esta en la lista se procede almacenar")
                    server_error = ConnectionError(date_insert=datetime.datetime.now().strftime("%d-%m-%Y"),
                                                   date_connection=date_connection, hostname=i.hostname, ip=i.ip_admin)
                    self.session.add(server_error)
                    self.session.commit()
                    self.write_log.info_log(u"La información del server se guardo correctamente en la lista")


if __name__ == "__main__":
    if len(sys.argv) > 3:
        receiver_obj = Receiver()
        receiver_obj.receiver_info(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print ("Se debe indicar el periodo de tiempo del cual se realizara el reporte")
