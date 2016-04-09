# rtk                                                         
                                                              
This is [Tudor's](https://cs.stanford.edu/~tachim/) toolkit of helper methods for research code (**R**esearch **T**ool**k**it). 

The main modules you might be interested in are: [real-time plotting](https://github.com/tachim/rtk/blob/master/plot.py) in matplotlib, [python wrappers for libDAI](https://github.com/tachim/rtk/tree/master/pgm), and [abstractions](https://github.com/tachim/rtk/tree/master/dist) for running experiments on clusters without the overhead of managing logfiles. The other modules implemented in `rtk` are also quite useful but not summarized in this README right now.

### Real-time Plotting
To use the real-time plotting code simply call `rtk.plot.plot_rt_point(key, datapoint)` where `key` is the name of the data stream and `datapoint` is the value of the datapoint. If you have matplotlib up and running this will start plotting real-time data on your screen, with the default being second-by-second updates. Quite useful for tracing error curves and other statistics of your programs!

### Python wrappers for libDAI
Here's an example of calculating statistics of an Ising model, all from python, via calls to the python wrapper:
```python
W, f = rtk.pgm.ising.generate_grid(10, w=5, field=5)
with rtk.pgm.ising.IsingWriter(W, f) as filename:
    gt_logZ = rtk.pgm.dai.jtree_logZ(filename)
    gt_marginals = rtk.pgm.dai.exact_marginals(filename)
```
### Distributed Experiment Management
Running your code in a distributed way on your cluster is super easy. These instructions assume you're using PBS and are tested thoroughly on the Stanford clusters, but it's trivial to modify `rtk.dist.mgr` to handle other cluster systems.

1. Install MySQL and make sure it's somewhere accessible from your cluster machines.
2. Configure `rtk.dist.config` with the authentication/connection information of your database.
3. Run `rtk.dist.db.create_db()` to create the experiment results table.
4. Use it in your code!

```python
@rtk.dist.mgr.distributed
def run_trial(seed, sidelength, weight, method):
   your_code_here()

with rtk.dist.mgr.Dist(os.path.realpath(__file__)):
    for i, (weight, trial, sidelength) in enumerate(params):
        for method in ('structure', 'anneal'):
            run_trial(seed=trial, sidelength=sidelength, weight=weight, method=method)
```
Once this is running, go ahead and use the swiss-army knife analysis script to quickly get a handle on the results:
```
$ python ~/w/rtk/dist/analyze.py last seed method 1
Connecting to MySQL... (should print Done. in a second)
Done.
Experiment is AKiZqyiR
Analyzing logs for 60 results
(6, 0.5, u'anneal') 26.2050488941
(6, 0.5, u'structure') 26.2050408031
...
(6, 8, u'anneal') 132.173964493
(6, 8, u'structure') 132.173962252
```
which tells the script to look at the **last** experiment, aggregating along key **seed** (these correspond to our trials), and making sure to put the **method** key last so we can quickly compare the results. So we can see that there's not much difference between the methods above :).

## Status
                                                              
### Implemented                                                
* Timing module (`rtk.timing`)                                
* Stats tracking (`rtk.stats`)                                
* Debugging module (`rtk.debug`)                              
* libDAI python interface (`rtk.pgm.dai`)                     
* Parallel run module (`rtk.par`)                          

