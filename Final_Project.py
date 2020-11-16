'''
Initial housekeeping
'''

import numpy as np
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import tabula
path = r'C:\Users\bethk\Desktop\Data_Skills_II\BarStatistics'
os.chdir(path)

'''
Generate dataframes with bar exam data
'''

# Create the dataframe-generating functions (approach derived from Jeff Levy's Spring 2020 Week 8 Lecture 2)
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

def generate_df(url):
    new_df = build_df(create_list(make_table(url)))
    return(new_df)

# Build the dataframes

pass_rate_dict = {2015:'https://thebarexaminer.org/statistics/2015-statistics/persons-taking-and-passing-the-2015-bar-examination/',
                  2016:'https://thebarexaminer.org/statistics/2016-statistics/persons-taking-and-passing-the-2016-bar-examination/',
                  2017:'https://thebarexaminer.org/statistics/2017-statistics/persons-taking-and-passing-the-2017-bar-examination/',
                  2018:'https://thebarexaminer.org/statistics/2018-statistics/persons-taking-and-passing-the-2018-bar-examination/',
                  2019:'https://thebarexaminer.org/2019-statistics/persons-taking-and-passing-the-2019-bar-examination/#'
}

for year in pass_rate_dict.keys():
    if os.path.isfile(path+f'\\pass_rates_{year}.csv') == True:
        pass
    else:
        pass_rate_df = generate_df(pass_rate_dict[year])
        pass_rate_df.to_csv(f'pass_rates_{year}.csv')

df15 = pd.read_csv('pass_rates_2015.csv')
df16 = pd.read_csv('pass_rates_2016.csv')
df17 = pd.read_csv('pass_rates_2017.csv')
df18 = pd.read_csv('pass_rates_2018.csv')
df19 = pd.read_csv('pass_rates_2019.csv')

# Can I consolidate this? Or should I not bother and make one big dataframe rather than a bunch of small ones?
del df15['Unnamed: 0']
del df16['Unnamed: 0']
del df17['Unnamed: 0']
del df18['Unnamed: 0']
del df19['Unnamed: 0']

'''
Generate poverty rate dataframes
'''

# Get poverty rates chart if not in path
if os.path.isfile(path+'\pov_rates.csv') == True:
    pass
else:
    pov_rates = pd.read_excel('https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-poverty-people/hstpov21.xlsx', header=3)
    pov_rates.to_csv('pov_rates.csv')
pov_rates = pd.read_csv('pov_rates.csv')

def get_pov(start, end):
    state_rate = []
    for a_num in range(start, end):
        state_rate.append([pov_rates['2019'][a_num], float(pov_rates['Unnamed: 4'][a_num])/100])
    return(pd.DataFrame(state_rate, columns=['Jurisdiction', 'Poverty_Rate']))

pov15 = get_pov(266, 317)
pov16 = get_pov(213, 264)
pov17 = get_pov(160, 211)
pov18 = get_pov(54, 105)
pov19 = get_pov(1, 52)

'''
Merge bar exam and poverty rate dataframes
'''

# Note: this will drop US territories, leaving only states and Washington, D.C.
df15 = pd.merge(df15, pov15)
df16 = pd.merge(df16, pov16)
df17 = pd.merge(df17, pov17)
df18 = pd.merge(df18, pov18)
df19 = pd.merge(df19, pov19)

'''
Generate lawyer discipline dataframes
'''

# Get initial dataframes from PDFs (2015 and 2016 need to be broken up by page, partially cleaned, then recombined)

discipline_dict_1 = {2015:'https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/2015_sold_results.pdf',
                  2016:'https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/2016sold_results.pdf'}

for year in discipline_dict_1.keys():
    if os.path.isfile(path+f'\discipline_{year}.csv') == True:
        pass
    else:
        tabula.convert_into(discipline_dict_1[year], f'discipline_{year}_a.csv', output_format='csv', pages='5')
        tabula.convert_into(discipline_dict_1[year], f'discipline_{year}_b.csv', output_format='csv', pages='6')
        tabula.convert_into(discipline_dict_1[year], f'discipline_{year}_c.csv', output_format='csv', pages='7')

dis15a = pd.read_csv('discipline_2015_a.csv', encoding='cp1252', header=6)
dis15a.columns=['garbage', 'Jurisdiction', 'junk', 'Num_Lawyers', 'Num_Complaints', 'Central_Intake', 'Separate']
del dis15a['garbage']
del dis15a['junk']
dis15a['Jurisdiction'][13] = 'Iowa'

dis15b = pd.read_csv('discipline_2015_b.csv', encoding='cp1252', header=6)
dis15b.columns=['garbage', 'Jurisdiction', 'junk', 'Num_Lawyers', 'Num_Complaints', 'Central_Intake', 'Separate']
dis15b['Jurisdiction'][0] = 'Mississippi'
dis15b['Jurisdiction'][1] = 'to be deleted'
dis15b['Jurisdiction'][15] = 'New York: 3rd Department'
dis15b['Num_Lawyers'][15] = '65,000'
dis15b['Num_Complaints'][15] = '2,098'
dis15b['Jurisdiction'][3] = 'Montana'
dis15b['Jurisdiction'][23] = 'Oregon'
del dis15b['garbage']
del dis15b['junk']

dis15c = pd.read_csv('discipline_2015_c.csv', encoding='cp1252', header=4)
dis15c.columns=['Jurisdiction', 'Num_Lawyers', 'Num_Complaints', 'Central_Intake', 'Separate']

dis16a = pd.read_csv('discipline_2016_a.csv', encoding='cp1252', header=4)
del dis16a['Unnamed: 0']
del dis16a['Unnamed: 1']
del dis16a['Unnamed: 3']
dis16a.columns=['Jurisdiction', 'Num_Lawyers', 'Num_Complaints', 'Central_Intake', 'Separate']

dis16b = pd.read_csv('discipline_2016_b.csv', encoding='cp1252', header=4)
dis16b.columns=['garbage', 'trash', 'Jurisdiction', 'junk', 'Num_Lawyers', 'Num_Complaints', 'Central_Intake', 'Separate']
dis16b['Jurisdiction'][13] = 'New York: 3rd Department'
dis16b['Num_Lawyers'][13] = '70,000'
dis16b['Num_Complaints'][13] = '1,239'
del dis16b['garbage']
del dis16b['trash']
del dis16b['junk']

dis16c = pd.read_csv('discipline_2016_c.csv', encoding='cp1252', header=4)
dis16c.columns=['Jurisdiction', 'Num_Lawyers', 'Num_Complaints', 'Central_Intake', 'Separate']

discipline_dict_2 = {2017:'https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/2017sold-results.pdf',
                  2018:'https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/2018sold-results.pdf'
}

for year in discipline_dict_2.keys():
    if os.path.isfile(path+f'\discipline_{year}.csv') == True:
        pass
    else:
        tabula.convert_into(discipline_dict_2[year], f'discipline_{year}.csv', output_format='csv', pages='5-7')

dis15 = dis15a.append(dis15b).append(dis15c).reset_index(drop=True)
dis16 = dis16a.append(dis16b).append(dis16c).reset_index(drop=True)
dis17 = pd.read_csv('discipline_2017.csv', encoding='cp1252', header=7)
dis18 = pd.read_csv('discipline_2018.csv', encoding='cp1252')

dis_dfs = [dis15, dis16, dis17, dis18]

def adjust_columns(dis_df):
    dis_df.columns=['Jurisdiction', 'Num_Lawyers', 'Num_Complaints', 'Central_Intake', 'Separate']
    del dis_df['Central_Intake']
    del dis_df['Separate']

# Rename New York rows, since divided into districts
def rename_ny(dis_df):
# Approach to finding first instance of "New York" derived from https://www.geeksforgeeks.org/python-pandas-series-str-find/
    first_ny_list = dis_df['Jurisdiction'].str.find('New York')
    first_ny = (first_ny_list.values == 0).argmax()
    last_ny_list = dis_df['Jurisdiction'].str.find('North Carolina')
    last_ny = (last_ny_list.values == 0).argmax()
    for num in range(first_ny, last_ny):
        dis_df.loc[num][0] = 'New York'

def remove_non_states(dis_df):
    dis_df['Jurisdiction'] = dis_df['Jurisdiction'].replace("'","", regex=True)
    dis_df = dis_df[dis_df['Jurisdiction'].isin(df17['Jurisdiction'])].reset_index(drop=True)
    return(dis_df)

def numeric_columns(dis_df):
    for col in dis_df:
        if col != 'Jurisdiction':
            dis_df[col] = dis_df[col].replace([',', 'N', '\\*'],'', regex=True)
            for num in range(0, len(dis_df)):
                try:
                    int(dis_df[col][num])
                except ValueError:
                    dis_df[col][num] = 0
    dis_df = dis_df.astype(dtype={'Num_Lawyers':int, 'Num_Complaints':int})
    return(dis_df)

# Remove rows with only 0s, consolidate New York rows, and add column with complaints per lawyer
def consolidate(dis_df):
    dis_df = dis_df[(dis_df['Num_Lawyers'] != 0) & (dis_df['Num_Complaints'] != 0)]
    ny_lawyers = dis_df.loc[dis_df['Jurisdiction'] == 'New York'].sum()[1]
    ny_complaints = dis_df.loc[dis_df['Jurisdiction'] == 'New York'].sum()[2]
    ny = pd.DataFrame([['New York', ny_lawyers, ny_complaints]], columns=['Jurisdiction', 'Num_Lawyers', 'Num_Complaints'])
    dis_df = dis_df[dis_df['Jurisdiction'] != 'New York']
    dis_df = dis_df.append(ny).sort_values('Jurisdiction').reset_index(drop=True)
    dis_df['Complaints_Per_Lawyer'] = dis_df['Num_Complaints']/dis_df['Num_Lawyers']
    return(dis_df)

def get_disc(a):
    adjust_columns(a)
    rename_ny(a)
    b = remove_non_states(a)
    c = numeric_columns(b)
    d = consolidate(c)
    return(d)

df15 = pd.merge(df15, get_disc(dis15))
df16 = pd.merge(df16, get_disc(dis16))
df17 = pd.merge(df17, get_disc(dis17))
df18 = pd.merge(df18, get_disc(dis18))

'''
Rudimentary plotting
'''

df15 = df15.sort_values('Pass_Rate')

import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot(df15['Jurisdiction'], df15['Pass_Rate'])
ax.plot(df15['Jurisdiction'], df15['Poverty_Rate'])

