from sqlalchemy import create_engine, Column
from sqlalchemy import ForeignKey, Integer, String, event
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


def pragma_fk_conn(db_apicon, con_record):
    db_apicon.execute('pragma foreign_keys=ON')


class User(Base):
    __tablename__ = 'user'

    name = Column(String)
    email = Column(String)
    id = Column(Integer, primary_key=True)
    movies = relationship('Movie', back_populates="user",
                          cascade="all, delete-orphan", passive_deletes=True)


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    movies = relationship('Movie', back_populates="category",
                          passive_deletes=True, cascade="all, delete-orphan")


class Movie(Base):
    __tablename__ = 'movie'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    category_id = Column(Integer, ForeignKey(
        'category.id', ondelete='CASCADE'))
    description = Column(String)
    user = relationship("User", back_populates="movies")
    category = relationship("Category", back_populates="movies")

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name,
                'user': self.user.name,
                'category': self.category.name,
                'description': self.description}


engine = create_engine('sqlite:///items.db')
Base.metadata.create_all(engine)
