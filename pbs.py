__doc__ = """

Based on JoHo's original code.

"""

import os
import subprocess
import tempfile

def create_pbs_script(
        commands, outputfiles, jobname, queue, nodes, outputdir,
        walltime, ppn=1):
    assert len(commands) == len(outputfiles)
    template = '''#!/bin/bash

#PBS -l walltime={total_wall_hhmmss},nodes={nodes}
#PBS -j oe
#PBS -N {jobname}
#PBS -q {queue}
#PBS -o {outputdir}/$PBS_JOBNAME.out

read -r -d '' COMMANDS << END
{cmds_str}
END
cmd=$(echo "$COMMANDS" | awk "NR == $PBS_ARRAYID")
echo $cmd

read -r -d '' OUTPUTFILES << END
{outputfiles_str}
END
outputfile=$(echo "$OUTPUTFILES" | awk "NR == $PBS_ARRAYID")
echo $outputfile
# Make sure output directory exists
mkdir -p "`dirname \"$outputfile\"`" 2>/dev/null

SLEEP_TIME=$(( ( RANDOM % {sleep_sec}) + 1))
sleep $SLEEP_TIME

cd $PBS_O_WORKDIR
echo "RUNNING ON $HOSTNAME" > $outputfile
echo DIRECTORY IS $PBS_O_WORKDIR &>> $outputfile
pwd &>> $outputfile
ls &>> $outputfile
echo "AFS SLEEP $SLEEP_TIME" >> $outputfile
START_TIME=$( date +%s.%N )
eval "timeout {timeout_n_sec} $cmd" &>> $outputfile
END_TIME=$( date +%s.%N )
echo "PBS DURATION: $(echo $END_TIME - $START_TIME | bc)" >> $outputfile
'''
    hh, mm, ss = map(int, walltime.split(':'))

    timeout_n_sec = hh * 3600 + mm * 60 + ss
    sleep_sec = 60
    wall_sec = timeout_n_sec + sleep_sec + 20

    total_wall_hh = wall_sec / 3600
    total_wall_mm = (wall_sec % 3600) / 60
    total_wall_ss = wall_sec % 60
    total_wall_hhmmss = '%2.2d:%2.2d:%2.2d' % (total_wall_hh, total_wall_mm, total_wall_ss)

    nodes='+'.join('%s:ppn=%s,mem=5gb' % (node, ppn) for node in nodes)
    return template.format(
        jobname=jobname,
        queue=queue,
        cmds_str='\n'.join(commands),
        outputfiles_str='\n'.join(outputfiles),
        nodes=nodes,
        outputdir=outputdir,
        total_wall_hhmmss=total_wall_hhmmss,
        sleep_sec=sleep_sec,
        timeout_n_sec=timeout_n_sec)

def run(base_args, commands, outputfiles):
    jobname = base_args['jobname']
    nodes = base_args.get('nodes', '1')
    queue = base_args['queue']

    paired = zip(commands, outputfiles)
    filtered = [(cmd, fout) for cmd, fout in paired if not os.path.exists(fout)]
    if not filtered:
        return
    commands, outputfiles = zip(*filtered)

    script = create_pbs_script(
            commands, outputfiles, jobname, 
            queue, nodes, base_args['outputfile_dir'],
            walltime=base_args.get('walltime', '00:20:00'),
            ppn=base_args.get('ppn', 1))

    print script
    print 'ok?'
    raw_input()
    with tempfile.NamedTemporaryFile(suffix='.sh') as f:
        f.write(script)
        f.flush()
        subprocess.check_call('qsub -t %d-%d %s' % (1, len(commands), f.name), shell=True)

