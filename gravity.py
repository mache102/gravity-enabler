import os 
import sys
import time
import shutil
import numpy as np
import inspect 
import subprocess
import psutil

class Gravity:
    def __init__(self, 
                file_path,
                g=9.81,
                fps=10, 
                sim_length=30, 
                ground_distance=8):
        
        self.file_path = file_path
        with open(self.file_path, 'r') as f:
            self.content = f.read().splitlines()

        self.g = g
        self.fps = fps
        self.sim_length = sim_length
        self.ground_distance = ground_distance

    def to_array(self):
        # contents to array
        max_chars = 0
        content_arr = []

        for line in self.content:
            content_arr.append([*line])
            max_chars = max(len(line), max_chars)

        for line in content_arr:
            line[:] = [x if x != '' else ' ' for x in line]
            line.extend(' ' * (max_chars - len(line)))

        for _ in range(self.ground_distance):
            content_arr.append([' '] * max_chars)

        #print(content_arr)
        #sys.exit()
        return np.array(content_arr)
        

    def simulation(self, content_arr):
        # start simulation
        max_iter = self.sim_length * self.fps 
        prev_relative_pos = 0
        hidden_shift = 0
        next_shift = 0
        
        for iter in range(max_iter):
            print(f'iter {iter}')
            t1 = time.perf_counter()

            has_update = 0

            t = (iter + 1) / self.fps
            relative_pos = (self.g * (t ** 2)) / 2

            content_arr = content_arr.T 
            for col in content_arr:
                if all(s.isspace() for s in col):
                    continue 
                
                pos_shift = relative_pos - prev_relative_pos
                first_empty_idx = 0
                reverse = col[::-1]

                for idx, char in enumerate(reverse):
                    if char == ' ':
                        continue 

                    new_idx = int(np.ceil(idx - pos_shift - next_shift))
                    if first_empty_idx > new_idx:
                        new_idx = first_empty_idx 
                    else:
                        has_update = 1
                        

                    if new_idx != idx:
                        reverse[idx], reverse[new_idx] = reverse[new_idx], reverse[idx]
                        
                    first_empty_idx += 1

                col = reverse[::-1]

            next_shift = 0
            prev_relative_pos = relative_pos
            hidden_shift += relative_pos % 1
            if hidden_shift >= 1:
                next_shift = 1
                hidden_shift -= 1

            if not has_update:
                break

            #write
            content_arr = content_arr.T 
            with open(self.file_path, 'w') as f:
                for line in content_arr:
                    f.write(''.join(line) + '\n')

            tt = (1/self.fps) - (time.perf_counter() - t1)
            #print(f'{(tt * 1000):.4f} ms left')
            if tt > 0:
                time.sleep(tt)

    def start(self):
        content_arr = self.to_array()
        self.simulation(content_arr)

def yeet(file_path):
    process_list = psutil.process_iter()
    print(process_list)

    for process in process_list:
        try:
            process_info = process.as_dict(attrs=['pid', 'name', 'cmdline'])
            cmdline = process_info['cmdline']
            
            if cmdline is None or len(cmdline) == 0:
                continue
            print(process_info)
            if file_path in cmdline:
                process_pid = process_info['pid']
                # Terminate the process
                process.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, psutil.TimeoutExpired, psutil.Error):
            pass 

file_path = __import__('__main__').__file__
# frame = inspect.currentframe().f_back
# file_path = inspect.getframeinfo(frame).filename

gravity = Gravity(file_path)

try:
    gravity.start()
except KeyboardInterrupt:
    pass 

#yeet(file_path)
