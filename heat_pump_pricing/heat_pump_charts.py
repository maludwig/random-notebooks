#!/usr/bin/env python
# coding: utf-8

# In[34]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# In[35]:


electricity_cost_per_kwh = 0.0879  # $/kWh
gas_cost_per_gj = 4.59  # $/GJ
furnace_afue = 0.961

# Constants
GJ_per_MBtu = 1.055056
SECONDS_PER_HOUR = 3600

def fahrenheit_to_celsius(f):
    return (f - 32) * 5.0 / 9.0

def celsius_to_fahrenheit(c):
    return c * 9.0 / 5.0 + 32

def load_heat_pump_data(csv_path):
    """
    Loads heat pump performance data from a CSV and adds a Celsius temperature column.

    Args:
        csv_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Augmented DataFrame with 'OutdoorAirTempC' column added.
    """
    df = pd.read_csv(csv_path)

    # Add Celsius conversion
    df["OutdoorAirTempC"] = (df["OutdoorAirTempF"] - 32) * 5.0 / 9.0

    df["HeatPumpPricePerMBtu"] = (df["PowerInputkW"] * electricity_cost_per_kwh) / df["HeatOutputMBH"]
    # Furnace price per MBtu (same for all rows)
    furnace_price_per_mbtu = (gas_cost_per_gj / GJ_per_MBtu) / furnace_afue
    df["FurnacePricePerMBtu"] = furnace_price_per_mbtu
    return df

def load_heat_pump_data_si(csv_path):
    """
    Loads heat pump performance data and converts all units to SI (kW, GJ, etc.).

    Returns cost per GJ of useful heat for both the heat pump and furnace.
    """
    df = pd.read_csv(csv_path)

    # Convert temperature
    df["OutdoorAirTempC"] = (df["OutdoorAirTempF"] - 32) * 5.0 / 9.0

    # Convert MBH (thousands of BTU/hr) → kW
    df["HeatOutputkW"] = df["HeatOutputMBH"] * 0.29307107

    # Energy cost per GJ of useful heat
    df["HeatPumpPricePerHour"] = df["PowerInputkW"] * electricity_cost_per_kwh
    df["HeatPumpGJPerHour"] = df["HeatOutputkW"] * SECONDS_PER_HOUR / 1e6  # Convert kW to GJ/hr
    df["HeatPumpPricePerGJ"] = df["HeatPumpPricePerHour"] / df["HeatPumpGJPerHour"]

    # Furnace cost per GJ of useful heat
    df["FurnacePricePerGJ"] = gas_cost_per_gj / furnace_afue

    return df
def plot_cop_vs_outdoor_temp(df):
    """
    Plots Coefficient of Performance vs Outdoor Temperature (in Celsius).

    Args:
        df (pd.DataFrame): DataFrame containing 'OutdoorAirTempC' and 'CoefficientOfPerformance'.
    """
    plt.figure(figsize=(8, 5))
    plt.plot(df["OutdoorAirTempC"], df["CoefficientOfPerformance"], marker='o', linestyle='-')
    plt.title("Heat Pump Efficiency vs Outdoor Temperature")
    plt.xlabel("Outdoor Temperature (°C)")
    plt.ylabel("Coefficient of Performance (COP)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_price_comparison(df):
    """
    Plots Heat Pump vs Furnace cost per MBtu against outdoor temperature in °C.

    Args:
        df (pd.DataFrame): DataFrame with 'OutdoorAirTempC', 'HeatPumpPricePerMBtu', and 'FurnacePricePerMBtu'.
    """
    plt.figure(figsize=(8, 5))
    # Check for HeatPumpPricePerMBtu column
    is_in_mbtu = "HeatPumpPricePerMBtu" in df.columns
    if is_in_mbtu:
        heat_pump_price = df["HeatPumpPricePerMBtu"]
        furnace_price = df["FurnacePricePerMBtu"]
        units = "$/MBtu"
    else:
        heat_pump_price = df["HeatPumpPricePerGJ"]
        furnace_price = df["FurnacePricePerGJ"]
        units = "$/GJ"
    plt.plot(df["OutdoorAirTempC"], heat_pump_price, marker='o', linestyle='-', label=f"Heat Pump ({units})")
    plt.axhline(y=furnace_price.iloc[0], color='red', linestyle='--', label=f"Gas Furnace ({units})")

    plt.title(f"{units} vs Outdoor Temperature")
    plt.xlabel("Outdoor Temperature (°C)")
    plt.ylabel(units)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

# Example usage:
# df = load_heat_pump_data("your_file.csv")
# plot_cop_vs_outdoor_temp(df)
heat_pump_data_file = r'C:\Users\turiy\dev\experiments\copdata_rotated.csv'
heat_pump_df = load_heat_pump_data(heat_pump_data_file)

heat_pump_df


# In[36]:


plot_cop_vs_outdoor_temp(heat_pump_df)


# In[37]:


plot_price_comparison(heat_pump_df)


# In[38]:


heat_pump_df['HeatPumpPricePerMBtu'] / heat_pump_df['FurnacePricePerMBtu']


# In[39]:


si_df = load_heat_pump_data_si(heat_pump_data_file)
si_df


# In[41]:


plot_price_comparison(si_df)


# In[42]:


def plot_price_comparison(df):
    """
    Plots Heat Pump vs Furnace cost per MBtu against outdoor temperature in °C.

    Args:
        df (pd.DataFrame): DataFrame with 'OutdoorAirTempC', 'HeatPumpPricePerMBtu', and 'FurnacePricePerMBtu'.
    """
    plt.figure(figsize=(8, 5))
    # Check for HeatPumpPricePerMBtu column
    is_in_mbtu = "HeatPumpPricePerMBtu" in df.columns
    if is_in_mbtu:
        heat_pump_price = df["HeatPumpPricePerMBtu"]
        furnace_price = df["FurnacePricePerMBtu"]
        units = "$/MBtu"
    else:
        heat_pump_price = df["HeatPumpPricePerGJ"]
        furnace_price = df["FurnacePricePerGJ"]
        units = "$/GJ"
    plt.plot(df["OutdoorAirTempC"], heat_pump_price, marker='o', linestyle='-', label=f"Heat Pump ({units})")
    plt.axhline(y=furnace_price.iloc[0], color='red', linestyle='--', label=f"Gas Furnace ({units})")
    plt.axhline(y=0, color='green', linestyle='--', label=f"Heat Pump powered by solar ({units})")

    plt.title(f"{units} vs Outdoor Temperature")
    plt.xlabel("Outdoor Temperature (°C)")
    plt.ylabel(units)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
plot_price_comparison(si_df)

