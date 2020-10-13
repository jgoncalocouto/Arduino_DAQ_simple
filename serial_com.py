#region Import modules
import time
import serial
import datetime
import random
import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import re
import pandas as pd
import os
import sys
import matplotlib._color_data as mcd
from matplotlib.widgets import Button


matplotlib.use("tkAgg")
plt.style.use('seaborn-pastel')
#endregion

#region Functions:

def saveClick(event):
    global pause
    pause = 'save'
    return pause

def startClick(event):
    global pause
    pause = 'start'
    return pause

def unique_excel_filename(data_filename_identifier):
    excel_filename = str(datetime.datetime.now().year) + '.' + str(datetime.datetime.now().month) + '.' + str(
        datetime.datetime.now().day) + '_' + str(datetime.datetime.now().hour) + '.' + str(
        datetime.datetime.now().minute) + '.' + str(
        datetime.datetime.now().second) + '__' + data_filename_identifier + '.xls'
    return excel_filename

def save_testdata_to_xls(data,list_of_variables,excel_filename):
    # expects:
    # a list of lists (data) where the first column is relative time and the remaining columns are sensor data
    # information about those sensors is passed through "list_of_variables"
    # data_filename_identifier is a costum label to add to the uniquely generated name (based on datetime)

    #outputs:
    #saves an excel file to a relative-path "data" folder with the data
    #dataframe with data



    min=len(data[0])
    for i in range(len(data)):
        if len(data[i])<min:
            min=len(data[i])

    for i in range(len(data)):
        data[i]=data[i][:min]

    df_data = pd.DataFrame(data[0], columns=['Relative Time - [s]'])
    df_data['Absolute time']=data[1]


    for i in range(len(data[2:])-1):
        df_data[list_of_variables[i]] = data[i + 2]

    path=os.path.dirname(os.path.abspath(__file__)) + '\\data'

    df_data.to_excel((path + '/' + excel_filename), sheet_name='Sheet_name_1')

    return df_data

def initialize_graph(fig_title,fig_size,list_of_variables,list_of_subplots):
    fig=plt.figure(figsize=fig_size)
    fig.suptitle(fig_title)

    ax_list=[]
    for i in range(max(list_of_subplots)):
        if (max(list_of_subplots) > 1 and i > 0):
            ax_list.append(fig.add_subplot(max(list_of_subplots), 1, i + 1, sharex=ax_list[0]))
        else:
            ax_list.append(fig.add_subplot(max(list_of_subplots), 1, i + 1))

    fig.subplots_adjust(bottom=0.2)

    list_of_lines=[]
    for j in range(len(list_of_variables)):
        list_of_lines.append(ax_list[list_of_subplots[j] - 1].plot([]))
        list_of_lines[j][0].set_label(list_of_variables[j])
        list_of_lines[j][0].set_color((0.5, 0.2, (j / len(list_of_variables))))
    plt.ion()
    plt.show()
    return fig,ax_list,list_of_lines

def initialize_data(list_of_variables):
    for j in range(len(list_of_variables) + 2):
        if 'data' not in locals():
            data = []
        data.append([])
    return data

def decode_line(ser_bytes,data,t_0):
    decoded_bytes = ser_bytes.decode("utf-8")
    txt = decoded_bytes.split(" ,")  # data from arduino comes in the folowing format: "1:25.26,"
    data[0].append(time.time() - t_0)
    data[1].append(datetime.datetime.now().strftime('%x %X'))
    message='TimeStamp: ' + str(data[1][-1]) + '; '
    msg_part=''
    for i in range(len(data)-2):
        data[i + 2].append(float(txt[i][3:]))
        msg_part=list_of_variables[i]+': '+str(data[i+2][-1])+'; '+msg_part
    message=message+msg_part
    print(message)
    return data

def update_graph(sliding_window,data,ax_list,list_of_lines,plot_window=120):
    for i in range(len(data)-2):
        if sliding_window.lower() == "yes":
            for ax in ax_list:
                ax.set_xlabel('Last ' + str(plot_window) + ' samples')
            if len(data[i + 2]) > plot_window:
                list_of_lines[i][0].set_ydata(data[i + 2][-plot_window:])
                list_of_lines[i][0].set_xdata(list(range(0, plot_window)))
            else:
                list_of_lines[i][0].set_ydata(data[i + 2])
                list_of_lines[i][0].set_xdata(list(range(0, len(data[i + 2]))))
        else:
            list_of_lines[i][0].set_ydata(data[i + 2])
            list_of_lines[i][0].set_xdata(data[0])
            for ax in ax_list:
                ax.set_xlabel('Relative time - [s]')
        ax_list[list_of_subplots[i] - 1].grid(b=True)
        ax_list[list_of_subplots[i] - 1].legend()
    for ax in ax_list:
        ax.relim()
        ax.autoscale_view()
    plt.show()
    plt.pause(0.0001)
    return data,ax_list,list_of_lines

#endregion 


#region Inputs:

list_of_variables = [
    'REC',
    'P_in',
    'P_out',
    'Freq',
    'PWM_in',
    'Duty',
]

list_of_subplots=[
    1,
    1,
    1,
    2,
    2,
    2,
]


port='COM3'
sliding_window = 'yes'
data_filename_identifier = 'A001_fans'
plot_window = 300
auto_save_time=15*60 #[s]
fig_title='Continuous Data Acquisition'
fig_size=(20,10)

#endregion


# region Initialization:

# initializing buffer
data = initialize_data(list_of_variables)

# Initializing graph:
fig, ax_list, list_of_lines = initialize_graph(fig_title, fig_size, list_of_variables, list_of_subplots)

# Add buttons
axstart = plt.axes([0.7, 0.05, 0.1, 0.075])
axsave = plt.axes([0.81, 0.05, 0.1, 0.075])
bstart = Button(axstart, 'Start')
bsave = Button(axsave, 'Save')
bstart.on_clicked(startClick)
bsave.on_clicked(saveClick)


# endregion

# region Data Aquisition Loop:
pause='idle'

# Serial port
ser = serial.Serial(port)
ser.flushInput()

while pause == 'idle':
    # Define xls filename
    excel_filename = unique_excel_filename(data_filename_identifier)



    # Initializing time vectors
    t_0 = time.time()  # initial time
    t_autosave = t_0  # last autosave time'
    time.sleep(0.1)
    data, ax_list, list_of_lines = update_graph(sliding_window, data, ax_list, list_of_lines,
                                                plot_window)  # update graph
    print(pause)
else:
    while pause == 'start':
        try:
            ser_bytes = ser.readline()
            try:
                data = decode_line(ser_bytes, data, t_0)
            except:
                print("Some data may be missing...")
                continue
            data, ax_list, list_of_lines = update_graph(sliding_window, data, ax_list, list_of_lines,
                                                        plot_window)  # update graph

            # check if autosave condition is met and, if so, save the data to xls
            if time.time() - t_autosave >= auto_save_time:
                df_data = save_testdata_to_xls(data, list_of_variables, excel_filename)
                t_autosave = time.time()

        except:
            print("Keyboard Interrupt")

            # save data to xls
            df_data = save_testdata_to_xls(data, list_of_variables, excel_filename)
            break
    else:
        df_data = save_testdata_to_xls(data, list_of_variables, excel_filename)
