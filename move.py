import random
import copy


def swap(seq):
    # dont modify the input
    new_seq = copy.deepcopy(seq)

    pos1 = -1
    pos2 = -1

    while pos1 == pos2:
        pos1 = random.randint(0, len(new_seq) - 1)
        pos2 = random.randint(0, len(new_seq) - 1)

    new_seq[pos1], new_seq[pos2] = new_seq[pos2], new_seq[pos1]
    return new_seq

