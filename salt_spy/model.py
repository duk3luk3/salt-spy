from sqlalchemy import Column, Integer, Float, String, DateTime, Time, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import json
from datetime import datetime

Base = declarative_base()

class Return(Base):
    __tablename__ = 'salt_returns'

    fun = Column(String)
    jid = Column(String, ForeignKey('jids.jid'))
    mid = Column('id', String)
    fun_args = Column(String)
    date = Column(String)
    full_ret = Column(String)
    success = Column(String)
    rid = Column(Integer, primary_key=True)


    def full_ret_obj(self):
        if not hasattr(self, '_full_ret_obj'):
            self._full_ret_obj = json.loads(self.full_ret)
        return self._full_ret_obj

    def ret_fun(self):
        return self.full_ret_obj()['fun']

    def ret(self):
        return self.full_ret_obj().get('return')

    def is_test(self):
        return 'test=True' in self.full_ret_obj()['fun_args']

    def is_error(self):
        return '_error' in self.full_ret_obj()

    def is_state(self):
        return not self.is_error() and self.fun.startswith('state.')

    def user(self):
        return self.job.load_obj().get('user')

    def sls(self):
        if self.is_state():
            ret = []
            for state in self.ret().values():
                sls = state['__sls__']
                if not sls in ret:
                    ret.append(sls)
            return ret
        else:
            return None

    def _decode_state(self, state):
        key, val = state
        function_comps = key.split('_|-')
        function = function_comps[0] + '.' + function_comps[-1]

        return {
            'function': function,
            'name': val.get('name', function_comps[1]),
            'sls': val['__sls__'],
            'result': val['result'],
            'comment': val['comment']
            }


    def states(self):
        if self.is_state():
            return [self._decode_state(state) for state in self.ret().items()]
        else:
            return None

class Job(Base):
    __tablename__ = 'jids'

    jid = Column(String, primary_key=True)
    load = Column(String)

    returns = relationship("Return", backref='job')

    def load_obj(self):
        if not hasattr(self, '_load_obj'):
            self._load_obj = json.loads(self.load)
        return self._load_obj

class Minion:
    def __init__(self, mid, returns):
        self.mid = mid
        self.returns = returns

    def apply_age(self):
        if not hasattr(self, '_apply_age'):
            last_apply = None
            for r in reversed(self.returns):
                if r.fun == 'state.apply':
                    last_apply = r
                    break
            if last_apply:
                # 2017-10-13 02:49:04.513147
                apply_time = datetime.strptime(r.date, '%Y-%m-%d %H:%M:%S.%f')
                apply_age = datetime.now() - apply_time
                self._apply_age = apply_age.days
            else:
                self._apply_age = None
        return self._apply_age

    @staticmethod
    def from_returns(returns):
        minions = {}

        for r in returns:
            mid = r.mid
            if not mid in minions:
                minions[mid] = Minion(mid, [])
            minions[mid].returns.append(r)

        for m in minions.values():
            m.returns.sort(key=lambda r: r.date)

        return minions


