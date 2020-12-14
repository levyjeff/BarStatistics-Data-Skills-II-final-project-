import os
import pandas as pd

import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

path = r'C:\Users\bethk\Desktop\Data_Skills_II\BarStatistics'
os.chdir(path)
alldata = pd.read_csv('final_df.csv')
del alldata['Unnamed: 0']

'''
Regressions
'''

def regress(regressor, regressand):
    x = regressor
    y = regressand
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    print(model.summary())

kitchen_sink_data_1 = alldata[['Takers', 'Pass Rate', 'Poverty Rate',
       'Num Lawyers', 'No HS', 'HS', 'Percent with BA', 'Asian, Hispanic',
       'Asian, Not Hispanic',
       'Black, Hispanic', 'Black, Not Hispanic', 'Multiracial, Hispanic',
       'Multiracial, Not Hispanic', 'Native, Hispanic', 'Native, Not Hispanic',
       'Pacific, Hispanic', 'Pacific, Not Hispanic', 'White, Hispanic',
       'White, Not Hispanic', 'Unemployment Rate']]
kitchen_sink_data_2 = alldata[['Takers', 'Poverty Rate',
       'Num Lawyers', 'No HS', 'HS', 'Percent with BA', 'Asian, Hispanic', 'Asian, Not Hispanic',
       'Black, Hispanic', 'Black, Not Hispanic', 'Multiracial, Hispanic',
       'Multiracial, Not Hispanic', 'Native, Hispanic', 'Native, Not Hispanic',
       'Pacific, Hispanic', 'Pacific, Not Hispanic', 'White, Hispanic',
       'White, Not Hispanic', 'Unemployment Rate']]

# Complaints per lawyer regressions
regress(kitchen_sink_data_1, alldata['Complaints Per Lawyer'])
regress(alldata['Pass Rate'], alldata['Complaints Per Lawyer'])

# Pass rate regressions
regress(kitchen_sink_data_2, alldata['Pass Rate'])
regress(alldata['Black, Not Hispanic'], alldata['Pass Rate'])
regress(alldata['White, Not Hispanic'], alldata['Pass Rate'])
regress(alldata[['White, Not Hispanic', 'Poverty Rate']], alldata['Pass Rate'])
regress(alldata[['White, Not Hispanic', 'Unemployment Rate']], alldata['Pass Rate'])
regress(alldata['Percent with BA'], alldata['Pass Rate'])

'''
Plotting
'''

def scatter(x,y, color, a_df):
    plt.figure() # Prevents piling plots on top of one another
    sns.set_style("darkgrid")
    ax = sns.scatterplot(x,y, data=a_df, hue=color, s=50)
    ax.set(xlabel=x, ylabel=y, title=f'{x} Plotted Against {y}')
    yvals = ax.get_yticks() # Change ticks to percentages: solution at https://stackoverflow.com/questions/31357611/format-y-axis-as-percent
    ax.set_yticklabels(['{:,.0%}'.format(y) for y in yvals])
    xvals = ax.get_xticks()
    ax.set_xticklabels(['{:,.0%}'.format(x) for x in xvals])
    plt.savefig(f'{x} vs. {y}.png')

def reg_plot(x,y, a_df):
    plt.figure()
    sns.set_style("darkgrid")
    ax = sns.regplot(x,y, data=a_df)
    ax.set(xlabel=x, ylabel=y, title=f'{x} Plotted Against {y} with Line of Best Fit')
    yvals = ax.get_yticks()
    ax.set_yticklabels(['{:,.0%}'.format(y) for y in yvals])
    xvals = ax.get_xticks()
    ax.set_xticklabels(['{:,.0%}'.format(x) for x in xvals])
    plt.savefig(f'{x} vs. {y} regression.png')

# Examine effect of poverty on passage rates
scatter('Poverty Rate', 'Pass Rate', 'Percent with BA', alldata)
reg_plot('Poverty Rate', 'Pass Rate', alldata)

# Examine effect of unemployment on passage rates
scatter('Unemployment Rate', 'Pass Rate', 'Poverty Rate', alldata)
reg_plot('Unemployment Rate', 'Pass Rate', alldata)

# Examine effect of race on passage rates
scatter('White, Not Hispanic', 'Pass Rate', 'Poverty Rate', alldata)
reg_plot('White, Not Hispanic', 'Pass Rate', alldata)

# Examine effect of passage rates on complaints per lawyer
scatter('Pass Rate', 'Complaints Per Lawyer', 'Poverty Rate', alldata)
reg_plot('Pass Rate', 'Complaints Per Lawyer', alldata)
