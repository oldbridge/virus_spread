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

people_type = ['traveler', 'static', 'mover', 'free']
#people_type_p = [0.4, 0.495, 0.1, 0.005]
people_type_p = [0.5, 0.4, 0.1, 0]

add_labels = True
cities = [(250, 250), (250, 750), (750, 750), (750, 250)]
hospital_location = (500, 500)
city_radius = [50, 100, 150, 30]
health_status = ['healthy', 'infected', 'recovering', 'inmune', 'dead']
health_colors = ['k', 'r', 'g', 'b']

infect_radius = 10
infection_chance = 0.8
run_days = 50

world_size = 1000
move_speed = 100
num_persons = 1500

hospital_capacity = 60

class Person():
    def __init__(self, status='healthy', type=None, position=None):
        if type is None:
            self.type = np.random.choice(people_type, p=people_type_p)
        else:
            self.type = type
        if position is None:
            self.set_speed()
        else:
            self.x, self.y = position
            self.moving_speed = move_speed
            if self.type == 'traveler':
                self.traveler_set_target()
        self.age = np.random.normal(0.0, 100)
        self.status = status
        self.infected_days = 0
        self.hospital_access = True
    
    def set_speed(self):
        def get_pos():
            city_idx = np.random.randint(0, len(cities))
            x = np.random.normal(cities[city_idx][0], city_radius[city_idx])
            y = np.random.normal(cities[city_idx][1], city_radius[city_idx])
            return x, y
        
        if self.type == 'free':
            self.x = np.random.uniform(0, world_size)
            self.y =  np.random.uniform(0, world_size)
            self.moving_speed = move_speed
        elif self.type == 'static':
            self.x, self.y = get_pos()
            self.moving_speed = 0
        elif self.type == 'mover':
            self.x, self.y = get_pos()
            self.moving_speed = move_speed
        elif self.type == 'traveler':
            self.x, self.y = get_pos()
            self.traveler_set_target()
            self.moving_speed = move_speed
    
    def traveler_set_target(self):
        city_idx = np.random.randint(0, len(cities))
        self.target = cities[city_idx]
        self.direction = np.arctan2(self.target[0] - self.x, self.target[1] - self.y)
        
    def plot_person(self, ax):
        if self.status != "dead":
            ax.scatter(self.x, self.y, c=health_colors[health_status.index(self.status)], s=4)
    
    def update_position(self):
        if self.status == 'recovering':
            self.x = np.random.normal(hospital_location[0], 10)
            self.y = np.random.normal(hospital_location[1], 10)
        #elif self.status == 'inmune':
        #    self.set_speed()
        
        if self.status != "dead":
            if self.type == 'traveler':
                if np.sqrt((self.x - self.target[0]) ** 2 + (self.y - self.target[1]) ** 2) < move_speed:
                    self.traveler_set_target()
                else:
                    x_speed = self.moving_speed * np.sin(self.direction)
                    y_speed = self.moving_speed * np.cos(self.direction)
                    self.x = self.x + x_speed
                    self.y = self.y + y_speed
            else:
                self.x = self.x + np.random.normal() * self.moving_speed
                self.y = self.y + np.random.normal() * self.moving_speed
            
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
            
            if (self.status == 'infected' 
                and self.infected_days > np.random.normal(5.2, 6.25) 
                and self.hospital_access  # Only recovering if there is place in hospitals
                and np.random.uniform() > 0.7 ):  # 80% of cases are mild can recover at home
                self.status = 'recovering'
                self.moving_speed = 0
                
            if self.infected_days > np.random.normal(13, 3):
                if self.age > 70 and np.random.uniform() > 0.75 and self.status == 'recovering':
                    self.status = "dead"
                elif self.age > 70 and np.random.uniform() > 0.55 and self.status == 'infected':
                    self.status = "dead"
                else:
                    self.status = 'inmune'
                
                if np.random.uniform() > 0.08:
                    self.status = 'inmune'
                else:
                    self.status = 'dead'
                self.infected_days = 0
                self.set_speed()

        
class World():
    def __init__(self, person_num=2000):
        self.figure, (self.ax, self.ax_t) = plt.subplots(2, 1)
        
        # Set size
        self.figure.set_figheight(15)
        self.figure.set_figwidth(15)

        self.inhabitants = []
        for i in range(person_num):
            self.inhabitants.append(Person())
        # Add one sick fucker in one of the cities
        self.inhabitants.append(Person(status='infected', type='traveler', position=cities[0]))
        
        self.infected_list = []
        self.hospital_list = []
        self.dead_list = []
        self.healthy_list = []
        self.days = [0]
        self.update_counters()
        
    
    def update_counters(self):
        healthy_num = 0
        infected_num = 0
        recovering_num = 0
        dead_num = 0
        for inhabitant in self.inhabitants:
            if inhabitant.status == 'healthy' or inhabitant.status == 'inmune' :
                healthy_num += 1
            elif inhabitant.status == 'infected':
                infected_num += 1
            elif inhabitant.status == 'recovering':
                recovering_num += 1
            elif inhabitant.status == 'dead':
                dead_num += 1
        self.healthy_list.append(healthy_num)
        self.infected_list.append(infected_num)
        self.hospital_list.append(recovering_num)
        self.dead_list.append(dead_num)
        
    def plot_initial(self):
        for inhabitant in self.inhabitants:
            inhabitant.plot_person(self.ax)
        plt.show()
    
    def init_axis(self):               
        self.ax_t.set_xlabel("Egunak")
        self.ax_t.set_ylabel("Pertsonak")
        
        
    def add_labels(self):
        for city, city_r in zip(cities, city_radius):    
            self.ax.add_artist(plt.Circle(city, city_r, fill=False, color='b', linestyle='--'))
        self.ax.add_artist(plt.Circle(hospital_location, 10, fill=False, color='g', linestyle='--'))
            
    def update_day(self, i):
        self.days.append(i)
        self.ax.clear()
        self.ax.set_aspect(1)
        if add_labels:
            self.add_labels()
        self.ax.set_ylim([-world_size * 0.1, world_size + world_size * 0.1])
        self.ax.set_xlim([-world_size * 0.1, world_size + world_size * 0.1])
        
        for inhabitant in self.inhabitants:
            if self.hospital_list[-1] >= hospital_capacity:
                inhabitant.hospital_access = False
            else:
                inhabitant.hospital_access = True
            inhabitant.update_position()
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
        self.ax_t.plot(self.days, self.hospital_list, 'xy-')
        self.ax_t.plot(self.days, self.healthy_list, 'xk-')
        self.ax_t.plot(self.days, self.dead_list, 'xb-')
        self.ax_t.plot(self.days, [hospital_capacity] * len(self.days), 'k--')
        self.ax_t.legend(['Kutsatuta (kontrol gabe)', 'Ospitalean', 'Osasuntsu', 'Hilda', 'Osasun ahalmena'])
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