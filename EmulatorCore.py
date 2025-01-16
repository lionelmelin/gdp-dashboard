# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 09:58:15 2024

@author: F_ZHANG
"""


from abc import ABC, abstractmethod
import numpy as np
from numpy.linalg import matrix_power
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

from pathlib import Path


from CarbonModule import CarbonCycle
from TempModule import DICETemp

import os

# # Set the path to the folder you want as your working directory
# desired_path = r"C:\Users\F_ZHANG\Documents\GitHub\ClimateEmulatorAPP\EmulatorCode\PythonCode"

# os.chdir(desired_path)
# print(os.getcwd())  # Confirm you've moved to the right location

DATA_FILENAME_CMIP = Path(__file__).parent/'data/CMIPparas.xlsx'
CMIP = pd.read_excel(DATA_FILENAME_CMIP, sheet_name = 'CMIP')
# CMIP = pd.read_excel(r"Data\CMIPparas.xlsx",
#                       sheet_name = 'CMIP')
CMIP.set_index('Model', inplace=True)

DATA_FILENAME_CARBON = Path(__file__).parent/'data/CMIPparas.xlsx'
Carbon = pd.read_excel(DATA_FILENAME_CARBON, sheet_name = 'carbon')
# Carbon =  pd.read_excel(r"Data\CMIPparas.xlsx",
#                       sheet_name = 'carbon')
Carbon.set_index('Model', inplace=True)


class Emulator:
    def __init__(self, Carbon_emission = [], Model_name = 'MMM_CMIP6', dt = 1):
        self.start_year = 2020
        self.emission = Carbon_emission
        self.dt = dt
        self.end_year = self.start_year + len(self.emission)*self.dt
        self.Model = CMIP.loc[Model_name]
        self.CarbonModel = Carbon.loc['MMM']
        self.Forcing_factor = 1.1
        self.Model_name = Model_name
        self.tatm_max = 0
        self.tatm_min = 0
        self.fig = make_subplots(rows=1, cols=2,
                            horizontal_spacing=0.15, vertical_spacing=0.1)
        self.custom_colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
            '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5',
            '#ff9896', '#9467bd', '#c7c7c7', '#98df8a', '#ffbb78',
            '#17becf', '#ff7f0e', '#d62728', '#2ca02c', '#1f77b4'
            ]
        
    def TempParameter(self):
        c1 = self.Model['c1']
        c3 = self.Model['c3']
        c4 = self.Model['c4']
        ECS = self.Model['ECS']
        Lambda = self.Model['lambda']
        F2xco2 = self.Model['F2xco2']
        tatm0 = self.Model['Tatm0']
        tocean0 = self.Model['Tocean0']
        b12 = self.CarbonModel['b12']
        b23 = self.CarbonModel['b23']
        Meq_at = self.CarbonModel['Meq_at']
        Meq_up = self.CarbonModel['Meq_up']
        Meq_lo = self.CarbonModel['Meq_lo']
        M0_at = self.CarbonModel['M0_at']
        M0_up = self.CarbonModel['M0_up']
        M0_lo = self.CarbonModel['M0_lo']
        dt = self.dt
        para_Temp = {'c1':c1, 'c3': c3, 'c4':c4, 'ECS':ECS,  'lambda':Lambda}
        para_Forcing = {'F2xco2':F2xco2, 'Meq_at': Meq_at, 'Forc_fac':self.Forcing_factor}
        initial_Temp = {'tatm0': tatm0, 'tocean0': tocean0}
        para_Carbon = {'b12':b12, 'b23':b23, 'Meq_at':Meq_at,
                       'Meq_up':Meq_up, 'Meq_lo': Meq_lo}
        initial_Carbon_mass = {'M0_at':M0_at, 'M0_up':M0_up, 'M0_lo': M0_lo}
        TempClass = DICETemp(para_Temp, initial_Temp, para_Forcing, dt = dt)
        self.TempClass = TempClass
        CarbonClass = CarbonCycle(para_Carbon, initial_Carbon_mass, dt = dt)
        self.CarbonClass = CarbonClass
        
    
    def clear(self):
        self.TempParameter()
        self.CarbonClass.clear()
        self.TempClass.clear()
    def Run_sim(self):
        self.clear()
        num_periods = int(((self.end_year-self.start_year)/self.dt))
        
        for i_step in range(num_periods):
            carbon_emission= self.emission[i_step]*self.dt
            M_at, M_up, M_lo = self.CarbonClass.getLast()
            self.TempClass.updateForcing(M_at)
            tatm, tocean, forcing = self.TempClass.getLast()
            self.TempClass.updateSurTemp(tatm, tocean, forcing)
            self.TempClass.updateOceanTemp(tatm, tocean)
            self.CarbonClass.updateCarbon(carbon_emission, M_at, M_up, M_lo)
        tatm, tocean, forcing = self.TempClass.getFinal()
        if self.tatm_max < np.max(tatm['Tatm']):
            self.tatm_max = np.max(tatm['Tatm'])
        if self.tatm_min > np.min(tatm['Tatm']):
            self.tatm_min = np.min(tatm['Tatm'])
        return(tatm['Tatm'], tocean['Tocean']) 
    
    
    def Plot_Temp(self):
        tatm_value, _, = self.Run_sim()
        #n = int((end_year-self.start_year)/self.dt+1) ## number of periods
        x_year = np.arange(self.start_year, self.end_year, self.dt)
        # Create the first trace with the first y-axis
        #fig = go.Figure()
        self.fig.update_annotations(font_size=30)
        self.fig.add_trace(go.Scatter(x=x_year, y = self.emission, mode='lines', name='Emissions' ,
                                      
                                      showlegend= False),
                           row = 1, col = 1)

        # Create the second trace with the second y-axis
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_value, mode='lines', name=f"{self.Model_name}"),
                           row = 1, col = 2)
        
        self.fig.update_yaxes(title_text="Emission (Gigaton Carbon/year)",
                         range=[np.min(self.emission)-1,np.max(self.emission)+1],
                         title_standoff=25, title_font=dict(size=25), row = 1, col =1)
        self.fig.update_yaxes(title_text="Global surface temperature anomaly (°C)",
                         range = [0,self.tatm_max+1],
                         title_standoff=25, title_font=dict(size=25), row = 1, col =2)
        self.fig.update_xaxes(title_text ='Time', title_standoff =25,title_font=dict(size=25), row = 1, col =1)
        self.fig.update_xaxes(title_text ='Time', title_standoff =25,title_font=dict(size=25), row = 1, col =2)
        
        self.fig.update_layout(
            title_text = '',
            title=dict(
                font=dict(
                    size=25  # Adjust the font size here
                    )
                ),
            annotations=[
        dict(text="Emission data", x=0.2, y=1.05, xref="paper", yref="paper", showarrow=False, font=dict(size=25)),
        dict(text="Temperature anomaly prediction", x=0.9, y=1.05, xref="paper", yref="paper", showarrow=False, font=dict(size=25))
    ]
            )

        self.fig.update_layout(colorway=self.custom_colors)
        # # Show the plot
        # self.fig.write_html('first_figure.html', auto_open=True)
        return self.fig
        
    def update_model(self, Model_name):
        self.Model_name = Model_name
        self.Model = CMIP.loc[Model_name]
        self.TempParameter()
        self.update_Plot()
       
        
    def update_Plot(self):
        tatm_value, _, = self.Run_sim()
        
        #n = int((end_year-self.start_year)/self.dt+1) ## number of periods
        x_year = np.arange(self.start_year, self.end_year, self.dt)
        
        # Create the second trace with the second y-axis
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_value, mode='lines', name= f"{self.Model_name}"),
                           row = 1, col = 2)
        # Add layout settings
        self.fig.update_yaxes(title_text="Global surface temperature anomaly (°C)",
                         range = [0,self.tatm_max + 0.5],
                         title_standoff=25, title_font=dict(size=25), row = 1, col =2)
        self.fig.update_layout(colorway=self.custom_colors)
        # # Show the plot
        # self.fig.write_html('first_figure.html', auto_open=True)
        return self.fig
        
    def CMIP5_prediction(self):
        self.fig = make_subplots(rows=1, cols=2,
                            horizontal_spacing=0.15, vertical_spacing=0.1)
        self.Model = CMIP.loc['HadGEM2-ES']
        tatm_Had, _, = self.Run_sim()
        self.Model = CMIP.loc['FGOALS-s2']
        tatm_FGO ,_, =self.Run_sim()
        self.Model = CMIP.loc['CSIRO-Mk3.6.0']
        tatm_CSI ,_, =self.Run_sim()
        self.Model = CMIP.loc['IPSL-CM5A-LR']
        tatm_IPS ,_, =self.Run_sim()
        self.Model = CMIP.loc['BNU-ESM']
        tatm_BNU ,_, =self.Run_sim()
        self.Model = CMIP.loc['CanESM2']
        tatm_Can ,_, =self.Run_sim()
        self.Model = CMIP.loc['MPI-ESM-LR']
        tatm_MPI ,_, =self.Run_sim()
        self.Model = CMIP.loc['MMM_CMIP5']
        tatm_MMM ,_, =self.Run_sim()
        self.Model = CMIP.loc['CNRM-CM5']
        tatm_CNRM ,_, =self.Run_sim()
        self.Model = CMIP.loc['CCSM4']
        tatm_CC ,_, =self.Run_sim()
        self.Model = CMIP.loc['BCC-CSM1-1']
        tatm_BCC ,_, =self.Run_sim()
        self.Model = CMIP.loc['NorESM1-M']
        tatm_Nor ,_, =self.Run_sim()
        self.Model = CMIP.loc['MIROC5']
        tatm_MIR ,_, =self.Run_sim()
        self.Model = CMIP.loc['MRI-CGCM3']
        tatm_MRI ,_, =self.Run_sim()
        self.Model = CMIP.loc['GFDL-ESM2M']
        tatm_GFD ,_, =self.Run_sim()
        self.Model = CMIP.loc['GISS-E2-R']
        tatm_GISS ,_, =self.Run_sim()
        self.Model = CMIP.loc['INM-CM4']
        tatm_INM ,_, =self.Run_sim()
        
        

        
        x_year = np.arange(self.start_year, self.end_year, self.dt)
        # Create the first trace with the first y-axis
        #fig = go.Figure()
        width = 0.7
        self.fig.update_annotations(font_size=30)
        self.fig.add_trace(go.Scatter(x=x_year, y = self.emission, mode='lines', name='Emissions' ,
                                    
                                      showlegend= False),
                           row = 1, col = 1)

        # Create the second trace with the second y-axis
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_Had, mode='lines', name="HadGEM2-ES",
                                     line=dict(width=width) ),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_FGO, mode='lines', name="FGOALS-s2",
                                     line=dict(width=width) ),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_CSI, mode='lines', name="CSIRO-Mk3.6.0",
                                      line=dict(width=width)),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_IPS, mode='lines', name="IPSL-CM5A-LR",
                                      line=dict(width=width)),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_BNU, mode='lines', name="BNU-ESM",
                                      line=dict(width=width)),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_Can, mode='lines', name="CanESM2",
                                      line=dict(width=width)),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_MPI, mode='lines', name="MPI-ESM-LR",
                                      line=dict(width=width)),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_MMM, mode='lines', name="MMM_CMIP5",
                                      line=dict(dash = 'dash', width=5)),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_CNRM, mode='lines', name="CNRM-CM5",
                                      line=dict(width=width)),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_CC, mode='lines', name="CCSM4",
                                      line=dict(width=width)),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_BCC, mode='lines', name="BCC-CSM1-1",
                                      line=dict(width=width)),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_Nor, mode='lines', name="NorESM1-M",
                                      line=dict(width=width)),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_MIR, mode='lines', name="MIROC5",
                                      line=dict(width=width)),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_MRI, mode='lines', name="MRI-CGCM3",
                                      line=dict(width=width)),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_GFD, mode='lines', name="GFDL-ESM2M",
                                      line=dict(width=width)),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_GISS, mode='lines', name="GISS-E2-R",
                                      line=dict(width=width)),
                           row = 1, col = 2)
        self.fig.add_trace(go.Scatter(x=x_year, y = tatm_INM, mode='lines', name="INM-CM4",
                                      line=dict(width=width)),
                           row = 1, col = 2)
        
        
        self.fig.update_yaxes(title_text="Emission (Gigaton Carbon/year)",
                         range=[np.min(self.emission)-1,np.max(self.emission)+1],
                         title_standoff=25, title_font=dict(size=25), row = 1, col =1)
        self.fig.update_yaxes(title_text="Global surface temperature anomaly (°C)",
                         range = [0,self.tatm_max+1],
                         title_standoff=25, title_font=dict(size=25), row = 1, col =2)
        self.fig.update_xaxes(title_text ='Time', title_standoff =25,title_font=dict(size=25), row = 1, col =1)
        self.fig.update_xaxes(title_text ='Time', title_standoff =25,title_font=dict(size=25), row = 1, col =2)
        
        self.fig.update_layout(
            title_text = '',
            title=dict(
                font=dict(
                    size=25  # Adjust the font size here
                    )
                ),
            annotations=[
        dict(text="Emission data", x=0.2, y=1.05, xref="paper", yref="paper", showarrow=False, font=dict(size=25)),
        dict(text="Temperature anomaly prediction with CMIP5 models", x=1, y=1.05, xref="paper", yref="paper", showarrow=False, font=dict(size=25))
    ]
            )
        

    # Update the color scale
        self.fig.update_layout(colorway=self.custom_colors)


        # # Show the plot
        # self.fig.write_html('first_figure.html', auto_open=True)
        return self.fig
        
        Temp_CMIP5 = {
            'tatm_had':tatm_Had,
            'tatm_FGO':tatm_FGO,
            'tatm_CSI':tatm_CSI,
            'tatm_IPS':tatm_IPS,
            'tatm_BNU':tatm_BNU,
            'tatm_Can':tatm_Can,
            'tatm_MPI':tatm_MPI,
            'tatm_MMM':tatm_MMM,
            'tatm_CNRM':tatm_CNRM,
            'tatm_CC':tatm_CC,
            'tatm_BCC':tatm_BCC,
            'tatm_Nor':tatm_Nor,
            'tatm_MIR':tatm_MIR,
            'tatm_MRI':tatm_MRI,
            'tatm_GFD':tatm_GFD,
            'tatm_GISS':tatm_GISS,
            'tatm_INM':tatm_INM,
            }
        return(Temp_CMIP5)
        
        
        
    def CMIP6_prediction(self):
         self.fig = make_subplots(rows=1, cols=2,
                            horizontal_spacing=0.15, vertical_spacing=0.1)
         self.Model = CMIP.loc['CNRM-CM6-1']
         tatm_Had, _, = self.Run_sim()
         self.Model = CMIP.loc['CNRM-ESM2-1']
         tatm_FGO ,_, =self.Run_sim()
         self.Model = CMIP.loc['ACCESS-ESM1-5']
         tatm_CSI ,_, =self.Run_sim()
         self.Model = CMIP.loc['CNRM-CM6-1-HR']
         tatm_IPS ,_, =self.Run_sim()
         self.Model = CMIP.loc['SAM0-UNICON']
         tatm_BNU ,_, =self.Run_sim()
         self.Model = CMIP.loc['CMCC-CM2-SR5']
         tatm_Can ,_, =self.Run_sim()
         self.Model = CMIP.loc['BCC-ESM1']
         tatm_MPI ,_, =self.Run_sim()
         self.Model = CMIP.loc['MMM_CMIP6']
         tatm_MMM ,_, =self.Run_sim()
         self.Model = CMIP.loc['AWI-CM-1-1-MR']
         tatm_CNRM ,_, =self.Run_sim()
         self.Model = CMIP.loc['MRI-ESM2-0']
         tatm_CC ,_, =self.Run_sim()
         self.Model = CMIP.loc['NorCPM1']
         tatm_BCC ,_, =self.Run_sim()
         self.Model = CMIP.loc['GISS-E2-1-H']
         tatm_Nor ,_, =self.Run_sim()
         self.Model = CMIP.loc['MPI-ESM1-2-HR']
         tatm_MIR ,_, =self.Run_sim()
         self.Model = CMIP.loc['BCC-CSM2-MR']
         tatm_MRI ,_, =self.Run_sim()
         self.Model = CMIP.loc['MPI-ESM1-2-LR']
         tatm_GFD ,_, =self.Run_sim()
         self.Model = CMIP.loc['FGOALS-g3']
         tatm_GISS ,_, =self.Run_sim()
         self.Model = CMIP.loc['MIROC6']
         tatm_INM ,_, =self.Run_sim()
         self.Model = CMIP.loc['MIROC-ES2L']
         tatm_CMIP60 ,_, =self.Run_sim()
         self.Model = CMIP.loc['GISS-E2-1-G']
         tatm_CMIP61 ,_, =self.Run_sim()
         self.Model = CMIP.loc['CAMS-CSM1-0']
         tatm_CMIP62 ,_, =self.Run_sim()
         self.Model = CMIP.loc['GISS-E2-2-G']
         tatm_CMIP63 ,_, =self.Run_sim()
         
         

         width = 0.7
         x_year = np.arange(self.start_year, self.end_year, self.dt)
         # Create the first trace with the first y-axis
         #fig = go.Figure()
         self.fig.update_annotations(font_size=30)
         self.fig.add_trace(go.Scatter(x=x_year, y = self.emission, mode='lines', name='Emissions' ,
                                     
                                       showlegend= False),
                            row = 1, col = 1)

         # Create the second trace with the second y-axis
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_Had, mode='lines', name="CNRM-CM6-1",
                                    line=dict(width=width)  ),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_FGO, mode='lines', name="CNRM-ESM2-1",
                                      line=dict(width=width) ),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_CSI, mode='lines', name="ACCESS-ESM1-5",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_IPS, mode='lines', name="CNRM-CM6-1-HR",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_BNU, mode='lines', name="SAM0-UNICON",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_Can, mode='lines', name="CMCC-CM2-SR5",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_MPI, mode='lines', name="BCC-ESM1",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_MMM, mode='lines', name="MMM_CMIP6",
                                       line = dict(dash ='dash', width =5)),
                            
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_CNRM, mode='lines', name="AWI-CM-1-1-MR",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_CC, mode='lines', name="MRI-ESM2-0",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_BCC, mode='lines', name="NorCPM1",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_Nor, mode='lines', name="GISS-E2-1-H",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_MIR, mode='lines', name="MPI-ESM1-2-HR",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_MRI, mode='lines', name="BCC-CSM2-MR",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_GFD, mode='lines', name="MPI-ESM1-2-LR",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_GISS, mode='lines', name="FGOALS-g3",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_INM, mode='lines', name="MIROC6",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_CMIP60, mode='lines', name="MIROC-ES2L",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_CMIP61, mode='lines', name="GISS-E2-1-G",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_CMIP62, mode='lines', name="CAMS-CSM1-0",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         self.fig.add_trace(go.Scatter(x=x_year, y = tatm_CMIP63, mode='lines', name="GISS-E2-2-G",
                                       line=dict(width=width)),
                            row = 1, col = 2)
         
         
         self.fig.update_yaxes(title_text="Emission (Gigaton Carbon/year)",
                          range=[np.min(self.emission)-1,np.max(self.emission)+1],
                          title_standoff=25, title_font=dict(size=25), row = 1, col =1)
         self.fig.update_yaxes(title_text="Global surface temperature anomaly (°C)",
                          range = [0,self.tatm_max+1],
                          title_standoff=25, title_font=dict(size=25), row = 1, col =2)
         self.fig.update_xaxes(title_text ='Time', title_standoff =25,title_font=dict(size=25), row = 1, col =1)
         self.fig.update_xaxes(title_text ='Time', title_standoff =25,title_font=dict(size=25), row = 1, col =2)
         
         self.fig.update_layout(
             title_text = '',
             title=dict(
                 font=dict(
                     size=25  # Adjust the font size here
                     )
                 ),
             annotations=[
         dict(text="Emission data", x=0.2, y=1.05, xref="paper", yref="paper", showarrow=False, font=dict(size=25)),
         dict(text="Temperature anomaly prediction with CMIP6 models", x=1, y=1.05, xref="paper", yref="paper", showarrow=False, font=dict(size=25))
     ]
             )
            

        # Update the color scale
         self.fig.update_layout(colorway=self.custom_colors)


        #     # Show the plot
        #  self.fig.write_html('first_figure.html', auto_open=True)
        # return self.fig
         
         Temp_CMIP6 = {
             'tatm_had':tatm_Had,
             'tatm_FGO':tatm_FGO,
             'tatm_CSI':tatm_CSI,
             'tatm_IPS':tatm_IPS,
             'tatm_BNU':tatm_BNU,
             'tatm_Can':tatm_Can,
             'tatm_MPI':tatm_MPI,
             'tatm_MMM':tatm_MMM,
             'tatm_CNRM':tatm_CNRM,
             'tatm_CC':tatm_CC,
             'tatm_BCC':tatm_BCC,
             'tatm_Nor':tatm_Nor,
             'tatm_MIR':tatm_MIR,
             'tatm_MRI':tatm_MRI,
             'tatm_GFD':tatm_GFD,
             'tatm_GISS':tatm_GISS,
             'tatm_INM':tatm_INM,
             'tatm_CMIP60':tatm_CMIP60,
             'tatm_CMIP61':tatm_CMIP61,
             'tatm_CMIP62 ':tatm_CMIP62 ,
             'tatm_CMIP63':tatm_CMIP63
             
             }
         return(Temp_CMIP6)
            
        
        
        
   
        
    
    
    
    



      

