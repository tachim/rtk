import functools
import json
import os
import socket

import rtk

in_dist_creation = False
job_buffer = []

def distributed(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        assert args == (), args
        kwargs = json.dumps(kwargs)
        kwargs = json.loads(kwargs)
        if not in_dist_creation:
            print 'Calling', f.__name__, 'with args', kwargs
            ret = f(**kwargs)
            print 'Result:', ret
            return ret
        else:
            job_buffer.append((f.__name__, kwargs))
    return wrapper

class Dist(object):
    def __init__(self, module_filename, walltime='00:10:00', ppn=1):
        self.ignore_dist = 'scail' not in socket.gethostname()
        self.path = os.path.dirname(module_filename)
        self.module = os.path.splitext(os.path.basename(module_filename))[0]

        self.walltime = walltime
        self.ppn = ppn

    def __enter__(self):
        global in_dist_creation
        if not self.ignore_dist:
            assert in_dist_creation is False
            in_dist_creation = True

    def __exit__(self, typ, val, tb):
        if not self.ignore_dist:
            global in_dist_creation
            in_dist_creation = False

            if typ is not None:
                return

            experiment_id = create_jobs(self.path, self.module, self.walltime, self.ppn)
            print "Created experiment %s" % experiment_id

def runner_fname():
    return os.path.join(os.path.realpath(os.path.dirname(__file__)), 'run.py')

def create_jobs(run_directory, module, walltime, ppn):
    experiment_id = rtk.dist.db.gen_experiment_id()

    commands, outputfiles = [], []
    trial_creations = []
    for trial_id, (function_name, args) in enumerate(job_buffer):
        module_func = '.'.join([module, function_name])

        trial_creations.append((experiment_id, trial_id, run_directory, module_func, args))
        command = 'python %s %s %s' % (runner_fname(), experiment_id, trial_id)
        outputfile = os.path.join(rtk.dist.config.output_dir, '%s_%s.log' % (experiment_id, trial_id))

        commands.append(command)
        outputfiles.append(outputfile)

    base_args = {
            'jobname': experiment_id,
            'queue': 'atlas',
            'walltime': walltime,
            'ppn': ppn,
            'outputfile_dir': rtk.dist.config.output_dir,
            }

    title = rtk.dist.pbs.run(base_args, commands, outputfiles)
    for trial_creation in trial_creations:
        rtk.dist.db.create_trial(*trial_creation)
    rtk.dist.db.set_title(experiment_id, title)

    return experiment_id
