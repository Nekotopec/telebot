# Import token and data base url.
from settings_vars import DBURL, TOKEN

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker
engine = create_engine(DBURL, echo=True, encoding='utf-8')
Base = declarative_base()


class User(Base):

    __tablename__ = 'users'

    chat_id = Column(Integer, primary_key=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    telephone_number = Column(String(15), nullable=False)

    def __init__(self, chat_id, first_name, last_name, telephone_number):
        self.chat_id = chat_id
        self.first_name = first_name
        self.last_name = last_name
        self.telephone_number = telephone_number

    def __repr__(self):
        return 'User({}, {}, {}, {})'.format(self.chat_id, self.first_name, self.last_name, self.telephone_number)


class Ad(Base):

    __tablename__ = 'ads'

    id = Column(Integer, primary_key=True)
    obj = Column(String(64), nullable=False)
    description = Column(String(255))
    made_by = Column(Integer, ForeignKey('users.chat_id', ondelete='CASCADE'))
    price = Column(Float, nullable=False)

    user = relation('User', backref='ads', lazy=False)

    def __init__(self, obj, description, price):
        self.obj = obj
        self.description = description
        self.price = price

    def __repr__(self):
        return 'Ad({}, {}, {})'.format(self.obj, self.description, self.price)


if __name__ == "__main__":

    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    u = session.query(User).filter(User.chat_id == 243279187).one()
    print(u)

