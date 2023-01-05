# chessenv

## Setup & Running code
The easiest way to interact with this code is through the Dockerfile. To build
our docker image, run:
```
docker build . -t chessenv
```
Then, to run the benchmark:
```
docker run -it --rm chessenv python /workdir/benchmark.py
```

We have pushed a version to dockerhub to make running the code on singularity
easier. Simply run:
```
singluratity pull docker://mkrum/chessenv
```
to download the sif file, which you can then run as
```
singluratity run chessenv_latest.sif
```

## Overview and Structure
The code is split up into two main folders. The C code for this module is
contained in `src` and the python code is contained in `chessenv`. See
`build.py` for the code used to build the C module with CFFI.

## Verification
In order to verify the correctness of our environment and our transitions, we
have a series of regression tests that compare the outputs of our model to the
well tested `python-chess` library. See `test/test_env.py` and
`test/test_rep.py` for these test.
