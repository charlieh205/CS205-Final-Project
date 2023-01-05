LIBCHESS_DIR=/opt/

all:
	 g++ -fopenmp -std=c++17 -I ${LIBCHESS_DIR}/libchess/src/ -L ${LIBCHESS_DIR}/libchess/build/static/ -o main main.cpp -lchess

clean:
	rm -f main main_papi
