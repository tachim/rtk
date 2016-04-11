import os
import subprocess

def exact_marginals(fg_filename):
    assert fg_filename.endswith('.fg')
    path = os.path.join(os.path.dirname(__file__), 'run_jtree')
    p = subprocess.Popen([path, fg_filename],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
    p.wait()
    output = p.stdout.read().split('\n')
    # line format ({xi}, (%f, %f))
    marginals = [float(l.split()[2][:-2]) for l in output if l.startswith('(')]
    return marginals

def _logZ_runner(filename, option):
    p = subprocess.Popen([os.path.join(os.path.dirname(__file__), 'run_dai_logz'), filename, option],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
    p.wait()
    output = p.stdout.read().split('\n') + p.stderr.read().split('\n')
    if any('not converged' in l for l in output):
        print 'WARNING: FAILED TO CONVERGE!'
    log_partition_line = [l for l in output if l.startswith('Log partition')]
    logZ = float(log_partition_line[0].split()[-1])
    return logZ

def mf_logZ(filename):
    return _logZ_runner(filename, 'MF')

def trwbp_logZ(filename):
    return _logZ_runner(filename, 'TRWBP')

def bp_logZ(filename):
    return _logZ_runner(filename, 'BP')

def jtree_logZ(filename):
    return _logZ_runner(filename, 'JTREE')
