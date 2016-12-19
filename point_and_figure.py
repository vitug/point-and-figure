# coding: utf-8

# для совместимости с версией 3
from __future__ import (absolute_import, division,
                       print_function, unicode_literals)
from builtins import *

import matplotlib.pyplot as plt
plt.rc('figure', figsize=(15, 15))
import pandas as pd
import numpy as np
from math import floor
from bokeh.plotting import figure, show, output_server, curdoc, vplot
from bokeh.io import output_notebook
from bokeh.client import push_session
from bokeh.models import Slider
import bokeh

class Point_and_Figure():
    def __init__(self):        
        self.box_size = 1000. # размер интервала        
        self.boxes_to_reverse = 3 # количество интервалов для разворота
        self.boxes = [] # массив для рисования графика
        self.levels = np.zeros(1)
        self.start_point_graph = 0. # стартовая точка для построение графика 
        self.scale_factor = 1.
        self.bokeh_picture = None
        self.x_x = []
        self.x_y = []
        self.o_x = []
        self.o_y = []
        self.digits_x = []
        self.digits_y = []
        self.digits_text = []
        self.xticks = None
        self.yticks = None
        self.grid_divider = 50.
        self.asset_ticker = 'SPFB.RTS'
        self.bokeh_ticks_format = '0,0'
        self.digits_on_graph_format = '0:.0f'
        
    def draw(self):
        #,changes, start_point, box_size
        self.prepare_datasource()

        # one way to force dimensions is to set the figure size:
        fig = plt.figure(figsize=(10, 10))
        # fig, ax = plt.subplots()
        # another way is to control the axes dimensions
        # for axes to have specific dimensions:
        #                  [ x0,  y0,   w,   h]  in figure units, from 0 to 1
        #ax = fig.add_axes([.15, .15, .7*.5, .7])
        ax = fig.add_axes([.15, .15, .7, .7])
    #     ax = plt.gca() 
        ax.yaxis.get_major_formatter().set_useOffset(False)
    #     ax.yaxis.get_major_formatter().set_powerlimits((0,1))
        plt.ticklabel_format(style='plain', axis='y') # scilimits=(0,10)

        symbol = {-1:'o',
                   1:'x'}
        ax.scatter(self.x_x, self.x_y,
                   marker=symbol[1],
                   s=50)   #<----- control size of scatter symbol
        ax.scatter(self.o_x, self.o_y,
                   marker=symbol[-1],
                   s=50)   #<----- control size of scatter symbol

        ax.set_xlim(0, len(self.xticks)+1)
    #     plt.show()
        fig.savefig('pointandfigure.png', dpi=300) 
        
    def draw_bokeh(self):
        self.prepare_datasource()  
        
        # one way to force dimensions is to set the figure size:
        p = figure(width=400, height=400, tools = "pan,wheel_zoom,reset,save")
        #p.yaxis.ticker = bokeh.models.tickers.SingleIntervalTicker(BOX)
        yticker = bokeh.models.FixedTicker()        
        yticker.ticks = list(self.yticks)
        xticker = bokeh.models.FixedTicker()        
        xticker.ticks = list(self.xticks)
        # ticker.interval = 1
        #p.xaxis.ticker = ticker
        p.ygrid.ticker = yticker        
        p.xgrid.ticker = xticker
        p.yaxis.formatter = bokeh.models.NumeralTickFormatter(format=self.bokeh_ticks_format)
        p.yaxis.ticker = yticker        
        #glyphs_size = BOX / 4 / len(self.yticks) * self.scale_factor
        #glyphs_size = min(p.plot_height / 2 / (len(self.yticks) + 3), p.plot_width / 2 / (len(self.xticks) + 3))
        glyphs_size = min(p.plot_height / 1.2 / (len(self.yticks) + 3), p.plot_width / 1.2 
                          / (len(self.xticks) + 3))
        if glyphs_size < 3:
            glyphs_size = 3
        #print('plot..')
        p.circle(self.o_x, self.o_y, alpha=0.5, size=glyphs_size, color="navy")
        p.cross(self.x_x, self.x_y, alpha=0.5, size=glyphs_size, color="navy", angle=np.pi/4)               
        #output_server("pf")
        show(p)
        self.bokeh_picture = p           
            
    def prepare_datasource(self):
        #,changes, start_point, box_size
        BOX = self.box_size
        START = self.start_point_graph
        self.yticks = set([START, START + BOX, START - BOX])
        self.xticks = set([0, -1, 1])
        changes = self.boxes
        
        def sign(val):
            return val / abs(val)

        chgStart = START
        self.x_x = []
        self.x_y = []
        self.o_x = []
        self.o_y = []
        self.digits_x = []
        self.digits_y = []   
        self.digits_text = [] 
        for ichg, chg in enumerate(changes):  
            if chg == 0:
                print('zero changes!')
                continue
            direction = int(sign(chg))
            abs_change = abs(chg)
            #abs_change = abs(chg) + 1
            if direction < 0:
                pass
                #abs_change = abs_change - 1                        
            
            x = [ichg + 1] * abs_change
            self.xticks = self.xticks.union(x)
            x = [value - 0.5 for value in x]
            
            if direction > 0:
                y = [chgStart + (i + 1) * BOX * direction for i in range(abs_change)]
            else:
                y = [chgStart + (i + 1) * BOX * direction for i in range(abs_change)]
                
            #y = [chgStart + (i) * BOX * direction for i in range(abs_change)]
            self.yticks = self.yticks.union(y)
            #y = [value - 0.5 * BOX for value in y]
            y = [value + 0.5 * BOX for value in y]
                     
            #print(x, y)
            #chgStart += BOX * sign(chg) * (abs(chg)-2)
            if direction < 0:
                pass
                #abs_change = abs_change + 1                        
            chgStart += BOX * direction * (abs_change)
            #chgStart += BOX * direction * (abs_change + 1)
            #print(chgStart)
            #chgStart += self.levels[ichg] # BOX * sign(chg) * (abs(chg)-2)
            if direction == -1:
                self.o_x += x
                self.o_y += y
            elif direction == 1:
                self.x_x += x
                self.x_y += y
            #graph_data.append([direction, x, y])
            
            if len(self.x_x) > 0:
                last_x = self.x_x[-1]
            else:
                last_x = 0
            if len(self.o_x) > 0:
                last_o = self.o_x[-1]
            else:
                last_o = 0            
            if last_x > last_o:
                max_x = last_x
            else:
                max_x = last_o
            
        for tick in self.yticks:
            self.digits_x.append(max_x + 1 / 2)
            self.digits_y.append(tick - self.box_size)
            self.digits_text.append(('{' + self.digits_on_graph_format + '}').format(tick))
            
            self.digits_x.append(max_x + 2)
            self.digits_y.append(tick - self.box_size)
            self.digits_text.append('')            
            
    def process_df(self, quote):
        H = quote[self.asset_ticker + '_High'].values
        L = quote[self.asset_ticker + '_Low'].values
        C = quote[self.asset_ticker + '_Close'].values
        O = quote[self.asset_ticker + '_Open'].values 
        self.process(O, H, L, C)
                    
    def log(self, msg):
        #print(msg)
        pass
        
    def process(self, O, H, L, C):
        self.grid_divider = self.box_size
        self.boxes = []
        last_box_level = 0 # последнее значение уровня
        direction = 0 # направление
        start_point_0 = 0.
        start_point = 0.
        box_size = self.box_size
        boxes_to_reverse = self.boxes_to_reverse
        data_length = H.shape[0]
        self.levels = np.zeros(data_length)
        opposite_boxes = 0.
        for i in range(data_length):           
            if direction == 0: # начальная точка        
                if C[i] > O[i]:
                    direction = 1
                    #start_point = (floor(L[i] / self.grid_divider) + 1) * self.grid_divider
                    start_point = (floor(L[i] / self.grid_divider)) * self.grid_divider
                    #start_point = L[i]
                    extremum = H[i]
                else:
                    direction = -1
                    start_point = (floor(H[i] / self.grid_divider)) * self.grid_divider
                    #start_point = H[i]
                    extremum = L[i]
                #self.start_point_graph = start_point # - direction * 0 * box_size# + direction * box_size
                distance_from_start = direction * (extremum - start_point) # positive value
                boxes_from_start = int(floor(distance_from_start / box_size))
                self.log('start {} dir {} boxes {}'.format(start_point, direction, boxes_from_start))
#                 if boxes_from_start < boxes_to_reverse:
#                     start_point = start_point - direction * (boxes_to_reverse - boxes_from_start) * box_size
#                     boxes_from_start = boxes_to_reverse
                #self.start_point_graph = start_point - direction * box_size
                self.start_point_graph = start_point
                last_box_level = start_point + direction * boxes_from_start * box_size
                boxes = direction * boxes_from_start
                self.log(boxes)
                self.boxes.append(boxes)
                self.log('start {} dir {} boxes {}'.format(start_point, direction, boxes_from_start))
            elif direction == 1 or direction == -1:
                new_last_box_level = -1.
                if direction == 1:
                    continue_level = H[i]
                    opposite_level = L[i]
                    sign = 1
                else:
                    continue_level = L[i]
                    opposite_level = H[i]
                    sign = -1
                if sign * (continue_level - last_box_level) >= box_size:
                    distance_from_start = (continue_level - start_point)
                    boxes_from_start = int(floor(distance_from_start / box_size))
                    new_last_box_level = start_point + boxes_from_start * box_size
                    #last_box_level = start_point + direction * boxes_from_start * box_size                    
                opposite_distance = sign * (last_box_level - opposite_level)        
                opposite_boxes = int(floor(opposite_distance / box_size))
                if opposite_boxes >= boxes_to_reverse and new_last_box_level < 0:                    
                    direction = - direction
                    self.boxes.append(direction * (opposite_boxes))
                    #self.boxes.append(direction * (opposite_boxes - 1))
                    #self.boxes.append(-(opposite_boxes - 2))
                    start_point = last_box_level
                    last_box_level = start_point + direction * opposite_boxes * box_size
                    #boxes_from_start = opposite_boxes
                    self.log('{} opposite boxes {} new level {} {}'.format(i, opposite_boxes, last_box_level, direction))
                elif new_last_box_level > 0:
                    last_box_level = new_last_box_level
                    #self.boxes[-1] = boxes_from_start - direction
                    self.boxes[-1] = boxes_from_start
                    self.log('{} new boxes {} new level {} {}'.format(i, boxes_from_start, last_box_level, direction))
            else:
                raise Exception('Wrong direction {}!'.format(direction))
            self.levels[i] = last_box_level
            #print(direction, opposite_boxes, last_box_level, self.boxes[-1])           