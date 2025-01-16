# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 17:10:41 2024

@author: F_ZHANG
"""

from abc import ABC, abstractmethod
import numpy as np
from numpy.linalg import matrix_power
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
from scipy.interpolate import interp1d

class TempModule(ABC):
    
    @abstractmethod
    def updateForcing(self):
        pass
    
    @abstractmethod 
    def updateSurTemp(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def updateOceanTemp(self):
        pass
    
    
class DICETemp(TempModule):
    
    def __init__(self, para_Temp = {}, initial_Temp = {}, para_Forcing = {}, dt = 1):
        
        self.para_Temp = para_Temp
        self.initial_Temp = initial_Temp
        self.dt = dt
        self.Tatm = {'Tatm': [self.initial_Temp.get('tatm0')]}
        self.Tocean ={'Tocean':[self.initial_Temp.get('tocean0')]}
        self.Forc = {'Forcing':[]}
        self.para_Forcing = para_Forcing
    
    def updateForcing(self, M_at, fex = None):
        # fex: exogeous forcing;
        # if fex is none, forcing can be adjusted via the 'Forc_fac', eg, if forc_fac = 1.3, fex = 0.3 CO2 forcing;
        if fex is None:
            forcing = self.para_Forcing.get('F2xco2')*np.log(M_at/self.para_Forcing.get('Meq_at'))/np.log(2)*self.para_Forcing.get('Forc_fac') 
            self.Forc['Forcing'].append(forcing)
        else:
            forcing = self.para_Forcing.get('F2xco2')*np.log(M_at/self.para_Forcing.get('Meq_at'))/np.log(2)*self.para_Forcing.get('Forc_fac') + fex
            self.Forc['Forcing'].append(forcing)
    
    def updateSurTemp(self, tatm, tocean, forcing):
        tatm = tatm+ self.dt*self.para_Temp.get('c1') *(forcing-self.para_Temp.get('lambda')*tatm-self.para_Temp.get('c3')*(tatm-tocean))
        self.Tatm['Tatm'].append(tatm)
        
    def updateOceanTemp(self, tocean, tatm):
        tocean = tocean + self.dt*self.para_Temp.get('c4')*(tatm-tocean)
        self.Tocean['Tocean'].append(tocean)
        
       
    def getFinal(self):
        if self.Forc['Forcing'] == []:
            return(self.Tatm, self.Tocean)
        else:
            return(self.Tatm, self.Tocean, self.Forc)
        
    
        
    def getLast(self):
        if self.Forc['Forcing'] == []:
            return (self.Tatm['Tatm'][-1], self.Tocean['Tocean'][-1])
        else:
            return(self.Tatm['Tatm'][-1], self.Tocean['Tocean'][-1],self.Forc['Forcing'][-1])
        
    
    
    
    def clear(self):
        self.Tatm = {'Tatm': [self.initial_Temp.get('tatm0')]}
        self.Tocean ={'Tocean':[self.initial_Temp.get('tocean0')]}
        self.Forc = {'Forcing':[]}
        
     
