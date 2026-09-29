import numpy as np
import rebound
import random
from scipy.spatial.transform import Rotation as R

### SIM TRACKING FUNCTIONS ### 

#Track the resonant argument of Neptune and Pluto (or really any bodies in a 2:3 resonance, but I really doubt we'll use it for anything else)
def trackResonantArgument(pomega1, pomega2, M1, M2, p = 2, q = 1):
    #Get values together
    meanLongitude1 = M1 + pomega1 #Mean Longitude = Mean Anomoly + Longitude of Pericenter
    meanLongitude2 = M2 + pomega2

    #Calculate and return resonant argument
    phi = (p+q)*meanLongitude2 - p*meanLongitude1 - q*pomega2

    return phi

#Updates our position dictionary
def trackBodies3D(timeVal, posDict, sim):
    #Each value in the dictionary is a list of lists, of the form [[t, x, y, z], [t, x, y, z], [t, x, y, z],...]
    bodyIndex = 0

    for posList in posDict.values():
        #We update our dictionary of positions
        bodyCoords = [timeVal, (sim.particles[bodyIndex].x)/1.49598e11, (sim.particles[bodyIndex].y)/1.49598e11, (sim.particles[bodyIndex].z)/1.49598e11]
        posList.append(bodyCoords)
        bodyIndex += 1

    return posDict

#Pretty simple, really
def addPlanet9(sim, parameterList, infoDict):
    SemiMajorAxis = parameterList[0]
    Perastrum = parameterList[1]
    Mass = parameterList[2]
    Inclination = parameterList[3]
    Eccentricity = 1-Perastrum/SemiMajorAxis

    #Randomize omega, so that we don't bias the system by putting Planet 9 in a particular position
    pomegaParam = np.random.rand() * np.pi

    sim.add(m=Mass, a = SemiMajorAxis, e = Eccentricity, inc = Inclination, pomega = pomegaParam)

    infoDict.update({"Planet 9":[]})

    return sim, infoDict



def addPlanet9Random(sim, infoDict, fullReturn = False):
    #First we have to randomize the mass
    Mass = (5 + 15*random.random())*5.9742e24 #Random value between 5 and 20 Earth masses
    #print(Mass)

    #Now we generate a random semi-major axis and eccentricity by feeding the mass we've generated into Batygin's linear fit
    validVals = False
    while validVals == False:
        SemiMajorAxis = random.uniform((200 + 30*Mass/5.9742e24)*1.49598e11, (600 + 20*Mass/5.9742e24)*1.49598e11) #Randomly sample between two bounds scaled to the mass
        Eccentricity = 0.75 - ((250 + 20*Mass/5.9742e24)*1.49598e11/SemiMajorAxis)**8 #Eccentricity is just a function of semi-major axis, per Batygin et al.

        if Eccentricity >= 0:
            validVals = True #Occasionally we seem to get negative eccentricity from Batygin's equations; this prevents that

    #Now we need to find the inclination and pomega
    #Batygin's results suggest Inclination must be between 22 and 40 degrees, with 30 heavily favored. Thus, we sample from a tight distribution about 30, ensuring we keep close to that
    InclinationDegrees = np.random.normal(30, 1) #First find I in degrees
    Inclination = InclinationDegrees * 0.0174533 #Rebound takes the inclination in radians, so we convert

    #Next we decide omega. Batygin suggests that it must be between 120 and 160 degrees; we sample randomly from this range
    littleOmegaDegrees = (120 + 40*random.random())
    littleOmega = littleOmegaDegrees * 0.0174533

    #Lastly, we randomize where its position is along its orbit. We do this by randomizing theta
    TrueLongitude = random.random()*2*np.pi

    infoDict.update({"Planet 9":[]})
    
    sim.add(m=Mass, a = SemiMajorAxis, e = Eccentricity, inc = Inclination, omega = littleOmega, theta = TrueLongitude)
    if fullReturn == False:
        return sim, infoDict

    else: 
        return sim, infoDict, Mass/5.9742e24, SemiMajorAxis/1.49598e11, Eccentricity, Inclination, littleOmega, TrueLongitude


def goodResonance(resonanceData, periodRatioData, normalResArg, normalPRatio):
    badResPoints = []
    badPPoints = []
    
    for x in range(3501, 4000):
        if abs(resonanceData[x]) < abs(normalResArg[x] * 0.95) or abs(resonanceData[x]) > abs(normalResArg[x] * 1.05):
            badResPoints.append(x)

        if abs(periodRatioData[x]) < abs(normalPRatio[x] * 0.95) or abs(periodRatioData[x]) > abs(normalPRatio[x] * 1.05):
            badPPoints.append(x)

    if len(badResPoints) == 0 and len(badPPoints) == 0:
        return True, badResPoints, badPPoints

    else: 
        return False, badResPoints, badPPoints

#Function to check if any of the planets were ejected during the process
def checkForEjection(sim, maxPlanetIndex, infoDict):
    ejectedIndices = []

    for x in range(1, maxPlanetIndex): #Every planet; we start at 1 to skip the sun
        eccentricity = sim.particles[x].e
        if eccentricity > 1 or eccentricity < 0:
            ejectedIndices.append(x)

    return ejectedIndices

#Function to see if any planets had significant changes to eccentricity during the process
def checkForPerturbation(sim, maxPlanetIndex, startingEccentricityVals, infoDict):
    skewedIndices = []

    for x in range(1, maxPlanetIndex): #Every planet; we start at 1 to skip the sun
        eccentricity = sim.particles[x].e
        #Check whether the new eccentricity is significantly larger or smaller than the previous value
        if eccentricity > 1.1*startingEccentricityVals[x] or eccentricity < 0.9*startingEccentricityVals[x]:
            skewedIndices.append(x)

    return skewedIndices


#Now we can find the shortest distance between the sun and the flyby star:
def flybyDist(allBodiesDict, Body1 = "Sun"):
    sunX = [entry[1] for entry in allBodiesDict[str(Body1)]]
    sunY = [entry[2] for entry in allBodiesDict[str(Body1)]]
    sunZ = [entry[3] for entry in allBodiesDict[str(Body1)]]

    flybyX = [entry[1] for entry in allBodiesDict["Flyby Star"]]
    flybyY = [entry[2] for entry in allBodiesDict["Flyby Star"]]
    flybyZ = [entry[3] for entry in allBodiesDict["Flyby Star"]]

    minDist = 10**80

    for x in range(len(flybyX)):
        sunIndex = x + (len(sunX) - len(flybyX))
        distance = np.sqrt((sunX[sunIndex] - flybyX[x])**2 + (sunY[sunIndex] - flybyY[x])**2 + (sunZ[sunIndex] - flybyZ[x])**2)
        if distance < minDist:
            minDist = distance

    return minDist

### FUNCTIONS FOR RANDOMIZING STAR STATS ###

#Function to convert PDF to CDF
def pdf2cdf(pdf, x):
    delta_x = np.gradient(x) # Compute bin widths
    area = pdf * delta_x # Element-wise multiplication
    cdf = np.cumsum(area) # Cumulative sum to get CDF
    cdf /= cdf[-1]  # Normalize CDF

    return cdf

#Sampling Function
def sampling(numberSamples, cdf, x):
    randomNumbers = np.random.rand(numberSamples) # Generate random numbers
    indices = np.searchsorted(cdf, randomNumbers) #Binary search in CDF
    sampledx = x[indices] # Map to x-values
    sampledy = cdf[indices] #map to y-values

    return sampledx, sampledy

#Star generator function - runs all of the steps necessary to generate any number of stars.
def generateStars(numStars):
    #Get our mass sample using the Saltpeter Mass function
    mass = np.linspace(0.1, 3, 10000)  # Mass array
    N = 1.35 / (0.1**(-1.35) - 3**(-1.35))
    delta_m = np.gradient(mass)  # Compute mass bin widths
    pdfStellarMass = N * (mass**(-2.35)) * (delta_m / 1.0)
    cdfStellarMass = pdf2cdf(pdfStellarMass, mass)
    massSample = sampling(int(numStars), cdfStellarMass, mass)


    #Now for velocity
    velocity = np.linspace(10, 140, 10000)  # Velocity array
    pdfVelocity = (velocity/(21**2) * np.exp((-velocity**2) / (2*(21**2)))) #Rayleigh distribution
    cdfVelocity = pdf2cdf(pdfVelocity, velocity)
    vSample = sampling(int(numStars), cdfVelocity, velocity)


    massReturn = np.array(massSample[0])
    velocityReturn = np.array(vSample[0])


    return massReturn * 1.98892e30, velocityReturn * 1000 #Convert to m/s

### FUNCTIONS TO ACTUALLY ADD THE FLYBY ###
#This function will help with our modeling in a few places. There's probably one available on a library somewhere, but I figured it would
#be simplest to just make it myself.
def randomVector(magnitude):

    #Generate a random 3D vector
    random_rotation = R.random()
    random_direction = random_rotation.apply([0, 0, 1])


    #Convert to cartesian coordinates
    xVal = magnitude*random_direction[0]
    yVal = magnitude*random_direction[1]
    zVal = magnitude*random_direction[2]

    #Return the vector as a list
    return [xVal, yVal, zVal]


#First we need a function to do all of the evil linear algebra for us
def tiltVector(maxAngle, inputV):
    cosTheta = np.random.uniform(np.cos(maxAngle), 1.0)
    sinTheta = np.sqrt(1 - cosTheta**2)
    phi = np.random.uniform(0, 2*np.pi)

    randomV = np.array([
        sinTheta * np.cos(phi),
        sinTheta * np.sin(phi),
        cosTheta
    ])

    z = np.array([0.0, 0.0, 1.0])

    axis = np.cross(z, inputV)
    axis /= np.linalg.norm(axis)
    angle = np.arccos(np.dot(z, inputV))

    K = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])

    RodriguesMatrix = (
        np.eye(3)
        + np.sin(angle) * K
        + (1 - np.cos(angle)) * (K @ K)
    )

    FinalV = RodriguesMatrix @ randomV

    return FinalV

#And now we get to generate the actual flyby! This generator is the best I've developed so far, and does a pretty good job quickly creating distant stars with a preset flyby distance.
def addFlybyStarUpgraded(infoDict, mass, speed, sim, spawnDistance, maxDistance, verbose = False):
    #Generate initial condition using spherical coordinates. We'll generate all stars at a constant distance from the sun.
    #To start with, we'll make it completely random where they start on the outer sphere.
    sunPos = np.array(infoDict["Sun"][-1])
    posVector = np.array(randomVector(spawnDistance))
    starPos = np.array([(sunPos[0] + posVector[0]), (sunPos[1] + posVector[1]), (sunPos[2] + posVector[2])])

    #Now let's get our velocity vector going
    print(f"Adding star. Spawn distance: {spawnDistance/1.49598e11} AU, Max distance: {maxDistance/1.49598e11} AU, Mass: {mass} kg, Velocity: {speed} m/s")
    maxAngle = np.arctan(maxDistance/spawnDistance)

    invertedVector = posVector/-spawnDistance

    vDirection = tiltVector(maxAngle, invertedVector)
    vVector = vDirection * speed

    
    sim.add(m = mass[0],
            x = starPos[0],
            y = starPos[1],
            z = starPos[2],
            vx = vVector[0],
            vy = vVector[1],
            vz = vVector[2]
           )

    starName = "Flyby Star"
    
    if verbose == True:
        print("Star with mass of", mass, "and a velocity of", speed, "generated.")
        print("Star position vector:", starPos)
        print("Star velocity vector:", vVector)
        print("Normalized dot product:", dotProduct)

    infoDict.update({starName:[]})


    return infoDict, sim

### FUNCTION TO RUN THE SIMULATION! ###
#This function will run a basic simulation of the solar system and track the positions of the particles, as well as the resonant argument of Pluto and Neptune
def runSimWithP9(endTime, timeSteps, planetsData, ResArgData, PRatioData, eccentricityData, spawnDist, maxDist, sunMass = 1.98892e30, Verbose = False): #Input time in years; will be converted to seconds
    #Note for inputs - defining aList, eList, massList, and starMass ahead of time allows for cutting down on arguments
    #Boot up the simulation
    sim = rebound.Simulation()
    sim.units = ('m', 's', 'kg')
    au2m = 1.49598e11 #I don't like adding this, but it seems like it may be necessary
    
    #Add the star
    sim.add(m=sunMass)

    #Add our planets
    for stats in planetsData.values():
        sim.add(
            m=stats[0],
            a=stats[1],
            e=stats[2],
            inc=stats[3],
            Omega=stats[4],
            pomega=stats[5],
            M=stats[6]
        )
        
    sim.move_to_com()

    #allBodiesDict is our dictionary for tracking the positions of every body in the system
    allBodiesDict = {}
    allBodiesDict.update({"Sun":[]})
    for planetName in planetsData:
        allBodiesDict.update({planetName:[]})


    #Add planet 9 to the sim
    sim, allBodiesDict, p9M, p9A, p9E, p9I, p9omega, p9Theta = addPlanet9Random(sim, allBodiesDict, fullReturn = True)

    p9Stats = [p9M, p9A, p9E, p9I, p9omega, p9Theta]
    
    #NOTE - this needs to be changed if we ever do a different configuration of the solar system
    numPlanets = 6

    planetEccentricities = {}
    dumbWorkaroundCounter = 0

    for planetName in allBodiesDict.keys():
        #Store all planets' eccentricities
        if dumbWorkaroundCounter > 0 and dumbWorkaroundCounter <= numPlanets:
            planetEccentricities.update({str(planetName):sim.particles[dumbWorkaroundCounter].e})
        dumbWorkaroundCounter += 1

    sun = sim.particles[0]
    p9 = sim.particles[-1]
        
    #Now we quickly find the starting orbital plane of Planet 9
    r = np.array([p9.x - sun.x, p9.y - sun.y, p9.z - sun.z])
    v = np.array([p9.vx - sun.vx, p9.vy - sun.vy, p9.vz - sun.vz])

    # Orbital plane normal vector (angular momentum direction)
    h_vec = np.cross(r, v)
    planeVector = h_vec / np.linalg.norm(h_vec)  # Unit normal vector
            
    #Create our time array
    timeArray = np.linspace(0,endTime*31557600.7,timeSteps)

    spawnInterval = (endTime*31557600.7)/4

    #This sets the next spawntime
    resList = []

    PRatioList = []

    exoStarMass, exoStarV = generateStars(1)
    
    starSpawned = False

    sunStarDists = []

    p9StarDists = []

    
    for time in timeArray:

        #Check if we're due to spawn a star
        if time >= spawnInterval and starSpawned == False:
            #Now create a new star!
            allBodiesDict, sim = addFlybyStarUpgraded(
                allBodiesDict,
                exoStarMass, 
                exoStarV, 
                sim, 
                spawnDistance = spawnDist, 
                maxDistance = maxDist, 
                verbose = Verbose
                )
            
            starSpawned = True


        #Store relevant distances
        if starSpawned == True:
            sunStarDist = np.sqrt((sim.particles[0].x - sim.particles[-1].x)**2 + (sim.particles[0].y - sim.particles[-1].y)**2 + (sim.particles[0].z - sim.particles[-1].z)**2)
            sunStarDists.append(sunStarDist)


            p9StarDist = np.sqrt((sim.particles[-2].x - sim.particles[-1].x)**2 + (sim.particles[-2].y - sim.particles[-1].y)**2 + (sim.particles[-2].z - sim.particles[-1].z)**2)
            p9StarDists.append(p9StarDist)


        sim.integrate(time)
        sim.move_to_com()

        #Track where everything is
        allBodiesDict = trackBodies3D(time, allBodiesDict, sim)
        
        NeptuneOrbit = sim.particles[4].orbit(primary=sim.particles[0])
        PlutoOrbit = sim.particles[5].orbit(primary=sim.particles[0])
        
        lambdaN = NeptuneOrbit.M + NeptuneOrbit.pomega
        lambdaP = PlutoOrbit.M + PlutoOrbit.pomega
        
        phi = 3*lambdaP - 2*lambdaN - PlutoOrbit.pomega
        
        # Wrap to (-pi, pi]
        phi = np.arctan2(np.sin(phi), np.cos(phi))
        
        resList.append(np.degrees(phi))
        PRatioList.append(PlutoOrbit.P / NeptuneOrbit.P)


    #Now let's see what the damage is. First we check for ejections and perturbations
    dumbWorkaroundCounter = 0
    planetEccentricitiesFinal = {}
    ejectedPlanets = []
    perturbedPlanets = []

    for planetName in allBodiesDict.keys():
        if dumbWorkaroundCounter > 0 and dumbWorkaroundCounter <= numPlanets and planetName:
            planetEccentricitiesFinal.update({str(planetName):sim.particles[dumbWorkaroundCounter].e})

            if planetName != "Planet 9":
                planetExpectedE = eccentricityData[str(planetName)][-1]
            
            if sim.particles[dumbWorkaroundCounter].e > 1:
                ejectedPlanets.append(planetName)
                
            elif (sim.particles[dumbWorkaroundCounter].e > 1.1*float(planetExpectedE) or sim.particles[dumbWorkaroundCounter].e < 0.9*float(planetExpectedE)) and planetName != "Planet 9":
                
                print(f"\nThere's a perturbation in {planetName}'s orbit! Normal ending eccentricity: {planetExpectedE}. Simulated eccentricity: {sim.particles[dumbWorkaroundCounter].e}")

                perturbedPlanets.append(planetName)

        dumbWorkaroundCounter += 1

    print(planetEccentricitiesFinal)
        
    #Now we check for any issues with Neptune's resonance with Pluto
    resonanceStatus, badRes, badRat = goodResonance(resList, PRatioList, ResArgData, PRatioData)
    print(f"Resonance status: {resonanceStatus}")
    if starSpawned == True:
        print(f"\nMaximum distance from Sun to flyby star: {np.max(sunStarDists)/au2m} AU \nMinimum distance from Sun to flyby star: {np.min(sunStarDists)/au2m} AU\n")
    deltaEP9 = np.abs(planetEccentricitiesFinal["Planet 9"] - p9E)

    #We need to find the angle the exostar had as it passed Planet 9. To do this, we find the vector between the points before and after closest approach
    minDistIndex = p9StarDists.index(min(p9StarDists))
    posBefore = np.array([allBodiesDict["Flyby Star"][(minDistIndex - 1)][1], allBodiesDict["Flyby Star"][(minDistIndex - 1)][2], allBodiesDict["Flyby Star"][(minDistIndex - 1)][3]])
    posAfter = np.array([allBodiesDict["Flyby Star"][(minDistIndex + 1)][1], allBodiesDict["Flyby Star"][(minDistIndex + 1)][2], allBodiesDict["Flyby Star"][(minDistIndex + 1)][3]])
    flybyVector = posAfter - posBefore

    #From here, we find a vector to represent the orbital plane of Planet 9. We do this by obtaining three points from early in Planet 9's orbit, using those to make a plane, and obtaining the vector accordingly

    #We select points that surround the point of closest approach. This boolean language mainly eliminates edge cases so they don't break our code; we expect to get the else statement the vast majority of the time
    if minDistIndex + 50 >= len(timeArray):
        indices = [minDistIndex, (minDistIndex - 50), (minDistIndex - 100)]

    elif minDistIndex - 50 <= 0:
        indices = [minDistIndex, (minDistIndex + 50), (minDistIndex + 100)]

    else:
        indices = [minDistIndex, (minDistIndex - 50), (minDistIndex + 50)]
        

    #planeVector = np.cross(vector1, vector2)

    #orbitalAngle = np.arccos(dotProduct/(flybyMag * planeMag))
    #orbitalAngle = np.arcsin(abs(np.dot(flybyVector, planeVector))/(flybyMag * planeMag))


    # Unit flyby direction
    flybyUnit = flybyVector / np.linalg.norm(flybyVector)

    # Dot product with orbital-plane normal
    dot = np.dot(planeVector, flybyUnit)

    # Angle between flyby and orbital-plane normal
    angleToNormal = np.degrees(np.arccos(np.clip(abs(dot), -1.0, 1.0)))

    # Angle between flyby and orbital plane
    angleToPlane = 90.0 - angleToNormal

    orbitalAngle = angleToPlane
    
    print("angle to plane normal:", angleToNormal, "degrees")
    print("angle to orbital plane:", angleToPlane, "degrees")


    
    #Lastly, we'd like to find the distance between P9 and the sun when P9 is maximally close to the flyby star
    sunPos = np.array([allBodiesDict["Sun"][(minDistIndex)][1], allBodiesDict["Sun"][(minDistIndex)][2], allBodiesDict["Sun"][(minDistIndex)][3]])
    posDuring = np.array([allBodiesDict["Planet 9"][(minDistIndex)][1], allBodiesDict["Planet 9"][(minDistIndex)][2], allBodiesDict["Planet 9"][(minDistIndex)][3]])
    distDuringFlyby = np.sqrt((sunPos[0] - posDuring[0])**2 + (sunPos[1] - posDuring[1])**2 + (sunPos[2] - posDuring[2])**2)

    
    storageDict = {
        "p9DeltaE": deltaEP9,
        "Exostar mass": exoStarMass,
        "Exostar Velocity": exoStarV,
        "Nearest Approach to Sun": np.min(sunStarDists)/au2m,
        "Nearest Approach to Planet 9": np.min(p9StarDists)/au2m,
        "Planet 9 Data": p9Stats,
        "Flyby Angle": orbitalAngle,
        "P9 Dist to Sun During Flyby": distDuringFlyby
    }

    print(storageDict)

    
    #And now we're done!
    return timeArray, allBodiesDict, resonanceStatus, ejectedPlanets, perturbedPlanets, storageDict



#Run a dummy simulation that just runs the solar system normally, to confirm normal behaviors
def runDummySim(endTime, timeSteps, planetsData, sunMass = 1.98892e30): #Input time in years; will be converted to seconds

    #Note for inputs - defining aList, eList, massList, and starMass ahead of time allows for cutting down on arguments
    #Boot up the simulation
    sim = rebound.Simulation()
    sim.units = ('m', 's', 'kg')

    #Add the star
    sim.add(m=sunMass)

    #Add our planets
    for stats in planetsData.values():
        sim.add(
            m=stats[0],
            a=stats[1],
            e=stats[2],
            inc=stats[3],
            Omega=stats[4],
            pomega=stats[5],
            M=stats[6]
        )
        
    sim.move_to_com()
    

    #allBodiesDict is our dictionary for tracking the positions of every body in the system
    allBodiesDict = {}
    allBodiesDict.update({"Sun":[]})
    for planetName in planetsData:
        allBodiesDict.update({planetName:[]})

    eccentricitiesDict = {}
    for planetName in planetsData:
        eccentricitiesDict.update({planetName:[]})
        
    numPlanets = len(planetsData) - 1

    dumbWorkaroundCounter = 0

    #Create our time array
    timeArray = np.linspace(0,endTime*31557600.7,timeSteps)

    #This sets the next spawntime
    resList = []

    PRatioList = []

    for time in timeArray:
        
        sim.integrate(time)
        sim.move_to_com()

        #Track where everything is
        allBodiesDict = trackBodies3D(time, allBodiesDict, sim)

        bodyIndex = 1
        #Track the eccentricities of all bodies
        for eList in eccentricitiesDict.values():
            bodyE = sim.particles[bodyIndex].e
            eList.append(bodyE)
            bodyIndex += 1
    

        #Track the resonance of Pluto and Neptune
        NeptuneOrbit = sim.particles[4].orbit(primary=sim.particles[0])
        PlutoOrbit = sim.particles[5].orbit(primary=sim.particles[0])
        
        lambdaN = NeptuneOrbit.M + NeptuneOrbit.pomega
        lambdaP = PlutoOrbit.M + PlutoOrbit.pomega
        
        phi = 3*lambdaP - 2*lambdaN - PlutoOrbit.pomega
        
        # Wrap to (-pi, pi]
        phi = np.arctan2(np.sin(phi), np.cos(phi))
        
        resList.append(np.degrees(phi))
        PRatioList.append(PlutoOrbit.P / NeptuneOrbit.P)

                
    #And now we're done!
    return timeArray, eccentricitiesDict, resList, PRatioList
