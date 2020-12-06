'''
Initial housekeeping
'''

import os
import pandas as pd
import us

import requests
from bs4 import BeautifulSoup
import tabula
import PyPDF2
import spacy
import statsmodels.api as sm
import matplotlib.pyplot as plt

nlp = spacy.load("en_core_web_sm")
path = r'C:\Users\bethk\Desktop\Data_Skills_II\BarStatistics'
os.chdir(path)
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
state_names = [state.name for state in us.states.STATES] # List comprehension adapted from https://stackoverflow.com/questions/47168881/how-to-get-a-list-of-us-state-names-from-us-1-0-0-package


'''
Bar pass rate dataframe
'''

pass_rate_dict = {2015:'https://thebarexaminer.org/statistics/2015-statistics/persons-taking-and-passing-the-2015-bar-examination/',
                  2016:'https://thebarexaminer.org/statistics/2016-statistics/persons-taking-and-passing-the-2016-bar-examination/',
                  2017:'https://thebarexaminer.org/statistics/2017-statistics/persons-taking-and-passing-the-2017-bar-examination/',
                  2018:'https://thebarexaminer.org/statistics/2018-statistics/persons-taking-and-passing-the-2018-bar-examination/'
}

# Create functions to make a dataframe from the tables on the NCBE website
# (approach derived from Jeff Levy's Spring 2020 Week 8 Lecture 2)

def make_table(url): # Retrieves a table from NCBE bar pass rate website
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find('table')
    return(table)

def create_list(a_table): # Makes a list from the table
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

def build_df(a_list): # Makes a dataframe from the list
    the_df = pd.DataFrame(a_list, columns = ['Number', 'Jurisdiction', 'Month', 'Takers', 'Passers', 'Pass_Rate'])
    del the_df['Number']
    the_df = the_df.astype(dtype={'Takers':int, 'Passers':int})
    the_df['Pass_Rate'] = the_df['Passers']/the_df['Takers']
    the_df = the_df[the_df['Month'] == 'Total February and July']
    del the_df['Month']
    return(the_df)

def passrates_df(year): # Retrieves or builds the pass rate dataframe
    if os.path.isfile(path+f'\\pass_rates_{year}.csv') == True:
        pass_rate_df = pd.read_csv(path+f'\\pass_rates_{year}.csv')
    else:
        pass_rate_df = build_df(create_list(make_table(pass_rate_dict[year])))
        pass_rate_df.to_csv(f'pass_rates_{year}.csv')
    try:
        del pass_rate_df['Unnamed: 0']
    except KeyError:
        pass
    return(pass_rate_df)

'''
Poverty rates dataframe
'''

def povrates_df(year):
# Retrieve the CSV
    if os.path.isfile(path+'\pov_rates.csv') == True:
        pass
    else:
        pov_rates = pd.read_excel('https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-poverty-people/hstpov21.xlsx', header=4)
        pov_rates.to_csv('pov_rates.csv')
    pov_rates = pd.read_csv('pov_rates.csv')[['STATE', 'Percent']]
# Divide up the poverty rate dataframe by year
    # Get Alabama 2015-2018 indices, removing the duplicate 2017 portion
    ALs = list((pov_rates[pov_rates['STATE']=='Alabama'].index.values))[1:6]
    del ALs[1]
    # Match Alabama indices to years in a dictionary
    yrs = list(pass_rate_dict.keys())
    ALs_yrs_dict = {yrs[i]: ALs[i] for i in range(len(yrs))}
    # Isolate out the right year's data and change column names to match the bar dataframe
    state_rate = []
    for a_num in range(ALs_yrs_dict[year], ALs_yrs_dict[year] + 51):
        state_rate.append([pov_rates['STATE'][a_num], float(pov_rates['Percent'][a_num])/100])
    pov_rates = pd.DataFrame(state_rate, columns=['Jurisdiction', 'Poverty_Rate'])
    return(pov_rates)

'''
Lawyer discipline dataframes
'''

# Get initial dataframes from PDFs (2015 and 2016 need to be broken up by page, partially cleaned, then recombined)

discipline_dict_1 = {2015:'https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/2015_sold_results.pdf',
                  2016:'https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/2016sold_results.pdf'}
discipline_dict_2 = {2017:'https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/2017sold-results.pdf',
                  2018:'https://www.americanbar.org/content/dam/aba/administrative/professional_responsibility/2018sold-results.pdf'
}

def dis_15_16_csvs():
    for year in discipline_dict_1.keys():
        if os.path.isfile(path+f'\discipline_{year}.csv') == True:
            pass
        else:
            tabula.convert_into(discipline_dict_1[year],
                                f'discipline_{year}.csv',
                                output_format = 'csv')
            tabula.convert_into(discipline_dict_1[year],
                                f'discipline_{year}_a.csv',
                                output_format='csv', pages='5')
            tabula.convert_into(discipline_dict_1[year],
                                f'discipline_{year}_b.csv',
                                output_format='csv', pages='6')
            tabula.convert_into(discipline_dict_1[year],
                                f'discipline_{year}_c.csv',
                                output_format='csv', pages='7')

def df_15a():
    dis15a = pd.read_csv('discipline_2015_a.csv', encoding='cp1252', header=6)
    dis15a.columns = ['garbage', 'Jurisdiction', 'junk', 'Num_Lawyers', 'Num_Complaints', 'Central_Intake', 'Separate']
    del dis15a['garbage']
    del dis15a['junk']
    dis15a['Jurisdiction'][13] = 'Iowa'
    dis15a['Jurisdiction'][2] = 'Arizona'
#    dis15a['Jurisdiction'][9] = 'Hawaii'
    return(dis15a)

def df_15b():
    dis15b = pd.read_csv('discipline_2015_b.csv', encoding='cp1252', header=6)
    dis15b.columns = ['garbage', 'Jurisdiction', 'junk', 'Num_Lawyers', 'Num_Complaints', 'Central_Intake', 'Separate']
    dis15b['Jurisdiction'][0] = 'Mississippi'
    dis15b['Jurisdiction'][1] = 'to be deleted'
    dis15b['Jurisdiction'][15] = 'New York: 3rd Department'
    dis15b['Num_Lawyers'][15] = '65,000'
    dis15b['Num_Complaints'][15] = '2,098'
    dis15b['Jurisdiction'][3] = 'Montana'
    dis15b['Jurisdiction'][23] = 'Oregon'
    del dis15b['garbage']
    del dis15b['junk']
    return(dis15b)

def df_15c():
    dis15c = pd.read_csv('discipline_2015_c.csv', encoding='cp1252', header=4)
    dis15c.columns=['Jurisdiction', 'Num_Lawyers', 'Num_Complaints', 'Central_Intake', 'Separate']
    return(dis15c)

def df_16a():
    dis16a = pd.read_csv('discipline_2016_a.csv', encoding='cp1252', header=4)
    del dis16a['Unnamed: 0']
    del dis16a['Unnamed: 1']
    del dis16a['Unnamed: 3']
    dis16a.columns=['Jurisdiction', 'Num_Lawyers', 'Num_Complaints', 'Central_Intake', 'Separate']
#    dis16a['Jurisdiction'][9] = 'Hawaii'
    return(dis16a)

def df_16b():
    dis16b = pd.read_csv('discipline_2016_b.csv', encoding='cp1252', header=4)
    dis16b.columns=['garbage', 'trash', 'Jurisdiction', 'junk', 'Num_Lawyers', 'Num_Complaints', 'Central_Intake', 'Separate']
    dis16b['Jurisdiction'][13] = 'New York: 3rd Department'
    dis16b['Num_Lawyers'][13] = '70,000'
    dis16b['Num_Complaints'][13] = '1,239'
    del dis16b['garbage']
    del dis16b['trash']
    del dis16b['junk']
    return(dis16b)

def df_16c():
    dis16c = pd.read_csv('discipline_2016_c.csv', encoding='cp1252', header=4)
    dis16c.columns=['Jurisdiction', 'Num_Lawyers', 'Num_Complaints', 'Central_Intake', 'Separate']
    return(dis16c)

def consolidate_dis_15_16(year):
    dis_15_16_csvs()
    if year == 2015:
        a = df_15a()
        b = df_15b()
        c = df_15c()
    elif year == 2016:
        a = df_16a()
        b = df_16b()
        c = df_16c()
    dis_df = a.append(b).append(c).reset_index(drop=True)
    return(dis_df)

def dis_17_18_csvs():
    for year in discipline_dict_2.keys():
        if os.path.isfile(path+f'\discipline_{year}.csv') == True:
            pass
        else:
            tabula.convert_into(discipline_dict_2[year],
                                f'discipline_{year}.csv',
                                output_format='csv', pages='5-7')

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
    dis_df = dis_df[dis_df['Jurisdiction'].isin(
state_names)].reset_index(drop=True)
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
def finalize(dis_df):
    dis_df = dis_df[(dis_df['Num_Lawyers'] != 0) & (dis_df['Num_Complaints'] != 0)]
    ny_lawyers = dis_df.loc[dis_df['Jurisdiction'] == 'New York'].sum()[1]
    ny_complaints = dis_df.loc[dis_df['Jurisdiction'] == 'New York'].sum()[2]
    ny = pd.DataFrame([['New York', ny_lawyers, ny_complaints]], columns=['Jurisdiction', 'Num_Lawyers', 'Num_Complaints'])
    dis_df = dis_df[dis_df['Jurisdiction'] != 'New York']
    dis_df = dis_df.append(ny).sort_values('Jurisdiction').reset_index(drop=True)
    dis_df['Complaints_Per_Lawyer'] = dis_df['Num_Complaints']/dis_df['Num_Lawyers']
    return(dis_df)

def make_disc_dict():
    dis15 = consolidate_dis_15_16(2015)
    dis16 = consolidate_dis_15_16(2016)
    dis_17_18_csvs()
    dis17 = pd.read_csv('discipline_2017.csv', encoding='cp1252', header=3)
    dis18 = pd.read_csv('discipline_2018.csv', encoding='cp1252')
    dis_dfs_dict = {2015:dis15, 2016:dis16, 2017:dis17, 2018:dis18}
    return(dis_dfs_dict)

def get_disc(year):
    a = make_disc_dict()[year]
    adjust_columns(a)
    rename_ny(a)
    a = remove_non_states(a)
    a = numeric_columns(a)
    a = finalize(a)
    return(a)

get_disc(2015)
# Hawaii has disappeared from 2017 and 2018 but we're getting close

'''
Unemployment rates dataframe
'''

def unemprates_df():
# Get the data
    if os.path.isfile(path+ r'\unemp_rates.csv') == True:
        pass
    else:
        unemp_rates = pd.read_excel('https://www.ers.usda.gov/webdocs/DataFiles/48747/Unemployment.xls?v=4751.8', header=7)
        unemp_rates.to_csv('unemp_rates.csv')
    unemp = pd.read_csv('unemp_rates.csv')[['area_name', 'Unemployment_rate_2015', 'Unemployment_rate_2016', 'Unemployment_rate_2017', 'Unemployment_rate_2018']]
# Adjust the data
    unemp = unemp[unemp['area_name'].isin(state_names)].reset_index(drop=True)
    unemp = unemp.rename(columns={'area_name': 'Jurisdiction'})
    return(unemp)

'''
Educational attainment dataframe
'''

def edrates_df():
    if os.path.isfile(path+ r'\ed_attainment.csv') == True:
        pass
    else:
        ed = pd.read_excel('https://www.ers.usda.gov/webdocs/DataFiles/48747/Education.xls?v=4751.8', header=4)
        ed.to_csv('ed_attainment.csv')
    ed = pd.read_csv('ed_attainment.csv')
# Remove sub-state data
    ed = ed[ed['Area name'].isin(state_names)].reset_index(drop=True)
# Remove duplicate Washington, D.C.
    ed = ed.drop_duplicates(subset='Area name', inplace=False)
# Restrict columns to percentages, simplify column names, make percentages decimals
    ed = ed[['Area name',
       'Percent of adults with less than a high school diploma, 2014-18',
       'Percent of adults with a high school diploma only, 2014-18',
       "Percent of adults completing some college or associate's degree, 2014-18",
       "Percent of adults with a bachelor's degree or higher, 2014-18"]]
    ed.columns = ['Jurisdiction', 'No_HS', 'HS', 'Some_Coll', 'BA']
    for col in ed.columns:
        if ed[col].dtype == 'float64':
            ed[col] = ed[col]/100
    return(ed)

'''
Race dataframes
'''

# Get race names by key from census PDF
def get_statement(url):
    if ('sc-est2019-alldata6.pdf' in os.getcwd()):
        pass
    else:
        fname = url.split('/')[-1]
        response = requests.get(url)
        with open(os.path.join(path, fname), 'wb') as ofile:
            ofile.write(response.content)
def parse_pdf(a_pdf):
    a_pdf = path + '\\' + a_pdf
    fname = a_pdf.split('/')[-1]
    with open(os.path.join(path, fname), 'rb') as ifile:
        pdf_reader = PyPDF2.PdfFileReader(ifile)
        pages = [pdf_reader.getPage(p) for p in range(1,2)]
        pages = [p.extractText() for p in pages]
    return pages

get_statement('https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2010-2019/sc-est2019-alldata6.pdf')
codes = str(parse_pdf('sc-est2019-alldata6.pdf')).split('\\n')

racewords = ['White', 'Black', 'Indian', 'Asian', 'Hawaiian', 'races']
hispwords = ['Hispanic']

def get_races(race_set):
    racecodes = []
    for item in codes:
        for race in race_set:
            if (race in item) & ('=' in item):
                racecodes.append(item)
    return(racecodes)

def strip_whitespace(race_set):
    stripped = [item.strip() for item in race_set]
    return(stripped)

def make_race_dict(race_set):
    keys = []
    vals = []
    race_list = strip_whitespace(get_races(race_set))
    for item in race_list:
        first = int(item.split('=')[0].strip())
        second = item.split('=')[1].strip()
        keys.append(first)
        vals.append(second)
    output_dict = dict(zip(keys, vals))
    return(output_dict)

hisp = make_race_dict(hispwords)
nonhisp = make_race_dict(racewords)
nonhisp[1] = 'White'
nonhisp[2] = 'Black'
nonhisp[3] = 'Native'
nonhisp[4] = 'Asian'
nonhisp[5] = 'Pacific'
nonhisp[6] = 'Multiracial'

def race_df(): # Imports race data by state
    if os.path.isfile(path+f'\\race.csv') == True:
        racedata = pd.read_csv(path+f'\\race.csv')
    else:
        racedata = pd.read_csv('https://www2.census.gov/programs-surveys/popest/tables/2010-2019/state/asrh/sc-est2019-alldata6.csv')
        racedata.to_csv('race.csv')
# Remove region codes and aggregates
    racedata = racedata[racedata['ORIGIN'] != 0]
    racedata = racedata[racedata['SEX'] != 0]
    racedata = racedata[['NAME', 'ORIGIN', 'RACE', 'POPESTIMATE2015', 'POPESTIMATE2016', 'POPESTIMATE2017', 'POPESTIMATE2018']]
    return(racedata)

racedata = race_df()

# Map in race names
racedata['Hisp'] = racedata['ORIGIN'].map(hisp)
racedata['Nonhisp'] = racedata['RACE'].map(nonhisp)
racedata['Race'] = racedata[['Nonhisp','Hisp']].apply(lambda x: ', '.join(x), axis=1)
racedata = racedata[['NAME', 'POPESTIMATE2015', 'POPESTIMATE2016',
       'POPESTIMATE2017', 'POPESTIMATE2018', 'Race']]

# Make a dataframe with racial population estimates for each year
def race_by_state(year):
    r = racedata[['NAME', f'POPESTIMATE{year}', 'Race']]
    r = r.groupby(['NAME', 'Race']).sum().reset_index()
    r = r.pivot(index='NAME', columns='Race', values=f'POPESTIMATE{year}').reset_index()
# Get race numbers as percentages then rename state column to match other dataframes
    r['Total'] = r.sum(axis=1)
    for col in r.columns[1:]:
        r[col] = r[col]/r['Total']
    del r['Total']
    r = r.rename(columns={'NAME':'Jurisdiction'})
    return(r)

'''
Merge dataframes
'''

def merge_it(year):
    merged = pd.merge(passrates_df(year), povrates_df(year))
    merged = pd.merge(merged, get_disc(year))
    merged = pd.merge(merged, edrates_df())
    merged = pd.merge(merged, race_by_state(year))
# Add columns for unemployment rate for given year
    unemp = unemprates_df()
    unemp = unemp[unemp['Jurisdiction'].isin(
merged['Jurisdiction'])].reset_index(drop=True)
    merged['Unemployment_Rate'] = unemp[f'Unemployment_rate_{year}']/100
    merged['Year'] = year
    return(merged)
# Note: this will drop US territories, leaving only states and Washington, D.C. It will also drop states for which no discipline data is avaiable through the ABA.

def merge_dfs(start, end):
    dfs = []
    for year in range(start, end):
        merged = merge_it(year)
        dfs.append(merged)
    all = pd.concat(dfs, axis=0).reset_index(drop=True)
    return(all)

alldata = merge_dfs(2015, 2019)

'''
Regressions
'''

x = alldata[['Pass_Rate', 'Poverty_Rate', 'Num_Lawyers', 'Unemployment_Rate', 'Year']]
y = alldata['Complaints_Per_Lawyer']
x = sm.add_constant(x)
model = sm.OLS(y, x).fit()
predictions = model.predict(x)
model.summary()

x = alldata[['Poverty_Rate', 'BA', 'Unemployment_Rate', 'Year']]
y = alldata['Pass_Rate']
x = sm.add_constant(x)
model = sm.OLS(y, x).fit()
predictions = model.predict(x)
model.summary()

'''
Rudimentary plotting
'''

df15 = df15.sort_values('Pass_Rate')
df16 = df16.sort_values('Pass_Rate')

fig, ax = plt.subplots()
ax.plot(df15['Jurisdiction'], df15['Pass_Rate'])
ax.plot(df15['Jurisdiction'], df15['Poverty_Rate'])

