'''
DESCRIPTION:

Script to plot and record data from analog input channels from arduino board.
It is excepted that a 5V signal is connected in Digital Port "control_pin" in order to start the data aquisition. The data aquisition ends when the control signal is set to 0.
The data is saved in the "data" folder in the location of this script with an unique name + a identifier.

'''

#region Import Modules


import pyfirmata

import matplotlib.pyplot as plt

import time

import pandas as pd

import datetime

import os


#endregion

#region Inputs


port='COM3'

analog_input_ports=[
        0 ,
        1 ,
        2 ,
    ]

plot_colors=[
    'r-',
    'c-',
    'y-',
]

series_name=[
    'Water Level Sensor',
    'Joystick Up/Down',
    'Joystick Right/Left'
]

control_pin=13

t_daq=5*10**(-4)

data_filename_identifier='test'


#endregion

#region Set-up Board and Plotting


board=pyfirmata.Arduino(port)

it=pyfirmata.util.Iterator(board)

it.start()

data=[[]]

pin_list=[]

control_signal=board.get_pin('d:' + str(control_pin) + ':i')

for i in analog_input_ports:
    data.append([])
    pin_list.append(board.get_pin('a:' + str(i) + ':i'))
    #in_list[i].enable_reporting()

plt.ion()

fig=plt.figure()


#endregion

#region Data Aquisition Cycle


i=0

t_0=time.time()

while control_signal.value:
    i+=1
    data[0].append(time.time()-t_0)
    j=1

    for ai_port in analog_input_ports:
        data[j].append(pin_list[j-1].read())
        plt.plot(data[0], data[j],plot_colors[j-1],label=series_name[j-1])
        j += 1
    plt.show()

    if i==1:
        plt.xlabel('Elapsed time - [s]')
        plt.ylabel('Sensor signal - [0/1]')
        plt.title('Arduino DAQ')
        plt.legend()

    plt.pause(0.001)
    time.sleep(t_daq)


#endregion

#region Export Dataframe to Excel


df_data=pd.DataFrame(data[0],columns=['Relative Time - [s]'])

for i in range(len(data[1:])):
    df_data[series_name[i]]=data[i+1]

excel_filename=str(datetime.datetime.now().year)+'.'+str(datetime.datetime.now().month)+'.'+str(datetime.datetime.now().day)+'_'+str(datetime.datetime.now().hour)+'.'+str(datetime.datetime.now().minute)+'.'+str(datetime.datetime.now().second)+'__'+data_filename_identifier+'.xls'

path=os.path.dirname(__file__)+'/data'

df_data.to_excel((path+'/'+excel_filename), sheet_name='Sheet_name_1')


#endregion


'''
except KeyboardInterrupt:
board.exit()
os._exit()
'''