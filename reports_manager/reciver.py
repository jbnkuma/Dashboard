#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8
from __future__ import unicode_literals

import ast
import datetime
import sys

from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from novell_libraries import dashboard_utils
from novell_libraries.config import SQLALCHEMY_DATABASE_URI
from novell_libraries.models import Base, servers, services_status, logbook, ConnectionError, downtime_logbook


class Receiver:
    def __init__(self):
        file_log = dashboard_utils.FileConfig().reciver_file()
        self.write_log = dashboard_utils.Logs(file_log)
        try:
            self.write_log.info_log(u"Iniciando la aplicación")
            self.write_log.info_log(u"Iniciando la conexion con la base de datos")
            engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            self.session = Session()
            self.write_log.info_log(u"La conexión con la bd fue exitosa")
            self.ssh = dashboard_utils.SshCon()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.write_log.error_log(u"Se presento el error: %s %s %s0" % (exc_type, exc_value, exc_traceback))

    def save_downtime(self, file_name, downtime, hostname, time_file, date_log):
        try:
            q = self.session.query(downtime_logbook)
            n = q.filter(and_(downtime_logbook.file_name == file_name,
                              downtime_logbook.date_downtime == date_log)).one()
            n.file_name = file_name
            n.time_downtime = downtime
            n.date_downtime = date_log
        except:
            b_downtime = downtime_logbook(file_name=file_name, time_downtime=downtime, hostname=hostname,
                                          date_downtime=date_log, time_file=time_file)
            self.session.add(b_downtime)
            self.session.commit()

    def receiver_info(self, ini="", fin=""):
        self.write_log.info_log(u"Obteniendo los datos de los servidores operativos")
        q = self.session.query(servers)
        q = q.filter(or_(servers.status == "operativo", servers.status == "alta"))
        server = q.order_by(servers.id.asc()).all()
        self.write_log.info_log(u"Los datos de los servidores se han consultado exitosamente")

        for i in server:
            self.write_log.info_log(u"se inicia la conexion al servidor %s" % i.hostname)
            date_connection = datetime.datetime.now().strftime("%d-%m-%Y")

            data = (self.ssh.ssh_conn(i.ip_admin, self.write_log, ini, fin))
            self.write_log.info_log(u"Ordenando la información para almacenar en la bd")

            if data != "" and data != None:
                dict_data = ast.literal_eval(data.strip("\""))
                host = dict_data['Hostname']
                status = dict_data['Status']

                dict_files = dict_data['down_files']

                d_time = dict_data['Downtime_total']
                biometric = dict_data['Identity']
                ip = dict_data['Ip']
                aux_dict = {}
                for key in dict_files.keys():

                    extra_data = dict_files['linux-3yzq.availability.20160225-01']
                    md5 = extra_data[0]
                    aux_dict[key] = md5
                    downtime_in_file = extra_data[1]
                    server = extra_data[2]
                    time_file_down = extra_data[3]
                    date_down = extra_data[4]

                    if md5 != 'None'.strip():
                        try:

                            self.write_log.info_log(
                                u"Validando si el md5 de las bitacoras de downtime ya estan en la bd")

                            self.session.query(logbook).filter(
                                and_(logbook.hash_md5 == md5, logbook.file_name == key)).one()

                            self.write_log.info_log(u"Este md5 ya esta almacenado en la bd")
                        except NoResultFound:
                            self.write_log.info_log(u"Guardando los md5 de las bitacoras de downtime")
                            log = logbook(file_name=key, hash_md5=md5)
                            self.session.add(log)
                            self.session.commit()
                    else:
                        try:

                            self.write_log.info_log(
                                u"Validando si el md5 de las bitacoras de downtime ya estan en la bd")

                            self.session.query(logbook).filter(and_(logbook.file_name == key)).one()

                            self.write_log.info_log(u"Este md5 ya esta almacenado en la bd")
                        except NoResultFound:
                            self.write_log.info_log(u"Guardando los md5 de las bitacoras de downtime")
                            log = logbook(file_name=key, hash_md5=md5)
                            self.session.add(log)
                            self.session.commit()

                    try:
                        self.write_log.info_log(u"Validando si la información extra ya esta almacenada")
                        self.session.query(downtime_logbook).filter(and_(downtime_logbook.file_name == key,
                                                                         downtime_logbook.date_downtime == date_down))
                        self.write_log.info_log(u"Esta info ya esta almacenado en la bd")
                    except NoResultFound:
                        self.write_log.info_log(u"Guardando la información extra")
                        data_extra = downtime_logbook(file_name=key, hostname=server, time_downtime=downtime_in_file,
                                                      date_downtime=date_down, time_file=time_file_down)
                        self.session.add(data_extra)
                        self.session.commit()

                try:
                    files_d = str(aux_dict)
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
                        exit(0)
                except NoResultFound:
                    self.write_log.error_log(
                        u"Se encontro un error en el id del servidor %s verifica los datos de servidor o  dalo de alta de nuevo " % str(
                            i.hostname))
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
    if len(sys.argv) > 2:
        receiver_obj = Receiver()
        receiver_obj.receiver_info(sys.argv[1], sys.argv[2])
    else:
        receiver_obj = Receiver()
        receiver_obj.receiver_info()
