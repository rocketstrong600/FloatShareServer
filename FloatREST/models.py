from FloatREST.database import Base

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

import hashlib
import uuid
from time import time
import math

vote_assosiation_table = Table(
    "vote_assosiations",
    Base.metadata,
    Column("user_id", ForeignKey("tunes.tune_id"), primary_key=True),
    Column("tune_id", ForeignKey("users.user_id"), primary_key=True),
)

shared_assosiation_table = Table(
    "shared_assosiations",
    Base.metadata,
    Column("user_id", ForeignKey("tunes.tune_id"), primary_key=True),
    Column("tune_id", ForeignKey("users.user_id"), primary_key=True),
)

class User(Base):
    __tablename__ = 'users'
    id = Column("user_id", Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    description = Column(String(300), nullable=True)
    password = Column(String(256), nullable=True)
    level = Column(Integer)
    sessionID = Column(String(256), nullable=True)
    lifetime = Column(Integer)

    shared = relationship('Tune', secondary=shared_assosiation_table, back_populates="shared_with")

    messages = relationship('Message')
    voted = relationship('Tune', secondary=vote_assosiation_table, back_populates="voters")
    tunes = relationship('Tune')

    def StartSession(self):
        self.sessionID = str(uuid.uuid1())
        self.lifetime=math.floor(time())

    def SetupUser(self, username: str, password: str, level: int):
        self.username = username

        h = hashlib.new('sha256')
        h.update(password.encode('utf-8'))
        self.password = h.hexdigest()

        self.StartSession()

        self.level = level

    def CheckPassword(self, password: str) -> bool:
        if self.password == None:
            return False
        
        h = hashlib.new('sha256')
        h.update(password.encode('utf-8'))
        return h.hexdigest() == self.password

    def CheckSession(self, session: str):
        return session == self.sessionID and (time()-self.lifetime) < 3600


class Tune(Base):
    __tablename__ = 'tunes'
    id = Column("tune_id", Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(300), nullable=True)
    XML = Column(String, nullable=False)
    Public = Column(Boolean, default=False, nullable=False)
    Owner = Column(Integer, ForeignKey('users.user_id'), nullable=False)



    voters = relationship('User', secondary=vote_assosiation_table, back_populates="voted")
    shared_with = relationship('User', secondary=shared_assosiation_table, back_populates="shared")

    def votes(self):
        return len(self.voters)

    def __repr__(self):
        return ''

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    toUserID = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    fromUser = Column(String(256), nullable=False, default="Anonymous")
    subject = Column(String(60), nullable=False)
    message = Column(String(1024), nullable=False)

    def __repr__(self):
        return ''
    
    
