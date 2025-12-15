import numpy as np
import pandas as pd
import os
import pycountry 


def clean_data(DRI, BF, Plants,Methanol, Ammonia,region_mapping):

    DRI = DRI.copy()
    BF = BF.copy()
    Methanol = Methanol.copy()
    Ammonia = Ammonia.copy()

    Country_mapping = dict(Plants[['Plant ID', 'Country']].values)
    Region_mapping = dict(Plants[['Plant ID', 'Region']].values)

    DRI['Country'] = DRI['GEM Plant ID'].map(Country_mapping)
    BF['Country'] = BF['GEM Plant ID'].map(Country_mapping)
    # Add the region to the DRI and BF dataframes
    DRI['Region'] = DRI['GEM Plant ID'].map(Region_mapping)
    BF['Region'] = BF['GEM Plant ID'].map(Region_mapping)

    #assign region to the methanol data
    Methanol['Age'] = 2023 - Methanol['Year']
    #remove rows where production is 0
    Methanol = Methanol[Methanol['Production (Mt/yr)'] > 0]

    Methanol['Production (Mt/yr)'] = Methanol['Production (Mt/yr)']/1000
    Methanol['Route'] =  'Methanol-'+ Methanol['Route']


    #data is provided as average age of plants, so need to estimate the actual age of the plants
    new_ammonia = pd.DataFrame()

    age_range = (1,40)

    print(len(Ammonia['Country'].unique()), 'countries in the ammonia data')

    for index,row in Ammonia.iterrows():
        if row['Number of plants'] == 1:
            new_ammonia = new_ammonia._append(row)
            row['Year'] = 2023 - row['Age']
        else:
            av_age_age = row['Age']
            no_of_plants = row['Number of plants']
            #calculate the age of the plants
            ages = np.random.randint(age_range[0], age_range[1], size=no_of_plants)
            #scale to average age
            ages = ages * (av_age_age / np.mean(ages))
            #round ages to nearest integer, change to int
            ages = np.round(ages).astype(int)
            n=1
            for age in ages:
                new_row = row.copy()
                new_row['Age'] = age
                new_row['Plant Number'] = n
                n += 1
                new_row['Production (Mt/yr)'] = row['Production Capacity (Mt/yr)'] / no_of_plants
                new_row['Year'] = 2023 - age
                new_ammonia = new_ammonia._append(new_row, ignore_index=True)

    #remove spaces from values in the 'Country' column
    new_ammonia['Country'] = new_ammonia['Country'].str.replace(' ', '')
    print(len(new_ammonia['Country'].unique()), 'countries in the ammonia data')
    #apply the function to the country column
    new_ammonia['Country2'] = new_ammonia['Country'].apply(convert_country_code)
    print(len(new_ammonia['Country2'].unique()), 'countries in the ammonia data')

    BF['Country2'] = BF['Country'].apply(convert_country_code)
    DRI['Country2'] = DRI['Country'].apply(convert_country_code)
    Methanol['Country2'] = Methanol['Country'].apply(convert_country_code)

    new_ammonia.to_csv('Data/Model Data/Ammonia_Data.csv', index=False)

    #check all values in the country column are 2 letter country codes
    for df in [new_ammonia, BF, DRI, Methanol]:
        if not all(df['Country2'].str.len() == 2):
            print(f"Error: Not all values in the 'Country' column are 2 letter country codes")
            exit()
        else:
            print(f"All values in the 'Country' column are 2 letter country codes")

    #check that all countries are in the region country mapping
    for df in [new_ammonia, BF, DRI, Methanol]:
        for country in df['Country2'].unique():
            if country not in region_mapping['Country'].values:
                print(f"Error: {country} not found in region country mapping")
                exit()

    new_ammonia['Region'] = new_ammonia['Country2'].map(region_mapping.set_index('Country')['UN'])
    BF['Region'] = BF['Country2'].map(region_mapping.set_index('Country')['UN'])
    DRI['Region'] = DRI['Country2'].map(region_mapping.set_index('Country')['UN'])
    Methanol['Region'] = Methanol['Country2'].map(region_mapping.set_index('Country')['UN'])

    #remove all columns other than the ones needed
    DRI = DRI[['Country','Country2', 'Region', 'GEM Plant ID','GEM Unit ID','Year', 'Production (Mt/yr)','Age','Reductant']]

    DRI['Production (Mt/yr)'] = DRI['Production (Mt/yr)']/1000
    BF['Production (Mt/yr)'] = BF['Production (Mt/yr)'].astype(float)
    BF = BF[['Country','Country2', 'Region', 'GEM Plant ID','GEM Unit ID','Year', 'Production (Mt/yr)','Age']]
    Methanol = Methanol[['Country','Country2', 'Region', 'SITE','Route','Year', 'Production (Mt/yr)','Age']]        

    DRI.to_csv('Data/Model Data/DRI_Data.csv', index=False)
    BF.to_csv('Data/Model Data/BF_Data.csv', index=False)
    Methanol.to_csv('Data/Model Data/Methanol_Data.csv', index=False)
    new_ammonia.to_csv('Data/Model Data/Ammonia_Data.csv', index=False)

    return DRI, BF, new_ammonia, Methanol

#for all country columns, convert to 2 letter country code
def convert_country_code(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2
        
    except LookupError:
        try: 
            return pycountry.countries.search_fuzzy(country_name)[0].alpha_2
        except LookupError:
            if country_name == 'United States of America':
                return 'US'
            elif country_name == 'UNITEDKINGDOM':
                return 'GB'
            elif country_name == 'NEWZEALAND':
                return 'NZ'
            # If the country name is not found, return the original name or a placeholder
            return country_name
    






