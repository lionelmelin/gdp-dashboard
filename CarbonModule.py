# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 17:25:56 2024

@author: F_ZHANG
"""

from abc import ABC, abstractmethod
import numpy as np
from numpy.linalg import matrix_power
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd



class CarbonModule(ABC):
    
    @abstractmethod
    def carbon_diffusion(self):
        pass
    
    @abstractmethod
    def updateCarbon(self):
        pass
    
    
    @abstractmethod
    def updateForcing(self):
        pass
    
    
class CarbonCycle(CarbonModule):
    def __init__(self, para_Carbon, initial_Carbon_mass, dt = 1 ):
        self.para_Carbon = para_Carbon
        self.initial_Carbon_mass = initial_Carbon_mass
        self.dt = dt
        self.M_at = {'M_at':[self.initial_Carbon_mass.get('M0_at')]}
        self.M_up = {'M_up':[self.initial_Carbon_mass.get('M0_up')]}
        self.M_lo = {'M_lo':[self.initial_Carbon_mass.get('M0_lo')]}
       
    def carbon_diffusion(self):
        r1 = self.para_Carbon.get('Meq_at')/self.para_Carbon.get('Meq_up')
        r2 = self.para_Carbon.get('Meq_up')/self.para_Carbon.get('Meq_lo')
        b11 = -self.para_Carbon.get('b12')
        b13 = 0         
        b21 = self.para_Carbon.get('b12')*r1 
        b22 = -b21-self.para_Carbon.get('b23')
        b31 = 0
        b32 = self.para_Carbon.get('b23')*r2  
        b33 = -b32  
        b = np.array ([[b11,b21,b31],[self.para_Carbon.get('b12'),b22,b32],[b13,self.para_Carbon.get('b23'),b33]]) # time independent diffusion matrix
        bb = np.eye(3) + self.dt*b ## time-step dependent diffusion matrix
        
        b11 = bb[0,0]
        b13 = bb[2,0]         
        b21 = bb[0,1]
        b22 = bb[1,1]
        b31 = bb[0,2]
        b32 = bb[1,2]
        b33 = bb[2,2]
        b12 = bb[1,0]
        b23 = bb[2,1]
        return(b11,b13,b21,b22,b31,b32,b33,b12,b23,bb)
  
    def updateCarbon(self, carbon_emission, M_at, M_up, M_lo):
    
        b11,b13,b21,b22,b31,b32,b33,b12,b23,bb = self.carbon_diffusion()
        M_at = M_at*b11 + M_up*b21 + carbon_emission
        M_up = M_at*b12 + M_up*b22 + M_lo*b32
        M_lo = M_lo*b33 + M_up*b23
        
        self.M_at['M_at'].append(M_at)
        self.M_up['M_up'].append(M_up)
        self.M_lo['M_lo'].append(M_lo)
        
    def updateForcing(self):
        pass
        
        
        
    def getFinal(self):
        
        return(self.M_at, self.M_up, self.M_lo)
    
    def getLast(self):
        return (self.M_at['M_at'][-1], self.M_up['M_up'][-1], self.M_lo['M_lo'][-1])
    

    
    def clear(self):
        
        self.M_at = {'M_at':[self.initial_Carbon_mass.get('M0_at')]}
        self.M_up = {'M_up':[self.initial_Carbon_mass.get('M0_up')]}
        self.M_lo = {'M_lo':[self.initial_Carbon_mass.get('M0_lo')]}
       