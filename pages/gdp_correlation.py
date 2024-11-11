import math
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy.stats import pearsonr

var = st.selectbox('Variabel', ['sex', 'travel_reason', 'colombian_foreign', 'transport_type', 'country_nationality', 'age_range'])

def load_data():
    data = {}
    for m in sorted(os.listdir('migration_translate')):
        if f'total_{var}: ' in m:
            data[m.replace(f'total_{var}: ', '').replace('.csv', '')] = pd.read_csv(f'migration_translate/{m}')

    gdp = pd.read_csv('GDP/pdb at constant prices in columbia.csv', sep=';')

    gdp = gdp.groupby('Year').sum()['Accomodation and food services'].reset_index()

    return data, gdp

migs, gdp = load_data()

with st.expander('Correlation with GDP before COVID'):

    st.markdown(':red[(0-0.25)] :orange[(0.25-0.5)] :green[(0.5-0.75)] :blue[(0.75-1)]')

    corrs = []
    corrs_text = []

    for mig in migs:
        mig_temp = migs[mig]
        mig_temp[var] = mig
        mig_temp = mig_temp[mig_temp[var] == mig]

        x = []
        y = []

        for i in range(2012, 2021):
            if i in mig_temp['agnio'].to_list() and i in gdp['Year'].to_list():
                x.append(mig_temp[mig_temp['agnio'] == i]['total'].to_list()[0])
                y.append(gdp[gdp['Year'] == i]['Accomodation and food services'].to_list()[0])

        if len(x) > 2 and len(y) > 2:
            corr, pval = pearsonr(x, y)
            if math.isnan(corr):
                corr = 0

            if abs(corr) >= 0 and abs(corr) <= 0.25:
                corr_color = 'red'
            elif abs(corr) > 0.25 and abs(corr) <= 0.5:
                corr_color = 'orange'
            elif abs(corr) > 0.5 and abs(corr) <= 0.75:
                corr_color = 'green'
            elif abs(corr) > 0.75:
                corr_color = 'blue'

            corrs.append(corr)
            corrs_text.append(f'{var} - {mig}: :{corr_color}[{corr:.2f}] (pvalue {pval:.2f})')

    corrs_df = pd.DataFrame({
        'corr': corrs,
        'text': corrs_text
    })
    corrs_df = corrs_df.sort_values('corr', ascending=False)

    for corr_item, corr_text in zip(corrs_df['corr'], corrs_df['text']):
        st.progress(abs(corr_item), text=corr_text)

with st.expander('Correlation with GDP after COVID'):
    st.markdown(':red[(0-0.25)] :orange[(0.25-0.5)] :green[(0.5-0.75)] :blue[(0.75-1)]')

    corrs = []
    corrs_text = []

    for mig in migs:
        mig_temp = migs[mig]
        mig_temp[var] = mig
        mig_temp = mig_temp[mig_temp[var] == mig]

        x = []
        y = []

        for i in range(2020, 2025):
            if i in mig_temp['agnio'].to_list() and i in gdp['Year'].to_list():
                x.append(mig_temp[mig_temp['agnio'] == i]['total'].to_list()[0])
                y.append(gdp[gdp['Year'] == i]['Accomodation and food services'].to_list()[0])

        if len(x) > 2 and len(y) > 2:
            corr, pval = pearsonr(x, y)
            if math.isnan(corr):
                corr = 0

            if abs(corr) >= 0 and abs(corr) <= 0.25:
                corr_color = 'red'
            elif abs(corr) > 0.25 and abs(corr) <= 0.5:
                corr_color = 'orange'
            elif abs(corr) > 0.5 and abs(corr) <= 0.75:
                corr_color = 'green'
            elif abs(corr) > 0.75:
                corr_color = 'blue'

            corrs.append(corr)
            corrs_text.append(f'{var} - {mig}: :{corr_color}[{corr:.2f}] (pvalue {pval:.2f})')

    corrs_df = pd.DataFrame({
        'corr': corrs,
        'text': corrs_text
    })
    corrs_df = corrs_df.sort_values('corr', ascending=False)

    for corr_item, corr_text in zip(corrs_df['corr'], corrs_df['text']):
        st.progress(abs(corr_item), text=corr_text)

if var not in ['travel_reason', 'country_nationality']: 
    with st.expander('Explanation'):
        f = open(f'analysis/gdp_correlation/{var}.md', 'r')
        st.markdown(f.read())