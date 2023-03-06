import pandas               as pd
import plotly.express       as px
import streamlit            as st
import plotly.graph_objects as go 

from plotly.subplots import make_subplots
import inflection

dataframe = pd.read_csv('datasets/zomato.csv')


# Preenchimento do nome dos países

def country_name(country_id):
    COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
    }
    return COUNTRIES[country_id]

def to_dolar(country_name):
    # Conversão dólar
    CURRENCY = {
     "India": 83,
     "Australia": 1.47,
     "Brazil": 5.20,
     "Canada": 1.36,
     "Indonesia": 15.97,
     "New Zeland": 1.61,
     "Philippines": 55.11,
     "Qatar": 3.64,
     "Singapure": 1.34,
     "South Africa": 18.23,
     "Sri Lanka": 365,
     "Turkey": 19,
     "United Arab Emirates": 3.7,
     "England": 0.83,
     "United States of America": 1,
    }
    return CURRENCY[country_name]

def create_price_type(price_range):
    # Criação do Tipo de Categoria de Comida
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

def color_name(color_code):
    # Criação do nome das Cores
    COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
    }
    return COLORS[color_code]

def rename_columns(dataframe):
    # Renomear as colunas do DataFrame
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

def format_df(dataframe):
    # Formatting df
    df = rename_columns(dataframe)
    # Removing NaN
    df = df.loc[~df['cuisines'].isna(),:]
    # Removing columns
    df = df.drop(columns=['switch_to_order_menu'])
    # Column price_range_type
    df['price_range_type'] = df['price_range'].apply(lambda x: create_price_type(x) )
    # Column country_name
    df['country_name'] = df['country_code'].apply(lambda x: country_name(x))  
    # Columns color_name
    df['color_name'] = df['rating_color'].apply(lambda x: color_name(x) ) 
    # Cuisines
    df['cuisines'] = df.loc[:, 'cuisines'].apply(lambda x: x.split(",")[0])
    # Changing types
    df.loc[: , ['restaurant_id','country_code']] = df.loc[: , ['restaurant_id','country_code']].astype(str)
    # Dolar conversion
    df['dolar_price'] = df[['average_cost_for_two','country_name']].apply(lambda x: x['average_cost_for_two'] / to_dolar(x['country_name']), axis=1).round(2)
    df = df.loc[ df['dolar_price'] < 17006814.29 ]
    # Convert boolean colums
    df['has_delivery'] = df['has_online_delivery'].apply(lambda x: True if x == 1 else False)
    df['has_booking'] = df['has_table_booking'].apply(lambda x: True if x == 1 else False)
    # Reset index
    df = df.reset_index(drop=True)
    
    return df

def streamlit_config():
    st.set_page_config(layout="wide", page_title="Zomato Restaurants")  
    # tab1, tab2, tab3 = st.tabs(['Visao Gerencial', 'Visão Tática', 'Visão Geográfica'])
    ## sidebar
    st.sidebar.markdown('# Zomato Restaurants')
    st.sidebar.markdown('## Here you find the best restaurants')
    st.sidebar.markdown("""---""")
    return None


######## SIDEBAR FILTERS
def country_filter(df):
    countries_list  = df.loc[:,'country_name'].sort_values().unique()
    
    country_multiselect = st.sidebar.multiselect(
                            'Choose the country:',
                            options = countries_list,
                                  )    

    if len(country_multiselect) == 0:
        country_multiselect = df.loc[:,'country_name'].sort_values().unique()
    else:
        pass
    
    return country_multiselect

def sidebar_filters(df, country_multiselect):
    price_range_list  = df.loc[:,'price_range_type'].sort_values().unique()
    # countries_list  = df.loc[:,'country_name'].sort_values().unique()
    cities_list  = df.loc[ df['country_name'].isin(country_multiselect) ,'city'].sort_values().unique()

    min_value_cost    = int(df['dolar_price'].min())
    max_value_cost    = int(df['dolar_price'].max())
    median_value_cost = int(df['dolar_price'].median())

    city_multiselect = st.sidebar.multiselect(
                            'Choose the city:',
                            options = cities_list,
                                  )

    price_range_multiselect = st.sidebar.multiselect(
                                'Choose the price range:',
                                options = price_range_list,
                                      )

    price_slider = st.sidebar.slider(
                    'Choose the maximum price (USD) desired:',
                    value     = 37000,
                    min_value = min_value_cost,
                    max_value = max_value_cost)
    
    has_delivery =  st.sidebar.radio(
    "Has delivery?",
    ('Yes', 'No', 'Both'))

    if has_delivery == 'Yes':
        delivery = [True]
    elif has_delivery == 'No':
        delivery = [False]
    else: 
        delivery = [True,False]
        
    has_booking = st.sidebar.checkbox('Has Booking?')
    
    if has_booking:
        booking = [1]
    else:
        booking = [1,0]

    if len(city_multiselect) == 0:
        city_multiselect = df.loc[:,'city'].sort_values().unique()
    else:
        pass

    if len(price_range_multiselect) == 0:
        price_range_multiselect = df.loc[:,'price_range_type'].sort_values().unique()
    else:
        pass
    
    st.sidebar.markdown("""---""")
    
    columns =  st.sidebar.radio(
    "Map - Identify by:",
    ('cuisines', 'has_booking', 'has_delivery', 'price_range_type'))
    
    st.sidebar.markdown("""---""")
    st.sidebar.markdown('### Powered by Comunidade DS')
    
    # return country_multiselect, city_multiselect, price_range_multiselect, price_slider
    return city_multiselect, price_range_multiselect, price_slider, delivery, booking, columns

def filter_df(price_range_multiselect, country_multiselect, city_multiselect, price_slider, delivery, booking):
    selected_lines = (df['price_range_type'].isin(price_range_multiselect)) & (df['country_name'].isin(country_multiselect)) & (df['city'].isin(city_multiselect)) & (df['average_cost_for_two'] <= price_slider) & (df['has_delivery'].isin(delivery)) & (df['has_booking'].isin(booking))
    filtered_df = df.loc[ selected_lines , :]
    
    return filtered_df

def first_container(df):
    st.markdown("<h1 style='text-align: center; color: grey;'>Restaurants World Map</h1>", unsafe_allow_html=True)

    fig = px.scatter_mapbox( df,
                      lat='latitude',
                      lon='longitude',
                      color=columns,
                      size='average_cost_for_two',
                      hover_name='restaurant_name',
                      zoom=1
                     )
    fig.update_layout(mapbox_style='open-street-map')
    fig.update_layout(margin={'r':0, 'l':0, 't':0, 'b':0})
    st.plotly_chart( fig, use_container_width=True )
    st.text('Choose the identifier on the left side filters')    

    return None


#################
### StreamLit ###
#################

## Streamlit Page
streamlit_config()

## Dataframe
df = format_df(dataframe)

# Sidebar Filters
country_multiselect = country_filter(df)

city_multiselect, price_range_multiselect, price_slider, delivery, booking, columns = sidebar_filters(df, country_multiselect)

# Filtered DF
df = filter_df(price_range_multiselect, country_multiselect, city_multiselect, price_slider, delivery, booking)

# Graph 01
first_container(df)

