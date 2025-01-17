import streamlit as st
import pandas as pd
import math
from pathlib import Path
#### Import Emulator
from EmulatorCore import Emulator

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Climate Models',
    page_icon=':earth_africa:', # This is an emoji shortcode. Could be a URL too.
    layout="wide", # Use the full page instead of a narrow central column
    menu_items={
        # 'Get Help': 'https://www.extremelycoolapp.com/help',
        # 'Report a bug': "https://www.extremelycoolapp.com/bug",
        # 'About': "# This is a header. This is an *extremely* cool app!"
    }     
)


# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data

def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME_GDP = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME_GDP)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP
    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    # Convert years from string to integers
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])

    return gdp_df

gdp_df = get_gdp_data()

def get_data():
    ### Read in emissions data
    DATA_FILENAME_EMISSIONS = Path(__file__).parent/'data/RCPemissions.xlsx'
    Emission = pd.read_excel(DATA_FILENAME_EMISSIONS, sheet_name = 'Emission')
    # Emission = pd.read_excel(r"Data\RCPemissions.xlsx",
    #                   sheet_name = 'Emission')

    # DATA_FILENAME_CMIP = Path(__file__).parent/'data/CMIPparas.xlsx'
    # CMIP = pd.read_excel(DATA_FILENAME_CMIP, sheet_name = 'CMIP')
    # # CMIP = pd.read_excel(r"Data\CMIPparas.xlsx",
    # #                       sheet_name = 'CMIP')
    # CMIP.set_index('Model', inplace=True)

    # DATA_FILENAME_CARBON = Path(__file__).parent/'data/CMIPparas.xlsx'
    # Carbon = pd.read_excel(DATA_FILENAME_CARBON, sheet_name = 'carbon')
    # # Carbon =  pd.read_excel(r"Data\CMIPparas.xlsx",
    # #                       sheet_name = 'carbon')
    # Carbon.set_index('Model', inplace=True)

    return Emission #, CMIP, Carbon

Emission = get_data()

### choose one emission path
emission = Emission['SSP5-34-OS']

### Input emissions data to the emulator
test_Model = Emulator(Carbon_emission=emission)

### Default model prediction
fig=test_Model.Plot_Temp()

# Plot!
st.plotly_chart(fig, use_container_width=True)

### Add a new model
test_Model.update_model('DICE2016')
test_Model.update_model('MMM_CMIP5')
test_Model.update_model('HadGEM2-ES')
test_Model.update_model('INM-CM4')

    ### Default model prediction
fig=test_Model.Plot_Temp()

# Plot!
st.plotly_chart(fig, use_container_width=True)

#### CMIP6 
tatm0 = test_Model.CMIP6_prediction()

### Default model prediction
fig=test_Model.Plot_Temp()

# Plot!
st.plotly_chart(fig, use_container_width=True)


# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_africa: Climate Models :thermometer:

Flexible tool, allowing input of Carbon emission trajectory, to be translated in Temperature profiles for CMIP6 models. 
'''
col1, col2 = st.columns(2)

with col1:

    st.header('Emissions', divider='gray')

    with st.popover("Define Parameters"):
        year_range = st.slider("Select a range of years", 2020, 2100, (2020, 2100))
        # st.write("Year-range:", year_range)

        year_peak = st.slider("Select peak year", 2020, 2100, 2050)
        # st.write("Peak emissions of xx recorded in", year_peak, ".")

        emission_start = st.number_input(
            "Start Carbon emissions", value=1, placeholder="Type a number..."
        )
        emission_peak = st.number_input(
            "Peak Carbon emissions", value=4, placeholder="Type a number..."
        )
        emission_end = st.number_input(
            "End Carbon emissions", value=2, placeholder="Type a number..."
        )

    st.write("Start emission of ", emission_start, " recorded in ", year_range[0],
            "; Peak emissions of ",emission_peak, " recorded in ", year_peak,
            "; End emissions of ",emission_end, " recorded in ", year_range[1])

    # Create emission path, should have years (str) and emission values as columns
    emission = Emission[['Year','SSP5-34-OS']]

    # Plot the Emission Path
    st.line_chart(
        emission,
        x='Year',
        y='SSP5-34-OS'
    )

    with st.expander("Define Parameters"):
        year_range = st.slider("Select a range of years bis", 2020, 2100, (2020, 2100))
        # st.write("Year-range:", year_range)

        year_peak = st.slider("Select peak year bis", 2020, 2100, 2050)
        # st.write("Peak emissions of xx recorded in", year_peak, ".")

        emission_start = st.number_input(
            "Start Carbon emissions bis", value=1, placeholder="Type a number..."
        )
        emission_peak = st.number_input(
            "Peak Carbon emissions bis", value=4, placeholder="Type a number..."
        )
        emission_end = st.number_input(
            "End Carbon emissions bis", value=2, placeholder="Type a number..."
        )

    uploaded_file = st.file_uploader("Or if you prefer to use your own file")


with col2:

    st.header('Temperatures', divider='gray')

    list_CMIP6_models = [
    "CMIP6-MMMean",
    "ACCESS-ESM1-5",
    "AWI-CM-1-1-MR",
    "BCC-CSM2-MR",
    "BCC-ESM1",
    "CAMS-CSM1-0",
    "CMCC-CM2-SR5",
    "CNRM-CM6-1",
    "CNRM-CM6-1-HR",
    "CNRM-ESM2-1",
    "FGOALS-g3",
    "GISS-E2-1-G",
    "GISS-E2-1-H",
    "GISS-E2-2-G",
    "MIROC6",
    "MIROC-ES2L",
    "MPI-ESM1-2-HR",
    "MPI-ESM1-2-LR",
    "MRI-ESM2-0",
    "NorCPM1",
    "SAM0-UNICON"
    ]

    # # Compute the Emission paths for all possible models (CMIP6, maybe CMIP5 also) into a dataframe
    # raw_tatm_df = 
    # # Present the Dataframe with columns: Year, Model, Temperature
    # tatm_df = raw_tatm_df.melt(
    #     ['Model Code'],
    #     [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
    #     'Year',
    #     'Temperature',
    # )
    # # Convert years from string to integers
    # tatm_df['Year'] = pd.to_numeric(tatm_df['Year'])

    # Ask the user to select the models they want to display

    with st.popover("Choose models displayed"):
        container = st.container()
        all = st.checkbox("Select all CMIP6 models")

        if all:
            selected_models = container.pills("Select one or more models:",
                selection_mode="multi", options=list_CMIP6_models, default=list_CMIP6_models)
        else:
            selected_models =  container.pills("Select one or more models:",
                selection_mode="multi", options=list_CMIP6_models)

    # # Filter the dataframe according the the users' choice of models
    # filtered_tatm_df = tatm_df[
    #     (tatm_df['Model'].isin(selected_models))
    #     # & (gdp_df['Year'] <= to_year)
    #     # & (from_year <= gdp_df['Year'])
    # ]

    # # Plot the Temperatures
    # st.line_chart(
    #     filtered_tatm_df,
    #     x='Year',
    #     y='Temperature',
    #     color='Model',
    # )

# Add some spacing
''
''

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: GDP dashboard

Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
But it's otherwise a great source of data.
'''

# Add some spacing
''
''

min_value = gdp_df['Year'].min()
max_value = gdp_df['Year'].max()

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

countries = gdp_df['Country Code'].unique()

if not len(countries):
    st.warning("Select at least one country")

selected_countries = st.multiselect(
    'Which countries would you like to view?',
    countries,
    ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])

''
''
''

# Filter the data
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries))
    & (gdp_df['Year'] <= to_year)
    & (from_year <= gdp_df['Year'])
]

st.header('GDP over time', divider='gray')

''

st.line_chart(
    filtered_gdp_df,
    x='Year',
    y='GDP',
    color='Country Code',
)

''
''


first_year = gdp_df[gdp_df['Year'] == from_year]
last_year = gdp_df[gdp_df['Year'] == to_year]

st.header(f'GDP in {to_year}', divider='gray')

''

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]

    with col:
        first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
        last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000

        if math.isnan(first_gdp):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{country} GDP',
            value=f'{last_gdp:,.0f}B',
            delta=growth,
            delta_color=delta_color
        )
