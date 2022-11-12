#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8
from dialog import Dialog
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from novell_libraries.config import SQLALCHEMY_DATABASE_URI
from novell_libraries.models import Base, User


def add(user_name, password):
    engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    Session = session_factory
    session = Session()
    try:
        session.query(User).filter(User.name == user_name).one()
        session.close()
        return 1
    except NoResultFound:
        user = User(name=user_name,
                    password=password,
                    rol_admin=True,
                    )
        session.add(user)
        session.commit()
        session.close()
        return 0


def modify(user_name, password):
    engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    Session = session_factory
    session = Session()
    try:
        q = session.query(User).filter(User.name == user_name).one()
        q.password = password
        session.commit()
        session.close()
        return 0
    except NoResultFound:
        return 1


def delete(user):
    engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    Session = session_factory
    session = Session()
#    try:
    session.query(User).filter(User.name == user).delete()
    session.commit()
    session.close()
    return 0
#    except:
#        return 1


def search_user(user_name):
    engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    Session = session_factory
    session = Session()
    try:
        session.query(User).filter(User.name == user_name).one()
        session.close()
        return 0
    except NoResultFound:
        return 1


def add_user(tag):
    user = ""
    password = ""
    d = Dialog(dialog='dialog')
    d.setBackgroundTitle(u"SLA users admin")
    if tag == "1":
        while user == "":
            code1, user = d.inputbox("Teclea e nombre del nuevo usuario")
            if code1 != 0:
                menu()
        while password == "":
            message = "Teclea el password del usuario: %s" % user
            code2, password = d.passwordbox(message, init="")
            if code2 != 0:
                menu()
        result = add(user, password)
        if result == 0:
            message = "El usuario %s fue dado de alta exitosamente " % user
            d.msgbox(message)
            menu()
        elif result == 1:
            message = "El usuario %s ya existe intenta con otro nombre de usuario " % user
            r = d.msgbox(message)
            add_user(tag)
    elif tag == "2":
        modify_user()
    elif tag == "3":
        del_user()


def modify_user():
    user = ""
    password = ""
    d = Dialog(dialog='dialog')
    d.setBackgroundTitle(u"SLA users admin")
    tag = ""
    while user == "":
        code1, user = d.inputbox("Teclea el nombre del usuario para modificar el password")
        if code1 != 0:
            menu()
        else:
            if search_user(user) != 1:
                while password == "":
                    message = "Teclea el password nuevo password usuario: %s" % user
                    code2, password = d.passwordbox(message, init="")
                    if code2 != 0:
                        modify_user()
                    else:
                        if modify(user, password) == 0:
                            message = "Se modifico correctamente el password del usuario: %s " % user
                            d.msgbox(message)
                            menu()
                        else:
                            message = "El usuario %s no existe es necesario dar de alta este usuario " % user
                            d.msgbox(message)
                            menu()

            else:
                message = "El usuario %s no existe es necesario dar de alta este usuario " % user
                d.msgbox(message)
                menu()
    result = add(user, password)
    if result == 0:
        message = "El usuario %s fue dado de alta exitosamente " % user
        d.msgbox(message)
        menu()
    elif result == 1:
        message = "El usuario %s ya existe intenta con otro nombre de usuario " % user
        r = d.msgbox(message)
        add_user(tag)


def del_user():
    user = ""
    password = ""
    d = Dialog(dialog='dialog')
    d.setBackgroundTitle(u"SLA users admin")
    while user == "":
        code1, user = d.inputbox("Teclea el nombre del usuario a eliminar")
        if code1 != 0:
            del_user()
        else:
            if search_user(user) != 1:
                delete(user)
            else:
                message = "El usuario %s no existe es necesario dar de alta este usuario " % user
                d.msgbox(message)
                menu()
    result = add(user, password)
    if result == 0:
        message = "El usuario %s fue dado de baja exitosamente " % user
        d.msgbox(message)
        menu()


def menu():
    d = Dialog(dialog='dialog')
    d.setBackgroundTitle(u"SLA users admin")
    code, tag = d.menu(u"Seleccione una opción", choices=[("1", "Alta de usuario"),
                                                          ("2", "Reseteo de contraseña"),
                                                          ("3", "Baja de usuario")])
    if code == 0:
        add_user(tag)
    else:
        exit(0)


menu()
