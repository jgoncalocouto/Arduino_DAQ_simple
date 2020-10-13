#region Import Modules

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

#endregion

#region Inputs
signal_reference='Reference Pressure (Huba)'
Pressure_sensor='Bourns'

variables_to_treat=[
    signal_reference,
    'Measured Pressure'+' ('+Pressure_sensor+')'
]


sensor_limits={'Absolute Uncertainty':(-22.5,22.5)}
'''
range_to_remove=[
    [4200,4700],
      [5200,6500],]
'''

range_to_remove=[]
moving_average_period=15*10 #10s @ acquisition rate of 10

#endregion

df_data=pd.read_excel(r'C:\Users\JoãoGonçaloCouto\PycharmProjects\arduino\data\2020.5.21_15.22.5__nominal_uncertainty_bournes.xls')

for bounds in range_to_remove:
    df_data.loc[bounds[0]:bounds[1]]=np.nan
    #df_data = df_data.drop(index=range(bounds[0],bounds[1]))

for variable in variables_to_treat:
    #df_data[variable] = np.where((df_data[variable] < 0), np.nan, df_data[variable])
    df_data[(variable+' - '+'Moving Average')]=df_data[variable].rolling(window=moving_average_period).mean() #moving average in selected variables
    df_data[(variable+' - '+'Derivative')]=df_data[(variable+' - '+'Moving Average')].diff(periods=15) #moving average in selected variables


df_data['Stable'] = [1 if abs(x) <= 1.5 else np.nan for x in df_data[signal_reference+' - '+'Derivative']]
df_data['Classes']=round(df_data[signal_reference+' - '+'Moving Average']/100,1)*100
df_data['Classes'] = np.where((df_data['Stable'] != 1),np.nan,df_data['Classes'])

unique_classes=df_data['Classes'].unique()

for element in unique_classes:
    size_of_subclass=df_data['Classes'].loc[df_data['Classes']==element].count()
    if size_of_subclass<=20:
        df_data['Classes']=np.where((df_data['Classes'] == element), np.nan, df_data['Classes'])



lim1=df_data['Classes'].loc[df_data['Classes']==df_data['Classes'].max()].index[0]  #index of first item of the class
lim2=df_data['Classes'].loc[df_data['Classes']==df_data['Classes'].max()].index[-1] #index of last item of the class
lim=(lim1+lim2)*0.5
df_data['Direction of pressure variation']=['upward' if i <lim else 'downward' for i in range(len(df_data))]


df_data['Absolute difference']=df_data[variables_to_treat[1]+' - '+'Moving Average'].loc[df_data['Stable']==1] - df_data[signal_reference+' - '+'Moving Average'].loc[df_data['Stable']==1]
df_data['Relative difference']=(df_data['Absolute difference']/df_data[signal_reference+' - '+'Moving Average'])*100

unique_classes=df_data['Classes'].unique()
unique_classes=[round(x,0) for x in unique_classes]

unique_classes = [x for x in unique_classes if str(x) != 'nan']
unique_classes.sort()

df_statistics=pd.DataFrame()
df_statistics['Classes']=df_data['Classes'].unique()

i=0
l1, l2, l3, l4, l5 = [], [], [], [],[]
for class1 in df_data['Classes'].unique():
    des=df_data['Absolute difference'].loc[df_data['Classes']==class1].describe()
    l1.append(des['mean'])
    l2.append(des['min'])
    l3.append(des['max'])
    l4.append(des['std'])
    l5.append(des['count'])
df_statistics['Average']=l1
df_statistics['Minimum']=l2
df_statistics['Maximum']=l3
df_statistics['Std']=l4
df_statistics['Number of samples']=l5


fig1=plt.figure()
ax=fig1.add_subplot(1,1,1)
fig2=plt.figure()
ax2=fig2.add_subplot(1,1,1)
ax2.set_title('Effect of moving average period in pressure measurement time variation')
fig3=plt.figure()
ax3=fig3.add_subplot(1,1,1)
df_data['Normal Variation']=abs(df_data[signal_reference+' - '+'Moving Average']-df_data[signal_reference])
ax3.plot(df_data['Relative Time - [s]'], df_data[signal_reference],label='reference signal',color='black')
for period in [0.2,0.5,1,2,5,10,15]:
    print(period)
    df_data['Moving Average = ' + str(period)] = df_data[variables_to_treat[1]].rolling(window=int(10*period)).mean()  # moving average in selected variables
    #df_data['Variation = '+str(period)]=abs(df_data[signal_reference+' - '+'Moving Average']-df_data['Moving Average = ' + str(period)])
    df_data['Variation = ' + str(period)] = (df_data[signal_reference] - df_data['Moving Average = ' + str(period)])
    sns.scatterplot(x=df_data[signal_reference].loc[df_data['Stable']==1],y=df_data['Variation = '+str(period)].loc[df_data['Stable']==1], label=str(period),ax=ax)
    sns.distplot(df_data['Variation = ' + str(period)].loc[(df_data['Stable'] == 1) & (df_data['Classes']==df_data['Classes'].mode()[0])], label='Moving Average Period = '+str(period)+' [s]', ax=ax2)
    ax3.plot(df_data['Relative Time - [s]'], df_data['Moving Average = ' + str(period)] , label='Moving Average: '+str(period)+' [s]',alpha=0.5)
    print(df_data['Variation = ' + str(period)].loc[df_data['Stable'] == 1].mean())




ax2.set_xlabel('Pressure Signal Time Variation - [Pa]')
ax2.legend()



'''
#region Plots

fig1 = plt.figure(figsize=(8,8))
fig1.suptitle('Pressure Sensor Uncertainty'+': '+Pressure_sensor)
ax1_1=fig1.add_subplot(2, 1, 1)
l1_1_1=ax1_1.plot(df_data[signal_reference+' - '+'Moving Average'],df_data['Absolute difference'])
ax1_1.set_xlabel('Pressure Signal - [Pa]')
ax1_1.set_ylabel('Absolute difference - [Pa]')
l1_1_2=ax1_1.axhline(y=sensor_limits['Absolute Uncertainty'][0], color='r', linestyle='-', label='Lower Limit')
l3_1_3=ax1_1.axhline(y=sensor_limits['Absolute Uncertainty'][1], color='r', linestyle='--', label='Upper Limit')
ax1_1.legend()

ax1_2=fig1.add_subplot(2, 1, 2, sharex=ax1_1)
l1_2_1=ax1_2.plot(df_data[signal_reference+' - '+'Moving Average'],df_data['Relative difference'])
l1_2_2=ax1_2.plot(df_data[signal_reference+' - '+'Moving Average'],sensor_limits['Absolute Uncertainty'][0]/df_data[signal_reference+' - '+'Moving Average']*100,'r-',label='Lower Limit')
l1_2_2=ax1_2.plot(df_data[signal_reference+' - '+'Moving Average'],sensor_limits['Absolute Uncertainty'][1]/df_data[signal_reference+' - '+'Moving Average']*100,'r-',label='Upper Limit')
ax1_2.set_xlabel('Pressure Signal - [Pa]')
ax1_2.set_ylabel('Relative difference - [%]')
ax1_2.set_ylim([-50,50])
ax1_2.legend()


fig2 = plt.figure(figsize=(20,10))
fig2.suptitle('Test Overview')
ax2_1=fig2.add_subplot(4, 1, 1)
l2_1_1=ax2_1.plot(df_data['Relative Time - [s]'],df_data[signal_reference],label='Raw Data: '+signal_reference)
l2_1_2=ax2_1.plot(df_data['Relative Time - [s]'],df_data[variables_to_treat[1]],label='Raw Data: '+variables_to_treat[1])
l2_1_3=ax2_1.fill_between(df_data['Relative Time - [s]'],df_data['Stable']*500, label='Measurement Area',alpha=0.5)
ax2_1.set_xlabel('Relative Time - [s]')
ax2_1.set_ylabel('Pressure Signal - [Pa]')
ax2_1.legend()

ax2_2=fig2.add_subplot(4, 1, 2, sharex=ax2_1,sharey=ax2_1)
l2_2_1=ax2_2.plot(df_data['Relative Time - [s]'],df_data[signal_reference],label='Raw Data: '+signal_reference)
l2_2_2=ax2_2.plot(df_data['Relative Time - [s]'],df_data[signal_reference+' - '+'Moving Average'],label='Moving Average 10s :'+signal_reference)
ax2_2.set_xlabel('Relative Time - [s]')
ax2_2.set_ylabel('Pressure Signal - [Pa]')
ax2_2.legend()

ax2_3=fig2.add_subplot(4, 1, 3, sharex=ax2_1, sharey=ax2_1)
l2_3_1=ax2_3.plot(df_data['Relative Time - [s]'],df_data[variables_to_treat[1]],label='Raw Data: '+variables_to_treat[1])
l2_3_2=ax2_3.plot(df_data['Relative Time - [s]'], df_data[variables_to_treat[1]+' - '+'Moving Average'],label='Moving Average 10s :'+variables_to_treat[1])
ax2_3.set_xlabel('Relative Time - [s]')
ax2_3.set_ylabel('Pressure Signal - [Pa]')
ax2_3.legend()

ax2_4=fig2.add_subplot(4, 1, 4, sharex=ax2_1, sharey=ax2_1)
l2_4_1=ax2_4.plot(df_data['Relative Time - [s]'],df_data[signal_reference+' - '+'Moving Average'],label='Moving Average: '+signal_reference)
l2_4_2=ax2_4.plot(df_data['Relative Time - [s]'],df_data[variables_to_treat[1]+' - '+'Moving Average'],label='Moving Average: '+variables_to_treat[1])
l2_4_3=ax2_4.fill_between(df_data['Relative Time - [s]'],df_data['Stable']*500, label='Measurement Area',alpha=0.5)
ax2_4.set_xlabel('Relative Time - [s]')
ax2_4.set_ylabel('Pressure Signal - [Pa]')
ax2_4.legend()



fig3= plt.figure(figsize=(16,8))
fig3.suptitle('Box Plots: Error Overview for '+Pressure_sensor+' sensor')
ax3_1=fig3.add_subplot(2,1,1)
l3_1_1 = sns.boxplot(x="Classes", y="Absolute difference",data=df_data, palette="Set3", ax=ax3_1)
ax3_1.set_xlabel('Pressure Signal - [mbar]')
ax3_1.set_ylabel('Absolute Difference - [Pa]')
l3_1_2=ax3_1.axhline(y=sensor_limits['Absolute Uncertainty'][0], color='r', linestyle='-', label='Lower Limit')
l3_1_3=ax3_1.axhline(y=sensor_limits['Absolute Uncertainty'][1], color='r', linestyle='--', label='Upper Limit')
ax3_1.legend()
ax3_1.set_xticklabels(unique_classes)

ax3_2=fig3.add_subplot(2,1,2)
l3_2_1 = sns.boxplot(x="Classes", y="Relative difference",data=df_data, palette="Set3", ax=ax3_2)
ax3_2.set_xlabel('Pressure Signal - [mbar]')
ax3_2.set_ylabel('Relative Difference - [%]')
ax3_2.set_xticklabels(unique_classes)

fig4=plt.figure(figsize=(16,8))
fig4.suptitle('Hysteresis: Is it relevant?')
ax4_1=fig4.add_subplot(2,1,1)
g= sns.distplot(df_data['Absolute difference'].loc[df_data['Direction of pressure variation']=='downward'],label='downward',ax=ax4_1)
g= sns.distplot(df_data['Absolute difference'].loc[df_data['Direction of pressure variation']=='upward'],label='upward',ax=ax4_1)
ax4_1.legend(loc='lower right')

des = df_data['Absolute difference'].loc[df_data['Direction of pressure variation']=='downward'].describe()
ax4_1.axvline(des["25%"], ls='--')
ax4_1.axvline(des["mean"], ls='--')
ax4_1.axvline(des["75%"], ls='--')
ax4_1.grid(True)
des = round(des, 2).apply(lambda x: str(x))
box = '\n'.join(("min: "+des["min"], "25%: "+des["25%"], "mean: "+des["mean"], "75%: "+des["75%"], "max: "+des["max"]))
ax4_1.text(0.98, 0.95, box, transform=ax4_1.transAxes, fontsize=10, va='top', ha="right", bbox=dict(boxstyle='round', facecolor='tab:blue', alpha=0.5))

des = df_data['Absolute difference'].loc[df_data['Direction of pressure variation']=='upward'].describe()
ax4_1.axvline(des["25%"], ls='--',color='darkorange')
ax4_1.axvline(des["mean"], ls='--',color='darkorange')
ax4_1.axvline(des["75%"], ls='--',color='darkorange')
ax4_1.grid(True)
des = round(des, 2).apply(lambda x: str(x))
box = '\n'.join(("min: "+des["min"], "25%: "+des["25%"], "mean: "+des["mean"], "75%: "+des["75%"], "max: "+des["max"]))
ax4_1.text(0.98, 0.5, box, transform=ax4_1.transAxes, fontsize=10, va='top', ha="right", bbox=dict(boxstyle='round', facecolor='tab:orange', alpha=0.5))





ax4_2=fig4.add_subplot(2,1,2)
g = sns.scatterplot(x=variables_to_treat[1]+' - '+'Moving Average', y="Absolute difference", hue="Direction of pressure variation", data=df_data, ax= ax4_2)
ax4_2.set_xlabel('Pressure Signal - [Pa]')
ax4_2.set_ylabel('Absolute difference - [Pa]')
'''
'''
ax5_1=sns.jointplot(x=df_data[signal_reference+' - '+'Moving Average'].loc[df_data['Direction of pressure variation']=='upward'], y=df_data["Absolute difference"].loc[df_data['Direction of pressure variation']=='upward'], label='Upward')
ax5_1.set_axis_labels('Pressure Signal - [Pa]','Absolute difference - [Pa]')
ax6_1=sns.jointplot(x=df_data[signal_reference+' - '+'Moving Average'].loc[df_data['Direction of pressure variation']=='downward'], y=df_data["Absolute difference"].loc[df_data['Direction of pressure variation']=='downward'], label='Downward', color='g')
ax6_1.set_axis_labels('Pressure Signal - [Pa]','Absolute difference - [Pa]')
'''

'''
fig5=plt.figure(figsize=(8,4))
ax5=fig5.add_subplot(1,1,1)
g= sns.distplot(df_data[signal_reference].loc[df_data['Classes']==df_data['Classes'].max()],ax=ax5)

des = df_data[signal_reference].loc[df_data['Classes']==df_data['Classes'].max()].describe()
ax5.axvline(des["25%"], ls='--')
ax5.axvline(des["mean"], ls='--')
ax5.axvline(des["75%"], ls='--')
ax5.grid(True)
des = round(des, 2).apply(lambda x: str(x))
box = '\n'.join(("min: "+des["min"], "25%: "+des["25%"], "mean: "+des["mean"], "75%: "+des["75%"], "max: "+des["max"], "std: "+des["std"]))
ax5.text(0.95, 0.95, box, transform=ax5.transAxes, fontsize=10, va='top', ha="right", bbox=dict(boxstyle='round', facecolor='tab:blue', alpha=0.5))


#endregion
'''