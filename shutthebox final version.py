from time import perf_counter
from itertools import combinations
import multiprocessing


def playable_moves(position):
    child = []
    all_dice_roll = dice_roll()
    for roll in all_dice_roll:
        roll_sum = sum(roll)
        move = [list(c) for c in combinations(position, 2) if sum(c) == roll_sum]
        if roll_sum in position:
            move.append([roll_sum])
        child.append(move)
    return child


def dice_roll():
    return [(a, b) for a in range(1, 7) for b in range(a, 7)]


def win_probability(position):
    if not position:
        return 1
    probability = []
    for moves in playable_moves(position):
        if not moves:
            probability.append(0)
        else:
            controllable_probability = []
            for move in moves:
                child_position = list(set(position) - set(move))
                controllable_probability.append(win_probability(child_position))
            probability.append(max(controllable_probability))
    return sum(probability) / len(probability)


def worker(i, positions, starting_position, probability_dict):
    probability = []
    for moves in positions:
        if not moves:
            probability.append(0)
        else:
            pos_eval = []
            for move in moves:
                pos_eval.append(win_probability(list(set(starting_position) - set(move))))
            probability.append(max(pos_eval))
    probability_dict[i] = probability


if __name__ == '__main__':
    t = perf_counter()
    all_dice_roll = dice_roll()
    starting_position = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    position = playable_moves(starting_position)
    cpu_amount = 12
    manager = multiprocessing.Manager()
    probability_dict = manager.dict()
    jobs = []
    for i in range(cpu_amount):
        positions = position[i*len(position)//cpu_amount:(i+1)*len(position)//cpu_amount]
        p = multiprocessing.Process(target=worker,
                                    args=(i, positions, starting_position, probability_dict))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()
    probability = [f for e in probability_dict.values() for f in e]
    print(100 * sum(probability) / len(probability))
    print(f"{perf_counter()-t} s")