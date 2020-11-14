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
