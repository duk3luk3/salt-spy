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

    def job_args(self):
        load = self.job.load_obj()

        args = load.get('arg', [])

        nargs = []
        kwargs = []

        for arg in args:
            if '=' in arg:
                kwargs.append(arg)
            else:
                nargs.append(arg)

        return nargs, kwargs

    def full_ret_obj(self):
        if not hasattr(self, '_full_ret_obj'):
            self._full_ret_obj = json.loads(self.full_ret)
        return self._full_ret_obj

    def ret_fun(self):
        return self.full_ret_obj()['fun']

    def ret(self):
        return self.full_ret_obj().get('return')

    def is_test(self):
        nargs, kwargs = self.job_args()
        return 'test=True' in kwargs

    def is_error(self):
        return '_error' in self.full_ret_obj() or isinstance(self.full_ret_obj().get('return'), str) or isinstance(self.full_ret_obj().get('return'), list)

    def is_state(self):
        return not self.is_error() and self.fun.startswith('state.')

    def is_high(self):
        if self.fun == 'state.highstate':
            return True

        if self.fun == 'state.apply':
            nargs, kwargs = self.job_args()
            if len(nargs) > 0:
                return False
            else:
                return True

    def is_success(self):
        if self.is_error():
            return False

        if self.is_state():
            for state, state_ret in self.ret().items():
                if state_ret['result'] == False:
                    return False
            return True
        else:
            if 'retcode' in self.full_ret_obj():
                return self.full_ret_obj().get('retcode') == 0
            else:
                return None

    def user(self):
        return self.job.load_obj().get('user')

    def sls(self):
        if self.is_state():
            ret = []
            for state in self.ret().values():
                sls = state.get('__sls__')
                if sls and not sls in ret:
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
            'sls': val.get('__sls__'),
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

    def highstates(self):
        if not hasattr(self,'_highstates'):
            self._highstates = []
            for r in reversed(self.returns):
                if r.is_high() and not r.is_test():
                    self._highstates.append(r)
        return self._highstates


    def last_apply(self):
        highstates = self.highstates()
        if highstates:
            return highstates[0]
        else:
            return None

    def apply_age(self):
        last_apply = self.last_apply()
        if last_apply:
            # 2017-10-13 02:49:04.513147
            apply_time = datetime.strptime(last_apply.date, '%Y-%m-%d %H:%M:%S.%f')
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


