This Github contains everything necessary to run a highly scalable simulation of Planet 9 experiencing a stellar flyby. The sim operates by
first tracking the resonance of Pluto and Neptune with no activity over the given timescale, then looping over the specified number of runs to 
generate Planet 9 with realistic parameters, then generates a close flyby 25% of the way through the time interval. The flyby's mass is sampled from Saltpeter, 
while its speed is sampled from a Rayleigh distribution meant to roughly model relative star velocities in the Milky Way.


The sim was intended to be run on an hpc cluster, and can be efficiently run in large volumes by modifying the arguments input in the scriptRunner program. 
For use on a local device, use p9MassRun with the arguments of your choice. From there, the data can be reviewed and graphed using dataParser.ipynb. The data are organized into four groups: 

1.) "Clean ejections," in which the flyby ejects Planet 9 without meaningfully affecting the rest of the solar system

2.) Events in which the outer known planets (ie. Jupiter, Saturn, Uranus, and Neptune) have their orbits significantly altered (based on their orbital eccentricity). We place events in this category regardless of an ejection of Planet 9; as the goal is to see if a flyby could have ejected Planet 9 in the solar system's history, outcomes that meaningfully alter that history cannot be counted as signal.

3.) Events in which the Pluto-Neptune resonance is disrupted. This is quite similar to category 2, but with a more strict condition - whereas a slight eccentricity change might not change the Solar System, even a very small alteration to Pluto and Neptune's orbits could cause them to eventually fall out of resonance, with Pluto likely ejected in the long run. 

4.) Events in which the flyby has no effect on Planet 9 or the rest of the Solar System. This is the most common category, unless you set the flybys to come extremely close to the Sun.

Distributions for Planet 9's parameters are sourced from this paper by Brown and Batygin: https://arxiv.org/pdf/1603.05712
