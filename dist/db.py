import argparse as ap
from collections import defaultdict as dd
import cPickle as pickle
import itertools
import os
import matplotlib.pyplot as plt
import numpy as np
import random

import json
import time


import config

def gen_conn():
    global conn
    conn = MySQLdb.connect(
        host=config.db['host'],
        port=config.db['port'],
        user=config.db['username'],
        passwd=config.db['password'],
        db=config.db['db'],
        connect_timeout=5)

try:
    import MySQLdb
    conn = None
    gen_conn()
except:
    print 'Couldn\'t import mysql.'

class ErrIntegrity(BaseException): pass

def query(q, *args, **kwargs):
    c = conn.cursor()

    def execute():
        c.execute(q, args)
        ret = c.fetchall()
        if len(ret) > 0:
            col_names = [e[0] for e in c.description]
            ret = [dict(zip(col_names, row)) for row in ret]
        conn.commit()
        if kwargs.get('return_autoinc'):
            assert len(ret) == 0
            return c.lastrowid
        else:
            return ret

    try:
        return execute()
    except MySQLdb.OperationalError, e:
        gen_conn()
        c = conn.cursor()
        return execute()
    finally:
        c.close()

def create_db():
    username = config.db['username']
    db_name = '%s_experiments' % username

    query('''
        CREATE TABLE experiment_metadata (
        experiment_id VARCHAR(255) NOT NULL,
        title LONGTEXT,
        PRIMARY KEY(experiment_id)
        ) Engine=InnoDB
        ''')

    query('''
        CREATE TABLE results(
        experiment_id VARCHAR(255) NOT NULL,
        trial_id BIGINT NOT NULL,
        directory LONGTEXT NOT NULL,
        function LONGTEXT NOT NULL,
        arguments LONGTEXT NOT NULL,
        title LONGTEXT,
        result LONGBLOB,
        creation_timestamp BIGINT NOT NULL,
        job_start_timestamp BIGINT,
        completion_timestamp BIGINT,
        PRIMARY KEY(experiment_id, trial_id)
        ) Engine=InnoDB''')

def trial_count(experiment_id):
    return query('''
        select count(1) cnt from results where experiment_id = %s
        ''', experiment_id)[0]['cnt']

def gen_experiment_id():
    import rtk
    while True:
        experiment_id = rtk.rand.rand_string(8)
        if trial_count(experiment_id) == 0:
            return experiment_id

def create_trial(experiment_id, trial_id, directory, function, arguments):
    print experiment_id, trial_id, directory, function, arguments
    n_results = query('''
        select count(1) cnt from results where experiment_id = %s and trial_id = %s
        ''', experiment_id, trial_id)[0]['cnt']
    assert n_results == 0
    creation_timestamp = int(time.time() * 1e6)
    args = json.dumps(arguments)
    query('''
        INSERT INTO results
        (experiment_id, trial_id, directory, function, arguments, creation_timestamp)
        VALUES
        (%s, %s, %s, %s, %s, %s)
        ''', experiment_id, trial_id, directory, function, args, creation_timestamp)

def _iter_failed_trials(experiment_id):
    n_failed, n_total = 0, 0
    for row in query('''
        SELECT trial_id
        FROM results
        WHERE experiment_id = %s and completion_timestamp is null
        ''', experiment_id):
        n_total += 1
        yield (experiment_id, row['trial_id'])

def iter_failed_trials(experiment_ids):
    return itertools.chain(*[
        _iter_failed_trials(eid) for eid in experiment_ids.split(',')
        ])

def fetch_args(experiment_id, trial_id):
    for row in query('''
        select directory, function, arguments from results
        where experiment_id = %s and trial_id = %s
        ''', experiment_id, trial_id):
        return row['directory'], row['function'], json.loads(row['arguments'])
    assert False  

def fetch_title(experiment_id):
    for row in query('''
        select title from experiment_metadata
        where experiment_id = %s
        ''', experiment_id):
        return row['title']
    return None  

def mark_start(experiment_id, trial_id):
    start_time = int(time.time() * 1e6)
    query('''
        UPDATE results SET job_start_timestamp = %s
        WHERE experiment_id = %s AND trial_id = %s
        ''', start_time, experiment_id, trial_id)

def mark_done(experiment_id, trial_id, results):
    completion = int(time.time() * 1e6)
    results = pickle.dumps(results, pickle.HIGHEST_PROTOCOL)
    query('''
        UPDATE results 
        SET completion_timestamp = %s, result = %s
        WHERE experiment_id = %s AND trial_id = %s
        ''', completion, results, experiment_id, trial_id)

def _iter_results(experiment_id):
    n_failed, n_total = 0, 0
    for row in query('''
        SELECT function, trial_id, arguments, job_start_timestamp, completion_timestamp, result
        FROM results
        WHERE experiment_id = %s
        ''', experiment_id):
        n_total += 1

        try:
            args = json.loads(row['arguments'])
            duration = row['completion_timestamp'] - row['job_start_timestamp']
            result = pickle.loads(row['result'])
            yield (row['function'], args, duration, result)
        except:
            #print "Failed on", row
            n_failed += 1
            continue
    if n_failed:
        print '%d failed out of %d in iter_results(%s)' % (n_failed, n_total, experiment_id)

def iter_results(experiment_ids):
    return itertools.chain(*[
        _iter_results(eid) for eid in experiment_ids.split(',')
        ])

def completion_counts(experiment_id):
    for row in query('''
        SELECT SUM(if(result is not null, 1, 0)) n_completed,
            COUNT(1) n_started
        FROM results
        WHERE experiment_id = %s
        ''', experiment_id):

        return row['n_completed'], row['n_started']

def last_experiment():
    for row in query('''
        SELECT experiment_id FROM results
        WHERE result IS NOT NULL
        ORDER BY completion_timestamp DESC
        LIMIT 1
        '''):
        return row['experiment_id']

def set_title(experiment_id, title):
    query('''
        insert into experiment_metadata
        (experiment_id, title)
        values (%s, %s)
        on duplicate key update title = %s
        ''', experiment_id, title, title)
