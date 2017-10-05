from sqlalchemy import Column, Integer, Float, String, DateTime, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Minion(Base):
    __tablename__ = 'minion'

    minion_id = Column(Integer, primary_key=True)
    name = Column(String)

class StateRun(Base):
    __tablename__ = 'run'

    run_id = Column(Integer, primary_key=True)
    minion_id = Column(Integer, ForeignKey('minion.minion_id'))
    ret_time = Column(DateTime)
    is_test = Column(Boolean(create_constraint=True))
    user = Column(String)

    minion = relationship('Minion', backref='runs')

    def sls(self):
        ret = []
        for state in self.states:
            if not state.sls in ret:
                ret.append(state.sls)
        return ret

class StateExecution(Base):
    __tablename__ = 'state'

    state_id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey('run.run_id'))
    function = Column(String)
    salt_id = Column('__id__', String)
    sls = Column('__sls__', String)
    run_num = Column('__run_num__', Integer)
    comment = Column(String)
    changes = Column(String)
    name = Column(String)
    start_time = Column(Time)
    duration = Column(Float)
    result = Column(Boolean(create_constraint=True))

    run = relationship('StateRun', backref='states')

