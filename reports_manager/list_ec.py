#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8
from __future__ import unicode_literals
import datetime
import ast
import sys

from sqlalchemy import create_engine, and_

from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm.exc import NoResultFound

from novell_libraries import dashboard_utils
from novell_libraries.models import Base, ConnectionError, services_status, logbook, servers
from novell_libraries.config import SQLALCHEMY_DATABASE_URI


class ListConnectionError:
    def __init__(self):
        file_log = dashboard_utils.FileConfig().error_conn_file()
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

    def get_connection_servers(self, ini="", fin=""):
        self.write_log.info_log(u"Obteniendo los datos de los servidores que no  se  pudieron contactar")
        q = self.session.query(ConnectionError)
        server = q.order_by(ConnectionError.id.asc()).all()
        self.write_log.info_log(u"Los datos de los servidores se han consultado exitosamente")
        for i in server:
            self.write_log.info_log(u"se inicia la conexion al servidor %s" % i.hostname)
            date_connection = datetime.datetime.now().strftime("%d-%m-%Y")
            ini = i.date_connection
            fin = i.date_connection
            data = (self.ssh.ssh_conn(i.ip, self.write_log, ini, fin))

            self.write_log.info_log(u"Ordenando la información para actualizarla en la bd")

            if data != "" and data != None:
                dict_data = ast.literal_eval(data.strip("\""))
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
                        self.session.query(logbook).filter(logbook.hash_md5 == md5).one()
                        self.write_log.info_log(u"Este md5 ya esta almacenado en la bd")
                    except NoResultFound:
                        self.write_log.info_log(u"Guardando los md5 de las bitacoras de downtime")
                        md5 = dict_files[key]
                        log = logbook(file_name=key, hash_md5=md5)
                        self.session.add(log)
                        self.session.commit()
                try:
                    self.write_log.info_log(u"Continuando con la actualización de la información")
                    hash_server = self.session.query(servers).filter(servers.biometric == biometric).one()
                    id = hash_server.id
                    host_server = hash_server.hostname

                    try:
                        self.write_log.info_log(
                            u"Validando si hay una entrada en la bd con fecha %s " % i.data_connection)
                        time = self.session.query(services_status).filter(
                            services_status.date == i.data_connection).all()

                        q = self.session.query(services_status)
                        q = q.filter(
                            and_(services_status.servers_id == id,
                                 services_status.date == datetime.datetime.now().strftime("%d-%m-%Y")))
                        self.write_log.info_log(
                            u"Existe la entrada con fecha %s, se actualiza el estatus" % i.data_connection)

                        record = q.one()
                        record.time_down = d_time
                        record.files_down = files_d
                        self.session.flush()
                        self.session.commit()
                        self.write_log.info_log(u"La actualización del estatus se realizo correctamente")
                        self.write_log.info_log(u"Borrando el servidor en la lista de espera")
                        q = self.session.query(ConnectionError).filter(ConnectionError.id == i.id).delete()
                        self.write_log.info_log(u"El servidor fue borrado de la lista de espera correctamente")

                    except NoResultFound:

                        self.write_log.info_log(u"Almacenando la nueva información obtenida")
                        service_s = services_status(date=datetime.datetime.now().strftime("%d-%m-%Y"),
                                                    time_down=d_time, files_down=files_d, servers_id=id,
                                                    hostname=host_server)
                        self.session.add(service_s)
                        self.session.commit()
                        self.write_log.info_log(u"La información del estatus se almaceno correctamente")
                        self.write_log.info_log(u"Borrando el servidor en la lista de espera")
                        q = self.session.query(ConnectionError).filter(ConnectionError.id == i.id).delete()
                        self.write_log.info_log(u"El servidor fue borrado de la lista de espera correctamente")

                except:
                    pass


if __name__ == "__main__":
    if len(sys.argv) > 2:
        receiver_obj = ListConnectionError()
        receiver_obj.get_connection_servers(sys.argv[1], sys.argv[2])
    else:
        receiver_obj = ListConnectionError()
        receiver_obj.get_connection_servers()
