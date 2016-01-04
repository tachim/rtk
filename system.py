import subprocess
import tempfile

class RetCode(Exception): pass

def run(cmd, capture_stdout=True, ignore_ret=False, print_stdout=False):
    if capture_stdout:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        ret = []
        for line in iter(process.stdout.readline, ''):
            ret.append(line.strip())
            if print_stdout:
                print line.strip()
        retval = process.wait()
        if retval != 0 and not ignore_ret: raise RetCode()
        return '\n'.join(ret)
    else:
        retval = subprocess.Popen(cmd).wait()
        if retval != 0 and not ignore_ret: raise RetCode()

tmpf = tempfile.mkstemp
