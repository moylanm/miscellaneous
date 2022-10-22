# coding: utf-8

'''
Author: Myles Moylan
Task:
    - Write a program that solves the following problem:
        - Three missionaries and three cannibals come to a river and find a boat that holds two people.

        - Everyone must get across the river to continue on the journey.
        - However, if the cannibals ever outnumber the missionaries on either bank, the missionaries
        will be eaten.
        - Find a series of crossings that will get everyone safely to the other side of the river.

    - Incorporate recursion and use classes to model the problem appropriately.
Notes:
    - Boat holds two, but problem does not say that there must be two in the boat at a time.
'''


from collections import Counter
import random


class Missionary:

    def __str__(self):
        return 'M'


class Cannibal:

    def __str__(self):
        return 'C'


class River:

    def __init__(self, missionaries=3, cannibals=3):
        if cannibals > missionaries:
            raise Exception('Need at least as many missionaries as cannibals to start.')

        self.start_bank = set([Missionary() for _ in range(missionaries)]
                              + [Cannibal() for _ in range(cannibals)])
        self.end_bank = set()
        self.crossings = set()

    def cross_safely(self, sequence):
        if len(self.start_bank) == 0:
            self.crossings.add(tuple(sequence))
        else:
            while True:
                try:
                    space_one = random.sample(self.start_bank, 1)[0]
                    self.start_bank.remove(space_one)
                except ValueError:
                    space_one = None

                try:
                    space_two = random.sample(self.start_bank, 1)[0]
                    self.start_bank.remove(space_two)
                except ValueError:
                    space_two = None

                if self.is_valid_cross_combo(self.end_bank.union({space_one, space_two})):
                    break

                self.start_bank.update({space_one, space_two})

            sequence.append((str(space_one), str(space_two)))
            self.end_bank.update({space_one, space_two})

            self.cross_safely(sequence)

    def is_valid_cross_combo(self, new_end_bank):
        start_bank_count = Counter([getattr(obj, '__class__') for obj in self.start_bank])
        end_bank_count = Counter([getattr(obj, '__class__') for obj in new_end_bank])

        if start_bank_count[Missionary] < start_bank_count[Cannibal] or \
           end_bank_count[Missionary] < end_bank_count[Cannibal]:
            return False

        return True

    def find_safe_crossing_sequences(self, iterations=10):
        for _ in range(iterations):
            self.cross_safely([])
            self.start_bank = self.end_bank.copy()
            self.end_bank.clear()

    def print_crossing_sequences(self):
        counter = Counter([getattr(obj, '__class__') for obj in self.start_bank])

        for list_ in self.crossings:
            start_bank_count = {'M': counter[Missionary], 'C': counter[Cannibal], 'None': 0}
            end_bank_count = {'M': 0, 'C': 0, 'None': 0}

            print('{0: >32} {1: >43}'.format('Starting Bank', 'Ending Bank'))
            for i, ele in enumerate(list_, 1):
                start_bank_count[ele[0]] -= 1
                start_bank_count[ele[1]] -= 1
                end_bank_count[ele[0]] += 1
                end_bank_count[ele[1]] += 1

                print('{0: <3} {1: <15}'.format(i, str(ele)), end='')
                print('Missionaries: {0: <3} -- {1: >10}: {2: <5}'.format(start_bank_count['M'],
                      'Cannibals', start_bank_count['C']), end=' | | '.ljust(8))
                print('Missionaries: {0: <3} -- {1: >10}: {2: <5}'.format(end_bank_count['M'],
                      'Cannibals', end_bank_count['C']))
            print()


if __name__ == '__main__':
    river = River(15, 12)

    river.find_safe_crossing_sequences()
    river.print_crossing_sequences()
