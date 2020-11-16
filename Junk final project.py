### SPECIFIC TO 2019 ###

import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

url = 'https://thebarexaminer.org/2019-statistics/persons-taking-and-passing-the-2019-bar-examination/#'
path = r'C:\Users\bethk\Desktop\Data_Skills_II'

# Approach derived from Jeff Levy's Week 8 Lecture 2 from Spring 2020
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')
table = soup.find('table')

# Create list with data
unparsed_rows = []
for row in table.find_all('tr'):
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

# Create dataframe
df19 = pd.DataFrame(unparsed_rows, columns = ['Number', 'Jurisdiction', 'Month', 'Takers', 'Passers', 'Pass_Rate'])
del df19['Number']
df19 = df19.astype(dtype={'Takers':int, 'Passers':int})
df19['Pass_Rate'] = df19['Passers']/df19['Takers']



year_locs = [1]
for x in range(len(pov_rates)):
    for year in range(2015, 2020):
        if pov_rates[2019][x] == year:
            year_locs.append(x)
year_locs

'''
Generate lawyer discipline dataframes
'''

############## NEXT STEP IS TO GENERALIZE EVERYTHING EXCEPT NEW YORK ROW ADJUSTMENTS

# Read in the PDF as a CSV
# pip install tabula-py
import tabula
file = 'https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/2018-chart-1-part-a.pdf'
tabula.convert_into(file, 'discipline_2017.csv', output_format='csv', pages='5-7')
dis17 = pd.read_csv('discipline_2017.csv', encoding='cp1252')

# Adjust columns
dis17.columns=['Jurisdiction', 'Num_Lawyers', 'Num_Complaints', 'Central_Intake', 'Separate']
del dis17['Central_Intake']
del dis17['Separate']

# Rename New York rows, since divided into districts
for num in range(37, 47):
    dis17.loc[num][0] = 'New York'

# Remove rows if not state name
x = dis17[dis17['Jurisdiction'].isin(df17['Jurisdiction'])].reset_index()
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

# Remove rows with only 0s and consolidate New York rows
x = x[(x['Num_Lawyers'] != 0) & (x['Num_Complaints'] != 0)]
ny_lawyers = x.loc[x['Jurisdiction'] == 'New York'].sum()[1]
ny_complaints = x.loc[x['Jurisdiction'] == 'New York'].sum()[2]
ny = pd.DataFrame([['New York', ny_lawyers, ny_complaints]], columns=['Jurisdiction', 'Num_Lawyers', 'Num_Complaints'])
x = x[x['Jurisdiction'] != 'New York']
x = x.append(ny).sort_values('Jurisdiction').reset_index()
x['Complaints_Per_Lawyer'] = x['Num_Complaints']/x['Num_Lawyers']
del x['index']

# Merge with 2017 dataframe
df17 = pd.merge(df17, x)
df17
