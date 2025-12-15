import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

#Importing datasets required
lifetimes = pd.read_csv('Data/Input Data/lifetimes.csv')
emissions_factors = pd.read_csv('Data/Input Data/Emissions Factors.csv')
emissions_factors['EF'] = emissions_factors['EF'].astype(float)

def committed_capacities2(df, process,lifetime,SD,min_lifetime,max_lifetime,contour):
    if process == 'Methanol':
        df['EF'] = 0.0
        #assign methanol emissions based on the route
        for route in df['Route'].unique():
            if route in emissions_factors['Process'].values:
                df.loc[df['Route'] == route,'EF'] = emissions_factors.loc[emissions_factors['Process'] == route, 'EF'].values[0]
            else:
                df.loc[df['Route'] == route,'EF'] = emissions_factors.loc[emissions_factors['Process'] == 'Methanol-NATURAL GAS', 'EF'].values[0]

    elif process == 'DRI':
        #assign all but coal to NG
        df.loc[df['Reductant']!='coal','EF'] = emissions_factors.loc[emissions_factors['Process'] == 'NG-DRI', 'EF'].values[0]
        df.loc[df['Reductant']=='coal','EF'] = emissions_factors.loc[emissions_factors['Process'] == 'Coal-DRI', 'EF'].values[0]


    elif process == 'BF':
        bf_ef = emissions_factors.loc[emissions_factors['Process'] == 'BF'].copy()
        list_of_countries = bf_ef['Country'].unique().tolist()
        df['EF'] = bf_ef.loc[bf_ef['Country'] == 'Global', 'EF'].values[0]
        for country in list_of_countries:
            if country != 'Global':
                df.loc[df['Country'] == country,'EF'] = bf_ef.loc[bf_ef['Country'] == country, 'EF'].values[0]

    elif process == 'Ammonia':
        df['EF'] = emissions_factors.loc[emissions_factors['Process'] == 'NG-Ammonia', 'EF'].values[0]
        #if the country is China, then assign the emissions factor for China-Ammonia
        df.loc[df['Country'] == 'CHINA','EF'] = emissions_factors.loc[emissions_factors['Process'] == 'China-Ammonia', 'EF'].values[0]

    #if production is not a number, then set to 0
    df['Production (Mt/yr)'] = df['Production (Mt/yr)'].replace('#VALUE!', 0)
    df['Production (Mt/yr)'] = df['Production (Mt/yr)'].astype(float)
    df['Current Emissions (MtCO2/yr)'] = df['Production (Mt/yr)'] * df['EF']
    df['Current Emissions (MtCO2/yr)'] = df['Current Emissions (MtCO2/yr)'].astype(float)

    df['Age'] = df['Age'].astype(int)

    if contour == False:
        #define normal distribution for the lifetimes
        sector_lifetime = stats.truncnorm.rvs((min_lifetime - lifetime) / SD, (max_lifetime - lifetime) / SD, loc=lifetime, scale=SD,size=len(df))
        #sector_lifetime = np.random.normal(loc=lifetime, scale=SD, size=len(df))
        #add the retirement year to the DRI and BF dataframes
        df['Retirement Year'] = 2023 + (sector_lifetime-df['Age'])

        #if the retirement year is before 2023, then assume reinvestment has occurred and add another rotation
        while df['Retirement Year'].min() < 2023:
            if lifetime >1:
                df['Retirement Year'] = np.where(df['Retirement Year'] < 2023, df['Retirement Year'] + 
                                                np.random.randint(5,lifetime),
                                                df['Retirement Year']).round().astype(int)
            else:
                df['Retirement Year'] = np.where(df['Retirement Year'] < 2023, 2023,
                                                df['Retirement Year']).round().astype(int)

    if contour == True:
        sector_lifetime = lifetime

        df['Retirement Year'] = 2023 + (sector_lifetime-df['Age'])

        #if the retirement year is before 2023, then assume reinvestment has occurred and add another rotation
        while df['Retirement Year'].min() < 2023:
                df['Retirement Year'] = np.where(df['Retirement Year'] < 2023, df['Retirement Year'] + 
                                                lifetime,
                                                df['Retirement Year']).round().astype(int)

    return df


def growth_capacity(process,assumption_df,gr,demand,ct0,start_year):
    #calculate the growth capacity for each new process using a logistic function

    #b = growth rate
    #c_max = maximum capacity
    #ct0 = initial capacity
    #t = number of time steps

    b = gr
    start_year = start_year
    cmax = demand
    ct0 = ct0
    t=100

    #initialise list with initial capacity
    c = [ct0]
    ct = ct0

    for i in range(t):
        ct = ct + b*ct*(1-ct/cmax)
        c.append(ct)

    #check demand reached
    if c[-1] < cmax-1:
        #print(f"Warning: {process} demand not reached")
        #print(c[-1], cmax)
        z=1

    #create dataframe with years and capacities
    years = np.arange(start_year, start_year+t+1)
    capacities = pd.DataFrame({'Year': years, 'Capacity (Mt/yr)': c})

    #save to csv with process name + growth_capacity.csv
    #capacities.to_csv(f'Data/Model Data/{process}_growth_capacity.csv', index=False)

    return capacities




