#Basic rebound imports
print("Basic imports!\n", end="", flush=True)

import numpy as np
import random
import rebound
from scipy.spatial.transform import Rotation as R
import argparse
import json
import re
import ast

print("Basic imports complete!\n", end="", flush=True)

parser = argparse.ArgumentParser(description='Runs a large number of Planet 9 simulations')
parser.add_argument('-r','--numRuns', help='Number of runs of the sim per distance', required=True)
parser.add_argument('-d','--numDists', help='Number of different star distances', required=True)
parser.add_argument('-t','--time', help='Duration of the sim, in years', required=True)
parser.add_argument('-ts','--timeSteps', help='Number of time steps in the sim', required=True)
parser.add_argument('-in','--instance', help='Instance of the Sim', required=True)

args = vars(parser.parse_args())

numRuns = int(args['numRuns'])
numDists = int(args['numDists'])
timeRange = int(args['time'])
timeStepsArg = int(args['timeSteps'])
instanceArg = int(args['instance'])

writeChar = 'a'


print(f"Number of runs: {numRuns}\n", end="", flush=True)

#Some standard astrophysical constants
au2m       = 1.49598e11
days2sec    = 86400.
years2sec    = 31557600.7
mSun_kg     = 1.98892e30;
mEarth_kg   = 5.9742e24;
mJupiter_kg = 1.8987e27;
G_Nm2pkg2   = 6.67384e-11;

#Download NASA's data on the planets
sim = rebound.Simulation()
sim.units = ('m', 's', 'kg')
planetList = ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
time = "2020-01-01 00:00"

with open('OrbitalData.txt', 'r', encoding='utf-8') as file:
    for line in file:
            line = re.sub(r"np\.float64\((.*?)\)", r"\1", line)
            line = re.sub(r"array\((.*?)\)", r"\1", line)
            planetsDict = ast.literal_eval(line)
            
print(f"Orbits fetched!\n", end="", flush=True)

print("Importing p9Functions\n", end="", flush=True)

#Import our functions
from p9Functions import trackResonantArgument, addPlanet9, goodResonance, checkForEjection, checkForPerturbation, flybyDist, pdf2cdf, sampling, generateStars, tiltVector, addFlybyStarUpgraded, runSimWithP9, runDummySim, addPlanet9Random
print("p9Functions imported!\n", end="", flush=True)

### FIRST WE RUN A BASIC SIM OF THE SOLAR SYSTEM TO GET COMPARATIVE DATA ###
print("Running dummy solar system!")
timeArray, trueEccentricities, truePNRes, truePRatios = runDummySim(timeRange, timeStepsArg, planetsData = planetsDict)
print("Dummy solar system run successfully!")

### NOW WE BEGIN THE ACTUAL SIM ###
maxDistances = np.linspace(1000, 1000, numDists)
totRuns = numDists*numRuns

massList, vList = generateStars(totRuns)

perturbedRuns = []
offResRuns = []
cleanEjectionRuns = []
noActivityRuns = []

planetsPerturbedElim = 0
planetsEjectedElim = 0
offResElim = 0
cleanEject = 0
noEffect = 0

currentRun = 0


print("Starting the loop!\n", end="", flush=True)

print(f"Looping over {totRuns} runs\n", end="", flush=True)

for distance in maxDistances:
    for iteration in range(int(numRuns)):
        currentRun += 1
        print(f"\nBEGINNING RUN! MAX DISTANCE: {distance} AU, ITERATION: {iteration}; TOTAL PROGRESS: {currentRun}/{totRuns}")
        times, positionalData, resonance, ejectedList, perturbedList, deltaEP9 = runSimWithP9(
            endTime = timeRange, 
            timeSteps = timeStepsArg,
            planetsData = planetsDict,
            ResArgData = truePNRes,
            PRatioData = truePRatios,
            eccentricityData = trueEccentricities,
            spawnDist = 5000*au2m, 
            maxDist = distance*au2m
            )

        print("Run complete! Processing now.\n", end="", flush=True)
        
        if (len(perturbedList) == 1 and "Planet 9" not in perturbedList) or len(perturbedList) > 1:
            perturbedRuns.append(deltaEP9)
            print(f"Planet(s) unacceptably perturbed: {perturbedList}\n", end="", flush=True)
            planetsPerturbedElim += 1

            if planetsPerturbedElim == 1:
                with open("storedGraphs/perturbedGraph.txt", str(writeChar)) as output:
                    json.dump(positionalData, output)
            
        elif len(ejectedList) > 1 or (len(ejectedList) == 1 and "Planet 9" not in ejectedList):
            perturbedRuns.append(deltaEP9)
            print("Known planet(s) ejected: {ejectedList}\n", end="", flush=True)
            planetsEjectedElim += 1

            if planetsEjectedElim == 1:
                with open("storedGraphs/ejectedGraph.txt", str(writeChar)) as output:
                    json.dump(positionalData, output)
            
        elif resonance == False:
            offResRuns.append(deltaEP9)
            print("Pluto-Neptune resonance distrupted\n", end="", flush=True)
            offResElim += 1

            if offResElim == 1:
                with open("storedGraphs/offResonanceGraph.txt", str(writeChar)) as output:
                    json.dump(positionalData, output)

        elif len(ejectedList) == 1 and "Planet 9" in ejectedList:
            cleanEjectionRuns.append(deltaEP9)
            print("Clean ejection!\n", end="", flush=True)
            cleanEject += 1
            if cleanEject == 1:
                with open("storedGraphs/cleanEjectionGraph.txt", str(writeChar)) as output:
                    json.dump(positionalData, output)
                    
        else:
            noActivityRuns.append(deltaEP9)
            print("Nothing happened.\n", end="", flush=True)
            noEffect += 1
            if noEffect == 1:
                with open("storedGraphs/noActivityGraph.txt", str(writeChar)) as output:
                    json.dump(positionalData, output)
                    

with open("perturbedRuns.txt", str(writeChar)) as output:
    output.write('\n'.join(str(item) for item in perturbedRuns) + '\n')

with open("offResonanceRuns.txt", str(writeChar)) as output:
    output.write('\n'.join(str(item) for item in offResRuns) + '\n')

with open("cleanEjectionRuns.txt", str(writeChar)) as output:
    output.write('\n'.join(str(item) for item in cleanEjectionRuns) + '\n')

with open("noActivityRuns.txt", str(writeChar)) as output:
    output.write('\n'.join(str(item) for item in noActivityRuns) + '\n')


writeDict = {"RUN":instanceArg, "CLEAN EJECT":cleanEject, "PLANETS PERTURBED":planetsPerturbedElim, "PLANETS EJECTED":planetsEjectedElim, "OFF RESONANCE":offResElim, "NO EFFECT":noEffect}

with open("writeData.txt", str(writeChar)) as output:
    json.dump(writeDict, output)
    output.write("\n")
    
print("All done!")
