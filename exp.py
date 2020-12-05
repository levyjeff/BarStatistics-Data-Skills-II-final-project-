'''
Add some data
'''
import pandas as pd
import os

# Unemployment rates
if os.path.isfile(path+ r'\unemp_rates.csv') == True:
    pass
else:
    unemp_rates = pd.read_excel('https://www.ers.usda.gov/webdocs/DataFiles/48747/Unemployment.xls?v=4751.8', header=7)
    unemp_rates.to_csv('unemp_rates.csv')

unemp = pd.read_csv('unemp_rates.csv')[['area_name', 'Unemployment_rate_2015', 'Unemployment_rate_2016', 'Unemployment_rate_2017', 'Unemployment_rate_2018']]
unemp = unemp[unemp['area_name'].isin(z['Jurisdiction'])].reset_index(drop=True)


# Educational attainment

if os.path.isfile(path+ r'\ed_attainment.csv') == True:
    pass
else:
    ed = pd.read_excel('https://www.ers.usda.gov/webdocs/DataFiles/48747/Education.xls?v=4751.8', header=4)
    ed.to_csv('ed_attainment.csv')
ed = pd.read_csv('ed_attainment.csv')
ed = ed[ed['Area name'].isin(z['Jurisdiction'])].reset_index(drop=True)
# Get rid of duplicate Washington, D.C.
ed = ed.drop_duplicates(subset='Area name', inplace=False)

ed = ed[['Area name', 'Less than a high school diploma, 2014-18',
       'High school diploma only, 2014-18',
       "Some college or associate's degree, 2014-18",
       "Bachelor's degree or higher, 2014-18",
       'Percent of adults with less than a high school diploma, 2014-18',
       'Percent of adults with a high school diploma only, 2014-18',
       "Percent of adults completing some college or associate's degree, 2014-18",
       "Percent of adults with a bachelor's degree or higher, 2014-18"]]

