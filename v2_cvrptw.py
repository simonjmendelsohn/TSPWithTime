from __future__ import print_function
from six.moves import xrange
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from termcolor import colored
import time
import sys
import numpy as np
import math
import multiprocessing
import signal

'''
This code based on code from Google Optimization Tools for the Capacitated Vehicle Routing Problem with Time Windows (CVRPTW).  It is applied towards the Traveling Salesman Problem with Appointments (a subproblem of the Traveling Salesman Problem with Time Windows).  In order to do this, we pretend that the time between each appointment is a different vehicle, so we could use the multiple vehicle capabilities of Google's code.  And in order to solve the problem of different time windows for each of these vehicles, we give each vehicle "busy-work" at the beginning of its journey, effectively serving as time-windows.  Finally, since Google's code tries to minimize distance, which is not our main objective, we use binary search to optimize for the earliest time that we could complete the final task, which is what we really want.

See https://developers.google.com/optimization/routing/cvrptw for Google's explanation of the original code.
'''

horizon = 10000 #The amount of time give after the last appointment to complete the remaining tasks.  It just has to be a sufficiently large number.

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

###########################
# Problem Data Definition #
###########################
class Vehicle():
    """Stores the property of a vehicle"""
    def __init__(self):
        """Initializes the vehicle properties"""
        self._capacity = 1000000
        # Travel speed
        self._speed = 1

    @property
    def capacity(self):
        """Gets vehicle capacity"""
        return self._capacity

    @property
    def speed(self):
        """Gets the average travel speed of a vehicle"""
        return self._speed

class CityBlock():
    """City block definition"""
    @property
    def width(self):
        """Gets Block size West to East"""
        return 1

    @property
    def height(self):
        """Gets Block size North to South"""
        return 1

class DataProblem():
    """Stores the data for the problem"""
    def __init__(self):
        """Initializes the data for the problem"""
        self._vehicle = Vehicle()

        # Locations in block unit
        locations =  [(36, 23), (13, 5), (1, 31), (27, 25), (43, 19), (40, 21), (12, 0), (28, 49), (36, 38), (49, 26), (40, 41), (44, 27), (23, 7), (45, 6), (0, 10), (11, 35), (30, 3), (34, 8), (25, 20), (39, 34), (3, 49), (5, 43), (33, 21), (10, 39), (31, 27), (0, 36), (11, 38), (15, 19), (11, 13), (21, 24), (38, 22), (5, 33), (36, 10), (41, 29), (22, 25), (37, 39), (33, 31), (15, 30), (28, 32), (21, 4), (24, 10), (11, 46), (33, 8), (6, 22), (17, 34), (11, 27), (19, 9), (10, 20), (12, 36), (28, 35), (16, 47), (34, 10), (41, 46), (4, 13), (24, 41), (46, 2), (7, 49), (32, 40), (18, 10), (22, 8), (22, 42), (13, 14), (26, 1), (33, 10), (47, 22), (48, 2), (44, 26), (49, 6), (25, 33), (38, 35), (46, 17), (31, 28), (36, 20), (38, 37), (4, 11), (42, 23), (25, 25), (30, 12), (8, 38), (27, 22), (41, 9), (23, 5), (9, 31), (14, 29), (15, 36), (43, 42), (38, 28), (27, 18), (21, 37), (7, 37), (34, 31), (23, 42), (25, 14), (7, 1), (27, 39), (25, 37), (44, 15), (13, 35), (2, 3), (17, 9), (36, 23)]
        locations = locations[:-1]  #The last location is a repeat of the first one.
        
        # locations in meters using the city block dimension
        city_block = CityBlock()
        self._locations = [(
            loc[0]*city_block.width,
            loc[1]*city_block.height) for loc in locations]

        #self._depot = 0 
        
        time_windows = [(0, 0), (41, 42), (79, 80), (111, 112), (133, 134), (138, 139), (187, 188), (252, 253), (271, 272), (296, 297), (320, 321), (338, 339), (379, 380), (402, 403), (451, 452), (487, 488), (538, 539), (547, 548), (568, 569), (596, 597), (647, 648), (655, 656), (705, 706), (746, 747), (779, 780), (819, 820), (832, 833), (855, 856), (865, 866), (886, 887), (905, 906), (949, 950), (1003, 1004), (1027, 1028), (1050, 1051), (1079, 1080), (1091, 1092), (1110, 1111), (1125, 1126), (1160, 1161), (1169, 1170), (1218, 1219), (1278, 1279), (1319, 1320), (1342, 1343), (1355, 1356), (1381, 1382), (1401, 1402), (1419, 1420), (1436, 1437), (1460, 1461), (1515, 1516), (1558, 1559), (1628, 1629), (1676, 1677), (1737, 1738), (1823, 1824), (1857, 1858), (1901, 1902), (1907, 1908), (1941, 1942), (1978, 1979), (2004, 2005), (2020, 2021), (2046, 2047), (2067, 2068), (2095, 2096), (2120, 2121), (2171, 2172), (2186, 2187), (2212, 2213), (2238, 2239), (2251, 2252), (2270, 2271), (2330, 2331), (2380, 2381), (2399, 2400), (2417, 2418), (2465, 2466), (2500, 2501), (2527, 2528), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000)] #The time-windows consist of a (0,0) followed by the times for the appointments in increasing order, followed by (0, 1000), where 1000, could be any sufficiently large number.
        time_windows = time_windows[:-1] #Since I got rid of the last location, I have 1 too many time windows.

        starts = [window[0] for window in time_windows]
        self._distadder = max(starts) #The time that I complete the last task will be equal to the time of the last appointment plus the time it takes to complete any remaining tasks after that.  distadder is the time of the last appointment.

        num = 1
        for window in time_windows:
            if window[0] != 0:
                num += 1
        self._num_vehicles = num

        self._time_windows = [(0,0)]
        for i in range(1, len(time_windows)):
            self._time_windows.append((0,horizon))
        
        #Since the code as google has it does not generalize well to appointments, I use the demands, instead of time_windows, to effectively set the time limits.
        self._demands = []
        prev = 0
        for i in range(1, len(time_windows)):
            if time_windows[i][0] == 0:
                self._demands.append(0)
            else:
                self._demands.append(horizon - (time_windows[i][0] - prev))
            prev = time_windows[i][0]
        self._demands.append(0)

        #print (self._demands)

    @property
    def vehicle(self):
        """Gets a vehicle"""
        return self._vehicle

    @property
    def num_vehicles(self):
        """Gets number of vehicles"""
        return self._num_vehicles

    @property
    def locations(self):
        """Gets locations"""
        return self._locations

    @property
    def num_locations(self):
        """Gets number of locations"""
        return len(self.locations)

    @property
    def depot(self):
        """Gets depot location index"""
        return self._depot

    @property
    def demands(self):
        """Gets demands at each location"""
        return self._demands

    @property
    def time_per_demand_unit(self):
        """Gets the time (in min) to load a demand"""
        return 1 

    @property
    def time_windows(self):
        """Gets (start time, end time) for each locations"""
        return self._time_windows

#######################
# Problem Constraints #
#######################

#I calculate the distance between two points.  If the word "euclid" was used as a command line argument, the distance is calculated using Euclidean Distance.  Otherwise, it uses Manhattan Distance.  
def distance(position_1, position_2, imeanit = False):
    if sys.argv[-1] == "euclid":
        if imeanit:
            euclid = np.sqrt((position_1[0] - position_2[0]) ** 2 + (position_1[1] - position_2[1]) ** 2)
        else:
            euclid = np.ceil(np.sqrt((position_1[0] - position_2[0]) ** 2 + (position_1[1] - position_2[1]) ** 2)) #Unfortunately I have to take the ceiling, as google's code is only compatible with integers.  Fortunately, it rarely makes any difference, and when it does make a difference, it is usually quite insignificant.
        return euclid
    return (abs(position_1[0] - position_2[0]) +
            abs(position_1[1] - position_2[1]))

class CreateDistanceEvaluator(object): # pylint: disable=too-few-public-methods
    """Creates callback to return distance between points."""
    def __init__(self, data):
        """Initializes the distance matrix."""
        self._distances = {}

        # precompute distance between location to have distance callback in O(1)
        for from_node in xrange(data.num_locations):
            self._distances[from_node] = {}
            for to_node in xrange(data.num_locations):
                if from_node == to_node:
                    self._distances[from_node][to_node] = 0
                else:
                    self._distances[from_node][to_node] = (
                        distance(
                            data.locations[from_node],
                            data.locations[to_node]))

    def distance_evaluator(self, from_node, to_node):
        """Returns the distance between the two nodes"""
        return self._distances[from_node][to_node]

class CreateDemandEvaluator(object): # pylint: disable=too-few-public-methods
    """Creates callback to get demands at each location."""
    def __init__(self, data):
        """Initializes the demand array."""
        self._demands = data.demands

    def demand_evaluator(self, from_node, to_node):
        """Returns the demand of the current node"""
        del to_node
        return self._demands[from_node]

def add_capacity_constraints(routing, data, demand_evaluator):
    """Adds capacity constraint"""
    capacity = "Capacity"
    routing.AddDimension(
        demand_evaluator,
        0, # null capacity slack
        data.vehicle.capacity, # vehicle maximum capacity
        True, # start cumul to zero
        capacity)

class CreateTimeEvaluator(object):
    """Creates callback to get total times between locations."""
    @staticmethod
    def service_time(data, node):
        """Gets the service time for the specified location."""
        return data.demands[node] * data.time_per_demand_unit

    @staticmethod
    def travel_time(data, from_node, to_node):
        """Gets the travel times between two locations."""
        if from_node == to_node:
            travel_time = 0
        else:
            travel_time = distance(
                data.locations[from_node],
                data.locations[to_node]) / data.vehicle.speed
        return travel_time

    def __init__(self, data):
        """Initializes the total time matrix."""
        self._total_time = {}
        # precompute total time to have time callback in O(1)
        for from_node in xrange(data.num_locations):
            self._total_time[from_node] = {}
            for to_node in xrange(data.num_locations):
                if from_node == to_node:
                    self._total_time[from_node][to_node] = 0
                else:
                    self._total_time[from_node][to_node] = int(
                        self.service_time(data, from_node) +
                        self.travel_time(data, from_node, to_node))

    def time_evaluator(self, from_node, to_node):
        """Returns the total time between the two nodes"""
        return self._total_time[from_node][to_node]

def add_time_window_constraints(routing, data, time_evaluator):
    """Add Global Span constraint"""
    time = "Time"
    routing.AddDimension(
        time_evaluator,
        horizon, # allow waiting time
        horizon, # maximum time per vehicle
        True, # start cumul to zero
        time)
    time_dimension = routing.GetDimensionOrDie(time)
    for location_idx, time_window in enumerate(data.time_windows):
        time_dimension.CumulVar(location_idx).SetRange(time_window[0], time_window[1])

###########
# Printer #
###########
class ConsolePrinter():
    """Print solution to console"""
    def __init__(self, data, routing, assignment):
        """Initializes the printer"""
        self._data = data
        self._routing = routing
        self._assignment = assignment

    @property
    def data(self):
        """Gets problem data"""
        return self._data

    @property
    def routing(self):
        """Gets routing model"""
        return self._routing

    @property
    def assignment(self):
        """Gets routing model"""
        return self._assignment

    def print(self):
        """Prints assignment on console"""
        # Inspect solution.
        capacity_dimension = self.routing.GetDimensionOrDie('Capacity')
        time_dimension = self.routing.GetDimensionOrDie('Time')
        total_dist = self.data._distadder
        total_time = 0
        loc = [] #I will want to graph the locations.
        for vehicle_id in xrange(self.data.num_vehicles):
            index = self.routing.Start(vehicle_id)
            plan_output = 'Route for vehicle {0}:\n'.format(vehicle_id)
            route_dist = 0
            veh = [] #I need to separate by vehicles
            while not self.routing.IsEnd(index):
                node_index = self.routing.IndexToNode(index)
                next_node_index = self.routing.IndexToNode(
                    self.assignment.Value(self.routing.NextVar(index)))
                route_dist += distance(
                    self.data.locations[node_index],
                    self.data.locations[next_node_index], True)
                veh.append(list(self.data.locations[node_index])) #I add to vehicle
                load_var = capacity_dimension.CumulVar(index)
                route_load = self.assignment.Value(load_var)
                time_var = time_dimension.CumulVar(index)
                time_min = self.assignment.Min(time_var)
                time_max = self.assignment.Max(time_var)
                plan_output += ' {0} Load({1}) Time({2},{3}) ->'.format(self.data.locations[node_index], route_load, time_min, time_max)
                index = self.assignment.Value(self.routing.NextVar(index))

            node_index = self.routing.IndexToNode(index)
            veh.append(list(self.data.locations[node_index])) #I add to vehicle
            loc.append(veh)
            load_var = capacity_dimension.CumulVar(index)
            route_load = self.assignment.Value(load_var)
            time_var = time_dimension.CumulVar(index)
            route_time = self.assignment.Value(time_var)
            time_min = self.assignment.Min(time_var)
            time_max = self.assignment.Max(time_var)
            if vehicle_id == self.data.num_vehicles - 1:
                total_dist += route_dist
            total_time += route_time
            plan_output += ' {0} Load({1}) Time({2},{3})\n'.format(self.data.locations[node_index], route_load, time_min, time_max)
            plan_output += 'Distance of the route: {0}m\n'.format(route_dist)
            plan_output += 'Load of the route: {0}\n'.format(route_load)
            plan_output += 'Time of the route: {0}min\n'.format(route_time)
            print(plan_output)
        printMap(loc) #I print the map.
        print('Time of last action: {0}m'.format(total_dist))
        return total_dist #This is not actually distance; rather, it is the time when the last task is completed.

########
# Main #
########
def main():

    best_time = horizon
    minval = 0
    maxval = horizon
    if horizon > 50000: #If there are too many tasks, binary search would take too long.
        minval = 10
        maxval = 10

    #I let the average of minval and maxval be the amount of time allotted after the last appointment to complete the remaining tasks (The amount of time allotted is actually equal to the average if minval and maxval subtracted from the horizon, but that distinction is not important to the overall logic of the program).  If it is too little time, I allot more time.  If it is too much time, I allot less time.  I continue this process until I find exactly how much time the program needs to be able to successfully run.  This binary search is necessary because if I give the program too much time, it will minimize distance traveled, rather than time of completing the last task. 
    while(maxval - minval > 2):

        """Entry point of the program"""
        # Instantiate the data problem.
        data = DataProblem()
        
        #Initialize the start and end locations to be the appointments.
        start_locations = []
        end_locations = []
        for i in range(data.num_vehicles):
            start_locations.append(i)
            end_locations.append(i + 1)
        end_locations[-1] = 0

        val = math.floor((minval + maxval) / 2)  #I'm using binary search to find the optimal value.  I floor the result as the code workes better with integers.
        data.demands[len(start_locations) - 1] = val

        routing = pywrapcp.RoutingModel(data.num_locations, data.num_vehicles, start_locations, end_locations)
        #routing = pywrapcp.RoutingModel(data.num_locations, data.num_vehicles, data.depot)
        
        # Define weight of each edge
        distance_evaluator = CreateDistanceEvaluator(data).distance_evaluator
        routing.SetArcCostEvaluatorOfAllVehicles(distance_evaluator)
        # Add Capacity constraint
        demand_evaluator = CreateDemandEvaluator(data).demand_evaluator
        add_capacity_constraints(routing, data, demand_evaluator)
        # Add Time Window constraint
        time_evaluator = CreateTimeEvaluator(data).time_evaluator
        add_time_window_constraints(routing, data, time_evaluator)

        # Setting first solution heuristic (cheapest addition).
        search_parameters = pywrapcp.RoutingModel.DefaultSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_MOST_CONSTRAINED_ARC) #PATH_CHEAPEST_ARC is sometimes better
        
        search_parameters.time_limit_ms = 1000 #The time limit on each iteration of the binary search.
        
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GREEDY_DESCENT) #This local search option usually makes no difference, but once in a while it helps.
        
        # Solve the problem.
        
        try:
            assignment = routing.SolveWithParameters(search_parameters)
        except:
            
            maxval = val
            print("error in solving")
            continue

        printer = ConsolePrinter(data, routing, assignment)

        try:
            time = printer.print() 
            if time < best_time:
                best_time = time
        except:
            maxval = val
            print("error in printing")
            print ("val", val)
            print ("demands", data.demands)
            continue
        else: 
            minval = val
            continue

    #Once I have the best path, I run the code once again to print out the result: 

    """Entry point of the program"""
    # Instantiate the data problem.
    data = DataProblem()

    # Create Routing Model
    start_locations = []
    end_locations = []
    for i in range(data.num_vehicles):
        start_locations.append(i)
        end_locations.append(i + 1)
    end_locations[-1] = 0

    data.demands[len(start_locations) - 1] = minval
    
    print("")
    print("Final Value: ", minval)
    if minval == 0:
        print ("")
        print("ERROR: IMPOSSIBLE CONSTRAINTS")
        print ("")
        exit()
    print("")

    routing = pywrapcp.RoutingModel(data.num_locations, data.num_vehicles, start_locations, end_locations)
    #routing = pywrapcp.RoutingModel(data.num_locations, data.num_vehicles, data.depot)
    
    # Define weight of each edge
    distance_evaluator = CreateDistanceEvaluator(data).distance_evaluator
    routing.SetArcCostEvaluatorOfAllVehicles(distance_evaluator)
    # Add Capacity constraint
    demand_evaluator = CreateDemandEvaluator(data).demand_evaluator
    add_capacity_constraints(routing, data, demand_evaluator)
    # Add Time Window constraint
    time_evaluator = CreateTimeEvaluator(data).time_evaluator
    add_time_window_constraints(routing, data, time_evaluator)

    # Setting first solution heuristic (cheapest addition).
    search_parameters = pywrapcp.RoutingModel.DefaultSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_MOST_CONSTRAINED_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GREEDY_DESCENT)
    # Solve the problem.
    

    assignment = routing.SolveWithParameters(search_parameters)
    printer = ConsolePrinter(data, routing, assignment)
    time = printer.print() 
    if time < best_time:
        best_time = time
    print ("")
    print ("Best Time of Last action: ", round(best_time))

if __name__ == '__main__':
    t0 = time.time()
    main()
    t1 = time.time()
    print ("Compute Time:", round(t1 - t0, 2))
    print ()