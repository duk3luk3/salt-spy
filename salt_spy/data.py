import sqlite3
import os
import json
from pkg_resources import resource_filename
from .model import Minion


class Data:
    def __init__(self, path, populate=True):
        self.path = path
        do_populate = populate and not os.path.exists(path)
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys = 1")
        self.conn.commit()
        if do_populate:
            schema = resource_filename(__name__, 'schema.sql')
            self.populate(schema)

    def populate(self, schema):
        cursor = self.conn.cursor()
        with open(schema) as f:
            sql = f.read()
        cursor.executescript(sql)
        self.conn.commit()

    def get_minions(self, minion_id=None, minion_name=None):
        cursor = self.conn.cursor()
        if minion_id is not None:
            query = "SELECT * from minion WHERE minion_id=?"
            result = cursor.execute(query, (minion_id,))
        elif minion_name is not None:
            query = "SELECT * from minion where name=?"
            result = cursor.execute(query, (minion_name,))
        else:
            query = "SELECT * from minion"
            result = cursor.execute(query)
        return [Minion(minion_id, minion_name) for minion_id, minion_name in result]

    def insert_minion(self, minion_name):
        cursor = self.conn.cursor()
        query = "INSERT INTO minion (name) VALUES (?)"
        cursor.execute(query, (minion_name,))
        return cursor.lastrowid

    def insert_run(self, minion_id, ret_time, is_test, user):
        cursor = self.conn.cursor()
        query = "INSERT INTO run (minion_id, ret_time, is_test, user) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (minion_id, ret_time, is_test, user))
        return cursor.lastrowid

    def insert_state(self, run_id, function, changes, bag):
        cursor = self.conn.cursor()
        query = "INSERT INTO state (run_id, function, changes, __id__, __sls__, __run_num__, comment, name, start_time, duration, result) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(query, (run_id, function, changes, bag['__id__'], bag['__sls__'], bag['__run_num__'], bag['comment'], bag['name'], bag['start_time'], bag['duration'], bag['result']))
        return cursor.lastrowid

    def insert_state_run(self, run):
        cursor = self.conn.cursor()
        minions = self.get_minions()
        minions_name_to_id = {m_name: m_id for m_name, m_id in [(m.name, m.minion_id) for m in minions]}
        sls_name_to_id = {}
        state = json.loads(run)
        print(state)
        ret_time = state['__ret_tm']
        user = state['__user']
        test = state['__test']
        state_ret = state['__run']
        print(state_ret)
        for minion_name, run_ret in state_ret.items():
            print(minion_name)
            if minion_name not in minions_name_to_id:
                minion_id = self.insert_minion(minion_name)
                minions_name_to_id[minion_name] = minion_id
            else:
                minion_id = minions_name_to_id[minion_name]
            run_id = self.insert_run(minion_id, ret_time, test, user)
            for run_key, run_val in run_ret.items():
                key_comps = run_key.split('_|-')
                function = key_comps[0] + '.' + key_comps[3]
                changes = json.dumps(run_val['changes'])
                self.insert_state(run_id, function, changes, run_val)
        self.conn.commit()






