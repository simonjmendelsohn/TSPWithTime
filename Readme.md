# Traveling Salesman Problem with Appointments

This folder has five different implementations of the Traveling Salesman Problem with Appointments.  It also has an RMarkdown file designed to create graphs from the results of these algorithms.

### Prerequisites

python3 is required to run the code.

### Files

nearest\_neighbors\_heuristic.py - nearest neighbor heuristic implementation  
aco.py - ant-colony optimization implementation  
genetic.py - simplified genetic algorithm implementation   
IntLinearOpt.py - MIP (Mixed Integer Programming)  implementation  
v2_cvrptw.py - Adapted Vehicle Routing Implementation  
Planning - Graphs.Rmd - RMarkdown File to create graphs of results from Results  
Results - csv file of results  
Results.xlsx - excell file of results  

(I believe all the other files are just screenshots or images of graphs outputted from the Markdown File).


## Running the tests

In the code for the algorithm you want to run, replace the "locations" and "time\_windows" variables with the locations and appointments that you want to test on.  For the time\_windows, put all the appointments at the front of the list, with (0, 10000) (or some other reasonably large number) for the rest of the time\_windows.  Also, keep the coordinates of the locations in the range from (0,0) to (50,50) for the graphing function to work. 

For example, you might have 

locations = [(8, 19), (49, 18), (13, 10), (27, 23), (44, 43), (5, 33), (17, 28), (8, 28), (24, 48), (4, 20), (7, 10), (0, 40), (47, 6), (11, 4), (16, 34), (18, 13), (34, 8), (32, 27), (43, 0), (8, 16), (35, 24), (0, 14), (40, 19), (37, 5), (34, 24), (37, 0), (5, 9), (17, 4), (24, 2), (43, 35), (8, 19)]

time\_windows = [(0, 0), (47, 48), (135, 136), (198, 199), (252, 253), (327, 328), (344, 345), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000), (0, 1000)]

To generate random examples to run, use randomizer.py.  You can change how many tasks you want and what percentage of them appointments inside randomizer.py.  Then you just run 

`python randomizer.py`

To finally run one of the solvers, type 

`python IntLinearOpt.py` (to solve using Manhattan distance)

or

`python Int LinearOpt.py euclid` (to solve using Euclidean distance)

for example. 


## Authors

Simon Mendelsohn and Alex Mendelsohn.  Please email at simonjmendelsohn@gmail.com or alexjmendelsohn@gmail.com with any questions.

## Acknowledgments

* Thank you Stephanie Rosenthal for all your help and encouragement.
* hats off to Google Optimization Tools, for making the MIP and vehicle routing implementations much more managable
