# -*- coding: utf-8 -*-

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import sqlalchemy_gevent
sqlalchemy_gevent.patch_all()

Base = declarative_base()

_contexts = {}
DEFAULT_CONTEXT_NAME = 'referee'


class StoreError(Exception):
    pass


def get_db_handle(name=DEFAULT_CONTEXT_NAME):
    if name in _contexts:
        return _contexts[name]
    else:
        raise StoreError("Database is not setup.")


def get_db_session(name=DEFAULT_CONTEXT_NAME):
    if name in _contexts:
        return _contexts[name]['session']
    else:
        raise StoreError("Database is not setup.")


def get_db_engine(name=DEFAULT_CONTEXT_NAME):
    if name in _contexts:
        return _contexts[name]['engine']
    else:
        raise StoreError("Database is not setup.")


def close_db_session(name=DEFAULT_CONTEXT_NAME):
    if name in _contexts:
        return _contexts[name]['session'].close()
    else:
        raise StoreError("Database is not setup.")


def init_db_handle(dburi, name=DEFAULT_CONTEXT_NAME):
    global _contexts

    if name not in _contexts:
        engine = create_engine(dburi, echo=False)
        engine.pool._use_threadlocal = True
        session = scoped_session(sessionmaker())
        session.configure(bind=engine)

        _contexts[name] = {
            "session": session,
            "engine": engine,
        }

    return get_db_handle(name)


def create_db(dburi, name=DEFAULT_CONTEXT_NAME):
    init_db_handle(dburi, name)
    engine = get_db_engine(name)
    Base.metadata.create_all(engine)
    return


def drop_db(name=DEFAULT_CONTEXT_NAME):
    global _contexts
    init_db_handle(name)

    # close db session
    session = get_db_session(name)
    session.close()

    engine = get_db_engine(name)
    Base.metadata.bind = engine
    Base.metadata.reflect()
    Base.metadata.drop_all()
    del _contexts[name]
