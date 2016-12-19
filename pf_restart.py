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
import subprocess, signal
import os
import time

wrong_pass_counter = 0

def show_exception_info():
    #text = PreText(text=traceback.format_exc()) 
    #curdoc().clear()
    #curdoc().add_root(text)
    print(traceback.format_exc())
    
def restart_server():
    time.sleep(1)
    if wrong_pass_counter > 3:
        status.text = 'you are blocked!'
        time.sleep(10)
        return
    if pass_input.value <> '1234*4321*1234':    
    #if pass_input.value <> 'q23':
        status.text = 'wrong pass!'
        wrong_pass_counter = wrong_pass_counter + 1
        time.sleep(5)
    else:
        status.text = 'restarting...'
        if os.name == 'nt':
            #p = subprocess.Popen(['tasklist'], stdout=subprocess.PIPE)
            p = subprocess.Popen(['WMIC', 'path', 'win32_process', 'get', 'Processid,Commandline'], stdout=subprocess.PIPE)
        else:
            p = subprocess.Popen(['ps', '-f'], stdout=subprocess.PIPE)        
        out, err = p.communicate()
        time.sleep(1)
        for line in out.splitlines():
            #print line
            if 'pf_app.py' in line:
                status.text = 'killing pf server...'
                pid = int(line.split(None, 2)[1])
                os.kill(pid, signal.SIGKILL)
        status.text = 'running server...'
        time.sleep(1)
        if os.name == 'nt':
            p = subprocess.Popen(['start_server.cmd'], stdout=subprocess.PIPE)         
        else:
            #p = subprocess.Popen(['/home/jupyter/bokeh/pf/start_server'], stdout=subprocess.PIPE)         
            p = subprocess.call(['/home/jupyter/bokeh/pf/start_server'], stdout=subprocess.PIPE)
        status.text = 'Restarted!'                     

try:    
    print(os.name)
    curdoc().clear()
    button = Button(label='Restart pf server')
    button.on_click(restart_server)
    curdoc().add_root(button)
    

    pass_input = TextInput(value = 'enter password here')
    
    curdoc().add_root(pass_input)

    status = PreText(text="") 
    curdoc().add_root(status)
        
    #curdoc().add_periodic_callback(reload_data, data_refresh_interval)
    
except Exception as e:
    #button = Button(label='Error!')
    #curdoc().add_root(button)
    show_exception_info()
    text = PreText(text=traceback.format_exc()) #str(e)
    curdoc().clear()
    curdoc().add_root(text)     
    

