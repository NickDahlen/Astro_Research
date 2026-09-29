import rebound
import json

#Download NASA's data on the planets                                                                                                                                                                                                                                               
sim = rebound.Simulation()
sim.units = ('m', 's', 'kg')
planetList = ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
time = "2020-01-01 00:00"

index = 1
sim.add("Sun")
planetsDict = {}
print(f"Fetching Orbits!\n", end="", flush=True)

for planetName in planetList:
    sim.add(str(planetName), date=str(time))
    planet = sim.particles[index]
    orbit = planet.orbit(primary = sim.particles[0])

    #Now we get our parameters, of the form [mass, semi-major axis, eccentricity, inclination]                                                                                                                                                                                     

    paramList = [
        sim.particles[index].m,
        orbit.a,
        orbit.e,
        orbit.inc,
        orbit.Omega,
        orbit.pomega,
        orbit.M
    ]

    planetsDict.update({planetName:paramList})

    index += 1

print(f"Orbits fetched!\n", end="", flush=True)

with open("OrbitalData.txt", 'w') as output:
    json.dump(planetsDict, output)

print("Written to file!")
