import pandas as pd
import plotly.express as px
import streamlit as st
from scipy.stats import pearsonr

def load_data():
    data = pd.read_csv('migration_translate/total.csv')
    
    gdp = pd.read_csv('GDP/pdb at constant prices in columbia.csv', sep=';')

    gdp = gdp.groupby('Year').sum()['Accomodation and food services'].reset_index()

    return data, gdp

mig, gdp = load_data()

st.header('GDP/PIB')

fig_gdp = px.line(gdp, x='Year', y='Accomodation and food services', labels={'Accomodation and food services': 'GDP/PIB Accomodation and food services (Billion $)'})
st.plotly_chart(fig_gdp)

corr, pval = pearsonr(mig.loc[(mig['agnio'] >= 2012) & (mig['agnio'] <= 2020), 'total'], gdp.loc[(gdp['Year'] >= 2012) & (gdp['Year'] <= 2020), 'Accomodation and food services'])
st.write(f'Correlation with GDP before COVID: {corr:.2f} (pvalue: {pval:.2f})')

corr, pval = pearsonr(mig.loc[(mig['agnio'] >= 2020) & (mig['agnio'] <= 2023), 'total'], gdp.loc[(gdp['Year'] >= 2020) & (gdp['Year'] <= 2023), 'Accomodation and food services'])
st.write(f'Correlation with GDP after COVID: {corr:.2f} (pvalue: {pval:.2f})')

with st.expander('Explanation'):
    f = open(f'analysis/gdp_correlation/gdp_correlation.md', 'r')
    st.markdown(f.read())