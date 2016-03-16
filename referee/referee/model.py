# -*- coding: utf-8 -*-

import warnings
import datetime
import uuid
import logging
from collections import defaultdict

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.exc import SAWarning
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from .db import Base, get_db_session

warnings.simplefilter('ignore', DeprecationWarning)
warnings.simplefilter('ignore', SAWarning)

log = logging.getLogger(__name__)
game_actor_map = defaultdict()


class BaseTable(Base):

    __abstract__ = True

    uid = Column(Integer, primary_key=True)
    uuid = Column(Unicode(255), unique=True, nullable=False,
                  default=lambda x: unicode(uuid.uuid4()))
    created = Column(DateTime(timezone=False), default=datetime.datetime.now)
    lastmodified = Column(DateTime(timezone=False), default=datetime.datetime.now,
                          onupdate=datetime.datetime.now)

    @classmethod
    def fetch(cls, **kwargs):
        session = get_db_session()
        try:
            res = session.query(cls).filter_by(**kwargs).one()
        except NoResultFound:
            res = None
        return res

    @classmethod
    def fetch_all(cls, **kwargs):
        session = get_db_session()
        try:
            res = session.query(cls).filter_by(**kwargs).all()
        except NoResultFound:
            res = None
        return res

    @classmethod
    def list(cls):
        session = get_db_session()
        return session.query(cls).all()

    def save(self):
        session = get_db_session()
        session.add(self)
        session.flush()
        session.commit()


class Player(BaseTable):

    __tablename__ = "player"

    name = Column(Unicode(255), nullable=False, unique=True)
    password = Column(Unicode(255))
    defense_strength = Column(Integer, nullable=False)
    endpoint = Column(Unicode(255))

    def __init__(self, data):
        for k,v in data.iteritems():
            setattr(self, k, v)

    def to_dict(self):
        return {
            "player_uuid": self.uuid,
            "name": self.name,
            "defense_strength": self.defense_strength,
        }


class ChampionshipPlayerAssociation(BaseTable):

    __tablename__ = 'championship_player_association'

    championship_uid = Column(Integer, ForeignKey('championship.uid'))
    player_uid = Column(Integer, ForeignKey('player.uid'))
    player = relationship("Player", backref="_championship_assocs")


class Championship(BaseTable):

    __tablename__ = "championship"

    name = Column(Unicode(255), nullable=False)
    _player_assocs = relationship("ChampionshipPlayerAssociation", backref="championship")

    def __init__(self, name):
        self.name = name

    @property
    def players(self):
        return [a.player for a in self._player_assocs]

    def add_player(self, player):
        if player in self.players:
            raise Exception("Player already part of championship")

        cpa = ChampionshipPlayerAssociation()
        cpa.player = player
        self._player_assocs.append(cpa)


    def remove_player(self, player):
        session = get_db_session()
        assoc = session.query(ChampionshipPlayerAssociation).\
                filter_by(championship_uid=self.uid).\
                filter_by(player_uid=player.uid).one()

        self._player_assocs.remove(assoc)


class Game(BaseTable):

    __tablename__ = "game"

    name = Column(Unicode(255), nullable=True, unique=False)
    p1_uid = Column(Integer)
    p2_uid = Column(Integer)
    championship_uid = Column(Integer)
    winner_uid = Column(Integer, nullable=True)
    stage = Column(Unicode(255), nullable=True)

    def __init__(self, name, p1_uid, p2_uid, championship_uid, stage):
        self.name = name
        self.p1_uid = p1_uid
        self.p2_uid = p2_uid
        self.championship_uid = championship_uid
        self.stage = stage

    def to_dict(self):
        return {
            "game_uuid": self.uuid,
            "game_name": self.name,
            "championship_uid": self.championship_uid,
            "winner_uid": self.winner_uid,
        }


class Round(BaseTable):

    __tablename__ = "round"

    number = Column(Integer)
    attacker_uid = Column(Integer)
    defender_uid = Column(Integer)
    game_uid = Column(Integer)
    championship_uid = Column(Integer)
    attacker_data = Column(Unicode(255))
    defender_data = Column(Unicode(255))
    winner_uid = Column(Integer, nullable=True)

    def __init__(self, number, attacker_uid, defender_uid, game_uid,
                 championship_uid, attacker_data, defender_data, winner_uid):
        self.number = number
        self.attacker_uid = attacker_uid
        self.defender_uid = defender_uid
        self.game_uid = game_uid
        self.championship_uid = championship_uid
        self.attacker_data = attacker_data
        self.defender_data = defender_data
        self.winner_uid = winner_uid

    def to_dict(self):
        #TODO
        return {}

    @classmethod
    def number_of_wins(cls, game_uid, player_uid):
        session = get_db_session()
        return session.query(cls).filter_by(game_uid=game_uid, winner_uid=player_uid).count()
