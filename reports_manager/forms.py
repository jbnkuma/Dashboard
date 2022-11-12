# -*- coding: utf-8 -*-
# coding=utf-8
from __future__ import unicode_literals

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from wtforms import Form, PasswordField, SelectField, SelectMultipleField
from wtforms import TextAreaField, StringField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import DataRequired, IPAddress
from wtforms.validators import Length

from novell_libraries.config import SQLALCHEMY_DATABASE_URI
from novell_libraries.dashboard_utils import FileConfig
from novell_libraries.models import Base, servers

menu = FileConfig().menus()


class LoginForm(Form):
    user_name = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class AddServerForm(Form):
    hostname = StringField(u'Hostname', validators=[DataRequired()])
    ip = StringField(u'Ip Adminstrativa', validators=[DataRequired(), IPAddress()])
    environment = SelectField(u'Ambiente',
                              choices=menu[1],
                              validators=[DataRequired()])
    ip_prod = StringField(u'Ip Productiva', validators=[DataRequired()])
    platform = SelectField(u'Plataforma', choices=menu[0], validators=[DataRequired()])
    service = StringField(u'Servicio', validators=[DataRequired()])
    port = StringField(u'Puerto', validators=[DataRequired()])
    status = SelectField(u'Estatus',
                         choices=menu[2],
                         validators=[DataRequired()])

    service_group = StringField(u'Grupo de servicio', validators=[DataRequired()])


class SearchServerForm(Form):
    search_server = StringField(u"Busqueda de servidor", validators=[DataRequired()])


class SearchStoreLog(Form):
    search_log = StringField(u"Busqueda de bitacoras", validators=[DataRequired()])


class ReportGenForm(Form):
    month = StringField(u'Mes', validators=[DataRequired()])
    year = StringField(u'Año', validators=[DataRequired()])


class ModifyServerForm(Form):
    #    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    #    Base.metadata.create_all(engine)
    #    Session = sessionmaker(bind=engine)
    #    global session1
    #    session1 = Session()

    #    hostname = QuerySelectField(
    #        label='hostname',
    #        validators=[DataRequired()],
    #        allow_blank=True,
    #        blank_text=u'-- selecciona hostname --',
    #        query_factory=lambda: session1.query(servers).order_by(servers.id.asc()).all(),
    #        get_pk=lambda item: item.hostname,
    #        get_label=lambda item: item.hostname,
    #    )
    hostname = StringField(u"Hostname", validators=[DataRequired()])
    ip = StringField(u'Ip Adminstrativa', validators=[DataRequired(), IPAddress()])
    environment = SelectField(u'Ambiente',
                              choices=menu[1],
                              validators=[DataRequired()])
    ip_prod = StringField(u'Ip productiva', validators=[DataRequired()])
    platform = SelectField(u'Plataforma', choices=menu[0], validators=[DataRequired()])
    service = StringField(u'Servicio', validators=[DataRequired()])
    port = StringField(u'Puerto', validators=[DataRequired()])
    status = SelectField(u'Estatus',
                         choices=menu[2],
                         validators=[DataRequired()])
    service_group = StringField(u'Grupo de servicio', validators=[DataRequired()])


class AddChange(Form):
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    global session2
    session2 = Session()
    date_cab = StringField(u'Fecha de sesion CAB', validators=[DataRequired()])
    reference = StringField(u'Folio RFC SAT', validators=[DataRequired()])
    change_name = StringField(u'Nombre del cambio', validators=[DataRequired()])
    category = SelectField(u'Categoria', choices=menu[6],
                           validators=[DataRequired()])
    environment = SelectField(u'Ambiente',
                              choices=menu[1],
                              validators=[DataRequired()])
    platform = SelectMultipleField(u'Plataforma',
                                   choices=menu[0],
                                   validators=[DataRequired()])

    description = TextAreaField(u'Descripción', validators=[DataRequired(), Length(max=500)])
    in_charge = StringField(u'Ejecutor del cambio', validators=[DataRequired()])
    applicant = StringField(u'Solicitante del cambio', validators=[DataRequired()])
    listing = QuerySelectMultipleField(
        label=u'Listado de equipo/Aplicaciones/Componentes/Servicios en el cambio',
        validators=[DataRequired()],
        allow_blank=False,
        blank_text=u'-- selecciona hostname --',
        query_factory=lambda: session2.query(servers).order_by(servers.id.asc()).all(),
        get_pk=lambda item: item.hostname,
        get_label=lambda item: item.hostname,
    )
    date_initial = StringField(u'Fecha de Implementación', validators=[DataRequired()])
    time_ini = StringField(u'Hora de inicio', validators=[DataRequired()])
    time_end = StringField(u'Hora de finalización', validators=[DataRequired()])
    vobo = SelectField(u'VoBo de Gobierno', choices=menu[5],
                       validators=[DataRequired()])
    notes = TextAreaField(u'Notas', validators=[DataRequired(), Length(max=800)])
    support = SelectField(u'Grupo de soporte', choices=menu[3]
                          , validators=[DataRequired()])
    priority = SelectField(u'Prioridad', choices=menu[4],
                           validators=[DataRequired()])


class Incident(Form):
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    global session3
    session3 = Session()
    date_incident = StringField(u'Fecha de incidente', validators=[DataRequired()])
    reference = StringField(u'Folio', validators=[DataRequired()])
    incident_name = StringField(u'Nombre de la incidencia', validators=[DataRequired()])
    environment = SelectField(u'Ambiente',
                              choices=menu[1],
                              validators=[DataRequired()])
    platform = SelectMultipleField(u'Plataforma',
                                   choices=menu[0],
                                   validators=[DataRequired()])
    description = TextAreaField(u'Descripción', validators=[DataRequired(), Length(max=500)])
    listing = QuerySelectMultipleField(
        label=u'Listado de equipo/Aplicaciones/Componentes/Servicios en el cambio',
        validators=[DataRequired()],
        allow_blank=False,
        blank_text=u'-- selecciona hostname --',
        query_factory=lambda: session3.query(servers).order_by(servers.id.asc()).all(),
        get_pk=lambda item: item.hostname,
        get_label=lambda item: item.hostname,
    )
    time_ini = StringField(u'Hora inicial del incidente', validators=[DataRequired()])
    time_end = StringField(u'Hora de cierre del incidente', validators=[DataRequired()])
    notes = TextAreaField(u'Notas', validators=[DataRequired(), Length(max=800)])
