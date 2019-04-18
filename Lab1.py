#!/usr/bin/env python
# coding: utf-8

# In[222]:


# Import stuff
import pandas as pd 
import math as m
from matplotlib import pyplot as plt

def split_data(data, var, name):
    # Used to split data into multiple dataframes
    df = []
    for v in var:
        df.append(data[data[name] == v])
    return df

def split_averages(data, var, name):
    # Used to find mean values based on selected constant variable
    df = pd.DataFrame()
    for v in var:
        df_new = data[data[name] == v]
        df_ave = df_new.mean()
        df = pd.concat([df, df_ave], axis=1, sort=False)
                
    df = df.transpose()
    return df 

def find_ratio(data):
    # Find pressure and temperature ratios
    p_atm = 1.01325
    p_ratio = []
    t_ratio = []
    for df in data:
        p_ratio.append(list(df['Absolute pressure (bar)']/p_atm))
        t_ratio.append(list(df['T1 (K)']/df['T3 (K)']))
    return p_ratio, t_ratio

def split_n(p_ratio, t_ratio):
    # Find n values in a list
    n_values = []
    for i in range(len(p_ratio)):
        new_list = []
        zipped = zip(p_ratio[i], t_ratio[i])
        for p, t in zipped:
            n = find_n(p, t)
            new_list.append(n)
        n_values.append(new_list)
    return n_values

def find_n(p, T):
    # Find a singular n value
    n = m.log10(p)/(m.log10(T) + m.log10(p))
    return n

def merge_lists(ratio):
    # Merge lists to form the x,y values of the graph
    values = []
    for i in range(len(ratio[0])):
        new_list = []
        for j in range(len(ratio)):
            new_list.append(ratio[j][i])
        values.append(new_list)
    return values


# In[223]:


# Read the file
data = pd.read_csv('lab1.csv')

# Set lists to hold each variable increment
pressure = [2.0, 4.0, 6.0, 8.0, 10.0]
flowrate = [1.0, 1.5, 2.0, 2.5]
rpm = [600, 650, 700, 750, 800, 850, 900]


# In[225]:


# Split dataframes in to each pressure
#p2, p4, p6, p8, p10 = split_data(data, pressure, 'P1 (bar)')
df_pressures = split_data(data, pressure, 'P1 (bar)')


# In[226]:


# Average values for each rpm at each pressure
df_rpms_ave = []
for df in df_pressures:
    df_rpms_ave.append(split_averages(df, rpm, 'rpm'))
    
# Average values for each waterflow at each pressure
df_flowrates_ave = []
for df in df_pressures:
    df_flowrates_ave.append(split_averages(df, flowrate, 'Water Flow Rate (L/min)'))


# In[227]:


# Find the pressure and temperature ratios for rpms and flowrates
p_ratio_rpms, t_ratio_rpms = find_ratio(df_rpms_ave)
p_ratio_flowrates, t_ratio_flowrates = find_ratio(df_flowrates_ave)


# In[228]:


# Takes in two lists, returns a single list for n ratios then appends that list to another list
n_values_rpms = split_n(p_ratio_rpms, t_ratio_rpms)
n_values_flowrates = split_n(p_ratio_flowrates, t_ratio_flowrates)


# In[229]:


# Combine values from each list into respective rpms
x_values_rpm = merge_lists(p_ratio_rpms)
y_values_rpm = merge_lists(n_values_rpms)


# In[230]:


# Combine values from each list into respective flowrates
x_values_flowrates = merge_lists(p_ratio_flowrates)
y_values_flowrates = merge_lists(n_values_flowrates)


# In[231]:


plt.rcParams['figure.figsize'] = [10, 6]
for i in range(len(x_values_rpm)):
    plt.plot(x_values_rpm[i], y_values_rpm[i], linewidth=0.5)
    
plt.xlabel('Pressure ratio')
plt.ylabel('n value')
# plt.title('Effect of rpm on n values')
plt.legend([
    '600 rpm',
    '650 rpm',
    '700 rpm',
    '750 rpm',
    '800 rpm',
    '850 rpm',
    '900 rpm',
])


# In[268]:


# Find isoentropic T3 using k = 1.4
T_3 = df_rpms_ave[0]['rpm']
for i,df in enumerate(df_rpms_ave):
    new_df = df['T1 (K)']*[(1/ratio)**(-0.4/1.4) for ratio in p_ratio_rpms[i]]
    T_3 = pd.concat([T_3, new_df], axis=1, sort=False)
T_3.columns = ['rpm', '2 bar', '4 bar', '6 bar', '8 bar', '10 bar']


# In[269]:


# Find mechanical work
w_mech = pd.DataFrame()
for i,df in enumerate(df_rpms_ave):
    new_df = df['Torque (Nm)'] * 6 * m.pi * df['rpm'] / 60
    w_mech = pd.concat([w_mech, new_df], axis=1, sort=False)
#w_mech.columns = ['rpm', '2 bar', '4 bar', '6 bar', '8 bar', '10 bar']   
w_mech = w_mech*0.8


# In[270]:


# Find electrical work
w_elec = df_rpms_ave[0]['rpm']
for i,df in enumerate(df_rpms_ave):
    new_df = df['Voltage (V)'] * df['Current (A)']
    w_elec = pd.concat([w_elec, new_df], axis=1, sort=False)
w_elec.columns = ['rpm', '2 bar', '4 bar', '6 bar', '8 bar', '10 bar']


# In[271]:


# Find mass flow rate
A = 0.000127
C = 0.62
D = 25.4e-3
d = 12.7e-3
E = (1-(d/D)**4)**(-0.5)
R = 287

air_flow = pd.DataFrame()
for i,df in enumerate(df_rpms_ave):
    new_df = C * E * A * (2 * 101325 * df['Manometer delta_P (mmH2O)'] * 9.80665 /(R * df['T1 (K)'])) ** 0.5
    air_flow = pd.concat([air_flow, new_df], axis=1, sort=False)


# In[272]:


# Find change in enthalpy
enthalpy = pd.DataFrame()
for i,df in enumerate(df_rpms_ave):
    new_df = 1.005 * (df['T3 (K)'] - df['T1 (K)'])
    enthalpy = pd.concat([enthalpy, new_df], axis=1, sort=False)
enthalpy = enthalpy * air_flow
enthalpy


# In[316]:


# Find entropy 
entropy = pd.DataFrame()
for i,df in enumerate(df_flowrates_ave):
    r1 = df['T5 (K)']/df['T4 (K)']
    r1 = r1.map(m.log)
    r2 = df['T8 (K)']/df['T7 (K)']
    r2 = r2.map(m.log)
    new_df = 1.005 * r1 + 4.182 * r2
    entropy = pd.concat([entropy, new_df], axis=1, sort=False)
entropy.columns = ['2 bar', '4 bar', '6 bar', '8 bar', '10 bar']


# In[273]:


# Find Q for water
Q_water = df_flowrates_ave[0]['Water Flow Rate (L/min)']
for i,df in enumerate(df_flowrates_ave):
    new_df = -4.182 * (df['T7 (K)'] - df['T8 (K)']) * df['Water Flow Rate (L/min)'] * 0.01667
    Q_water = pd.concat([Q_water, new_df], axis=1, sort=False)
Q_water.columns = ['flowrate', '2 bar', '4 bar', '6 bar', '8 bar', '10 bar']


# In[274]:


# Find Q for air
Q_air = pd.DataFrame()
for i,df in enumerate(df_flowrates_ave):
    new_df = - 1.005 * (df['T4 (K)'] - df['T5 (K)'])
    Q_air = pd.concat([Q_air, new_df], axis=1, sort=False)
    
air_flow_2 = pd.DataFrame()
for i,df in enumerate(df_flowrates_ave):
    new_df = C * E * A * (2 * 101325 * df['Manometer delta_P (mmH2O)'] * 9.80665 /(R * df['T1 (K)'])) ** 0.5
    air_flow_2 = pd.concat([air_flow_2, new_df], axis=1, sort=False)    
    
Q_air = air_flow_2 * Q_air
    
Q_air = pd.concat([df_flowrates_ave[0]['Water Flow Rate (L/min)'], Q_air], axis=1, sort=False)
Q_air.columns = ['flowrate', '2 bar', '4 bar', '6 bar', '8 bar', '10 bar']


# In[275]:


Q_out = w_mech * 0.001 - enthalpy
Q_out


# In[277]:


# Append data 
air_flow = pd.concat([df_rpms_ave[0]['rpm'], air_flow], axis=1, sort=False)
enthalpy = pd.concat([df_rpms_ave[0]['rpm'], enthalpy], axis=1, sort=False)
Q_out = pd.concat([df_rpms_ave[0]['rpm'], Q_out], axis=1, sort=False)
w_mech = pd.concat([df_rpms_ave[0]['rpm'], w_mech], axis=1, sort=False)


# In[278]:


air_flow.columns = ['rpm', '2 bar', '4 bar', '6 bar', '8 bar', '10 bar']
enthalpy.columns = ['rpm', '2 bar', '4 bar', '6 bar', '8 bar', '10 bar']
Q_out.columns = ['rpm', '2 bar', '4 bar', '6 bar', '8 bar', '10 bar']
w_mech.columns = ['rpm', '2 bar', '4 bar', '6 bar', '8 bar', '10 bar']


# In[279]:


table1 = pd.DataFrame({'rpm': rpm,
                      'P Ratio 1': p_ratio_rpms[0],
                      'P Ratio 2': p_ratio_rpms[1],
                      'P Ratio 3': p_ratio_rpms[2],
                      'P Ratio 4': p_ratio_rpms[3],
                      'P Ratio 5': p_ratio_rpms[4]}
                    )
table2 = pd.DataFrame({'rpm': rpm,
                      'T Ratio 1': t_ratio_rpms[0],
                      'T Ratio 2': t_ratio_rpms[1],
                      'T Ratio 3': t_ratio_rpms[2],
                      'T Ratio 4': t_ratio_rpms[3],
                      'T Ratio 5': t_ratio_rpms[4]}
                     )
table3 = pd.DataFrame({'rpm': rpm,
                       'n1': n_values_rpms[0],
                       'n2': n_values_rpms[1],
                       'n3': n_values_rpms[2],
                       'n4': n_values_rpms[3],
                       'n5': n_values_rpms[4]}
                     )


# In[318]:


with pd.ExcelWriter('table5.xlsx') as writer:
    table1.to_excel(writer, sheet_name='rpm P Ratio')
    table2.to_excel(writer, sheet_name='rpm T Ratio')
    table3.to_excel(writer, sheet_name='rpm n')
    w_elec.to_excel(writer, sheet_name='w elec')
    w_mech.to_excel(writer, sheet_name='w mech')
    T_3.to_excel(writer, sheet_name='T3')
    Q_out.to_excel(writer, sheet_name='Q out')
    Q_air.to_excel(writer, sheet_name='Q air')
    Q_water.to_excel(writer, sheet_name='Q water')
    air_flow.to_excel(writer, sheet_name='airflow')
    air_flow_2.to_excel(writer, sheet_name='airflow_2')
    entropy.to_excel(writer, sheet_name='entropy')

