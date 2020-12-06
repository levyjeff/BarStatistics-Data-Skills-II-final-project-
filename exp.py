'''
Initial housekeeping
'''

import os
import pandas as pd

import PyPDF2
import requests
import spacy
nlp = spacy.load("en_core_web_sm")

path = r'C:\Users\bethk\Desktop\Data_Skills_II\BarStatistics'
os.chdir(path)

'''
Race data
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
# Get race numbers as percentages
    r['Total'] = r.sum(axis=1)
    for col in r.columns[1:]:
        r[col] = r[col]/r['Total']
    del r['Total']
    r['Year'] = year
    return(r)


x['Total'] = 0

for num in range(len(x)):
    for col in x.columns[1:]:
        x[col] = (x[col])/(x.iloc[num].sum())


    for col in x.columns[1:]:
        print([col][num])

        x[col][num] = (x[col][num])/(x.iloc[num].sum())

def combine_years():
    dfs = []
    for year in range(2015, 2018):


        def merge_dfs(start, end):
    dfs = []
    for year in range(start, end):
        merged = merge_it(year)
        dfs.append(merged)
    all = pd.concat(dfs, axis=0).reset_index(drop=True)
    return(all)
