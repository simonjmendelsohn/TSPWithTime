import math
from termcolor import colored
import sys
import time
import random

'''
This algorithm is an adaptation of the nearest-neighbor's algorithms for the Traveling Salesman Problem with Appointments.  It takes some ideas from genetic programming, using repetition, building on the best previous results, in order to improve the scheduled path.
'''

#This function graphs the path scheduled by the algorithm.  The appointments are printed in magenta, and the paths taken in between each appointment are printed in a rotation a various different colors.  
def printMap(loc):
    #print (loc)

    colors = {
        0: "red",
        1: "yellow",
        2: "green",
        3: "blue",
        4: "grey",
        5: "white",
        6: "cyan",
        7: "magenta",
    }

    #This simple graphing function makes a plot of size 55 x 55 and is not designed for points with the x or y coordinate greater than 50.
    grid = [ ([[' ', 4, False]] * 55) for row in range(55) ]

    j = 0
    for veh in range(len(loc)): #loop through the breaks between appointments
        for i in range(len(loc[veh])): #for each task
            if (veh == len(loc) - 1 and i == len(loc[veh]) - 1) or i == 0: #If the current task is an appointment or the final task:
                if i != 0: #We don't want to increment the task counter if it is the first task because it is also the last task, and we don't want to count it twice.
                    j += 1 
                grid[loc[veh][i][0]][loc[veh][i][1]] = [j, 7, loc[veh][i]] #The "j" is the task counter, "7" is to print the task as magenta, and "loc[veh][i]" is the coordinate of the task
            else: 
                j += 1
                grid[loc[veh][i][0]][loc[veh][i][1]] = [j, veh % 7, loc[veh][i]] #Print the task as some other color
            
    print('+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +')
    for y in range(51):
        print('+ ',end='')
        ender = []
        for x in range(53):
            if grid[x][y][2]: #If there was a task in this location:
                print(colored(grid[x][y][0], colors[grid[x][y][1]]),end='') #Print the task number with its color decided above
                ender.append(grid[x][y][2]) #We will print it's coordinate at the end of the line.
            else:
                print (' ', end='')
            print(' ', end='')
        print('+ ', *ender)
    print('+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +')

#I calculate the distance between two points.  If the word "euclid" was used as a command line argument, the distance is calculated using Euclidean Distance.  Otherwise, it uses Manhattan Distance. 
def distance (point1, point2):
    if sys.argv[-1] == "euclid":
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
    return (abs(point1[0] - point2[0]) +
            abs(point1[1] - point2[1]))

#Flatten a nested list.
def flat(l):
    return [item for sublist in l for item in sublist]

def main():
    locations = [(36, 23), (13, 5), (1, 31), (27, 25), (43, 19), (40, 21), (12, 0), (28, 49), (36, 38), (49, 26), (40, 41), (44, 27), (23, 7), (45, 6), (0, 10), (11, 35), (30, 3), (34, 8), (25, 20), (39, 34), (3, 49), (5, 43), (33, 21), (10, 39), (31, 27), (0, 36), (11, 38), (15, 19), (11, 13), (21, 24), (38, 22), (5, 33), (36, 10), (41, 29), (22, 25), (37, 39), (33, 31), (15, 30), (28, 32), (21, 4), (24, 10), (11, 46), (33, 8), (6, 22), (17, 34), (11, 27), (19, 9), (10, 20), (12, 36), (28, 35), (16, 47), (34, 10), (41, 46), (4, 13), (24, 41), (46, 2), (7, 49), (32, 40), (18, 10), (22, 8), (22, 42), (13, 14), (26, 1), (33, 10), (47, 22), (48, 2), (44, 26), (49, 6), (25, 33), (38, 35), (46, 17), (31, 28), (36, 20), (38, 37), (4, 11), (42, 23), (25, 25), (30, 12), (8, 38), (27, 22), (41, 9), (23, 5), (9, 31), (14, 29), (15, 36), (43, 42), (38, 28), (27, 18), (21, 37), (7, 37), (34, 31), (23, 42), (25, 14), (7, 1), (27, 39), (25, 37), (44, 15), (13, 35), (2, 3), (17, 9), (36, 23)]
    locations = locations[:-1] #The last location is a repeat of the first one.

    numlocs = len(locations)

    time_windows = [(0, 0), (41, 42), (79, 80), (111, 112), (133, 134), (138, 139), (187, 188), (252, 253), (271, 272), (296, 297), (320, 321), (338, 339), (379, 380), (402, 403), (451, 452), (487, 488), (538, 539), (547, 548), (568, 569), (596, 597), (647, 648), (655, 656), (705, 706), (746, 747), (779, 780), (819, 820), (832, 833), (855, 856), (865, 866), (886, 887), (905, 906), (949, 950), (1003, 1004), (1027, 1028), (1050, 1051), (1079, 1080), (1091, 1092), (1110, 1111), (1125, 1126), (1160, 1161), (1169, 1170), (1218, 1219), (1278, 1279), (1319, 1320), (1342, 1343), (1355, 1356), (1381, 1382), (1401, 1402), (1419, 1420), (1436, 1437), (1460, 1461), (1515, 1516), (1558, 1559), (1628, 1629), (1676, 1677), (1737, 1738), (1823, 1824), (1857, 1858), (1901, 1902), (1907, 1908), (1941, 1942), (1978, 1979), (2004, 2005), (2020, 2021), (2046, 2047), (2067, 2068), (2095, 2096), (2120, 2121), (2171, 2172), (2186, 2187), (2212, 2213), (2238, 2239), (2251, 2252), (2270, 2271), (2330, 2331), (2380, 2381), (2399, 2400), (2417, 2418), (2465, 2466), (2500, 2501), (2527, 2528), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000)] #The time-windows consist of a (0,0) followed by the times for the appointments in increasing order, followed by (0, 1000), where 1000, could be any sufficiently large number.
    time_windows = time_windows[:-1] #Since I got rid of the last location, I have 1 too many time windows.
    horizon = time_windows[-1][1]

    #precompute distances between points to make the algorithm faster:
    distances = {}
    for fromnode in locations:
        distances[fromnode] = {}
        for tonode in locations:
            if fromnode == tonode:
                distances[fromnode][tonode] = 0
            else:
                distances[fromnode][tonode] = distance(fromnode, tonode)

    print ("")
    print ("Locations: ", locations)
    print (" ")

    num = 1
    for window in time_windows:
        if window[0] != 0:
            num += 1

    start_locations = []
    end_locations = []
    for i in range(num):
        start_locations.append(i)
        end_locations.append(i + 1)
    end_locations[-1] = 0

    #Getting my start and end locations
    start_locations = [locations[i] for i in start_locations]
    end_locations = [locations[i] for i in end_locations]

    #I don't want to go to a task twice.
    for location in end_locations:
        locations.remove(location)

    sums = []
    #'sums' is a list of how much time I have between each of my appointments.
    prev = 0
    for i in range(1, len(time_windows)):
        if time_windows[i][0] != 0:
            sums.append(time_windows[i][0] - prev)
        prev = time_windows[i][0]
    sums.append(horizon) #After the last appointment, I have plenty of time to complete the rest of the tasks, should it be needed.
    print ("Time between each appointment: ", sums)

    #The time that I complete the last task will be equal to the time of the last appointment plus the time it takes to complete any remaining tasks after that.  As such, allsum (the time I complete the last task) is initalized to be the time of the last appointment.
    starts = [window[0] for window in time_windows]
    distadder = max(starts)
    allsum = distadder

    temp = locations[:] #I need a copy of 'locations', as I remove locations from 'locations' each time I add one to my schedule.  And since I will be doing this multiple times, I need to be able to go back to the original list of 'locations'
    bestsum = 10000000
    improvedsum = 1000000
    bestpath = []
    improvedpath = []
    lastimprove = 0
    while lastimprove < 10: #I repeat until I stop improving.
        for slot in range(len(start_locations)): #I separately randomize the break between each appointment.
            for gene in range(round(10000/numlocs)):
                locations = temp[:]
                allsum = distadder
                allpath = bestpath[0:slot] #Start with the best solution obtained when randomizing the previous slot.
                for loc in flat(allpath):
                    if loc in locations:
                        locations.remove(loc)

                for vehicle in range(slot, len(start_locations)): #Each "vehicle" is the time between each of my appointments.
                    onesum = 0
                    onemax = sums[vehicle]
                    path = [start_locations[vehicle]]
                    
                    while path[-1] != end_locations[vehicle] or len(path) < 2:

                        remaining = distances[path[-1]][end_locations[vehicle]] #How much time I have need to get to the next appointment in time.

                        if len(locations) == 0:
                            path.append(end_locations[vehicle])
                            onesum += remaining
                            break

                        if gene > 0 and (len(path) == 1 or random.randint(1,10) > 8) and vehicle == slot: #If I want to randomize this slot, then I randomize every path except the first one.  Specifically, I randomize the first location after the appointment, in addition to any other with some small probability.
                            closest = random.choice(locations)
                            dist = distances[path[-1]][closest]
                        else:
                            closest = () #Otherwise I just choose the closest coordinate
                            dist = 10000
                            for loc in locations:
                                if distances[path[-1]][loc] < dist:
                                    dist = distances[path[-1]][loc]
                                    closest = loc

                        returndist = distances[closest][end_locations[vehicle]]
                        # print (onesum)
                        # print (dist)
                        # print (remaining)
                        if onesum + dist + returndist > onemax: #If I can't go to the nearest location and still get to the next appointment in time:
                            if onesum + remaining > onemax: #If I can't even get to the next appointment in time at all:
                                print ("")
                                print("ERROR: IMPOSSIBLE CONSTRAINTS")
                                print ("")
                                exit()
                            path.append(end_locations[vehicle])
                            onesum += remaining
                        
                        else:
                            #print (closest)
                            path.append(closest)
                            locations.remove(closest)
                            onesum += dist

                    # print ("path: ", path)
                    # print ("length: ", len(path))
                    # print ("distance: ", onesum)
                    if vehicle == len(start_locations) - 1: #If it is the last stretch (I already completed the last appointment):
                        allsum += onesum
                    allpath.append(path)

                # print (len(flat(allpath)))
                # print (numlocs + num)
                assert len(flat(allpath)) == numlocs + num #Make sure I did the right number of tasks

                #print (allsum)
                if bestsum > allsum:
                    bestsum = allsum
                    bestpath = allpath

        if bestsum < improvedsum:
            improvedsum = bestsum
            improvedpath = bestpath
        else:
            lastimprove += 1

            
    printMap(improvedpath)
    print ("Time of last action: ", round(improvedsum))

if __name__ == '__main__':
    t0 = time.time()
    main()
    t1 = time.time()
    print ("Compute Time", round((t1 - t0), 2))
