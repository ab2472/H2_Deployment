import Steel_Scenario
import Ammonia_Scenario
import Methanol_Scenario
import Clean_Data 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import Sobol_Analysis
import seaborn as sns


#define the input data
DRI = pd.read_csv('Data/Input Data/DRI_Data.csv')
BF = pd.read_csv('Data/Input Data/BF_Data.csv')
Plants = pd.read_csv('Data/Input Data/Plant_data_steel_iron.csv')
Methanol = pd.read_csv('Data/Input Data/methanol_production.csv')
Ammonia = pd.read_csv('Data/Input Data/ammonia_production.csv')
emissions_factors = pd.read_csv('Data/Input Data/Emissions Factors.csv')
region_mapping = pd.read_csv('Data/Input Data/Region_Country_mapping.csv')

#define the ranges for key assumptions
values_steel = {
    'Start Capacity (Mt/yr)': [2.5, 5], #small range as based on current projects
    'Growth Rate (%)': [0.05, 1.5], # range between current growth rate and unrealistic unconventional growth rate
    'Demand (Mt/yr)': [1890, 2500], # range between current demand and maximum possible demand
    'Lifetime (years)': [10, 25], 
    'Lifetime DRI (years)': [18, 32],#SD of DRI lifetime
    'Recycling Rate (%)': [0.3, 0.9], #range between current recycling rate and maximum possible recycling rate
    'Start Year': [2026, 2027]    #Small range for uncertainty as based on current projects                                                                      
    }

values_ammonia = {
    'Start Capacity (Mt/yr)': [0.3, 0.6], #small range as based on current projects
    'Growth Rate (%)': [0.05, 1.5], # range between current growth rate and unrealistic unconventional growth rate
    'Demand (Mt/yr)': [184, 253], # range between current demand and IEA Stated Policies Scenario
    'Lifetime (years)': [19, 31],
    'Start Year': [2020, 2022]    #Small range for uncertainty as based on current projects
    }

values_methanol = {
    'Start Capacity (Mt/yr)': [0.2, 0.67], #https://www.methanol.org/renewable/ Low= operational, high = with those under construction. 0.079
    'Growth Rate (%)': [0.05, 1.5], # range between current growth rate and unconventional growth rate
    'Demand (Mt/yr)': [111, 500], # range between current demand and total demand estimated for 2050 (IRENA/WEF)
    'Lifetime (years)': [19, 31],
    'Start Year': [2020, 2022]    #Small range for uncertainty as based on current projects
    }

yearmin = 2023
yearmax = 2050


def produce_results(iterations=2):
    """
    Produce results for the steel, ammonia, and methanol scenarios.
    """
    #find results for the steel scenarios
    steel_results = Steel_Scenario.monte_carlo_steel(BF, DRI,yearmin=yearmin,yearmax=yearmax,
                                                     low_demand=values_steel['Demand (Mt/yr)'][0],
                                                     high_demand=values_steel['Demand (Mt/yr)'][1],
                                                     recycling_rate=0.45,
                                                     gr_low=0.2, gr_high=0.5, 
                                                     lifetime_low_BF=11, lifetime_standard_BF=17, lifetime_low_DRI = 17, lifetime_standard_DRI=25,
                                                     start_capacity=2.5,start_recycled=490,start_year=2026,
                                                     lifetime_SD=7,lifetimelow_SD=5,
                                                     contour=False, iterations=iterations)
                  
    #find results for the ammonia scenarios
    ammonia_results = Ammonia_Scenario.monte_carlo_ammonia(Ammonia,yearmin=yearmin, yearmax=yearmax,
                                                           low_demand=values_ammonia['Demand (Mt/yr)'][0],
                                                           high_demand=values_ammonia['Demand (Mt/yr)'][1],
                                                           gr_low=0.5, gr_high=1,
                                                           lifetime_low_Ammonia = 15,lifetime_standard_Ammonia=25,
                                                           start_capacity=0.3,start_year=2020,
                                                           lifetime_SD=6,lifetimelow_SD=4,
                                                           iterations=iterations)
                  
    #find results for the methanol scenarios
    methanol_results = Methanol_Scenario.monte_carlo_methanol(Methanol,yearmin=yearmin, yearmax=yearmax,
                                                              low_demand=values_methanol['Demand (Mt/yr)'][0],
                                                              high_demand=values_methanol['Demand (Mt/yr)'][1],
                                                              gr_low=0.5, gr_high=1,
                                                              lifetime_standard_methanol = 25, lifetime_low_methanol=15,
                                                              start_capacity=0.2,start_year=2020,
                                                              lifetime_SD=6,lifetimelow_SD=4,
                                                              contour=False, iterations=iterations)

    return steel_results, ammonia_results, methanol_results

#define plots for main results

def sankey_data(sector_results):
    """
    Create results for sankey diagram, for which we need to add some columns to the dataframes.
    """
    china_emissions_FF =[]
    RoW_emissions_FF = []
    new_FF = []
    reinvested_FF = []
    H2_production = []
    EAF_production = []
    Annual_emissons = []

    for year in [2023,2030,2040,2050]:
        #change from sum to values[0]
        china_emissions_FF.append(sector_results.loc[sector_results['Year'] == year, 'China Emissions FF (MtCO2/yr)'].values[0])
        RoW_emissions_FF.append(sector_results.loc[sector_results['Year'] == year, 'RoW Emissions FF (MtCO2/yr)'].values[0])
        new_FF.append(sector_results.loc[sector_results['Year'] == year, 'New FF Emissions (MtCO2/yr)'].values[0])
        reinvested_FF.append(sector_results.loc[sector_results['Year'] == year, 'Replaced FF Emissions (MtCO2/yr)'].values[0])
        H2_production.append(sector_results.loc[sector_results['Year'] == year, 'H2 Production (Mt/yr)'].values[0])
        EAF_production.append(sector_results.loc[sector_results['Year'] == year, 'Scrap Production (Mt/yr)'].values[0])
        Annual_emissons.append(sector_results.loc[sector_results['Year'] == year, 'Annual Emissions (MtCO2/yr)'].values[0])

    #create a dataframe with each list a row and the years as columns
    sankey_data = pd.DataFrame({
        'Year': [2023, 2030, 2040, 2050],
        'China Emissions from FF (MtCO2/yr)': china_emissions_FF,
        'RoW Emissions from FF (MtCO2/yr)': RoW_emissions_FF,
        'New FF Emissions (MtCO2/yr)': new_FF,
        'Reinvested FF Emissions (MtCO2/yr)': reinvested_FF,
        'H2 Production (Mt/yr)': H2_production,
        'EAF Production (Mt/yr)': EAF_production,
        'Annual Emissions (MtCO2/yr)': Annual_emissons
    })

    return sankey_data

def sankey_formatting():
    steel_results = pd.read_csv('Data/Output Data/Steel/Steel_2_Monte_Carlo.csv')
    ammonia_results = pd.read_csv('Data/Output Data/Ammonia/Ammonia_2_Monte_Carlo.csv')
    methanol_results = pd.read_csv('Data/Output Data/Methanol/Methanol_2_Monte_Carlo.csv')

    steel_sankey = sankey_data(steel_results)
    ammonia_sankey = sankey_data(ammonia_results)
    methanol_sankey = sankey_data(methanol_results)

    #combine the three sankey dataframes into one by summing the columns
    combined_sankey = pd.DataFrame()
    combined_sankey['Year'] = [2023, 2030, 2040, 2050]
    for col in steel_sankey.columns:
        if col != 'Year':
            combined_sankey[col] = steel_sankey[col].fillna(0) + ammonia_sankey[col].fillna(0) + methanol_sankey[col].fillna(0)

    #save individual sankey dataframes to csv
    steel_sankey.to_csv('Data/Output Data/Steel_Sankey.csv', index=False)   
    ammonia_sankey.to_csv('Data/Output Data/Ammonia_Sankey.csv', index=False)
    methanol_sankey.to_csv('Data/Output Data/Methanol_Sankey.csv', index=False)
    #save combined sankey dataframe to csv
    combined_sankey.to_csv('Data/Output Data/Combined_Sankey.csv', index=False)

    sankey_df = combined_sankey.copy()
    
def sankeymatic_formatting(name='Combined_Sankey'):

    sankey_df = pd.read_csv('Data/Output Data/'+name+'.csv')
    """Format the sankey data for the sankeymatic website."""
    #format data to be in the format required for the sankey diagram, source, target, value
    sankey_list = []
    #first deal with the china emission from FF

    sankey_df['Diff Reinvestments'] = sankey_df['Reinvested FF Emissions (MtCO2/yr)'].diff().fillna(0)
    sankey_df['Avoided Emissions'] = sankey_df['Annual Emissions (MtCO2/yr)'].diff().fillna(0)*-1

    print(sankey_df)

    years = [2023, 2030, 2040, 2050]
    orders_avoided= [9, 8, 7,5]  # order for avoided emissions, decreasing with each year
    for i in range(len(years)):
        
        #China Emissions from FF
        sankey_list.append({
            'source': 'China Emissions from FF (MtCO2/yr)'+str(years[i]),
            'target': years[i],
            'value': sankey_df.loc[sankey_df['Year'] == years[i], 'China Emissions from FF (MtCO2/yr)'].values[0],
            'order': 1
        })
        #RoW Emissions from FF
        sankey_list.append({
            'source': 'RoW Emissions from FF (MtCO2/yr)'+str(years[i]),
            'target': years[i],
            'value': sankey_df.loc[sankey_df['Year'] == years[i], 'RoW Emissions from FF (MtCO2/yr)'].values[0],
            'order': 2
        })

        #next year flow, if not the last year
        if i < len(years) - 1:
            sankey_list.append({
                'source': years[i],
                'target': 'China Emissions from FF (MtCO2/yr)'+str(years[i+1]),
                'value': sankey_df.loc[sankey_df['Year'] == years[i+1], 'China Emissions from FF (MtCO2/yr)'].values[0],
                'order': 1
            })
            sankey_list.append({
                'source': years[i],
                'target': 'RoW Emissions from FF (MtCO2/yr)'+str(years[i+1]),
                'value': sankey_df.loc[sankey_df['Year'] == years[i+1], 'RoW Emissions from FF (MtCO2/yr)'].values[0],
                'order': 2
            })

        #avoided emissions

        if sankey_df.loc[sankey_df['Year'] == years[i], 'Diff Reinvestments'].values[0] > 0:
            sankey_list.append({
                'source': years[i-1],
                'target': 'Reinvested FF Emissions (MtCO2/yr)'+str(years[i]),
                'value': sankey_df.loc[sankey_df['Year'] == years[i], 'Diff Reinvestments'].values[0],
                'order': 3
            })

            sankey_list.append({
                'source': years[i-1],
                'target': 'Avoided Emissions (MtCO2/yr)',
                'value': sankey_df.loc[sankey_df['Year'] == years[i], 'Avoided Emissions'].values[0],
                'order': orders_avoided[i]
            })

        elif sankey_df.loc[sankey_df['Year'] == years[i], 'Diff Reinvestments'].values[0] <= 0:
            #move from reinvested to avoided
            sankey_list.append({
                'source': 'Reinvested FF Emissions (MtCO2/yr)'+str(years[i-1]),
                'target': 'Avoided Emissions (MtCO2/yr)',
                'value': sankey_df.loc[sankey_df['Year'] == years[i], 'Diff Reinvestments'].values[0]*-1,
                'order': 6
            })

            #add other avoided from previous year
            sankey_list.append({
                'source': years[i-1],
                'target': 'Avoided Emissions (MtCO2/yr)',
                'value': sankey_df.loc[sankey_df['Year'] == years[i], 'Avoided Emissions'].values[0]-\
                        sankey_df.loc[sankey_df['Year'] == years[i], 'Diff Reinvestments'].values[0]*-1,
                'order': orders_avoided[i]
            })

    sankey_list.append({
        'source': 'Reinvested FF Emissions (MtCO2/yr)2030',
        'target': 'Reinvested FF Emissions (MtCO2/yr)2040',
        'value': sankey_df.loc[sankey_df['Year'] == 2030, 'Diff Reinvestments'].values[0],
        'order': 3})

    sankey_list.append({
        'source': 'Reinvested FF Emissions (MtCO2/yr)2040',
        'target': 'Reinvested FF Emissions (MtCO2/yr)2050',
        'value': '*',
        'order': 3})
   
    sankey_df = pd.DataFrame(sankey_list)

    sankey_df['Sankey Matic'] = sankey_df['source'].astype(str)  + ' [' + sankey_df['value'].astype(str) + ']'+ sankey_df['target'].astype(str)

    #sort by order column
    sankey_df = sankey_df.sort_values(by='order')

    sankey_df.to_csv('Data/Output Data/'+name+'.csv', index=False)

    """ Link to the Sankey Matic website for visualisation:
    https://sankeymatic.com/build/?i=MICwlgdghgBAogWzAZ2WA9hZMBmAndBGAMWJgAoBZAF2AHkAmAegE88BKBgBgYGYYA2gEYAnCIAcAOgDs0gGxchvXuIYjeXcQF1ufAFChIsRCjSZs%2BQiTJVajVh24BWLoK6S5AFl5OdXF3rcnq4C7l4%2BWobQ8EioGFi4BESkFDT0zGyc%2DlyBXBqCQtJCHk7iGnJO0k4MQp6FkeDRJnHmiVYptukOWcEGjcaxZgmWyTZp9plBIYXFFWVcFVU1ddJ%2BvVEDpvEWSdapdhmOedOVDJLiTp4KckpOTsq%2B3Bq5fAWn55fXt%2DcRGzFbrRGe06EyOzwASugAOr%2DFrDXYdcaHLL5YRCaqSES1cTqZQMJxyXgMPwQ6GwoY7dpjA7dZwhM6iDSebR0vSQmHNCltUb7LqTHj8YSVMJeCS8IRcHhOERyPz6dnk7bc4FI2lcYIFVSSS7qnFVWrKPJrHJTQQM9S6rQKzlKoGImn8gJPaZanXMkT67waXhWsk2wEI6l8o69XSCoTos5Y93KIkEom%2BjmDW2B3mglEmgWCFzSGRqcXi7w8aQ%2B8EAU0gADcy8hqGWACZ7f0JEHI525VGFOQiSQacSKCT4pmrctVmt1xspZvYVtq3qjiDV2sNpvJ1qz%2DmonN59RKA3F0sVxfjldTtct1X8%2BdHpcT1cAi8OkMhABUVpvJ8nZGnabb2VyGoCD4xS8HIDAMMyRJyF40giFoACClboGA9Yrj%2BG4cGyH7Ll%2Birrpez7Zp4TiSIoXiaOIsiXEUCFIShaHnjOBHsB2IQKLwpEiAS9xcVioGyohyGoY26HMS8grKHIkjgRcKhlCIeRXLRQkMQ%2BTFPixaAAF5ljAADuMD9jkMAwCAMAKDkCBQHgADmkAwAANjAQgMHoJl4M5rkmdQzniG5MAAEYwNwegBTZMAAMboA56AeQAxDgiVJf51B4FAWAAA7WWWEA%2BQAcnoEDoKh%2Bmef5ZkBCZyBZRFkDhVU%2DkBbFqEecZMDUCAZYILpRUQGW%2DlRTF8WeDgI0jf56A1WA1AsM5eg4DFBkRQArnglZQNQq26e4lz%2BZAnV4NNQK9f1JmDbFMBxZ4AWeCIt0TVNM0wGETh6A5UAsOgy0%2Bc1ZYeWWAAeUARdQ%2DkAFbLbWYA4J9h12QkBUmRDUMwzl9bYIjMB4GW1Z4MgZY2WlGVmZjG3UMDjRRQgGUOWWda1ugMB9dltZvVAAVlg52DnfFkp8214AlZj4A2SADlgKLPnuA1Jk4Jg1A4MDunIOlyAALT44dOD%2BeLfXVcDdXPdJ%2DnY%2B91BgEuYA6c5Er%2BVZNkQNDs0Sjk70cw50DdTAUAZRlZbWRj%2DnabpQhyP5ekVpLMDBK77Oc%2BtDnLbpPt%2BwHMCYzgy0OQ5GXY7VQwwAAmv5GXoGg5uYIFnPoHp4eRyAPkx2z7ul%2BX8Te996BQOLDvPUHEWdV7UCd%2D5OBgHjPkc3L2ONdjUAANal5APkiHoCdJ7gsVWT5ADkAA0kg7yX2NjwDMA70fVXLYlYBnxfegdV1ZboIl%2BM%2BbAYcmUFbURX3JmNpZOmsBuq5W2OleeZYWDbzAL%2DTG4soYIACt3dKEUaxFz0AgdA1ZgpZjVu4FyXg94wDwdqS4pQMFYN0n8H8dogzpjDM9IhJDeC3TAhQ7B1pGLKntMGLIrwSGSj3Ew9wclxBCHYVQ%2DoeF4RUl%2DGqfIAiWGqGEdJJQOIJEwE4WpbhdC%2DwKPcIpUCKjxR5DDpg7BzpiH4LAtBYx1RoIaIXLeU834uEYR6K4ARohPAMBURBXgHoNHUK4bQuRV5PEGN4NIPgKj%2DDLEcX6EJqZ3GmkUVcIQKiDS1A0ak6xATpCZLiY47Cd4zzaJSdkI2LlKK8EyVxZQxSxw4XvHCdSvDLEkNDjEqx0kuKiA0YJeiIk3HMR6YoDQIhYl3AYGYyhmjEnaNCRUlwYyokyhUcEFw4jzG6TpD09ElQ5DGJmT4oJUiaHJOYnsxRIgGAFJ6USfsIggA"""
    return sankey_df

def figure_2_scenario_plots():
    #open the steel, ammonia, and methanol results csv files
    colours = ['#8dd3c7','#fb8072','#bebada','#ffffb3','#80b1d3','#fdb462','#b3de69']

    results_by_scenario = {}
    for n in range(1, 8):
        steel_results = pd.read_csv(f'Data/Output Data/Steel/Steel_{n}_Monte_Carlo.csv')
        ammonia_results = pd.read_csv(f'Data/Output Data/Ammonia/Ammonia_{n}_Monte_Carlo.csv')
        methanol_results = pd.read_csv(f'Data/Output Data/Methanol/Methanol_{n}_Monte_Carlo.csv')


        steel_results['H2 Use (Mt/yr)'] = steel_results['H2 Production (Mt/yr)']*0.06
        ammonia_results['H2 Use (Mt/yr)'] = ammonia_results['H2 Production (Mt/yr)']*3/17
        methanol_results['H2 Use (Mt/yr)'] = methanol_results['H2 Production (Mt/yr)']*0.2

        steel_results['Renewable Electricity Use (TWh/yr)'] = steel_results['H2 Production (Mt/yr)'] * 3.4 + steel_results['Scrap Production (Mt/yr)'] * 0.450
        ammonia_results['Renewable Electricity Use (TWh/yr)'] = ammonia_results['H2 Production (Mt/yr)'] * 10.4
        methanol_results['Renewable Electricity Use (TWh/yr)'] = methanol_results['H2 Production (Mt/yr)'] * 12

        #change units for plots
        for df in [steel_results, ammonia_results, methanol_results]:
            df['Cumulative Emissions (MtCO2)'] = df['Annual Emissions (MtCO2/yr)'].cumsum()
            df['Cumulative Emissions (GtCO2)'] = df['Cumulative Emissions (MtCO2)'] / 1000

            df['Annual Emissions (GtCO2/yr)'] = df['Annual Emissions (MtCO2/yr)']/1000

        #combine the results into one dataframe, other than year column and last year column which the max is taken for each row
        year_min = min(steel_results['Year'].min(), ammonia_results['Year'].min(), methanol_results['Year'].min())
        year_max = max(steel_results['Year'].max(), ammonia_results['Year'].max(), methanol_results['Year'].max())

        total_results = pd.DataFrame({'Year': np.arange(year_min, year_max +1)} )
        for col in steel_results.columns:
            if col != 'Year' and col != 'Last Retirement Year':
                total_results[col] = steel_results[col].fillna(0) + ammonia_results[col].fillna(0) + methanol_results[col].fillna(0)
        
        results_by_scenario[n] = {
            'steel': steel_results,
            'ammonia': ammonia_results,
            'methanol': methanol_results,
            'total': total_results
        }

    fig, ax = plt.subplots(2,2, figsize=(12, 12))

    order1_2  = [1,7,3,5,4,2,6]

    order3 = [2,4,5,3,7,1,6]

    """Plot 1: Cumulative Emissions by Scenario"""
    
    #add horizontal lines relating to the total carbon budget for 1.5C and 2C scenarios

    #1.5C Carbon Budget 67% Probability (400 GtCO2) - steel, ammonia, methanol are ~ 8, 1.8, 0.8 = 10.6
    #ax[0,0].fill_between([2023,2060],400*0.10,500*0.1, color='black', alpha=0.1, label='1.5C Carbon Budget 67% Probability (400 GtCO2)',linewidth=0)

    #Tseke et al. 2023 https://link.springer.com/article/10.1007/s42452-023-05482-w Steel 27.8, Chemicals 19.589
    ax[0,0].axhline(y=47.389, color='grey', linestyle='--', label='Teske et al. 2023 Steel and Chemicals',linewidth=1)
    #region based on proportion of emissions in 2023 and 1.5 carbon budget (9.8%), taking carbon budget from 2020 and subtracting emissions from years between
    ax[0,0].fill_between([2023,2060],24,38, color='grey', alpha=0.2, label='Teske et al. 2023 Steel and Chemicals',linewidth=0)
    ax[0,0].text(2023.5,27,'1.5\N{DEGREE SIGN}C Carbon Budget\n(Proportional)', color='grey', fontsize=8) #https://www.ipcc.ch/report/ar6/wg1/downloads/faqs/IPCC_AR6_WGI_FAQ_Chapter_05.pdf
    ax[0,0].fill_between([2023,2060],102,122, color='grey', alpha=0.2, label='Teske et al. 2023 Steel and Chemicals',linewidth=0)
    #add label to the line
    ax[0,0].text(2023.5, 109, '2\N{DEGREE SIGN}C Carbon Budget\n(Proportional)', color='grey', fontsize=8)

    #add text label to the line
    ax[0,0].text(2023.5, 47.389 +2, '1.5\N{DEGREE SIGN}C Carbon Budget\n(Steel and Chemicals)\nTeske et al. 2023', color='grey', fontsize=8)
    
    ax[0,0] = axes_plot(ax[0,0], results_by_scenario, colours,'Cumulative Emissions (GtCO2)',1,order1_2,'Cumulative Emissions (Gt CO\u2082)')
    ax[0,0].set_title('A. Cumulative Emissions (Gt CO\u2082)')


    """Plot 2: Annual Emissions by Scenario"""
    ax[0,1] = axes_plot(ax[0,1], results_by_scenario, colours,'Annual Emissions (GtCO2/yr)',1,order1_2,'Annual Emissions (Gt CO\u2082/yr)')
    ax[0,1].set_title('B. Annual Emissions (Gt CO\u2082/yr)')

    #add lines at 50% reudction and 80% reduction from 2023 emissions
    total_emissions = results_by_scenario[1]['total']['Annual Emissions (GtCO2/yr)'].loc[results_by_scenario[1]['total']['Year'] == 2023].values[0]
    print(f'Total emissions in 2023: {total_emissions} GtCO2/yr')
    ax[0,1].axhline(y=total_emissions*0.5, color='grey', linestyle='--', label='50% Reduction from 2023 Emissions',linewidth=1)
    #add label to the line
    ax[0,1].text(2023.5, total_emissions*0.5 - 0.18, '50% Emissions\nReduction', color='grey', fontsize=8)
    ax[0,1].axhline(y=total_emissions*0.2, color='grey', linestyle='--', label='80% Reduction from 2023 Emissions',linewidth=1)
    #add label to the line
    ax[0,1].text(2023.5, total_emissions*0.2 - 0.18, '80% Emissions\nReduction', color='grey', fontsize=8)

    """Plot 3: Hydrogen Use by Scenario"""
    ax[1,0] = axes_plot(ax[1,0], results_by_scenario, colours,'H2 Use (Mt/yr)',2,order3,'Hydrogen Demand (Mt H\u2082/yr)')
    ax[1,0].set_title('C. Hydrogen Demand (Mt H\u2082/yr)')

    #add horizontal line at 100 Mt/yr for H2 demand
    ax[1,0].axhline(y=52, color='grey', linestyle='--', label='Total Fossil Supply',linewidth=1)

    #add label to the line
    ax[1,0].text(2023.5, 52 + 2, '2023 Steel, Ammonia\nand Methanol Fossil\nHydrogen Use - 52 Mt/yr', color='grey', fontsize=8)

    ax[1,0].axhline(y=1, color='grey', linestyle='--', label='Total Green Supply',linewidth=1)
    #add label to the line
    ax[1,0].text(2023.5, 1 + 0.2, '2023 Green Hydrogen\nProduction <1 Mt/yr', color='green', fontsize=8)

    """Plot 4: Renewable Electricity Use by Scenario"""
    ax[1,1] = axes_plot(ax[1,1], results_by_scenario, colours,'Renewable Electricity Use (TWh/yr)',2,order3,'Renewable Electricity Demand (TWh/yr)')
    ax[1,1].set_title('D. Renewable Electricity Demand (TWh/yr)')
    ax[1,1].axhline(y=1400, color='grey', linestyle='--', label='Current Electricity Use (TWh/yr)',linewidth=1)
    ax[1,1].text(2023.5, 1400 + 200, '2023 Steel, Ammonia\nand Methanol Electricty\nUse - 1600 TWh/yr', color='grey', fontsize=8)



    #format legend
    handles, labels = ax[0,0].get_legend_handles_labels()
    #remove the first label (the horizontal lines)
    handles = handles[1:]
    #rename the labels to more descriptive names
    for i in range(len(labels)):
        if labels[i] == 'Scenario 1':
            labels[i] = 'Committed Infrastructure Only'
        elif labels[i] == 'Scenario 2':
            labels[i] = 'Standard H2 Deployment, Standard Committed Infrastructure'
        elif labels[i] == 'Scenario 3':
            labels[i] = 'Accelerated H2 Deployment, Standard Committed Infrastructure'
        elif labels[i] == 'Scenario 4':
            labels[i] = 'Standard H2 Deployment, Accelerated Retirement'
        elif labels[i] == 'Scenario 5':
            labels[i] = 'Standard H2 Deployment Only '
        elif labels[i] == 'Scenario 6':
            labels[i] = 'Demand Growth with Standard Decommissioning and H2 Deployment'
        elif labels[i] == 'Scenario 7':
            labels[i] = 'Accelerated H2 Deployment, Accelerated Retirement'
    labels = labels[1:]
    #add the legend underneath the plots
    fig.legend(handles, labels,ncol=3)
    #fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0, 0), fontsize='small', ncol=8)
    #set the layout to be tight
    #fig.tight_layout(rect=[0, 0.1, 1, 1])  # Adjust the bottom margin to make space for the legend


    #remove right and top spines
    for a in ax.flat:
        a.spines['right'].set_visible(False)
        a.spines['top'].set_visible(False)
        #set x limits 
        a.set_xlim([2023, 2060])

    #set y limits
    ax[0,0].set_ylim([0, 125])
    ax[0,1].set_ylim([0, 4.5])
    ax[1,0].set_ylim([0, 200])
    ax[1,1].set_ylim([0, 13000])

    plt.savefig('Figures\Figure_2_Scenario_Plots.svg', dpi=300, bbox_inches='tight')
    plt.show()
    
    return results_by_scenario

def axes_plot(axes, results_by_scenario, colours,column_name,lowest_scenario,order,title):
    
    
    for n in range(1, 8):
        total_results = results_by_scenario[n]['total']
        axes.plot(total_results['Year'], total_results[column_name], color=colours[n-1], label=f'Scenario {n}', linewidth=2)
        axes.set_title(title)
        axes.set_xlabel('Year')
        axes.set_ylabel(title)

    #add fill between to ax[0, 0] for the range of scenarios, including changes because of overlapping scenarios where required

    #order for fill between is not 1-7

    if column_name == 'H2 Demand (Mt/yr)':
        axes.set_ylabel('Hydrogen Use (Mt H\u2082/yr)')
        #find point where scenario 6 and scenario 1 cross

    for n in range(1, 8):
        scenario = order[n-1]
        
        total_results_n = results_by_scenario[scenario]['total']
     
        if n == 1:
            pass
            #axes.fill_between(total_results_n['Year'], 0, 
            #                        total_results_n[column_name], alpha=0.3, color=colours[scenario-1])
                
        elif n < 7 or column_name in ('Cumulative Emissions (GtCO2)', 'Annual Emissions (GtCO2/yr)'):
            previous_scenario = order[n-2]
            total_results_n_1 = results_by_scenario[previous_scenario]['total']
            #axes.fill_between(total_results_n['Year'], total_results_n[column_name], 
            #                        total_results_n_1[column_name], alpha=0.3, color=colours[scenario-1])            
        else:
            axes.plot(total_results_n['Year'], total_results_n[column_name], color=colours[scenario-1], label=f'Scenario {scenario}', linewidth=2)

    axes.plot(results_by_scenario[2]['total']['Year'], results_by_scenario[2]['total'][column_name], color=colours[2-1], label=f'Scenario {2}', linewidth=2)
    #for the first scenario, add shading to show the contributions from steel, ammonia and methanol individually
    hatch_patterns = {
        'steel': '///',
        'ammonia': '...',
        'methanol': 'xxx'
    }

    steel_results = results_by_scenario[lowest_scenario]['steel']
    ammonia_results = results_by_scenario[lowest_scenario]['ammonia'] 
    methanol_results = results_by_scenario[lowest_scenario]['methanol']

    #change from fill between to line

    axes.plot(steel_results['Year'], steel_results[column_name], color=colours[lowest_scenario-1], label='Steel', linewidth=1,linestyle='--')
    axes.plot(ammonia_results['Year'], ammonia_results[column_name] + steel_results[column_name], color=colours[lowest_scenario-1], label='Ammonia', linewidth=1,linestyle='--')
    axes.plot(methanol_results['Year'], methanol_results[column_name] + steel_results[column_name] + ammonia_results[column_name], color=colours[lowest_scenario-1], label='Methanol', linewidth=1,linestyle='--')

    """"
    axes.fill_between(steel_results['Year'], 0, 
                                steel_results[column_name], 
                                alpha=0.1, color=colours[lowest_scenario-1], label='Steel',hatch=hatch_patterns['steel']
                                )
    axes.fill_between(ammonia_results['Year'], steel_results[column_name],
                                ammonia_results[column_name] +
                                steel_results[column_name], 
                                alpha=0.1, color=colours[lowest_scenario-1], label='Ammonia', hatch=hatch_patterns['ammonia']
                                )
    axes.fill_between(methanol_results['Year'],
                                steel_results[column_name] + 
                                ammonia_results[column_name],
                                methanol_results[column_name] +
                                steel_results[column_name] +
                                ammonia_results[column_name], 
                                alpha=0.1, color=colours[lowest_scenario-1], label='Methanol', hatch=hatch_patterns['methanol']
                                )
    """
    return axes
    #combine the results of the three sectors into one dataframe
    
def sobol_analysis(iterations):

    for values,sector in zip([ values_methanol,values_ammonia,values_steel], [ 'Methanol','Ammonia','Steel']):
        #run sobol analysis for each sector
        
        Sobol_Analysis.run_sobol_analysis(values, 'CE', sector,iterations)
        print(f'Sobol analysis for {sector} completed with {iterations} iterations.')

    pass

def sobol_plotting(variable):
    """
    Plot the results of the Sobol analysis.
    """
    #read in the sobol results
    steel_sobol = pd.read_csv('Data/Sobol/sobol_results_'+variable+'Steel.csv')
    ammonia_sobol = pd.read_csv('Data/Sobol/sobol_results_'+variable+'Ammonia.csv')
    methanol_sobol = pd.read_csv('Data/Sobol/sobol_results_'+variable+'Methanol.csv')

    #add sector column to the dataframes
    steel_sobol['Sector'] = 'Steel'
    ammonia_sobol['Sector'] = 'Ammonia'
    methanol_sobol['Sector'] = 'Methanol'

    #add column name to unamed column
    steel_sobol.rename(columns={'Unnamed: 0': 'Variable'}, inplace=True)
    ammonia_sobol.rename(columns={'Unnamed: 0': 'Variable'}, inplace=True)
    methanol_sobol.rename(columns={'Unnamed: 0': 'Variable'}, inplace=True)

    #combine the dataframes
    sobol_results = pd.concat([steel_sobol, ammonia_sobol, methanol_sobol], ignore_index=True)
    #save the combined results to csv
    sobol_results.to_csv('Data/Sobol/sobol_results'+variable+'Combined.csv', index=False)

    sobol_results.rename(columns={'': 'Variable'})

    df = sobol_results.copy()

    variables = df['Variable'].unique()
    sectors = df['Sector'].unique()

    # Bar positioning
    x = np.arange(len(variables))
    bar_width = 0.25

    # Set up plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Colors per sector
    colors = {'Steel': '#8dd3c7', 'Ammonia': '#ffffb3', 'Methanol': '#bebada'}

    # Plot each sector
    for i, sector in enumerate(sectors):
        sector_data = df[df['Sector'] == sector].set_index('Variable').reindex(variables)
        offsets = x + (i - 1) * bar_width  # center around x
        ax.bar(offsets, sector_data['ST'], bar_width,
            yerr=sector_data['ST_conf'],
            label=sector,
            color=colors[sector],
            capsize=5)

    #change the x ticks to be the variable names
    ax.set_xticks(x)
    ax.set_xticklabels(variables, rotation=45, ha='right',fontsize=11)
    ax.set_ylim(0,1.3)
    ax.set_ylabel('Total Sobol Index',fontsize=12)
    ax.set_xlabel('Variable',fontsize=12)
    ax.legend(title='Sector')
    #remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig('Data/Sobol/sobol_results'+variable+'2Plot.svg', dpi=300)
    plt.show()

    return

def fig_4_contour_plots(sector,variable1,variable2,divisions,divisions2):
    results = []

    DRI_processed = pd.read_csv('Data/Model Data/DRI_Data.csv')
    BF_processed = pd.read_csv('Data/Model Data/BF_Data.csv')
    Ammonia_processed = pd.read_csv('Data/Model Data/Ammonia_Data.csv')
    Methanol_processed = pd.read_csv('Data/Model Data/Methanol_Data.csv')

    if sector == 'Steel':

        base_values = {'Start Capacity (Mt/yr)': 2.5, #small range as based on current projects
                        'Growth Rate (%)': 0.2, # range between current growth rate and unrealistic unconventional growth rate
                        'Demand (Mt/yr)': 1890, # range between current demand and maximum possible demand
                        'Lifetime (years)': 18, 
                        'Lifetime DRI (years)': 25,#SD of BF lifetime
                        'Recycling Rate (%)': 0.45, #range between current recycling rate and maximum possible recycling rate
                        'Start Year': 2024    #Small range for uncertainty as based on current projects                                                                      
                        }
        
        varied_steel = {
                        'Start Capacity (Mt/yr)': [2.5, 5], #small range as based on current projects
                        'Growth Rate (%)': [0.05, 1.5], # range between current growth rate and unrealistic unconventional growth rate
                        'Demand (Mt/yr)': [1890, 2500], # range between current demand and maximum possible demand
                        'Lifetime (years)': [10, 25], 
                        'Lifetime DRI (years)': [10, 40],#SD of DRI lifetime
                        'Recycling Rate (%)': [0.3, 0.7], #range between current recycling rate and maximum possible recycling rate
                        'Start Year': [2026, 2027]    #Small range for uncertainty as based on current projects                                                                      
                        }
        
        #range for variable1 and variable2

        variable1_range = np.linspace(varied_steel[variable1][0], varied_steel[variable1][1], divisions)
        variable2_range = np.linspace(varied_steel[variable2][0], varied_steel[variable2][1], divisions2)

        print('var range',variable2_range)
        
        for var_1 in variable1_range:
            #edit the base values with the variable1 value
            scenario_values = base_values.copy()
            scenario_values[variable1] = var_1
            for var_2 in variable2_range:
                #edit the base values with the variable2 value
                scenario_values[variable2] = var_2
                #run the steel scenario with the edited values
                result = Steel_Scenario.steel_scenarios(BF_processed,DRI_processed,
                                                        yearmin=2023, 
                                                        yearmax=2050,
                                                        low_demand=scenario_values['Demand (Mt/yr)'],
                                                        high_demand=2500,
                                                        recycling_rate=scenario_values['Recycling Rate (%)'],
                                                        gr_low=scenario_values['Growth Rate (%)'], 
                                                        gr_high=0.4, 
                                                        lifetime_low_BF=10, 
                                                        lifetime_standard_BF=scenario_values['Lifetime (years)'], 
                                                        lifetime_low_DRI = 17, 
                                                        lifetime_standard_DRI=scenario_values['Lifetime DRI (years)'],
                                                        lifetimelow_SD=5,
                                                        start_capacity=scenario_values['Start Capacity (Mt/yr)'],
                                                        start_recycled=420,
                                                        start_year=scenario_values['Start Year'],
                                                        lifetime_SD=1,
                                                        contour=True)
            
                #get the cumulative emissions for the scenario by 2050

                H2_demand = result.loc[result['Year']<=2050,'Annual Emissions (MtCO2/yr)'].sum()
                
                results.append({variable1: var_1,variable2: var_2,'Cumulative Emissions (MtCO2e)': H2_demand})

    elif sector == 'Ammonia':

        base_values =  {
            'Start Capacity (Mt/yr)': 0.2, #small range as based on current projects
            'Growth Rate (%)': 0.4, # range between current growth rate and unrealistic unconventional growth rate
            'Demand (Mt/yr)': 184, # range between current demand and IEA Stated Policies Scenario
            'Lifetime (years)': 25,
            'Start Year': 2024    #Small range for uncertainty as based on current projects
            }
        
        varied_ammonia = {
                        'Start Capacity (Mt/yr)': [2.5, 5], #small range as based on current projects
                        'Growth Rate (%)': [0.05, 1.5], # range between current growth rate and unrealistic unconventional growth rate
                        'Demand (Mt/yr)': [184, 253], # range between current demand and maximum possible demand
                        'Lifetime (years)': [10, 40], 
                        'Start Year': [2020, 2021]    #Small range for uncertainty as based on current projects                                                                      
                        }
        #range for variable1 and variable2
        variable1_range = np.linspace(varied_ammonia[variable1][0], varied_ammonia[variable1][1], divisions)
        variable2_range = np.linspace(varied_ammonia[variable2][0], varied_ammonia[variable2][1], divisions2)

        for var_1 in variable1_range:
            scenario_values = base_values.copy()
            scenario_values[variable1] = var_1
            for var_2 in variable2_range:
                scenario_values[variable2] = var_2
                #run the ammonia scenario with the edited values
                result = Ammonia_Scenario.ammonia_scenarios(Ammonia_processed,
                                                            yearmin=2023, 
                                                            yearmax=2050,
                                                            low_demand=scenario_values['Demand (Mt/yr)'],
                                                            high_demand=250,
                                                            gr_low=scenario_values['Growth Rate (%)'], 
                                                            gr_high=0.6, 
                                                            lifetime_standard_Ammonia=scenario_values['Lifetime (years)'],
                                                            lifetime_low_Ammonia=20,
                                                            lifetimelow_SD=5,
                                                            start_capacity=scenario_values['Start Capacity (Mt/yr)'],
                                                            start_year=scenario_values['Start Year'],
                                                            lifetime_SD=1,
                                                            contour=True)
            
                #get the cumulative emissions for the scenario by 2050
                H2_demand = result.loc[result['Year']<=2050,'Annual Emissions (MtCO2/yr)'].sum()
                
                results.append({variable1: var_1,variable2: var_2,'Cumulative Emissions (MtCO2e)': H2_demand})


    elif sector == 'Methanol':

        base_values =  {
            'Start Capacity (Mt/yr)': 0.2, #small range as based on current projects
            'Growth Rate (%)': 0.4, # range between current growth rate and unrealistic unconventional growth rate
            'Demand (Mt/yr)': 111, # range between current demand and IEA Stated Policies Scenario
            'Lifetime (years)': 25,
            'Start Year': 2024    #Small range for uncertainty as based on current projects
            }
        
        varied_methanol = {
                        'Start Capacity (Mt/yr)': [2.5, 5], #small range as based on current projects
                        'Growth Rate (%)': [0.05, 1.5], # range between current growth rate and unrealistic unconventional growth rate
                        'Demand (Mt/yr)': [111, 500], # range between current demand and maximum possible demand
                        'Lifetime (years)': [10, 40], 
                        'Start Year': [2020, 2021]    #Small range for uncertainty as based on current projects                                                                      
                        }
        
        #range for variable1 and variable2
        variable1_range = np.linspace(varied_methanol[variable1][0], varied_methanol[variable1][1], divisions)
        variable2_range = np.linspace(varied_methanol[variable2][0], varied_methanol[variable2][1], divisions2)

        

        for var_1 in variable1_range:
            scenario_values = base_values.copy()
            scenario_values[variable1] = var_1
            for var_2 in variable2_range:
                scenario_values[variable2] = var_2
                #run the ammonia scenario with the edited values
                result = Methanol_Scenario.methanol_scenarios(Methanol_processed,
                                                            yearmin=2023, 
                                                            yearmax=2050,
                                                            low_demand=scenario_values['Demand (Mt/yr)'],
                                                            high_demand=250,
                                                            gr_low=scenario_values['Growth Rate (%)'], 
                                                            gr_high=scenario_values['Growth Rate (%)'], 
                                                            lifetime_standard_methanol=scenario_values['Lifetime (years)'],
                                                            lifetime_low_methanol=20,
                                                            lifetimelow_SD=5,
                                                            start_capacity=scenario_values['Start Capacity (Mt/yr)'],
                                                            start_year=scenario_values['Start Year'],
                                                            lifetime_SD=1,
                                                            contour=True)
            
                #get the cumulative emissions for the scenario by 2050
                H2_demand = result.loc[result['Year']<=2050,'Annual Emissions (MtCO2/yr)'].sum()
                
                results.append({variable1: var_1,variable2: var_2,'Cumulative Emissions (MtCO2e)': H2_demand})
        
    #convert results to dataframe
    results_df = pd.DataFrame(results)
    #save the results to csv
    results_df.to_csv(f'Data/Output Data/{sector}_{variable1}_{variable2}_contour_results.csv', index=False)

    return results_df

def plot_contour_results(contour_results,column_name,index_name,plot_title,cmap,sector,var1flipped=False,
                         var2flipped=False,divisionsx=10,divisionsy=10,carbon_budget=40000,yline=40,xline=20,colour='white'):

    
    #if growth rate multiply by 100 to get percentage
    if column_name == 'Growth Rate (%)':
        contour_results[column_name] = contour_results[column_name] * 100

    if index_name == 'Recycling Rate (%)':
        contour_results['Proportion Recycled Steel (%)'] = contour_results[index_name]
        index_name = 'Proportion Recycled Steel (%)'
        contour_results[index_name] = contour_results[index_name] * 100

    # Pivot the DataFrame to get the desired format for contour plotting
    contour_results_pivot = contour_results.pivot(index=index_name, columns=column_name, values=plot_title)

    #adjust values to be % of cumulative emission budget
    contour_results_pivot = contour_results_pivot / carbon_budget *100
    
    print(contour_results_pivot) 

    sector_dict = {
        'Steel': values_steel,
        'Ammonia': values_ammonia,
        'Methanol': values_methanol
    }
    x_min = contour_results[column_name].min()
    x_max = contour_results[column_name].max()
    y_min = contour_results[index_name].min()
    y_max = contour_results[index_name].max()

    print(f'X min: {x_min}, X max: {x_max}, Y min: {y_min}, Y max: {y_max}')

    delta_x = (x_max - x_min) / (divisionsx-1)  # Assuming 20 intervals

    if index_name == 'Lifetime (years)':
        delta_y = 1  #because years always increase by 1
    else:
        delta_y = (y_max-y_min) / divisionsy  

    #print(f'Delta X: {delta_x}, Delta Y: {delta_y}')

    if var1flipped:
        x = np.arange(x_max,x_min,-delta_x)
    else:
        x = np.arange(x_min,x_max+delta_x, delta_x)
    if var2flipped:
        y = np.arange(y_max,y_min, -delta_y)
    else:
        y = np.arange(y_min,y_max+delta_y, delta_y)
        
    X,Y =np.meshgrid(x,y)
    print(f'X: {X}, Y: {Y}')
    #decide on levels for contour plot



    min_value=100
    max_value=250
    #define levels at intervales of 25% between min and max
    step = 25 
    levels_rounded = np.arange(min_value, max_value+step, step)
    print(f'Levels for contour plot: {levels_rounded}')


    """ Plot contour results """

    fig,ax = plt.subplots(1,2, figsize=(20, 10))



    a = np.array([[min_value,max_value]])


    img = plt.imshow(a, cmap=cmap)
    plt.gca().set_visible(False)
    cax = fig.add_axes([0.49, 0.11, 0.02, 0.77])  # [left, bottom, width, height]
    cbar = plt.colorbar(orientation="vertical", cax=cax,ax=ax[1])
    #change width of colorbar
    #cbar.ax.set_aspect(40)

    filled = ax[0].contourf(X,Y,contour_results_pivot.values, levels=200, cmap=cmap,vmin=min_value, vmax=max_value)
    lines = ax[0].contour(X,Y,contour_results_pivot.values, levels=levels_rounded, 
                        colors=colour, linewidths=1.5, linestyles = 'dashed')
    filled.set_edgecolor("face")

    n=0
    for level in levels_rounded:
        cbar.ax.axhline(level, c=colour, linestyle='--', label=f'{level} MtCO2e', linewidth=1.5)
        n+=1
    cbar.set_ticks(levels_rounded)
    cbar.ax.set_yticklabels([f'{int(level)}' for level in levels_rounded])
    cbar.set_label('Percent of sector 1.5\N{DEGREE SIGN}C Carbon Budget ('+ str(carbon_budget/1000)+' Gt CO\u2082e)', rotation=270, labelpad=20)

    #invert the y axis
    #ax[0].invert_yaxis()

    ax[0].set_xlabel(column_name)
    ax[0].set_ylabel(index_name)
    ax[0].axhline(xline,linestyle='dashdot',c='white')
    ax[0].axvline(yline,linestyle='dashdot',c='white')
    plt.savefig(sector+"contour.svg", dpi=300)
    plt.show()
            

"""clean data and ensure in the format required"""
DRI, BF, Ammonia, Methanol = Clean_Data.clean_data(DRI, BF, Plants, Methanol, Ammonia, region_mapping)


""" Run model to get the mean results based on monte carlo simulations"""
#produce_results(iterations=200)

""" Produce Results for Figure 1"""
#sankey_formatting()

#sankeymatic_formatting('Ammonia_Sankey')
#sankeymatic_formatting('Methanol_Sankey')
#sankeymatic_formatting('Steel_Sankey')
#sankeymatic_formatting('Combined_Sankey')

""" Produce Results for Figure 2"""

#figure_2_scenario_plots()

""" Run Sobol Analysis for Figure 3"""
#sobol_analysis(2**11)

""" Plot Sobol Results"""

sobol_plotting('CE')


def plot_all_contour(run=False):

    if run == True:
        """ Produce Contour Plots for Figure 4"""
        contour_results = fig_4_contour_plots('Methanol', 'Lifetime (years)', 'Growth Rate (%)', 31,15)
        contour_results = fig_4_contour_plots('Ammonia', 'Lifetime (years)', 'Growth Rate (%)', 31,15)
        contour_results = fig_4_contour_plots('Steel', 'Lifetime (years)', 'Growth Rate (%)', 16,15)
        contour_results = fig_4_contour_plots('Steel', 'Recycling Rate (%)', 'Growth Rate (%)', 20,15)


    #plot the contour results for Methanol
    contour_results = pd.read_csv('Data/Output Data/Methanol_Lifetime (years)_Growth Rate (%)_contour_results.csv')
    plot_contour_results(contour_results, 'Growth Rate (%)', 'Lifetime (years)',  'Cumulative Emissions (MtCO2e)', plt.cm.Reds,'Methanol',
                        var1flipped=False,var2flipped=False,divisionsx=15,divisionsy=21,carbon_budget=1800,yline=40,xline=30,colour = '#7993fcff')

    #plot for ammonia
    contour_results = pd.read_csv('Data/Output Data/Ammonia_Lifetime (years)_Growth Rate (%)_contour_results.csv')
    plot_contour_results(contour_results, 'Growth Rate (%)', 'Lifetime (years)',  'Cumulative Emissions (MtCO2e)', plt.cm.Greens,'Ammonia',
                            var1flipped=False,var2flipped=False,divisionsx=20,divisionsy=31,carbon_budget=4800,yline=40,xline=30,colour = '#ff7d0cff')

    #plot steel lifetime and growth rate
    contour_results = pd.read_csv('Data/Output Data/Steel_Lifetime (years)_Growth Rate (%)_contour_results.csv')
    plot_contour_results(contour_results, 'Growth Rate (%)', 'Lifetime (years)',  'Cumulative Emissions (MtCO2e)',
                            plt.cm.Blues,'Steel',var1flipped=False,var2flipped=False,divisionsx=20,divisionsy=16,carbon_budget=27000,yline=20,xline=17,colour = '#ff393bff')

    #plot the contour results for Steel
    contour_results = pd.read_csv('Data/Output Data/Steel_Recycling Rate (%)_Growth Rate (%)_contour_results.csv')
    plot_contour_results(contour_results,'Growth Rate (%)', 'Recycling Rate (%)',  'Cumulative Emissions (MtCO2e)', 
                        plt.cm.Blues,'Steel',var1flipped=False,var2flipped=False,divisionsx=20,divisionsy=9,carbon_budget=27000,yline=20,xline=55,colour = '#ff393bff')
    

#plot_all_contour(run=True)