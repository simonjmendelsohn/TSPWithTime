import math
from termcolor import colored
import sys
import time
import random

'''
This algorithm is an adaptation of ant-colony optimization for the Traveling Salesman Problem with Appointments.  It also uses two-opt local search to improve the results and speed.
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


#This function determines the next point for the current ant to take, based on current distance to the next point, distance from the next point to the next appointment, and pheromones (how much success previous ants had taking the path from the current point to a certain next point).
def nextpoint(point, endloc, locations, inverse_distances, pheromones, percent_app):
    #beta is a hyperparameter that I found to work better when it is larger if there are few appointments.  This is because the relative importance of the different distance factors, and pheromones change based on how many appointments there are.  However, I do not have any theoretical justification for why these specific numbers seem to work well, and if other numbers seem to work better, feel free to change them.  Similarly with alpha, pheromones += 10, 10/allsum (in update_pheromone), and 0.5 * pheromones (in graph_update) may very well be better off adjusted depending on the problem.  I don't know.
    alpha = 0.8
    beta = 1
    if percent_app < 0.1:
        beta = 10
    if percent_app < 0.4:
    	beta = 2
    
    inverse_sum = 0
    for l in locations:
        inverse_sum += (inverse_distances[point][l]*beta + 0.5 * inverse_distances[l][endloc])**beta * pheromones[point][l]**alpha

    #I use a randomly generated number to use inverse_sum as a probability distribution where I can pick the coordinate I want based on relevant factors.
    rand = random.random() * inverse_sum
    for l in locations:
        rand -= (inverse_distances[point][l]*beta + 0.5 * inverse_distances[l][endloc])**beta * pheromones[point][l]**alpha
        if rand < 0:
            return l, 1/inverse_distances[point][l]

#This function updates the pheromones on the path taken by a specific ant.
def update_pheromone(allsum, path, pheromones, best):
    path = flat(path)
    for i in range(1,len(path)):
        if best:
            pheromones[path[i-1]][path[i]] += 30 #If this ant had the best path so far, add an entire 10 pheromones.
        else:
            pheromones[path[i-1]][path[i]] += 30/allsum  #Otherwise, add some pheromones inversely proportional to the distance of the path.

#Evaporate half the pheromones in the graph.  This is done every once in a while decrease the importance of obsolete information.
def graph_update(pheromones):
    for key1 in pheromones.keys():
        for key2 in pheromones[key1].keys():
            pheromones[key1][key2] = 0.5 * pheromones[key1][key2]

#Apply two-opt local search on the path between two appointments, to help the ants find better solutions, and do so faster.
def two_opt(path, onesum, distances):
    for i in range(1, len(path) - 1):
        for k in range(i + 1, len(path) - 1):
            # print (path)
            # print ("Trying ", path[i], path[k])
            if distances[path[i-1]][path[i]] + distances[path[k]][path[k + 1]] > distances[path[i-1]][path[k]] + distances[path[i]][path[k + 1]]: #If a switch would decrease distance:
                onesum = onesum + (distances[path[i-1]][path[k]] + distances[path[i]][path[k + 1]]) - (distances[path[i-1]][path[i]] + distances[path[k]][path[k + 1]])
                subpath = path[i:k + 1]
                subpath = subpath[::-1]
                path = path[0:i] + subpath + path[k + 1:len(path)]

    return path, onesum

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

    print ("")
    print ("Locations: ", locations)
    print (" ")

    #Precompute distances and inverse-distances between points to make the algorithm faster.  I also initialize the pheromones here.  
    distances = {}
    inverse_distances = {}
    pheromones = {}
    for fromnode in locations:
        distances[fromnode] = {}
        inverse_distances[fromnode] = {}
        pheromones[fromnode] = {}
        #inverse_sum = 0
        for tonode in locations:
            pheromones[fromnode][tonode] = 1
            if fromnode == tonode:
                distances[fromnode][tonode] = 0
                inverse_distances[fromnode][tonode] = 0
            else:
                distances[fromnode][tonode] = distance(fromnode, tonode)
                inverse_distances[fromnode][tonode] = 1/float(distances[fromnode][tonode])

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

    #The time that I complete the last task will be equal to the time of the last appointment plus the time it takes to complete any remaining tasks after that.  As such, allsum (the time I complete the last task) will be initalized to be the time of the last appointment.
    starts = [window[0] for window in time_windows]
    distadder = max(starts)

    bestpath = []
    bestsum = 10000000

    lastimprove = 0
    temp = locations[:] #I need a copy of 'locations', as I remove locations from 'locations' each time I add one to my schedule.  And since I will be doing this multiple times, I need to be able to go back to the original list of 'locations'

    thresh = 100000/len(locations)
    originalthresh = thresh

    
    while lastimprove < thresh: #I repeat until I stop improving.
        allsum = distadder
        allpath = []
        locations = temp[:]
        for vehicle in range(len(start_locations)): #Each "vehicle" is the time between each of my appointments.
            onesum = 0
            onemax = sums[vehicle]
            path = [start_locations[vehicle]]
            
            while path[-1] != end_locations[vehicle] or len(path) < 2:

                remaining = distances[path[-1]][end_locations[vehicle]] #How much time I have need to get to the next appointment in time.

                if len(locations) == 0: #At the end of my journey, I apply some two-opt local search.
                    path, onesum = two_opt(path, onesum, distances)
                    path.append(end_locations[vehicle])
                    onesum += remaining
                    break

                
                closest, dist = nextpoint(path[-1], end_locations[vehicle], locations, inverse_distances, pheromones, (num-1)/(num + len(temp)))
                returndist = distances[closest][end_locations[vehicle]]
                # print (onesum)
                # print (dist)
                # print (remaining)
                if onesum + dist + returndist > onemax: #If I can't go to the chosen next location and still get to the next appointment in time:
                    if onesum + remaining > onemax: #If I can't even get to the next appointment in time at all:
                        print ("")
                        print("ERROR: IMPOSSIBLE CONSTRAINTS")
                        print ("")
                        exit()
                    path, onesum = two_opt(path, onesum, distances) #Before I give up, I try two-opt local search.
                    if onesum + dist + returndist <= onemax:
                        path.append(closest)
                        locations.remove(closest)
                        onesum += dist
                    else:
                        path.append(end_locations[vehicle])
                        onesum += remaining
                
                else:
                    path.append(closest)
                    locations.remove(closest)
                    onesum += dist

                
            # print ("path: ", path)
            # print ("length: ", len(path))
            # print ("distance: ", onesum)
            if vehicle == len(start_locations) - 1: #If it is the last stretch (I already completed the last appointment):
                allsum += onesum
            allpath.append(path)

        
        if allsum < bestsum: #If this is the best path so far:
            update_pheromone(allsum, allpath, pheromones, True) #Update the pheromones on the path taken by this ant
            bestsum = allsum
            bestpath = allpath
            if len(temp) < 500: #As long as the problem is not too big such that this will take forever, add more time to the threshold (allowing the algorithm to keep running until it stops improving).
                thresh = originalthresh + lastimprove
            print("Best Value So Far: ", allsum)
            print ("Progress: ", lastimprove/thresh)
        
        else:
            update_pheromone(allsum, allpath, pheromones, False) #Update pheromones on the path taken by this ant
            lastimprove += 1
            if lastimprove % 100 == 0: #If it has been a while:
                graph_update(pheromones) #Evaporate half the pheromones from the graph.
    
    

    assert len(flat(bestpath)) == numlocs + num #Make sure I did the right number of tasks
    printMap(bestpath)
    pher = []
    path = flat(bestpath)
    for i in range(1, len(path)):
        pher.append(((path[i-1], path[i]), pheromones[path[i-1]][path[i]]))
    print ("pheromones: ", pher)
    print ("Time of last action: ", round(bestsum))


if __name__ == '__main__':
    t0 = time.time()
    main()
    t1 = time.time()
    print (round((t1 - t0), 2))
