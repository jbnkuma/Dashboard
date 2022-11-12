from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy import Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import synonym
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from werkzeug.security import check_password_hash, generate_password_hash

from novell_libraries.config import SQLALCHEMY_DATABASE_URI

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column('name', String(200))
    _password = Column('password', String(100))
    active = Column(Boolean, default=True)
    rol_admin = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        if password:
            password = password.strip()
        self._password = generate_password_hash(password)

    password_descriptor = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password_descriptor)

    def check_password(self, password):
        if self.password is None:
            return False
        password = password.strip()
        if not password:
            return False
        return check_password_hash(self.password, password)

    @classmethod
    def authenticate(cls, query, username, password):
        user_name = username.strip().lower()
        try:
            user = query(cls).filter(cls.name == user_name).one()
        except (MultipleResultsFound, NoResultFound) as e:
            return None, False

        if user is None:
            return None, False
        if not user.active:
            return user, False

        return user, user.check_password(password)

    def get_id(self):
        return str(self.id)

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def __repr__(self):
        return u'<{self.__class__.__name__}: {self.id}>'.format(self=self)


class servers(Base):
    __tablename__ = 'servers'

    id = Column(Integer, primary_key=True)
    date_admission = Column('date_admission', String(200), nullable=False)
    hostname = Column('hostname', String(200), nullable=False)
    ip_admin = Column('ip_admin', String(100), nullable=False)
    ip_prod = Column('ip_prod', String(100), nullable=False)
    biometric = Column('biometric', String(300), nullable=False)
    # port = Column('port', String(100))
    status = Column('status', String(100))
    environment = Column('environment', String(100))
    # admin_iface = Column('admin_iface', String(100))
    service_group = Column('service_group', String(1000))
    platform = Column('platform', String(100))
    service = Column('service', String(100))
    service_status = relationship("services_status", backref='servers')


class downtime_logbook(Base):
    __tablename__ = 'dowtime_logbook'

    id = Column(Integer, primary_key=True)
    hostname = Column('hostname', String(200), nullable=False)
    file_name = Column('file_name', String(200), nullable=False)
    time_downtime = Column('time_downtime', Integer, nullable=False)
    date_downtime = Column('date_downtime', String(200), nullable=False)
    time_file = Column('time_file', String(200), nullable=False)


class changes(Base):
    __tablename__ = 'changes'

    id = Column(Integer, primary_key=True)
    date_now = Column('date_now', String(50), nullable=False)
    datecab = Column('date_cab', String(50), nullable=False)
    reference = Column('reference', String(2000), nullable=False)
    change_name = Column('change_name', String(1000), nullable=False)
    category = Column('category', String(1000), nullable=False)
    environment = Column('environment', String(1000))
    platform = Column('platform', String(1000))
    description = Column('description', String(5000), nullable=False)
    in_charge = Column('in_charge', String(1000), nullable=False)
    applicant = Column('applicant', String(1000), nullable=False)
    listing = Column('listing', String(80000), nullable=False)
    date_ini = Column('date_ini', String(50), nullable=False)
    date_end = Column('date_end', String(50), nullable=False)
    time_ini = Column('time_ini', String(10), nullable=False)
    time_end = Column('time_end', String(10), nullable=False)
    vobo = Column('vobo', String(1000), nullable=False)
    notes = Column('notes', String(80000), nullable=False)
    support = Column('support', String(1000), nullable=False)
    priority = Column('priority', String(1000), nullable=False)


class incidents(Base):
    __tablename__ = 'incidents'

    id = Column(Integer, primary_key=True)
    date_now = Column('date_now', String(50), nullable=False)
    datecab = Column('date_cab', String(50), nullable=False)
    reference = Column('reference', String(100), nullable=False)
    incident_name = Column('incident_name', String(100), nullable=False)
    environment = Column('environment', String(100))
    platform = Column('platform', String(100))
    description = Column('description', String(500), nullable=False)
    listing = Column('listing', String(100), nullable=False)
    time_ini = Column('time_ini', String(10), nullable=False)
    time_end = Column('time_end', String(10), nullable=False)
    notes = Column('notes', String(10000), nullable=False)


class services_status(Base):
    __tablename__ = 'services_status'

    id = Column(Integer, primary_key=True)
    date = Column(String(200), nullable=False)
    time_down = Column('time_down', Integer, nullable=False)
    files_down = Column('files_down', String(1000000), nullable=False)
    servers_id = Column(Integer, ForeignKey('servers.id'))
    hostname = Column('hostname', String(100), nullable=False)


class ConnectionError(Base):
    __tablename__ = 'conexionerror'

    id = Column(Integer, primary_key=True)
    date_insert = Column(String(10), nullable=False)
    date_connection = Column(String(10), nullable=False)
    hostname = Column('hostname', String(200), nullable=False)
    ip = Column('ip', String(20), nullable=False)


class logbook(Base):
    __tablename__ = 'logbook'

    id = Column(Integer, primary_key=True)
    file_name = Column('file_name', String(500), nullable=False)
    hash_md5 = Column('hash_md5', String(32), nullable=False)


class logbook_store(Base):
    __tablename__ = 'logbook_store'

    id = Column(Integer, primary_key=True)
    environment = Column('environment', String(1000))
    absolute_route = Column('absolute_route', String(300), nullable=False)
    file_name = Column('file_name', String(100), nullable=False)
    hash_md5 = Column('hash_md5', String(32), nullable=False)
    month = Column('month', String(30), nullable=False)
    year = Column('year', String(10000), nullable=False)


# class progress_bar(Base):
#     __tablename__ = 'progress_bar'
#
#     id = Column(Integer, primary_key=True)
#     percent_id = Column('percent_id', Integer)
#     percent = Column('percent', Integer)
#     pid = Column('pid', Integer)


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(SQLALCHEMY_DATABASE_URI)

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Add a sample user.
    user = User(name='admin',
                password='secret',
                rol_admin=True,
                )
    session.add(user)
    session.commit()
    now = datetime.now()
