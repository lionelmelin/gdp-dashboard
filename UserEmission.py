# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 11:05:22 2024

@author: F_ZHANG
"""
import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator
import matplotlib.pyplot as plt

class Emission():
    def __init__(self, peak_emission = 1.4, peak_year = 2035, halve_year = 2065, 
                 end_year = 2100, end_emission = 0.1):
        self.start_year = 2020
        self.peak_year = peak_year
        self.start_emission = 10
        self.peak_emission = self.start_emission*peak_emission
        self.halve_year =  halve_year
        self.end_year = end_year
        self.end_emission = end_emission*self.start_emission
        
    def EmissionInterpolate(self):
        # Define the four points a, b, c, and d
        a = (self.start_year, self.start_emission)  # (x, y)
        b = (self.peak_year, self.peak_emission)
        c = (self.halve_year, self.end_emission)#0.5*self.start_emission)
        d = (self.end_year, self.end_emission)
        
        # Determine the maximum y value among a, c, and d
        max_y = max(a[1], c[1], d[1], b[1])

        # Ensure b is the maximum among a, c, and d
        b = (b[0], max_y)

        # Arrange points for PchipInterpolator
        x = np.array([a[0], b[0], c[0], d[0]])
        y = np.array([a[1], b[1], c[1], d[1]])

        # Perform cubic Hermite interpolation (PchipInterpolator)
        interp = PchipInterpolator(x, y)

        # Generate points along the curve for smooth visualization
        x_interp = np.linspace(min(x), max(x), self.end_year - self.start_year + 1)
        emission_interp = interp(x_interp)
        year = np.arange(self.start_year, self.end_year+1,1)
        emission_data = {'Year':year, 
                         'Emission': emission_interp}
        emission_df = pd.DataFrame(emission_data)
        return(emission_df)

        