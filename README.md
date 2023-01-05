# Team 21

## Contributors

* Rudra Barua, Harvard University, <rudrabarua@college.harvard.edu>  
* Charlie Harrington, Harvard University, <charlesharrington@g.harvard.edu>  
* Fiona Henry, Harvard University, <fhenry@g.harvard.edu>  
* Michael Krumdick, Harvard University, <mkrumdick@g.harvard.edu>  
* Team supervisor is Fabian: <fabianw@seas.harvard.edu>

## Overview
Our code is split up into two main parts. The top level directory contains
contains all of our initial C++ code and our benchmarking. The `python` folder
contains our original python based baselines. The `chessenv` folder contains the
code for our python module. This folder contains its own reference readme for
instructions on how to build the python module. 

## Setup
The easiest way to interact with our code is through the provided Dockerfile. To
run the code locally, you can:

1. Build the image
```
docker build . -t chess
```
2. Run the container
```
docker run -it --rm chess ./main
```
On the cluster, we have already converted from Docker to Singularity and stored
it in the `shared_data` directory. Unless any changes are made to the
[Dockerfile](Dockerfile) itself, there is no need to rebuild the image. To run,
execute the following.
```
singularity run ~/shared_data/students/team21/t21.sif
```

## Reproducing Scaling Results 

`main.cpp` is configured to print out wall clock times for steping 100 steps on
n boards. To collect results for scaling analysis tables compile `main.cpp` then
run with the desired numbers of threads and boards. For example the command: 
```
OMP_NUM_THREADS=4 ./main 512
```
steps 512 boards 100 times using 4 threads. 
