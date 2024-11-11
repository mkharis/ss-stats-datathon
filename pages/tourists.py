import os
import pandas as pd
import plotly.express as px
import streamlit as st

var = st.selectbox('Variabel', ['sex', 'travel_reason', 'colombian_foreign', 'transport_type', 'country_nationality', 'age_range'])

def load_data():
    data = {}
    for m in sorted(os.listdir('migration_translate')):
        if f'total_{var}: ' in m:
            data[m.replace(f'total_{var}: ', '').replace('.csv', '')] = pd.read_csv(f'migration_translate/{m}')
    return data

migs = load_data()

for i, mig in enumerate(migs):
    if i == 0:
        migs_join = migs[mig]
        migs_join[var] = mig
    else:
        migs_temp = migs[mig]
        migs_temp[var] = mig
        migs_join = pd.concat([migs_join, migs_temp])

if var in ['country_nationality', 'travel_reason']:
    top_10 = migs_join.groupby(var).sum().sort_values('total', ascending=False).head(10).index.to_list()
    migs_join_top_ten = migs_join[migs_join[var].isin(top_10)]
    migs_join_not_top_ten = migs_join[~migs_join[var].isin(top_10)]
    migs_join_not_top_ten = migs_join_not_top_ten.groupby('agnio').sum().reset_index()
    migs_join_not_top_ten[var] = 'Other'
    migs_join = pd.concat([migs_join_top_ten, migs_join_not_top_ten])

st.header('Total Tourists')

fig_mig = px.line(migs_join, x='agnio', y='total', color=var, labels={'agnio': 'Year', 'total': 'Total Tourists'})
st.plotly_chart(fig_mig)

with st.expander('Explanation'):
    f = open(f'analysis/tourists/{var}.md', 'r')
    st.markdown(f.read())