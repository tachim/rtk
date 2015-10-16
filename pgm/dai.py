import os
import subprocess

def exact_marginals(fg_filename):
    assert fg_filename.endswith('.fg')
    print 'Running libDAI'
    path = os.path.join(os.path.dirname(__file__), 'run_jtree')
    p = subprocess.Popen([path, fg_filename],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
    p.wait()
    output = p.stdout.read().split('\n')
    # line format ({xi}, (%f, %f))
    marginals = [float(l.split()[2][:-2]) for l in output if l.startswith('(')]
    return marginals

def exact_log_partition(fg_filename):
    assert False, "TODO tudor implement this"
    assert fg_filename.endswith('.fg')
    print 'Running libDAI'
    p = subprocess.Popen(['./run_libdai', fg_filename],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
    p.wait()
    print 'Done.'
    output = p.stdout.read().split('\n')
    log_partition_line = [l for l in output if l.startswith('Exact log partition')]
    exact = float(log_partition_line[0].split()[-1])
    return exact

def trwbp_upper_bound(fg_filename):
    assert fg_filename.endswith('.fg')
    print 'Running libDAI'
    p = subprocess.Popen(['./run_trwbp', fg_filename],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
    p.wait()
    print 'Done.'
    output = p.stdout.read().split('\n')
    log_partition_line = [l for l in output if l.startswith('Log partition upper bound')]
    upper_bound = float(log_partition_line[0].split()[-1])
    return upper_bound
