#!/usr/bin/env python
# coding: utf-8

# In[27]:


# Import stuff
import pandas as pd 
import math as m
from matplotlib import pyplot as plt

# Read the file
data = pd.read_csv('lab2.csv')


# In[71]:


monday = data[data['Lab Group'] == 'MON'].mean()
tuesday = data[data['Lab Group'] == 'TUE'].mean()
wednesday = data[data['Lab Group'] == 'WED'].mean()
thursday = data[data['Lab Group'] == 'THU'].mean()


# In[84]:


data_ave = pd.concat([monday, tuesday, wednesday, thursday], axis=1, sort=False)
data_ave.columns = ['Mon', 'Tue', 'Wed', 'Thu']
data_ave = data_ave.T


# In[137]:


def interpolate(know, big1, small1, big2, small2):
    return small1 + (know - small2) * (big1 - small1) / (big2 - small2)

# Method applied to each row of data
h1 = interpolate(7.931056, 43.82, 41.17, -6, -8)
h2 = interpolate(-8.620200, 203.14, 204.59, -6, -8)
h = interpolate(0.7931056, h2, h1, 0.8, 0.7)


# In[117]:


S1 = pd.Series([0.361, 0.354, 0.352, 0.351])
S2 = pd.Series([0.377, 0.365, 0.366, 0.374])
S3 = pd.Series([0.949, 0.950, 0.950, 0.953])
S4 = pd.Series([1.032, 1.005, 1.019, 1.033])
entropy = pd.concat([S1, S2, S3, S4], axis=1, sort=False)


# In[87]:


H1 = pd.Series([97.578, 95.532, 94.991, 94.765])
H2 = pd.Series([97.578, 95.532, 94.991, 94.765])
H3 = pd.Series([236.169, 235.879, 235.585, 233.255])
H4 = pd.Series([304.249,294.384, 299.532, 303.184])
enthalpy = pd.concat([H1, H2, H3, H4], axis=1, sort=False)


# In[119]:


with pd.ExcelWriter('table3.xlsx') as writer:
    enthalpy.to_excel(writer, sheet_name='enthalpy')
    data_ave.to_excel(writer, sheet_name='averages')
    entropy.to_excel(writer, sheet_name='entropy')

