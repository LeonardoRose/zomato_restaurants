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
    
    # country_multiselect = st.sidebar.multiselect(
    #                         'Choose the country:',
    #                         options = countries_list,
    #                               )

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
        delivery = [1]
    elif has_delivery == 'No':
        delivery = [0]
    else: 
        delivery = [1,0]
        
    has_booking = st.sidebar.checkbox('Has Booking?')
    
    if has_booking:
        booking = [1]
    else:
        booking = [1,0]
    
    # if len(country_multiselect) == 0:
    #     country_multiselect = df.loc[:,'country_name'].sort_values().unique()
    # else:
    #     pass

    if len(city_multiselect) == 0:
        city_multiselect = df.loc[:,'city'].sort_values().unique()
    else:
        pass

    if len(price_range_multiselect) == 0:
        price_range_multiselect = df.loc[:,'price_range_type'].sort_values().unique()
    else:
        pass
    
    st.sidebar.markdown("""---""")
    st.sidebar.markdown('### Powered by Comunidade DS')
    
    # return country_multiselect, city_multiselect, price_range_multiselect, price_slider
    return city_multiselect, price_range_multiselect, price_slider, delivery, booking

def filter_df(price_range_multiselect, country_multiselect, city_multiselect, price_slider, delivery, booking):
    selected_lines = (df['price_range_type'].isin(price_range_multiselect)) & (df['country_name'].isin(country_multiselect)) & (df['city'].isin(city_multiselect)) & (df['average_cost_for_two'] <= price_slider) & (df['is_delivering_now'].isin(delivery)) & (df['has_table_booking'].isin(booking))
    filtered_df = df.loc[ selected_lines , :]
    
    return filtered_df

# def filter_df(price_range_multiselect, city_multiselect, price_slider):
#     selected_lines = (df['price_range_type'].isin(price_range_multiselect)) & (df['city'].isin(city_multiselect)) & (df['average_cost_for_two'] <= price_slider)
#     filtered_df = df.loc[ selected_lines , :]
    
#     return filtered_df

def country_rests(df):
    # Gráfico 1
    # 01. Gráfico Eixo X = Países / Eixo Y = #restaurantes e eixo secundário média de avaliacao
    df_aux = df.loc[:,['country_name','restaurant_id','aggregate_rating']].groupby(['country_name']).agg({'restaurant_id': ['nunique'] , 'aggregate_rating':['mean']}).round(2)
    df_aux.columns = ['restaurants','mean']
    df_aux = df_aux.reset_index().sort_values('restaurants', ascending=False)

    # use specs parameter in make_subplots function
    st.markdown('### Restaurants by Country')
    # to create secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # plot a scatter chart by specifying the x and y values
    # Use add_trace function to specify secondary_y axes.
    fig.add_trace(
        go.Bar(x=df_aux['country_name'], y=df_aux['restaurants'], name="Restaurants by Country"),
        secondary_y=False)

    # Use add_trace function and specify secondary_y axes = True.
    fig.add_trace(
        go.Scatter(x=df_aux['country_name'], y=df_aux['mean'], name="Mean Rating"),
        secondary_y=True)

    # Naming y-axes
    fig.update_yaxes(title_text=" Restaurants ", secondary_y=False)
    fig.update_yaxes(title_text=" Rating ", secondary_y=True)
    
    return st.plotly_chart( fig, use_container_width=True )

def city_rests(df):
    # #################################
    # 02. Gráfico Eixo X = Cities / Eixo Y = #restaurantes e eixo secundário média de avaliacao

    df_aux = df.loc[:,['city','restaurant_id','aggregate_rating']].groupby(['city']).agg({'restaurant_id': ['nunique'] , 'aggregate_rating':['mean']}).round(2)
    df_aux.columns = ['restaurants','mean']
    df_aux = df_aux.reset_index().sort_values('restaurants', ascending=False)

    # Gráfico 02 - By City

    # use specs parameter in make_subplots function
    st.markdown('### Restaurants by Cities')
    # to create secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # plot a scatter chart by specifying the x and y values
    # Use add_trace function to specify secondary_y axes.
    fig.add_trace(
        go.Bar(x=df_aux['city'], y=df_aux['restaurants'], name="Restaurants by City"),
        secondary_y=False)

    # Use add_trace function and specify secondary_y axes = True.
    fig.add_trace(
        go.Scatter(x=df_aux['city'], y=df_aux['mean'], name="Mean Rating"),
        secondary_y=True)

    # Naming y-axes
    fig.update_yaxes(title_text=" Restaurants ", secondary_y=False)
    fig.update_yaxes(title_text=" Rating ", secondary_y=True)

    return st.plotly_chart( fig, use_container_width=True )    


def cuisines(df):
    # 03. Gráfico Eixo X = Cuisines / Eixo Y = #restaurantes e eixo secundário média de avaliacao
    # Gráfico 03 - By Cuisines

    df_aux = df.loc[:,['cuisines','restaurant_id','aggregate_rating']].groupby(['cuisines']).agg({'restaurant_id': ['nunique'] , 'aggregate_rating':['mean']}).round(2)
    df_aux.columns = ['restaurants','mean']
    df_aux = df_aux.reset_index().sort_values('restaurants', ascending=False).head(20)

    # use specs parameter in make_subplots function
    st.markdown('### Most Popular Cuisines')
    # to create secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # plot a scatter chart by specifying the x and y values
    # Use add_trace function to specify secondary_y axes.
    fig.add_trace(
        go.Bar(x=df_aux['cuisines'], y=df_aux['restaurants'], name="Restaurants by Cuisines"),
        secondary_y=False)

    # Use add_trace function and specify secondary_y axes = True.
    fig.add_trace(
        go.Scatter(x=df_aux['cuisines'], y=df_aux['mean'], name="Mean Rating"),
        secondary_y=True)

    # Naming y-axes
    fig.update_yaxes(title_text=" Restaurants ", secondary_y=False)
    fig.update_yaxes(title_text=" Rating ", secondary_y=True)

    return st.plotly_chart( fig, use_container_width=True )

def home(df):
    st.markdown("<h1 style='text-align: center; color: grey;'>Overview</h1>", unsafe_allow_html=True)
    
    restaurants_uniques = df['restaurant_id'].nunique()
    country_unique = df['country_code'].nunique()
    city_unique = df['city'].nunique()
    avg_rating = round(df['aggregate_rating'].mean(),2)

    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns( 10 )

    with col4:
        st.metric(label="# Países", value=country_unique)

    with col5:
        st.metric(label="# Cidades", value=city_unique)

    with col6:
        st.metric(label="# Restaurants", value=restaurants_uniques)

    with col7:
        st.metric(label="# Avg Rating", value=avg_rating)
    
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

city_multiselect, price_range_multiselect, price_slider, delivery, booking = sidebar_filters(df, country_multiselect)

# Filtered DF
df = filter_df(price_range_multiselect, country_multiselect, city_multiselect, price_slider, delivery, booking)

# Home
home(df)

# Graph 01
country_rests(df)

# Graph 02
city_rests(df)

# Graph 03
cuisines(df)
