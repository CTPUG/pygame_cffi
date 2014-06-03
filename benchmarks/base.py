''' Base class and tools for benchmarks '''

import pygame


class Benchmark(object):
    '''
    The base class for benchmarks.
    '''

    def __init__(self, *args):
        '''
        Arbitrary args can be passed to __init__ by the run_benchmark.py script.
        It's meant for stuff like number of sprites, surface dimensions, etc.
        '''
        pass

    def setUp(self):
        # necessary to receive the benchmark runner's QUIT event
        pygame.display.init()

    def main(self, clock):
        '''
        The performance of the stuff in here will be measured in FPS.
        '''
        pass

    def tearDown(self):
        pygame.display.quit()
