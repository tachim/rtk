import subprocess

def run(cmd, capture_stdout=True):
    if capture_stdout:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        ret = []
        for line in iter(process.stdout.readline, ''):
            ret.append(line.strip())
            print line.strip()
        retval = process.wait()
        assert retval == 0
        return '\n'.join(ret)
    else:
        retval = subprocess.Popen(cmd).wait()
        assert retval == 0
