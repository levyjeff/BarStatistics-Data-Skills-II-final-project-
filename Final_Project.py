'''
Initial housekeeping
'''

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
    if os.path.isfile(path+'f\pass_rates_{year}.csv') == True:
        pass
    else:
        pass_rate_df = generate_df(pass_rate_dict[year])
        pass_rate_df.to_csv(f'pass_rates_{year}.csv')

df15 = pd.read_csv('pass_rates_2015')
df16 = pd.read_csv('pass_rates_2016')
df17 = pd.read_csv('pass_rates_2017')
df18 = pd.read_csv('pass_rates_2018')
df19 = pd.read_csv('pass_rates_2019')

'''
Generate poverty rate dataframes
'''

# Get poverty rates chart if not in path
if os.path.isfile(path+'\pov_rates.csv') == True:
    pass
else:
    pov_rates = pd.read_excel('https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-poverty-people/hstpov21.xlsx', header=3)
    pov_rates.to_csv('pov_rates.csv')

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

'''
Generate lawyer discipline dataframes - GENERALIZED
'''

# Read in the PDFs as CSVs if not already in path

discipline_dict = {2015:'https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/2015_sold_results.pdf',
                  2016:'https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/2016sold_results.pdf',
                  2017:'https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/2017sold-results.pdf',
                  2018:'https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/2018sold-results.pdf'
}

for year in discipline_dict.keys():
    if os.path.isfile(path+'f\discipline_{year}.csv') == True:
        pass
    else:
        tabula.convert_into(file, f'discipline_{year}.csv', output_format='csv', pages='5-7')

dis15 = pd.read_csv('discipline_2015')
dis16 = pd.read_csv('discipline_2016')
dis17 = pd.read_csv('discipline_2017')
dis18 = pd.read_csv('discipline_2018')



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

