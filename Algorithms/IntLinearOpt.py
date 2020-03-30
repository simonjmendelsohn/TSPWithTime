from __future__ import print_function
from ortools.linear_solver import pywraplp
import random
from operator import itemgetter
import sys
import math
import time
from termcolor import colored
import ast

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
      #print(values)
      val, index = min((val, idx) for (idx, val) in enumerate(values))
      #print(index)
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
  num_tasks = 30        #The number of tasks.
  timed = False          #If true some randomly generated times for tasks will be assigned
  data = "manual"
  if len(sys.argv) > 2 and sys.argv[1] == "file":
  	data = 'file'        #If manual tasks and time windows must be given manually rather than randomly constructed or taken from file.
  M = 1000000           #Can be any sufficiently large integer for the linear opt algorithm to work.

  if data == 'manual':
    #The first and last locations must be the same and are the starting location of the vehicle.  They do not count as tasks.
    locations = [(34, 32), (31, 10), (37, 5), (8, 33), (3, 31), (2, 49), (12, 4), (13, 49), (11, 49), (4, 12), (32, 15), (32, 24), (19, 0), (24, 36), (3, 44), (4, 6), (3, 3), (48, 22), (15, 19), (44, 24), (39, 6), (8, 41), (1, 18), (20, 19), (43, 32), (47, 24), (46, 31), (13, 2), (31, 22), (17, 11), (34, 32)]
    num_tasks = len(locations) - 2
    time_windows = [(0, horizon)]*(num_tasks+2)
    time_windows = [(0, 0), (25, 26), (36, 37), (93, 94), (100, 101), (119, 120), (174, 175), (220, 221), (222, 223), (266, 267), (297, 298), (306, 307), (343, 344), (384, 385), (413, 414), (452, 453), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000), (0, 10000)]

    demands = [0]*(num_tasks+2)

  elif data == 'file':
    filename = sys.argv[2]
    file = open(filename, 'r')
    locations = ast.literal_eval(file.readline())
    time_windows = ast.literal_eval(file.readline())
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
