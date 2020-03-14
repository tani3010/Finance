# -*- coding,  utf-8 -*-
import time

class StopWatch:
    def __init__(self):
        self.reset()

    def reset(self):
        self.start_time = time.time()
        
    def get_elapsed_time(self):
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        return elapsed_time

    def show_elapsed_time(self):
        print ('elapsed time:{0:.2f}'.format(self.get_elapsed_time()) + '[sec]')