
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String,ForeignKey,UniqueConstraint,Index
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

class Form(Base):
    __tablename__ = "kewo_forms"
    id = Column(Integer,primary_key=True,autoincrement=True)
    content = Column(String(255))
    type = Column(Integer)
    word_id = Column(Integer, ForeignKey("kewo_words.id",ondelete="CASCADE",onupdate="CASCADE"))
    word = relationship("Word", foreign_keys=[word_id], backref=backref("words", passive_deletes="all"),passive_deletes="all")
    origin_id = Column(Integer, ForeignKey("kewo_words.id",ondelete="CASCADE",onupdate="CASCADE"))
    explain_id = Column(Integer, ForeignKey("kewo_explains.id",ondelete="CASCADE",onupdate="CASCADE"))
    sentences = relationship("Sentence", backref="form", passive_deletes="all")

    def __repr__(self):  # 使返回的内存对象变的可读
        return "<id:{0} name:{1}>".format(self.id, self.content)


class Word(Base):
    __tablename__ = "kewo_words"
    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String(255))
    pid = Column(String(255))
    forms = relationship("Form",foreign_keys=[Form.origin_id],backref="origin",passive_deletes="all")
    explains = relationship("Explain",backref="word",passive_deletes="all")
    sentences = relationship("Sentence", backref="word", passive_deletes="all")

    def __repr__(self):  # 使返回的内存对象变的可读
        return "<id:{0} name:{1}>".format(self.id, self.name)



class Explain(Base):
    __tablename__ = "kewo_explains"
    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String(255))
    content = Column(String(255))
    type = Column(Integer)
    word_id = Column(Integer, ForeignKey("kewo_words.id",ondelete="CASCADE",onupdate="CASCADE"))
    sentences = relationship("Sentence", backref="explain", passive_deletes="all")
    forms = relationship("Form", backref="explain",passive_deletes="all")

    __table_args__ = (
        Index('word_id', 'word_id'),
    )

    def __repr__(self):  # 使返回的内存对象变的可读
        return "<id:{0} name:{1}>".format(self.id, self.name)

class Sentence(Base):
    __tablename__ = "kewo_sentences"
    id = Column(Integer(),primary_key=True)
    content = Column(String(255))
    content_zh = Column(String(255))
    source = Column(String(255))
    word_id = Column(Integer, ForeignKey("kewo_words.id",ondelete="CASCADE",onupdate="CASCADE"))
    explain_id = Column(Integer, ForeignKey("kewo_explains.id",ondelete="CASCADE",onupdate="CASCADE"))
    form_id = Column(Integer, ForeignKey("kewo_forms.id",ondelete="CASCADE",onupdate="CASCADE"))


