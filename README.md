This Github contains everything necessary to run a highly scalable simulation of Planet 9 experiencing a stellar flyby. The sim operates by
first tracking the resonance of Pluto and Neptune with no activity over the given timescale, then looping over the specified number of runs to 
generate Planet 9 with realistic parameters, then generates a close flyby 25% of the way through the time interval. The flyby's mass is sampled from Saltpeter, 
while its speed is sampled from a Rayleigh distribution meant to roughly model relative star velocities in the Milky Way.


The sim was intended to be run on an hpc cluster, and can be efficiently run in large volumes by modifying the arguments input in the scriptRunner program. 
For use on a local device, use p9MassRun with the arguments of your choice. From there, the data can be reviewed and graphed using dataParser.ipynb.


Distributions for Planet 9's parameters are sourced from this paper by Brown and Batygin: https://arxiv.org/pdf/1603.05712
