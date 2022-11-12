import json
import datetime

from novell_libraries import dashboard_utils


class WebReceiver:
    def __init__(self):
        pass

    def validate_web(self, js):
        host = json.dumps(js['Hostname']).strip("\"").strip()
        identity = json.dumps(js['Identity']).strip("\"").strip()
        calc_identity = dashboard_utils.Utils().identity_validator(host).strip()
        if identity == calc_identity:
            db = dashboard_utils.Database().table_servers()
            db_service = dashboard_utils.Database().table_services_status()
            try:
                ips = json.dumps(js['Ip']).strip("\"").strip()
                stat = json.dumps(js['Status']).strip("\"").strip()
                downtime = json.dumps(js['Downtime_total']).strip("\"").strip()
                with db[1].connect() as conn:
                    sl = db[0].select().where(db[0].c.biometric == identity)
                    result = conn.execute(sl)
                    data = result.fetchone()
                    if data is None:
                        ins = db[0].insert().values(hostname=host, ip=ips, biometric=identity, status=stat,
                                                    environment='')
                        conn.execute(ins)
                        sl = db[0].select(db[0].c.biometric == identity)
                        result = conn.execute(sl)
                        id = result.fetchone()[0]
                        ins = db_service[0].insert().values(date=datetime.datetime.now(),
                                                            timetotal_down=downtime, id_servers=id)
                        conn.execute(ins)
                        conn.close()

                    elif data[3] != identity:
                        ins = db[0].insert().values(hostname=host, ip=ips, biometric=identity, status=stat,
                                                    environment='')
                        conn.execute(ins)
                        sl = db[0].select(db[0].c.biometric == identity)
                        result = conn.execute(sl)
                        id = result.fetchone()[0]
                        conn.close()

                    else:
                        sl = db[0].select(db[0].c.biometric == identity)
                        result = conn.execute(sl)
                        id = result.fetchone()[0]
                        sl = db_service[0].select(db_service[0].c.id_servers == id)
                        result = conn.execute(sl).fetchone()
                        if result is None:
                            ins = db_service[0].insert().values(date=datetime.datetime.now(),
                                                                timetotal_down=downtime, id_servers=id)
                            conn.execute(ins)
                            conn.close()
                        else:
                            ins = db_service[0].update().values(date=datetime.datetime.now(),
                                                                timetotal_down=downtime, id_servers=id)
                            conn.execute(ins)
                            conn.close()

                resp = 200, 'text/plain'
                return resp
            except:
                resp = 500, 'text/plain'
                return resp
