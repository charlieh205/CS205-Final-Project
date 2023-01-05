
import time
import queue

import chess
import numpy as np
import multiprocessing as mp

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
    "P",
]

def vec_to_board(rep):
    board = chess.Board()
    board.clear()

    for (i, square) in enumerate(chess.SQUARES_180):
        if rep[i] > 0:
            piece = chess.Piece.from_symbol(PIECES[int(rep[i] - 1)])
            board.set_piece_at(square, piece)
    return board


def board_to_vec(board):
    rep = np.zeros((64, ))

    for (i, square) in enumerate(chess.SQUARES_180):
        piece = board.piece_at(square)
        if piece:
            rep[i] = PIECES.index(piece.symbol()) + 1
    return rep


def get_board_reward_white(board):
    outcome = board.outcome()
    if outcome.winner:
        return int(outcome.winner)
    elif outcome.winner is None:
        return 0.0
    else:
        return -1

def random_sample(board):
    moves = list(board.legal_moves)
    return np.random.choice(moves)

def random_sample_vec(board_vec):
    board = vec_to_board(board_vec)
    moves = list(board.legal_moves)
    return np.random.choice(moves)

def step_board(opponent, board, move):
    
    reward = 0
    done = False
    if board.is_legal(move):

        board.push(move)

        if board.is_game_over():
            done = True
            reward = get_board_reward_white(board)
            board = chess.Board()
        else:
            response = opponent(board)
            board.push(response)
    
            if board.is_game_over():
                done = True
                reward = get_board_reward_white(board)
                board = chess.Board()
    else:
        reward = -1
        done = True
        board = chess.Board()

    return board, reward, done

class SequentialEnv:

    def __init__(self, n_envs):
        self.n_envs = n_envs
        self.games = [chess.Board() for _ in range(n_envs)]

    def reset(self):
        states = np.zeros((self.n_envs, 64))

        for (i, b) in enumerate(self.games):
            states[i] = board_to_vec(b)

        return states

    def step(self, actions):
        new_boards = np.zeros((self.n_envs, 64))
        rewards = np.zeros((self.n_envs, 1))
        dones = np.zeros((self.n_envs, 1))
        for (i, a) in enumerate(actions):
            new_board, reward, done = step_board(random_sample, self.games[i], a)

            new_boards[i] = board_to_vec(new_board)
            rewards[i] = reward
            dones[i] = done

        return new_boards, rewards, dones

    def clean(self):
        pass


def worker(state_q, action_q):
    env = SequentialEnv(1)

    state = env.reset()
    state_q.put(state)

    while True:
        action = action_q.get()
        out = env.step([action])
        state_q.put(out)


class StackedEnv:
    def __init__(self, n):
        self.n = n
        self._reset()

    def _reset(self):
        self.action_qs = [mp.Queue() for _ in range(self.n)]
        self.state_qs = [mp.Queue() for _ in range(self.n)]

        self.procs = [
            mp.Process(target=worker, args=(self.state_qs[i], self.action_qs[i]))
            for i in range(self.n)
        ]

        for p in self.procs:
            p.start()

    def reset(self):
        states = np.zeros((self.n, 64))

        total = {i: s for (i, s) in enumerate(self.state_qs)}

        while len(total.items()) > 0:
            for (i, s) in list(total.items()):
                try:
                    out = s.get_nowait()
                    states[i] = out
                    total.pop(i)
                except queue.Empty as e:
                    pass
                
        return states

    def step(self, actions):

        for i, aq in enumerate(self.action_qs):
            aq.put(actions[i])

        states = np.zeros((self.n, 64))
        rewards = np.zeros((self.n, 1))
        dones = np.zeros((self.n, 1))

        total = {i: s for (i, s) in enumerate(self.state_qs)}

        while len(total.items()) > 0:
            for (i, s) in list(total.items()):
                try:
                    s_out, r_out, d_out = s.get_nowait()
                    states[i] = s_out
                    dones[i] = d_out
                    rewards[i] = r_out
                    total.pop(i)
                except queue.Empty as e:
                    pass

        return states, rewards, dones

    def clean(self):
        for p in self.procs:
            p.kill()
            p.join()

def benchmark(env_type, n_envs, n_steps):
    env = env_type(n_envs)
    
    times = []
    states = env.reset()
    for _ in range(n_steps):
        actions = list(map(random_sample_vec, states))

        start = time.time()
        states, rewards, dones = env.step(actions)
        times.append(time.time() - start)

    env.clean()
    return times
    

if __name__ == '__main__':

    for n in range(10):
        times = benchmark(SequentialEnv, 2**n, 100)
        mean_time = np.mean(times)
        top_percent = np.percentile(times, 95)
        bottom_percent = np.percentile(times, 5)
        print(f'{2**n},{mean_time},{top_percent},{bottom_percent}')
