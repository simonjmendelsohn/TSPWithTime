import random
import math
import sys
import numpy as np

'''
This program is designed to generate random sets of tasks and appointments for the Traveling Salesman Problem with Appointments.  See IntLinearOpt.py, nearest_neighbors_heuristic.py, genetic.py, aco.py, or v2_cvrptw.py for implementations.  
'''

#I calculate the distance between two points.  If the word "euclid" was used as a command line argument, the distance is calculated using Euclidean Distance.  Otherwise, it uses Manhattan Distance.  I am calculating the distance between points in this program in order to make sure all the appointments I generate are feasible. 
def distance(position_1, position_2):
    if sys.argv[-1] == "euclid":
        distance = np.sqrt((position_1[0] - position_2[0]) ** 2 + (position_1[1] - position_2[1]) ** 2)
        # print ("position_1[0], position_2[0], position_1[1], position_2[1]", position_1[0], position_2[0], position_1[1], position_2[1])
        # print ("euclid:", euclid)
        return np.ceil(distance)
    return (abs(position_1[0] - position_2[0]) +
            abs(position_1[1] - position_2[1]))

def main():

	num_tasks = 30 #Change this number for a different number of tasks

	#Change the numbers in percent to get lists of tasks with different percentages of them appointments.
	percent = {
		0: 0,
		1: 0.2,
		2: 0.5,
		3: 0.8,
	}

	for i in range(2,4):
		percent_appointment = percent[i]
		print ()
		print ()
		print ("Percentage Appointments: ", percent_appointment)

		locations = []
		for i in range(num_tasks):
			#Each location is an (x,y) coordinate, where x and y are in the range of 0 to 49.  The limit of 49 is just to make it easy to visualize on a graph.
		    location = (random.randint(0,49), random.randint(0, 49))
		    while location in locations:
		    	location = (random.randint(0,49), random.randint(0, 49))
		    locations.append(location)
		locations.append(locations[0])

		time_windows = [(0,0)]
		num_appointments = math.floor(percent_appointment * num_tasks)
		
		prev = 0
		for i in range(num_appointments):
			#The "time" variable represents the amount of time that will be allotted between two of the appointments.  I allot at least enough time to get to the next appointment, and randomly generate how much extra time is allotted (to be able to complete other tasks).  By default, this number is a randomly generated integer between 0 and 10.
			time = random.randint(distance(locations[i], locations[i + 1]), distance(locations[i], locations[i + 1]))
			time = time + prev
			time_windows.append((time, time + 1))
			prev = time

		#I add huge time-windows for the remaining points, effectively allowing them to be completed at any time.
		for i in range(len(locations) - num_appointments - 1):
			time_windows.append((0,10000))


		print("")
		print(locations )
		print (time_windows)
		print("")

if __name__ == '__main__':
	main()

