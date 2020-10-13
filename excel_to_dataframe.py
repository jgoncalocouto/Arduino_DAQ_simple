#region Import Modules

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import scipy.interpolate as interpolate

#endregion

#region Inputs

variables_to_treat=[
    'Measurement: On/Off',
    'Inlet Fans: Static Pressure',
    'Outlet Fans: Static Pressure',
]
list_of_files={0: 'data/2020.7.24_16.6.15__A001_fans_02.xls',
}

#endregion

#region Functions

def rpm(x,section):
    pwm_vs_rpm_inlet = {
        0: 4992,
        8: 5346,
        15.92: 5862,
        23.8: 6360,
        31.68: 6744,
        39.47: 7188,
        47.26: 7575,
        55.13: 7935,
        63: 8277,
        78.22: 8991,
        86.14: 9360,
        94.06: 9669,
        100: 9741,

    }
    pwm_vs_rpm_outlet = {
        0: 5268,
        8: 5616,
        15.92: 6165,
        23.8: 6705,
        31.68: 7215,
        39.47: 7716,
        47.26: 8175,
        55.13: 8595,
        63: 8976,
        78.22: 9597,
        86.14: 9915,
        94.06: 10245,
        100: 10290,
    }

    rpm_inlet=interpolate.interp1d(list(pwm_vs_rpm_inlet.keys()), list(pwm_vs_rpm_inlet.values()))
    rpm_outlet = interpolate.interp1d(list(pwm_vs_rpm_outlet.keys()), list(pwm_vs_rpm_outlet.values()))

    if section.lower()=='inlet':
        rpm=rpm_inlet(x)
    elif section.lower()=='outlet':
        rpm=rpm_outlet(x)
    return rpm

def pwm(x):
    arduino_vs_pwm = {
        0: 0,
        1: 0.995,
        5: 1.98,
        25: 8,
        50: 15.92,
        100: 31.68,
        150: 47.26,
        200: 63,
        250: 78.22,
        300: 94.06,
        310: 97.03,
        319: 99.5,
        320: 100,
    }
    pwm = interpolate.interp1d(list(arduino_vs_pwm.keys()), list(arduino_vs_pwm.values()))
    y=pwm(x)
    return y

#endregion

#region Extract test data

# import test files and concatenate them into a single dataframe
for i,key in enumerate(list_of_files):
    if i==0:
        df_data=pd.read_excel(list_of_files[key])
    else:
        print(i)
        df_to_append=pd.read_excel(list_of_files[key])
        df_data=df_data.append(df_to_append,ignore_index=True)

#Select only measurement areas
df_data=df_data[(np.isnan(df_data['DeltaP_in.1'])==False) & (np.isnan(df_data['DeltaPrd_out.1'])==False)]

df_data=df_data.rename(columns={"DeltaP_in.1": "Inlet Fans: Static Pressure", "DeltaPrd_out.1": "Outlet Fans: Static Pressure"})

#endregion

fig1=plt.figure(figsize=(16,8))

ax1=fig1.add_subplot(1,1,1)
sns.scatterplot(x='PWM',y='Inlet Fans: Static Pressure',data=df_data,ax=ax1, label='Inlet Fans')
sns.scatterplot(x='PWM',y='Outlet Fans: Static Pressure',data=df_data,ax=ax1, label='Outlet Fans')
ax1.set_xlabel('PWM - [%]')
ax1.set_ylabel('Static Pressure - [Pa]')





