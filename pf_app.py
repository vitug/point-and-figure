'''
Use the ``bokeh serve`` command to run the example by executing:

    bokeh serve pf_app.py

additonal parameter for fast close session (time in milliseconds):
--unused-session-lifetime 10 --check-unused-sessions 10


at your command prompt. Then navigate to the URL

    http://localhost:5006/pf_app

in your browser.
'''

import numpy as np
import pandas as pd
import sys
sys.path.insert(0, 'D:\\vit\\programing\\py\\robostocks')
sys.path.insert(0, 'Z:\\My_Folder\\Programming\\Python\\robostocks')
sys.path.insert(0, '/home/jupyter/bokeh/pf')
sys.path.insert(0, 'C:\\Users\\admin1c\\Documents\\robostocks')
sys.path.insert(0, 'c:\\python\\pf')
#print(sys.path)
import point_and_figure
from bokeh.plotting import Figure
from bokeh.models import ColumnDataSource, HBox, VBoxForm, CustomJS
from bokeh.models.widgets import Slider, TextInput, Button, PreText
from bokeh.io import curdoc, push, curstate
import bokeh
import traceback
from datetime import datetime, timedelta, date
from socket import timeout

def show_exception_info():
    #text = PreText(text=traceback.format_exc()) 
    #curdoc().clear()
    #curdoc().add_root(text)
    print(traceback.format_exc())
    
try:
    import finamquote_dwl as fn
except:
    show_exception_info()
markers = ['-', '\\', '|', '/',]
data_refresh_interval = 10000 # in milliseconds
days_look_back_min_candles = 30 # days look back when load data first time

class pf_graph:
    def end_date(self):
        now = date.today() + timedelta(hours = 4)        
        return now.strftime("%Y%m%d")
    
    def get_quotes(self):
        self.data_slice = slice(-self.data_length,None)        
        self.pf.asset_ticker = self.ticker
        quote = fn.get_quotes_finam(self.ticker, start_date=self.from_date, end_date=self.end_date(), period=self.quote_period, verbose=False, timeout=30)
        self.quote = quote[self.data_slice]
        #print(self.quote.tail())
        #self.quote.to_csv('/home/jupyter/bokeh/pf/quotes_{}'.format(self.quote_period))
        
    def update_quotes(self):
        quote = self.quote
        last_day = quote.ix[-1].name
        last_day_begin = datetime(last_day.year, last_day.month, last_day.day) 
        quote_base = quote.ix[:last_day_begin + timedelta(seconds = -1)]
        last_day_str = last_day_begin.strftime('%Y%m%d')
        #while True:
        #print('get quotes')
        try:
            quote = fn.get_quotes_finam(self.ticker, start_date=last_day_str, end_date=self.end_date(), period=self.quote_period, verbose=False, timeout=5)
        except timeout as e:
            print('get quotes: timeout, period={}!'.format(self.quote_period)) 
            self.text.value = 'timeout!'
            return
        except:
            self.text.value = 'get quote error!'
            return
        #print('obtain quotes')
        self.quote = quote_base.append(quote)[self.data_slice]
        time_str = quote.ix[-1].name.strftime('%Y-%m-%d %H:%M')
        if self.text_marker == len(markers) - 1:
            self.text_marker = 0
        else:
            self.text_marker += 1
        self.text.value = '{} [{}] {}'.format(markers[self.text_marker], time_str, quote.ix[-1][self.ticker + '_Close'])
        #time.sleep(1)        
        
    def __init__(self, quote_period, box_size, graph_name, candles = 30):
        # Set up data
        self.graph_counter = 0
        self.data_length = candles
        self.data_slice = slice(-self.data_length,None)
        self.quote_period = quote_period
        self.ticker = 'SPFB.RTS'
        self.box_size_divider = 1.
        
        self.pf = point_and_figure.Point_and_Figure()

        #print(quote_period)
        if (quote_period == 'daily' or quote_period == 'hour'):
            self.from_date = (date.today() - timedelta(days=days_look_back_min_candles * 5)).strftime('%Y%m%d')
        else:
            self.from_date = (date.today() - timedelta(days=days_look_back_min_candles)).strftime('%Y%m%d')

        self.get_quotes()
        self.last_quote_date = None
                
        self.pf.box_size = box_size
        self.pf.process_df(self.quote)
        self.pf.prepare_datasource()  
        
        self.plot = Figure(plot_height=400, plot_width=600, title=graph_name,
              tools="crosshair,pan,reset,resize,wheel_zoom,save",
             )
        self.yticker = bokeh.models.FixedTicker() 
        #print pf.yticks
        self.yticker.ticks = list(self.pf.yticks)
        self.xticker = bokeh.models.FixedTicker()        
        self.xticker.ticks = list(self.pf.xticks)
        # ticker.interval = 1
        #p.xaxis.ticker = ticker
        self.plot.ygrid.ticker = self.yticker        
        self.plot.xgrid.ticker = self.xticker
        self.plot.yaxis.formatter = bokeh.models.NumeralTickFormatter(format=self.pf.bokeh_ticks_format)
        self.plot.yaxis.ticker = self.yticker
        #self.plot.ygrid.band_fill_alpha = 0.05
        #self.plot.ygrid.band_fill_color = "navy"        
        #self.glyphs_size = 100.
        #self.glyphs_size = self.pf.box_size / 1. / len(self.pf.yticks) * self.pf.scale_factor
        
        self.scale = Slider(title="scale", value=300, start=300, end=3000, step=1)
        self.scale.on_change('value', self.scale_change)  
        
        self.recalc_glyphs_size = True
        self.calc_glyphs()    
        self.source_x = ColumnDataSource(data=dict(x=self.pf.x_x, y=self.pf.x_y, size=self.glyphs_size_x))
        self.source_o = ColumnDataSource(data=dict(x=self.pf.o_x, y=self.pf.o_y, size=self.glyphs_size_o))
        self.source_digits = ColumnDataSource(data=dict(x=self.pf.digits_x, y=self.pf.digits_y, text=self.pf.digits_text, size=self.font_size))
        self.graph_o = self.plot.circle('x', 'y', source=self.source_o, alpha=0.5, size='size', color="navy")
        self.graph_x = self.plot.cross('x', 'y', source=self.source_x, alpha=0.5, size='size', color="navy", angle=np.pi/4)
        self.graph_digits = self.plot.text('x', 'y', source=self.source_digits, alpha=0.5, text='text', color="navy", text_font_size='size') #text_font_size
        
        self.box = Slider(title="box", value=self.pf.box_size, start=10, end=500, step=1)
        self.box.on_change('value', self.box_change)       
  
        self.text = TextInput()
        self.text_marker = 0        
        
    def calc_glyphs(self):
        #self.glyphs_size = self.pf.box_size / 4. / len(self.pf.yticks) * self.pf.scale_factor
        #print self.glyphs_size
        if self.recalc_glyphs_size:
            self.glyphs_size = min(self.plot.plot_height / 1.2 / (len(self.pf.yticks) + 3), self.plot.plot_width / 1.2 / (len(self.pf.xticks) + 3))
            self.scale.value = int(self.glyphs_size * 100)
        self.recalc_glyphs_size = False
        if self.glyphs_size < 3:
            self.glyphs_size = 3
        self.glyphs_size_x = [self.glyphs_size for _ in self.pf.x_x]
        self.glyphs_size_o = [self.glyphs_size for _ in self.pf.o_x]
        self.font_size = ['{}px'.format(self.glyphs_size) for _ in self.pf.digits_x]
        #print(self.glyphs_size_x)
            
    def scale_change(self, attrname, old, new):
        self.glyphs_size = self.scale.value / 100.
        #print(self.glyphs_size)
        
    def box_change(self, attrname, old, new):
        self.pf.box_size = self.box.value / self.box_size_divider
        self.recalc_glyphs_size = True
            
    def update_data(self, attrname, old, new):
        #print('box')
        # Get the current slider values
             
        # Generate the new curve
        self.pf.process_df(self.quote)
        self.pf.prepare_datasource()
        self.yticker.ticks = list(self.pf.yticks)
        self.xticker.ticks = list(self.pf.xticks)
        self.calc_glyphs()
        #self.graph_o.glyph.size = self.glyphs_size
        #self.graph_x.glyph.size = self.glyphs_size
        #self.shuffle(x=self.pf.x_x, y=self.pf.x_y)
        data = dict(x=self.pf.x_x, y=self.pf.x_y, size=self.glyphs_size_x)
        self.source_x.data = data
        #self.shuffle(x=self.pf.o_x, y=self.pf.o_y)
        data = dict(x=self.pf.o_x, y=self.pf.o_y, size=self.glyphs_size_o)
        self.source_o.data = data
        data = dict(x=self.pf.digits_x, y=self.pf.digits_y, text=self.pf.digits_text, size=self.font_size)
        self.source_digits.data = data        
        #self.source_o.trigger('change')       
        #push()
        
#quote = pd.read_csv('rts.csv')


graphs = []
paused = False

def change_source():
    try:
        curdoc().remove_periodic_callback(reload_data)
        paused = True
        for graph in graphs:
            graph.ticker = ticker_input.value
            graph.box_size_divider = float(div_input.value)
            graph.pf.digits_on_graph_format = '0:.{}f'.format(format_input.value)
            zeroes = ''
            for i in range(int(format_input.value)):
                zeroes += '0'
            graph.pf.bokeh_ticks_format = '0,0.{}'.format(zeroes)
            #print(graph.pf.bokeh_ticks_format)
            graph.plot.yaxis.formatter = bokeh.models.NumeralTickFormatter(format=graph.pf.bokeh_ticks_format)
            graph.data_length = int(length_input.value)
            graph.box_change('value', 0, 0)
            graph.get_quotes()
            graph.recalc_glyphs_size = True
        paused = False
    except:
        print('error changing source!')
        show_exception_info()
    curdoc().add_periodic_callback(reload_data, data_refresh_interval)
def reload_data():
    try:
        curdoc().remove_periodic_callback(reload_data)
        if paused:
            return
        for graph in graphs:
            #print(graph.ticker)
            graph.update_quotes()
            graph.update_data('value',0 ,0)
    except:
        show_exception_info()
        for graph in graphs:
            graph.text.value = 'error!'
    curdoc().add_periodic_callback(reload_data, data_refresh_interval)        
try:    
    curdoc().clear()
    text = PreText(text="Loading data...") 
    #curdoc().add_root(text)
    button = Button(label='Please wait, loading data...')
    curdoc().add_root(button)
    
    start_candles = 30
    graph = pf_graph('5min', 50, '5 минут', start_candles)
    graphs.append(graph)

    graph = pf_graph('15min', 100, '15 минут', start_candles)
    graphs.append(graph)

    graph = pf_graph('hour', 150, '1 час', start_candles)
    graphs.append(graph)

    graph = pf_graph('daily', 300, '1 день', start_candles)
    graphs.append(graph)
    # Set up layouts and add to document
    #inputs = VBoxForm(children=[text, offset, amplitude, phase, freq])

    ticker_input = TextInput(value = 'SPFB.RTS')
    div_input = TextInput(value = '1.')
    length_input = TextInput(value = str(start_candles))
    format_input = TextInput(value = '0')    
    button = Button(label='Change')
    button.on_click(change_source)
    
    curdoc().clear()
    
    curdoc().add_root(HBox(children=[button, ticker_input, div_input, length_input, format_input], width=900))

    for graph in graphs:
        inputs = VBoxForm(children=[graph.box, graph.scale, graph.text])
        curdoc().add_root(HBox(children=[inputs, graph.plot], width=900))
        
    curdoc().add_periodic_callback(reload_data, data_refresh_interval)
    
except Exception as e:
    #button = Button(label='Error!')
    #curdoc().add_root(button)
    show_exception_info()
    text = PreText(text=traceback.format_exc()) #str(e)
    curdoc().clear()
    curdoc().add_root(text)     
    

