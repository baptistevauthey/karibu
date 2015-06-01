from sqlalchemy import Column, Integer, String, Float
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(50), unique=True)
    password = Column(String(200))
    ep = Column(Integer)

    def __init__(self, user_name, password):
        self.user_name = user_name
	self.password = password
        self.ep = 0

    def __repr__(self):
        return '<User %r with %d eneo points>' % (self.user_name, self.ep)

class Subscription(Base):
    __tablename__ = 'subscriptions'
    user = Column(Integer)
    community = Column(Integer)
    id = Column(Integer, primary_key = True, autoincrement=True)
    def __init__(self, user, community):
        self.user = user
        self.community = community

class Location(Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    community = Column(String(140), index=True)
    lat = Column(Float)
    long = Column(Float)
    name = Column(String(140))
    description = Column(String(400))
    ep = Column(Integer)

    def __init__(self, community = None, lat=None, long=None, name=None, description=None):
        self.community = community
        self.lat = lat
        self.long = long
        self.name = name
        self.description = description
        self.ep = 0

    def __repr__(self):
        return '<Location %r at (%f, %f)>' % (self.id, self.lat, self.long)

class Community(Base):
    __tablename__ = 'community'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    users = Column(Integer)

    def __init__(self, name=None):
        self.name = name
        self.users = 0

    def __repr__(self):
        return '<Community %s with %d users>' % (self.name, self.users)

class Vote(Base):
    __tablename__ = 'vote'
    location = Column(Integer, index=True, primary_key=True)
    user = Column(Integer, index=True)
    type = Column(Integer)
    def __init__(self, location, user, type):
        self.location = location
        self.user = user
	self.type = type
