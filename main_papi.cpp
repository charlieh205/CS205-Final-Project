#include <iostream>
#include <libchess/move.hpp>
#include <libchess/position.hpp>
#include <omp.h>
#include <string>
#include <vector>
#include <time.h> 
#include <algorithm>
#include <random>
#include "papi.h"

#define L1_SIZE_KB 32
#define L2_SIZE_KB 256
#define L3_SIZE_KB 40960

// template for generating random moves
template <class T>
T random_select(std::vector<T> input) {
    int total = input.size();
    std::vector<T> out;
    std::sample(input.begin(), input.end(), std::back_inserter(out),  1,  std::mt19937{std::random_device{}()});
    return out[0];
}

// engine class for random move generation
class Engine {
public:
    libchess::Move move(libchess::Position);
};

// method for generating random move
libchess::Move Engine::move(libchess::Position board) {
    // get legal moves from board
    std::vector<libchess::Move> moves = board.legal_moves();
    // randomly select from legal moves
    return random_select(moves);
}

// class for applying actions across vectors of boards
class Vectorized {
public:
    std::vector<libchess::Position> boards;

    Vectorized(int n, Engine e);

    Engine engine;

    void apply_moves(std::vector<libchess::Move>);
    std::vector<std::vector <int>> step(std::vector<libchess::Move>);
    std::vector<libchess::Move> sample_moves();

};

// initializer
Vectorized::Vectorized(int n, Engine e) {
    engine = e;
    for (int i = 0; i < n; i++) {
        libchess::Position new_start{"startpos"};
        boards.push_back(new_start);
    }
}

// method for applyting moves to every board
void Vectorized::apply_moves(std::vector<libchess::Move> moves) {
    for (int i = 0; i < moves.size(); i++) {
        boards[i].makemove(moves[i]);
    }
}

// method for sampling moves from every board
std::vector<libchess::Move> Vectorized::sample_moves() {
    std::vector<libchess::Move> sample(boards.size());
    for (int i = 0; i < boards.size(); i++) {
        // get legal moves from board
        std::vector<libchess::Move> moves = boards[i].legal_moves();
        // randomly select from legal moves
        sample[i] = random_select(moves);
    }

    return sample;
}

// function for converting libchess board to vector
// cast libcess pieces to integers
std::vector<int> board_to_vector(const libchess::Position pos) {
    // board is 8x8, flattens to 64x1
    std::vector<int> vec(64, 0);
    for (int i = 0; i < 64; i++) {
        const auto sq = libchess::Square(i);
        const auto bb = libchess::Bitboard{sq};
        // check piece type, see comment at bottom for mapping
        if (pos.pieces(libchess::Side::White, libchess::Piece::Pawn) & bb) {
            // os << 'P';
            vec[i] = 12;
        } else if (pos.pieces(libchess::Side::White, libchess::Piece::Knight) & bb) {
            // os << 'N';
            vec[i] = 8;
        } else if (pos.pieces(libchess::Side::White, libchess::Piece::Bishop) & bb) {
            // os << 'B';
            vec[i] = 9;
        } else if (pos.pieces(libchess::Side::White, libchess::Piece::Rook) & bb) {
            // os << 'R';
            vec[i] = 7;
        } else if (pos.pieces(libchess::Side::White, libchess::Piece::Queen) & bb) {
            // os << 'Q';
            vec[i] = 10;
        } else if (pos.pieces(libchess::Side::White, libchess::Piece::King) & bb) {
            // os << 'K';
            vec[i] = 11;
        } else if (pos.pieces(libchess::Side::Black, libchess::Piece::Pawn) & bb) {
            // os << 'p';
            vec[i] = 6;
        } else if (pos.pieces(libchess::Side::Black, libchess::Piece::Knight) & bb) {
            // os << 'n';
            vec[i] = 2;
        } else if (pos.pieces(libchess::Side::Black, libchess::Piece::Bishop) & bb) {
            // os << 'b';
            vec[i] = 3;
        } else if (pos.pieces(libchess::Side::Black, libchess::Piece::Rook) & bb) {
            // os << 'r';
            vec[i] = 1;
        } else if (pos.pieces(libchess::Side::Black, libchess::Piece::Queen) & bb) {
            // os << 'q';
            vec[i] = 4;
        } else if (pos.pieces(libchess::Side::Black, libchess::Piece::King) & bb) {
            // os << 'k';
            vec[i] = 5;
        } 
    }
    return vec;

}

// conduct single step on boards
std::vector<std::vector <int>> Vectorized::step(std::vector<libchess::Move> moves_vec) {
    std::vector<std::vector <int>> board_vec(boards.size(), std::vector<int>(64,0));
#pragma omp parallel for
    for (int i = 0; i < boards.size(); i++) {
        boards[i].makemove(moves_vec[i]);
        if (boards[i].legal_moves().size() == 0) {
            boards[i] = libchess::Position{"startpos"};
        }
        // convert libchess board to vector representation
        std::vector<int> newboard = board_to_vector(boards[i]);
        board_vec[i] = newboard;
    }
    return board_vec;
}

int main() {
    // define number of boards and create data structures
    const int nboards = 1000000;
    Vectorized ctxt(nboards, Engine());
    std::vector<libchess::Move> moves(nboards, ctxt.boards[0].parse_move("e2e4"));

    int N = 1; // number of steps

    // initialize PAPI
    int event_set = PAPI_NULL;
    int events[4] = {PAPI_TOT_CYC,
                     PAPI_TOT_INS,
                     PAPI_LST_INS,
                     PAPI_L1_DCM};
    long long int counters[4];
    PAPI_library_init(PAPI_VER_CURRENT);
    PAPI_create_eventset(&event_set);
    PAPI_add_events(event_set, events, 4);

    // start PAPI measurement
    PAPI_start(event_set);

    const long long int t0 = PAPI_get_real_nsec();
    Engine engine = Engine(); 
    for (int i = 0; i < N; i ++)  {
        std::vector<libchess::Move> moves_vec(nboards);
        for(int j = 0; j < nboards; j++){
            // make random moves
            moves_vec[j] = engine.move(ctxt.boards[j]);
        }
        // step every board
        ctxt.step(moves_vec);
    }

    const long long int t1 = PAPI_get_real_nsec();
    
    // stop PAPI and get counter values
    PAPI_stop(event_set, counters);

    const long long total_cycles = counters[0];       // cpu cycles
    const long long total_instructions = counters[1]; // any
    const long long total_load_stores = counters[2];  // number of such instructions
    const long long total_l1d_misses = counters[3];   // number of access request to cache line
    const long long flops = total_instructions - total_load_stores; // flops

    const double twall = (static_cast<double>(t1) - t0) * 1.0e-9; // seconds
    const double IPC = static_cast<double>(total_instructions) / total_cycles;
    const double OI =
        static_cast<double>(flops) / (total_load_stores);
    const double float_perf = flops / twall * 1.0e-9; // Gflop/s

    std::cout << "Total cycles:                 " << total_cycles << '\n';
    std::cout << "Total instructions:           " << total_instructions << '\n';
    std::cout << "Instructions per cycle (IPC): " << IPC << '\n';
    std::cout << "L1 cache size:                " << L1_SIZE_KB << " KB\n";
    std::cout << "L2 cache size:                " << L2_SIZE_KB << " KB\n";
    std::cout << "L3 cache size:                " << L3_SIZE_KB << " KB\n";
    std::cout << "Total flops:           " << flops << " FLOPS\n";
    std::cout << "Total L1 data misses:         " << total_l1d_misses << '\n';
    std::cout << "Total load/store:             " << total_load_stores << '\n';
    std::cout << "Operational intensity:        " << std::scientific << OI << '\n';
    std::cout << "Performance [Gflop/s]:        " << float_perf << '\n';
    std::cout << "Wall-time   [micro-seconds]:  " << twall * 1.0e6 << '\n';
}

/*
PIECES = [
    "r",
    "n",
    "b",
    "q",
    "k",
    "p",
    "R",
    "N",
    "B",
    "Q",
    "K",
    "P"
]
*/
