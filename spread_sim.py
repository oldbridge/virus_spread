# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 20:24:15 2020

@author: Xabi
"""


# TODO
# Limit mobility test
# Infection not always, but statistically
# Cure and inmune

import uuid
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter


health_status = ['healthy', 'infected', 'recovering', 'inmune', 'dead']
health_colors = ['k', 'r', 'g', 'b']

infect_radius = 8
infection_chance = 0.7
run_days = 50

world_size = 200
move_speed = 10
num_persons = 2000

hospital_capacity = 300

class Person():
    def __init__(self, status='healthy'):
        self.uuid = uuid.uuid4()
        self.x = np.random.uniform(0, world_size)
        self.y =  np.random.uniform(0, world_size)
        self.age = np.random.normal(0.0, 100)
        self.status = status
        self.infected_days = 0
        self.hospital_access = True
    
    def plot_person(self, ax):
        if self.status != "dead":
            ax.scatter(self.x, self.y, c=health_colors[health_status.index(self.status)])
    
    def update_position(self):
        if self.status != "dead":
            self.x = self.x + np.random.normal() * move_speed
            self.y = self.y + np.random.normal() * move_speed
            
            # Limit the people inside the world bounds
            if self.x < 0:
                self.x = 0
            if self.y < 0:
                self.y = 0
            if self.x > world_size:
                self.x = world_size
            if self.y > world_size:
                self.y = world_size
    
    def update_time_pass(self):
        if self.status != "dead":
            if self.status == 'infected' or self.status == 'recovering':
                self.infected_days += 1
            
            if self.infected_days == 7 and self.hospital_access:
                self.status = 'recovering'
                
            if self.infected_days > np.random.normal(13, 3):
                if self.age > 70 and np.random.uniform() > 0.55: # and np.random.uniform() > 0.55:
                    self.status = "dead"
                else:
                    self.status = 'inmune'
                if np.random.uniform() > 0.08:
                    self.status = 'inmune'
                else:
                    self.status = 'dead'
                self.infected_days = 0

        
class World():
    def __init__(self, person_num=2000):
        self.figure, (self.ax, self.ax_t) = plt.subplots(2, 1)
        
        # Set size
        self.figure.set_figheight(15)
        self.figure.set_figwidth(15)

        self.inhabitants = []
        for i in range(person_num):
            self.inhabitants.append(Person())
        # Add one sick fucker
        self.inhabitants.append(Person(status='infected'))
        
        self.infected_list = []
        self.dead_list = []
        self.healthy_list = []
        self.days = [0]
        self.update_counters()
        
    
    def update_counters(self):
        healthy_num = 0
        infected_num = 0
        dead_num = 0
        for inhabitant in self.inhabitants:
            if inhabitant.status == 'healthy' or inhabitant.status == 'inmune' :
                healthy_num += 1
            elif inhabitant.status == 'infected' or inhabitant.status == 'recovering':
                infected_num += 1
            elif inhabitant.status == 'dead':
                dead_num += 1
        self.healthy_list.append(healthy_num)
        self.infected_list.append(infected_num)
        self.dead_list.append(dead_num)
        
    def plot_initial(self):
        for inhabitant in self.inhabitants:
            inhabitant.plot_person(self.ax)
        plt.show()
    
    def init_axis(self):
        self.ax.clear()
        
        self.ax_t.set_xlabel("Egunak")
        self.ax_t.set_ylabel("Pertsonak")
        
    def update_day(self, i):
        self.days.append(i)
        self.ax.clear()
        self.ax.set_ylim([-world_size * 0.1, world_size + world_size * 0.1])
        self.ax.set_xlim([-world_size * 0.1, world_size + world_size * 0.1])
        
        for inhabitant in self.inhabitants:
            if self.infected_list[-1] >= hospital_capacity:
                inhabitant.hospital_access = False
            #inhabitant.update_position()
            inhabitant.update_time_pass()
            if inhabitant.status == 'infected':
                for vecino in self.inhabitants:  # See if it will infect people nearby
                    if np.sqrt((vecino.x - inhabitant.x) ** 2 + (vecino.y - inhabitant.y) ** 2) < infect_radius and vecino.status == 'healthy' and np.random.uniform() < infection_chance:
                        vecino.status = 'infected'
                        
            inhabitant.plot_person(self.ax)
        
        # End of day counting of people status
        self.update_counters()
        #rint(f"Healthy: {self.healthy_num} Infected: {self.infected_num}")
        
        # Plot time evolution
        self.ax_t.plot(self.days, self.infected_list, 'xr-')
        self.ax_t.plot(self.days, self.healthy_list, 'xk-')
        self.ax_t.plot(self.days, self.dead_list, 'xb-')
        self.ax_t.plot(self.days, [hospital_capacity] * len(self.days), 'k--')
        self.ax_t.legend(['Eri', 'Osasuntsu', 'Hilda', 'Osasun ahalmena'])
        self.ax.set_title(f"Eguna: {i} Hildakoak: {self.dead_list[-1]}")
        
        
    def iterate(self, num=100):
        return FuncAnimation(self.figure, self.update_day, init_func=self.init_axis, frames=num, repeat=False)
        
if __name__ == '__main__':
    write = False
    
    world = World(num_persons)
    line_ani = world.iterate(run_days)
    if write:
        writer = FFMpegWriter()
        line_ani.save('spread.mp4', writer=writer)
    else:
        plt.show()