import pandas as pd
import plotly.express as px
import streamlit as st
from scipy.stats import pearsonr

def load_data():
    data = pd.read_csv('migration_translate/total.csv')
    return data

mig = load_data()

st.header('Total Tourists')

fig_mig = px.line(mig, x='agnio', y='total', labels={'agnio': 'Year', 'total': 'Total Tourists'})
st.plotly_chart(fig_mig)

with st.expander('Explanation'):
    f = open(f'analysis/tourists/tourists.md', 'r')
    st.markdown(f.read())