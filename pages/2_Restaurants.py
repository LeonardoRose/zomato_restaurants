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
    st.sidebar.markdown('### Powered by Comunidade DS')
    
    return city_multiselect, price_range_multiselect, price_slider, delivery, booking

def filter_df(price_range_multiselect, country_multiselect, city_multiselect, price_slider, delivery, booking):
    selected_lines = (df['price_range_type'].isin(price_range_multiselect)) & (df['country_name'].isin(country_multiselect)) & (df['city'].isin(city_multiselect)) & (df['average_cost_for_two'] <= price_slider) & (df['has_delivery'].isin(delivery)) & (df['has_booking'].isin(booking))
    filtered_df = df.loc[ selected_lines , :]
    
    return filtered_df

def metrics(df):
    st.markdown("<h1 style='text-align: center; color: grey;'>Restaurantes</h1>", unsafe_allow_html=True)
    
    rests_uniques = df['restaurant_id'].nunique()
    rest_uniques_rating = df[['aggregate_rating']].mean().round(2)[0]
    
    best_rest = df.loc[: , ['restaurant_name','aggregate_rating','votes'] ].sort_values(by=['aggregate_rating','votes'], ascending=[False,False] ).reset_index().loc[0,'restaurant_name']
    best_rest_rate = df.loc[: , ['restaurant_name','aggregate_rating','votes'] ].sort_values(by=['aggregate_rating','votes'], ascending=[False,False] ).reset_index().loc[0,'aggregate_rating']
    
    worst_rest = df.loc[: , ['restaurant_name','aggregate_rating','votes'] ].sort_values(by=['aggregate_rating','votes'], ascending=[True,False] ).reset_index().loc[0,'restaurant_name']
    worst_rest_rate = df.loc[: , ['restaurant_name','aggregate_rating','votes'] ].sort_values(by=['aggregate_rating','votes'], ascending=[True,False] ).reset_index().loc[0,'aggregate_rating']
    
    with st.container():
        col1, col2, col3 = st.columns( 3 )

        with col1:
            st.metric(label="# Restaurants", value=rests_uniques)

        with col2:
            st.metric(label="# Best:", value=best_rest)

        with col3:
            st.metric(label="# Worst:", value=worst_rest)
            
    with st.container():
        col4, col5, col6 = st.columns( 3 )

        with col4:
            st.metric(label="Avg Rating", value=rest_uniques_rating)

        with col5:
            st.metric(label="Avg Rating:", value=best_rest_rate)

        with col6:
            st.metric(label="Avg Rating", value=worst_rest_rate)
    
    return None

def first_container():
    with st.container():
        col1, col2 = st.columns( 2 )
        
        with col1:
            # st.title('Has Delivery')
            st.markdown("<h1 style='text-align: center; color: black;'>Has Delivery</h1>", unsafe_allow_html=True)
            # Eixo 2o = Avaliação Média
            df_aux = df.loc[:, ['has_delivery','aggregate_rating','average_cost_for_two' ]].groupby(['has_delivery']).mean().reset_index()
            df_aux['has_delivery'] = df_aux['has_delivery'].astype('string')

            # use specs parameter in make_subplots function
            # to create secondary y-axis
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # plot a scatter chart by specifying the x and y values
            # Use add_trace function to specify secondary_y axes.
            fig.add_trace(
                go.Bar(x=df_aux['has_delivery'], y=df_aux['average_cost_for_two'], name="Averace Price"),
                secondary_y=False)

            # Use add_trace function and specify secondary_y axes = True.
            fig.add_trace(
                go.Scatter(x=df_aux['has_delivery'], y=df_aux['aggregate_rating'], name="Mean Rating"),
                secondary_y=True)

            # Naming y-axes
            fig.update_yaxes(title_text=" Average Price ", secondary_y=False)
            fig.update_yaxes(title_text=" Rating ", secondary_y=True)
            
            st.plotly_chart( fig, use_container_width=True )
            
            
        with col2:
            st.markdown("<h1 style='text-align: center; color: black;'>Has Booking</h1>", unsafe_allow_html=True)
            df_aux = df.loc[:, ['has_booking','aggregate_rating','average_cost_for_two' ]].groupby(['has_booking']).mean().reset_index()
            
            df_aux['has_booking'] = df_aux['has_booking'].astype('string')

            # use specs parameter in make_subplots function
            # to create secondary y-axis
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # plot a scatter chart by specifying the x and y values
            # Use add_trace function to specify secondary_y axes.
            fig.add_trace(
                go.Bar(x=df_aux['has_booking'], y=df_aux['average_cost_for_two'], name="Averace Price"),
                secondary_y=False)

            # Use add_trace function and specify secondary_y axes = True.
            fig.add_trace(
                go.Scatter(x=df_aux['has_booking'], y=df_aux['aggregate_rating'], name="Mean Rating"),
                secondary_y=True)

            # Naming y-axes
            fig.update_yaxes(title_text=" Average Price ", secondary_y=False)
            fig.update_yaxes(title_text=" Rating ", secondary_y=True)

            st.plotly_chart( fig, use_container_width=True )

    return None

def second_container():
    # st.title('Price type distribution by Cuisines')
    st.markdown("<h1 style='text-align: center; color: black;'>Price type distribution by Cuisines</h1>", unsafe_allow_html=True)
    x = df.loc[:,['cuisines', 'price_range_type', 'restaurant_id']].groupby(['cuisines','price_range_type']).nunique().sort_values(by='restaurant_id', ascending=False).reset_index()
    fig = px.bar(x, x="cuisines", y="restaurant_id", color="price_range_type")
    
    st.plotly_chart( fig, use_container_width=True )
    
    return None

def third_container(df):
    st.markdown("<h1 style='text-align: center; color: black;'>Do the most expensive restaurants get the best ratings? </h1>", unsafe_allow_html=True)
    aux = df.loc[ : , ['cuisines', 'average_cost_for_two', 'aggregate_rating'] ].groupby(['cuisines']).agg({'average_cost_for_two': 'mean' , 'aggregate_rating': 'mean'}).round(2)

    aux.columns = ['average_cost_for_two','aggregate_rating']
    aux = aux.reset_index()
    # aux = aux.loc[ aux['average_cost_for_two'] < 500 , : ]

    fig = px.scatter(aux, x='average_cost_for_two', y='aggregate_rating', color='cuisines')

    st.plotly_chart( fig, use_container_width=True )
    
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
metrics(df)

# Graph 01
first_container()

# Graph 02
second_container()

# Graph 03
third_container(df)
