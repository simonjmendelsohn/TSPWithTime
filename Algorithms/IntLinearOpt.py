from __future__ import print_function
from ortools.linear_solver import pywraplp
import random
from operator import itemgetter
import sys
import math
import time
from termcolor import colored

"""
This code was based on the code from google OR tools found at https://developers.google.com/optimization/mip/integer_opt
although not so much of the original code remains and a lot was added.


"""

#If true a bunch of print statements used for debugging will print.
debug = True
def dprint(line):
    if debug:
        print(line)

#If 'euclid' is passed as a command line argument euclidean distance is used.
#Otherwise manhattan distance is used.
def distance(position_1, position_2):
    if sys.argv[-1] == "euclid":
        return math.sqrt((position_1[0] - position_2[0]) ** 2 + (position_1[1] - position_2[1]) ** 2)

    return (abs(position_1[0] - position_2[0]) +
            abs(position_1[1] - position_2[1]))

#Function used to print a map of the locations, ordered by when they are visited.
#The locations with specific times are in red, and the starting location is the 
#same as the end location (which has the highest number)
def printMap(variable_list, locations, times, horizon):

    values = [variable.solution_value() for variable in variable_list]

    newlocs = []
    while (min(values) < 100000):
      val, index = min((val, idx) for (idx, val) in enumerate(values))
      #index = min(enumerate(values), key=itemgetter(1))[0] 
      values[index] = 10000000000
      newlocs.append((locations[index], val))

    grid = [ ([[' ', '', '']] * 55) for row in range(55) ]

    for i in range(len(newlocs)):
        grid[newlocs[i][0][0]][newlocs[i][0][1]] = [i, newlocs[i]]
          

    print('+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +')
    for y in range(51):
        print('+ ',end='')
        ender = []
        for x in range(53):
          if (not (grid[x][y][0] == ' ')) and (not(times[locations.index(newlocs[grid[x][y][0]][0])] == (0, horizon))) and (not(times[locations.index(newlocs[grid[x][y][0]][0])] == (0, 0))):
            print(colored(grid[x][y][0], 'red'), end='')
          else:
              print (grid[x][y][0], end='')
          if grid[x][y][1] != '':
              ender.append(grid[x][y][1])
          print(' ', end='')
        print('+ ', *ender)
    print('+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +')


def main():

  time_window_end = 9000 #The latest time for any appointments
  horizon = 10401        #The time by which all tasks must be done
  num_tasks = 100        #The number of tasks.
  timed = True          #If true some randomly generated times for tasks will be assigned
  data = 'manual'        #If true tasks and time windows must be given manually rather than randomly constructed.
  M = 1000000           #Can be any sufficiently large integer for the linear opt algorithm to work.

  if data == 'manual':
    #The first and last locations must be the same and are the starting location of the vehicle.  They do not count as tasks.
    locations = [(36, 23), (13, 5), (1, 31), (27, 25), (43, 19), (40, 21), (12, 0), (28, 49), (36, 38), (49, 26), (40, 41), (44, 27), (23, 7), (45, 6), (0, 10), (11, 35), (30, 3), (34, 8), (25, 20), (39, 34), (3, 49), (5, 43), (33, 21), (10, 39), (31, 27), (0, 36), (11, 38), (15, 19), (11, 13), (21, 24), (38, 22), (5, 33), (36, 10), (41, 29), (22, 25), (37, 39), (33, 31), (15, 30), (28, 32), (21, 4), (24, 10), (11, 46), (33, 8), (6, 22), (17, 34), (11, 27), (19, 9), (10, 20), (12, 36), (28, 35), (16, 47), (34, 10), (41, 46), (4, 13), (24, 41), (46, 2), (7, 49), (32, 40), (18, 10), (22, 8), (22, 42), (13, 14), (26, 1), (33, 10), (47, 22), (48, 2), (44, 26), (49, 6), (25, 33), (38, 35), (46, 17), (31, 28), (36, 20), (38, 37), (4, 11), (42, 23), (25, 25), (30, 12), (8, 38), (27, 22), (41, 9), (23, 5), (9, 31), (14, 29), (15, 36), (43, 42), (38, 28), (27, 18), (21, 37), (7, 37), (34, 31), (23, 42), (25, 14), (7, 1), (27, 39), (25, 37), (44, 15), (13, 35), (2, 3), (17, 9), (36, 23)]
    num_tasks = len(locations) - 2
    time_windows = [(0, horizon)]*(num_tasks+2)
    time_windows = [(0, 0), (41, 42), (79, 80), (111, 112), (133, 134), (138, 139), (187, 188), (252, 253), (271, 272), (296, 297), (320, 321), (338, 339), (379, 380), (402, 403), (451, 452), (487, 488), (538, 539), (547, 548), (568, 569), (596, 597), (647, 648), (655, 656), (705, 706), (746, 747), (779, 780), (819, 820), (832, 833), (855, 856), (865, 866), (886, 887), (905, 906), (949, 950), (1003, 1004), (1027, 1028), (1050, 1051), (1079, 1080), (1091, 1092), (1110, 1111), (1125, 1126), (1160, 1161), (1169, 1170), (1218, 1219), (1278, 1279), (1319, 1320), (1342, 1343), (1355, 1356), (1381, 1382), (1401, 1402), (1419, 1420), (1436, 1437), (1460, 1461), (1515, 1516), (1558, 1559), (1628, 1629), (1676, 1677), (1737, 1738), (1823, 1824), (1857, 1858), (1901, 1902), (1907, 1908), (1941, 1942), (1978, 1979), (2004, 2005), (2020, 2021), (2046, 2047), (2067, 2068), (2095, 2096), (2120, 2121), (2171, 2172), (2186, 2187), (2212, 2213), (2238, 2239), (2251, 2252), (2270, 2271), (2330, 2331), (2380, 2381), (2399, 2400), (2417, 2418), (2465, 2466), (2500, 2501), (2527, 2528), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000)]

    demands = [0]*(num_tasks+2)

  elif data == 'file':
    filename = "DaSilvaUrrutia/n200w100.001.txt"
    file = open(filename, 'r')
    length = 202
    l = 0
    locations = [(0, 0)] * length
    time_windows = [(0, 0)] * length
    for line in file:
      values = line.split()
      if l > 0:
        locations[l-1] = (int(values[1][0:-3]), int(values[2][0:-3]))
        time_windows[l-1] = (int(values[4][0:-3]), int(values[5][0:-3]))
      l += 1
    locations[201] = locations[0]
    time_windows[0] = (0, horizon)
    time_windows[201] = (0, horizon)
    num_tasks = len(locations) - 2
    demands = [0]*(num_tasks+2)

  else:
    #Randomly generate locations
    locations = []
    for i in range(num_tasks+1):
        location = (random.randint(0, 49), random.randint(0, 49))
        locations.append((location))
        #dprint("location: " + str(location))
    locations.append(locations[0])
    dprint("locations: " + str(locations))

    demands = [0]*(num_tasks+2)
    #dprint("demands: " + str(demands))
    time_windows = [(0, horizon)]*(num_tasks+2)
    for i in range(num_tasks+1):
        if i == 0:
            start = 0
            end = 0
        elif timed and i <= num_tasks and (random.random() < 0.2):
            start = random.randint(int(i*time_window_end/num_tasks), int((i+1)*time_window_end/num_tasks))
            end = start + random.randint(0, int((i+1)*time_window_end/num_tasks)-start)
        else: 
            start = 0
            end = horizon
        time_windows[i] = (start, end)
    time_windows[-1] = time_windows[0]

  print("num_tasks: ", num_tasks)
  dprint("Time Windows: " + str(time_windows))

  if debug:
    for i in range(len(locations)):
      mystring = "Location " + str(i) + ": " + str(locations[i])
      while len(mystring) < 22:
        mystring += " "
      mystring += "   Window: " + str(time_windows[i])
      while len(mystring) < 48:
        mystring += " "
      mystring += "   Demand: " + str(demands[i])
      dprint(mystring)

  setup_solver_time = time.time()
  # Instantiate a mixed-integer solver, naming it SolveIntegerProblem.
  solver = pywraplp.Solver('SolveIntegerProblem',
                           pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
  
  """
  The equations used in the linear program solver were taken from the paper
  'Formulations for Minimizing Tour Duration of the Traveling Salesman Problem with Time Windows'
  https://ac.els-cdn.com/S2212567115009260/1-s2.0-S2212567115009260-main.pdf?_tid=8b22c1ab-ed28-45e1-9ece-0c6f0eae4d0a&acdnat=1527880219_37a4186ec7ae8408b23d4c3d1203e1bb
  """

  #The start times of the tasks are nonnegative integers
  times = [0]*(num_tasks+2)
  for i in range(num_tasks+2):
    times[i] = solver.NumVar(0.0, solver.infinity(), 'times[' + str(i) + ']')

  y = [0] * (num_tasks + 1)
  for i in range(num_tasks + 1):
    y[i] = [0] * (num_tasks + 1)

  for i in range(len(y)):
    for j in range(len(y[i])):
      y[i][j] = solver.BoolVar('y[' + str(i) + '][' + str(j) + ']')

  #t_i - t_0 >= t_0i  1...n
  constraint2 = [0] * (num_tasks)
  for i in range(num_tasks):
    constraint2[i] = solver.Constraint(distance(locations[i+1], locations[0]), solver.infinity())
    constraint2[i].SetCoefficient(times[i+1], 1)
    constraint2[i].SetCoefficient(times[0], -1)

  #t_n+1 - t_i >= t_i0  1...n
  constraint4 = [0] * (num_tasks)
  for i in range(num_tasks):
    constraint4[i] = solver.Constraint(distance(locations[i+1], locations[0]), solver.infinity())
    constraint4[i].SetCoefficient(times[num_tasks+1], 1)
    constraint4[i].SetCoefficient(times[i+1], -1)

  #t_i >= a_i  1...n
  constraint5 = [0] * (num_tasks)
  for i in range(num_tasks):
    constraint5[i] = solver.Constraint(time_windows[i+1][0], solver.infinity())
    constraint5[i].SetCoefficient(times[i+1], 1)

  #t_i <= b_i  1...n
  constraint6 = [0] * (num_tasks)
  for i in range(num_tasks):
    constraint6[i] = solver.Constraint(-solver.infinity(), time_windows[i+1][1])
    constraint6[i].SetCoefficient(times[i+1], 1)

  #t_i >= 0  0...n+1
  constraint7 = [0] * (num_tasks + 2)
  for i in range(num_tasks + 2):
    constraint7[i] = solver.Constraint(0, solver.infinity())
    constraint7[i].SetCoefficient(times[i], 1)

  #t_i - t_j + M(y_ij) >= t_ij  0...n
  constraint8 = [0] * (num_tasks + 1)
  for i in range(num_tasks + 1):
    for j in range(num_tasks + 1):
      constraint8[i] = solver.Constraint(distance(locations[i], locations[j]), solver.infinity())
      constraint8[i].SetCoefficient(times[i], 1)
      constraint8[i].SetCoefficient(times[j], -1)
      constraint8[i].SetCoefficient(y[i][j], M)

  #t_j - t_i - M(y_ij) >= t_ij - M  0...n
  constraint9 = [0] * (num_tasks + 1)
  for i in range(num_tasks + 1):
    for j in range(num_tasks + 1):
      constraint9[i] = solver.Constraint((distance(locations[i], locations[j]) - M), solver.infinity())
      constraint9[i].SetCoefficient(times[i], -1)
      constraint9[i].SetCoefficient(times[j], 1)
      constraint9[i].SetCoefficient(y[i][j], -M)

  #t_0 = 0
  constraint10 = solver.Constraint(0, 0)
  constraint10.SetCoefficient(times[0], 1)

  # Minimize t_n+1 - t_0
  objective = solver.Objective()
  objective.SetCoefficient(times[num_tasks+1], 1)
  objective.SetCoefficient(times[0], -1)
  objective.SetMinimization()

  """Solve the problem and print the solution."""
  result_status = solver.Solve()
  # The problem has an optimal solution.
  #assert result_status == pywraplp.Solver.OPTIMAL

  # The solution looks legit (when using solvers other than
  # GLOP_LINEAR_PROGRAMMING, verifying the solution is highly recommended!).
  assert solver.VerifySolution(1e-7, True)

  finished_solving_time = time.time()

  print('Number of variables =', solver.NumVariables())
  print('Number of constraints =', solver.NumConstraints())

  # The objective value of the solution.
  print('Optimal objective value = %d' % round(solver.Objective().Value()))
  print()
  # The value of each variable in the solution.
  variable_list = times

  for variable in variable_list:
    print('%s = %d' % (variable.name(), round(variable.solution_value())))


  printMap(variable_list, locations, time_windows, horizon)

  solve_time = finished_solving_time - setup_solver_time
  print("solve_time: ", solve_time)

if __name__ == '__main__':
  t0 = time.time()
  main()
  t1 = time.time()
  totalTime = t1-t0
  print("totalTime: ", totalTime)
