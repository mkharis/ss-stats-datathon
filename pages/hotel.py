import datetime
import numpy as np
import os
import pandas as pd
import plotly.express as px
import pmdarima as pm
import streamlit as st

@st.cache_data
def load_migration():
    data = pd.read_csv('migration/total.csv')
    return data

@st.cache_data
def load_capitulo(c):
    data = {}
    for y in range(2012, 2016):
        data[y] = pd.read_csv(f'EAH/EAH_{y}/Capitulo{c}_{y}.csv', sep=';')
    return data

col_descs = [
    'VOCONSBL - Volume of bulk water consumption (in cubic meters/year)',
    'C3RHB3b3B - Volume of untreated wastewater discharged into rivers, lakes, and wetlands',
    'C3RHB3d3B - Volume of untreated wastewater discharged into the sea',
    'C4RGA1aRO - Generated organic waste (food) in Kg/year',
    'C4RGA2aPC - Generated paper and cardboard waste in Kg/year',
    'C4RGA3aP - Generated plastic waste in Kg/year',
    'C4RGA5aMT - Generated metal waste in Kg/year',
    'C4RGA6aT - Generated textiles waste in Kg/year',
    'C4RGA7aNMT - Generated non-metallic waste in Kg/year',
    'C4RGA4aV - Generated glass waste in Kg/year',
    'C5REB1a - Electricity consumption (kWh/year)',
    'C5REB2a - Natural gas consumption (m³/year)',
    'C5REB3a - LPG (Liquefied Petroleum Gas) consumption (L/year)',
    'C5REB16a - Gasoline consumption (gallons/year)',
    'C5REB4a - Diesel consumption (gallons/year)',
    'C5REB5a - Fuel oil consumption (gallons/year)',
    'C5REB6a - Crude oil consumption (gallons/year)',
    'C5REB7a - Kerosene consumption (gallons/year)',
    'C5REB8a - Mineral coal consumption (Kg/year)',
    'C5REB10a - Purchased firewood consumption (Kg/year)',
    'C5REB17a - I.F.O. (Intermediate Fuel Oil) consumption (gallons/year)',
    'CONBIOGAS - Biogas consumption (m³/year)'
]

if st.query_params['by'] == 'ihpn_ihpt':
    col_descs_by = [
        'IHPN - Number of nights sold',
        'IHPT - Total guests'
    ]
elif st.query_params['by'] == 'water':
    col_descs_by = [
        'VOCONSBL - Volume of bulk water consumption (in cubic meters/year)'
    ]
elif st.query_params['by'] == 'energy':
    col_descs_by = [
        'C5REB1a - Electricity consumption (kWh/year)',
        'C5REB2a - Natural gas consumption (m³/year)',
        'C5REB3a - LPG (Liquefied Petroleum Gas) consumption (L/year)',
        'C5REB16a - Gasoline consumption (gallons/year)',
        'C5REB4a - Diesel consumption (gallons/year)',
        'C5REB5a - Fuel oil consumption (gallons/year)',
        'C5REB6a - Crude oil consumption (gallons/year)',
        'C5REB7a - Kerosene consumption (gallons/year)',
        'C5REB8a - Mineral coal consumption (Kg/year)',
        'C5REB10a - Purchased firewood consumption (Kg/year)',
        'C5REB17a - I.F.O. (Intermediate Fuel Oil) consumption (gallons/year)',
        'CONBIOGAS - Biogas consumption (m³/year)'
    ]
elif st.query_params['by'] == 'waste':
    col_descs_by = [
        'C4RGA1aRO - Generated organic waste (food) in Kg/year',
        'C4RGA2aPC - Generated paper and cardboard waste in Kg/year',
        'C4RGA3aP - Generated plastic waste in Kg/year',
        'C4RGA5aMT - Generated metal waste in Kg/year',
        'C4RGA6aT - Generated textiles waste in Kg/year',
        'C4RGA7aNMT - Generated non-metallic waste in Kg/year',
        'C4RGA4aV - Generated glass waste in Kg/year'
    ]
elif st.query_params['by'] == 'wastewater':
    col_descs_by = [
        'C3RHB3b3B - Volume of untreated wastewater discharged into rivers, lakes, and wetlands',
        'C3RHB3d3B - Volume of untreated wastewater discharged into the sea'
    ]

mig = load_migration()

if os.path.exists('prediction/ihpn_ihpt.csv') and os.path.exists('prediction/cap3456.csv'):
    ihpn_ihpt = pd.read_csv('prediction/ihpn_ihpt.csv')
    cap3456 = pd.read_csv('prediction/cap3456.csv')
else:
    cap2 = load_capitulo(2)

    ihpn_ihpt = pd.DataFrame()
    for c in cap2:
        ihpn_ihpt = pd.concat([ihpn_ihpt, cap2[c].query('Sede == "Medellín" or Subsede == "Medellín"')[['Periodo', 'IHPN', 'IHPT']]])

    ihpn_ihpt = ihpn_ihpt.groupby('Periodo').sum().reset_index()

    ihpn_ihpt['status'] = 'original data'

    model_ihpn = pm.auto_arima(ihpn_ihpt['IHPN'], np.expand_dims(mig.loc[:3, 'total'].to_numpy(), axis=1), seasonal=False)
    model_ihpt = pm.auto_arima(ihpn_ihpt['IHPT'], np.expand_dims(mig.loc[:3, 'total'].to_numpy(), axis=1), seasonal=False)

    ihpn_ihpt = pd.concat([ihpn_ihpt, pd.DataFrame({
        'Periodo': range(2016, datetime.date.today().year + 1),
        'IHPN': model_ihpn.predict(datetime.date.today().year + 1 - 2016, np.expand_dims(mig.loc[4:, 'total'].to_numpy(), axis=1)).round(),
        'IHPT': model_ihpt.predict(datetime.date.today().year + 1 - 2016, np.expand_dims(mig.loc[4:, 'total'].to_numpy(), axis=1)).round(),
        'status': 'prediction data'
    })])

    ihpn_ihpt.to_csv('prediction/ihpn_ihpt.csv', index=False)

    cap3 = load_capitulo(3)

    cap3_filter = pd.DataFrame()
    for c in cap3:
        cap3_filter = pd.concat([cap3_filter, cap3[c].query('Sede == "Medellín" or Subsede == "Medellín"')[['Periodo', 'VOCONSBL']]])

    cap3_filter = cap3_filter.groupby('Periodo').sum().reset_index()

    cap3456 = cap3_filter

    cap4 = load_capitulo(4)

    cap4_filter = pd.DataFrame()
    for c in cap4:
        cap4_filter = pd.concat([cap4_filter, cap4[c].query('Sede == "Medellín" or Subsede == "Medellín"')[['Periodo', 'C3RHB3b3B', 'C3RHB3d3B']]])

    cap4_filter = cap4_filter.groupby('Periodo').sum().reset_index()

    cap3456 = cap3456.merge(cap4_filter, on='Periodo')

    cap5 = load_capitulo(5)

    cap5_filter = pd.DataFrame()
    for c in cap5:
        cap5_filter = pd.concat([cap5_filter, cap5[c].query('Sede == "Medellín" or Subsede == "Medellín"')[['Periodo', 'C4RGA1aRO', 'C4RGA2aPC', 'C4RGA3aP', 'C4RGA5aMT', 'C4RGA6aT', 'C4RGA7aNMT', 'C4RGA4aV']]])

    cap5_filter = cap5_filter.groupby('Periodo').sum().reset_index()

    cap3456 = cap3456.merge(cap5_filter, on='Periodo')

    cap6 = load_capitulo(6)

    cap6_filter = pd.DataFrame()
    for c in cap6:
        cap6_filter = pd.concat([cap6_filter, cap6[c].query('Sede == "Medellín" or Subsede == "Medellín"')[['Periodo', 'C5REB1a', 'C5REB2a', 'C5REB3a', 'C5REB16a', 'C5REB4a', 'C5REB5a', 'C5REB6a', 'C5REB7a', 'C5REB8a', 'C5REB10a', 'C5REB17a', 'CONBIOGAS']]])

    cap6_filter = cap6_filter.groupby('Periodo').sum().reset_index()

    cap3456 = cap3456.merge(cap6_filter, on='Periodo')

    cap3456['status'] = 'original data'

    mig_ihpn_ihpt = mig.merge(ihpn_ihpt, left_on='agnio', right_on='Periodo')

    model_cap = {}
    cap3456_predict = pd.DataFrame({'Periodo': range(2016, 2025)})

    for col in cap3456.columns[1:-1]:
        model_cap[col] = pm.auto_arima(cap3456[col], mig_ihpn_ihpt.loc[:3, ['total', 'IHPN', 'IHPT']], seasonal=False)
        cap3456_predict[col] = model_cap[col].predict(datetime.date.today().year + 1 - 2016, mig_ihpn_ihpt.loc[4:, ['total', 'IHPN', 'IHPT']]).round().to_list()

    cap3456_predict['status'] = 'prediction data'

    cap3456 = pd.concat([cap3456, cap3456_predict])

    cap3456.to_csv('prediction/cap3456.csv', index=False)

tab1, tab2 = st.tabs(['Prediction', 'Data per Year'])

with tab1:
    if st.query_params['by'] == 'ihpn_ihpt':
        with st.expander('IHPN (Number of nights sold)', expanded=True):
            fig_ihpn = px.line(ihpn_ihpt, x='Periodo', y='IHPN', labels={'Periodo': 'Year', 'IHPN': 'IHPN (Number of nights sold)'}, color='status', color_discrete_sequence=['lime', 'red'])
            st.plotly_chart(fig_ihpn)

        with st.expander('IHPT (Total guests)', expanded=True):
            fig_ihpt = px.line(ihpn_ihpt, x='Periodo', y='IHPT', labels={'Periodo': 'Year', 'IHPT': 'IHPT (Total guests)'}, color='status', color_discrete_sequence=['lime', 'red'])
            st.plotly_chart(fig_ihpt)
    else:
        for col, col_desc in zip([c.split(' - ')[0] for c in col_descs_by], col_descs_by):
            with st.expander(col_desc, expanded=True):
                fig_cap = px.line(cap3456, x='Periodo', y=col, labels={'Periodo': 'Year', col: col_desc}, color='status', color_discrete_sequence=['lime', 'red'])
                st.plotly_chart(fig_cap)

with tab2:
    year = st.slider('Year', cap3456['Periodo'].min(), cap3456['Periodo'].max(), cap3456['Periodo'].min())
    st.markdown(':green[- Original Data]')
    st.markdown(':red[- Prediction Data]')
    if st.query_params['by'] == 'ihpn_ihpt':
        for col, col_desc in zip([c.split(' - ')[0] for c in col_descs_by], col_descs_by):
            col_text = ihpn_ihpt.loc[ihpn_ihpt['Periodo'] == year, col].to_list()[0]
            if ihpn_ihpt.loc[ihpn_ihpt['Periodo'] == year, 'status'].to_list()[0] == 'original data':
                st.markdown(f'{col_desc}: :green[{int(col_text)}]')
            elif ihpn_ihpt.loc[ihpn_ihpt['Periodo'] == year, 'status'].to_list()[0] == 'prediction data':
                st.markdown(f'{col_desc}: :red[{int(col_text)}]')
    else:
        for col, col_desc in zip([c.split(' - ')[0] for c in col_descs_by], col_descs_by):
            col_text = cap3456.loc[cap3456['Periodo'] == year, col].to_list()[0]
            if cap3456.loc[cap3456['Periodo'] == year, 'status'].to_list()[0] == 'original data':
                st.markdown(f'{col_desc}: :green[{int(col_text)}]')
            elif cap3456.loc[cap3456['Periodo'] == year, 'status'].to_list()[0] == 'prediction data':
                st.markdown(f'{col_desc}: :red[{int(col_text)}]')