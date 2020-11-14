'''
Initial housekeeping
'''

import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
path = r'C:\Users\bethk\Desktop\Data_Skills_II\BarStatistics'

'''
Generate dataframes with bar exam data
'''

# Approach derived from Jeff Levy's Week 8 Lecture 2 from Spring 2020
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}

def make_table(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find('table')
    return(table)

def create_list(a_table):
    unparsed_rows = []
    for row in a_table.find_all('tr'):
        td_tags = row.find_all('td')
        unparsed_rows.append([val.text for val in td_tags])
# Remove first empty list, remove commas from integers, remove non-letters from Jurisdiction
    del unparsed_rows[0]
    for a_row in unparsed_rows:
        for a_num in [3,4]:
            a_row[a_num] = a_row[a_num].replace(',','')
            try:
                int(a_row[a_num])
            except ValueError:
                a_row[a_num] = 0
    for a_row in unparsed_rows:
        a_row[1] = a_row[1].replace('\t\t\t†', '')
        a_row[1] = a_row[1].replace('\t\t\t*', '')
        a_row[1] = a_row[1].rstrip()
    return(unparsed_rows)

def build_df(a_list):
    the_df = pd.DataFrame(a_list, columns = ['Number', 'Jurisdiction', 'Month', 'Takers', 'Passers', 'Pass_Rate'])
    del the_df['Number']
    the_df = the_df.astype(dtype={'Takers':int, 'Passers':int})
    the_df['Pass_Rate'] = the_df['Passers']/the_df['Takers']
    the_df = the_df[the_df['Month'] == 'Total February and July']
    del the_df['Month']
    return(the_df)

#def generate_df(url):
#    a_table = make_table(url)
#    a_list = create_list(a_table)
#    new_df = build_df(a_list)
#    return(new_df)

def generate_df(url):
    new_df = build_df(create_list(make_table(url)))
    return(new_df)

url_15 = 'https://thebarexaminer.org/statistics/2015-statistics/persons-taking-and-passing-the-2015-bar-examination/'
url_16 = 'https://thebarexaminer.org/statistics/2016-statistics/persons-taking-and-passing-the-2016-bar-examination/'
url_17 = 'https://thebarexaminer.org/statistics/2017-statistics/persons-taking-and-passing-the-2017-bar-examination/'
url_18 = 'https://thebarexaminer.org/statistics/2018-statistics/persons-taking-and-passing-the-2018-bar-examination/'
url_19 = 'https://thebarexaminer.org/2019-statistics/persons-taking-and-passing-the-2019-bar-examination/#'

df15 = generate_df(url_15)
df16 = generate_df(url_16)
df17 = generate_df(url_17)
df18 = generate_df(url_18)
df19 = generate_df(url_19)

# SAVE THESE DATAFRAMES AS CSVS SO THAT DO NOT NEED TO IMPORT EVERY TIME. USE TRY/EXCEPT OR ASSERT TO MAKE THE CODE SKIP OVER GENERATING IF CSVS ALREADY PRESENT IN PATH.

'''
Generate poverty rate dataframes
'''
pov_rates = pd.read_excel('https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-poverty-people/hstpov21.xlsx', header=3)

def get_pov(start, end):
    state_rate = []
    for a_num in range(start, end):
        state_rate.append([pov_rates[2019][a_num], pov_rates['Unnamed: 4'][a_num]])
    return(pd.DataFrame(state_rate, columns=['Jurisdiction', 'Poverty_Rate']))

pov15 = get_pov(266, 317)
pov16 = get_pov(213, 264)
pov17 = get_pov(160, 211)
pov18 = get_pov(54, 105)
pov19 = get_pov(1, 52)

'''
Merge bar exam and poverty rate dataframes
'''
# Note: this will drop US territories
df15 = pd.merge(df15, pov15)
df16 = pd.merge(df16, pov16)
df17 = pd.merge(df17, pov17)
df18 = pd.merge(df18, pov18)
df19 = pd.merge(df19, pov19)

#####################################

'''
Generate lawyer discipline dataframes
'''

############## NEXT STEP IS TO GENERALIZE EVERYTHING EXCEPT NEW YORK ROW ADJUSTMENTS

# Read in the PDF as a CSV
# pip install tabula-py
import tabula
file = 'https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/2018-chart-1-part-a.pdf'
tabula.convert_into(file, 'discipline_2018.csv', output_format='csv', pages='all')
dis18 = pd.read_csv('discipline_2018.csv', encoding='cp1252')

# Adjust columns
dis18.columns=['Jurisdiction', 'Num_Lawyers', 'Num_Complaints', 'Central_Intake', 'Separate']
del dis18['Central_Intake']
del dis18['Separate']

# Rename New York rows, since divided into districts
for num in range(37, 47):
    dis18.loc[num][0] = 'New York'

# Remove rows if not state name
x = dis18[dis18['Jurisdiction'].isin(df18['Jurisdiction'])].reset_index()
del x['index']

# Change numeric column types to integer and add complaints-per-lawyer ratio column
for col in x:
    if col != 'Jurisdiction':
        x[col] = x[col].replace([',', 'N', '\\*'],'', regex=True)
        for num in range(0, len(x)):
            try:
                int(x[col][num])
            except ValueError:
                x[col][num] = 0
x = x.astype(dtype={'Num_Lawyers':int, 'Num_Complaints':int})
x['Complaints_Per_Lawyer'] = x['Num_Complaints']/x['Num_Lawyers']

# Remove rows with only 0s and consolidate New York rows
x = x[(x['Num_Lawyers'] != 0) & (x['Num_Complaints'] != 0)]
ny_lawyers = x.loc[x['Jurisdiction'] == 'New York'].sum()[1]
ny_complaints = x.loc[x['Jurisdiction'] == 'New York'].sum()[2]
ny = pd.DataFrame([['New York', ny_lawyers, ny_complaints]], columns=['Jurisdiction', 'Num_Lawyers', 'Num_Complaints'])
x = x[x['Jurisdiction'] != 'New York']
x = x.append(ny).sort_values('Jurisdiction').reset_index()
del x['index']

# Merge with 2018 dataframe
df18 = pd.merge(df18, x)
df18
