# ===================================================================================== #
#                                         IMPORTS                                       #
# ===================================================================================== #

import os
import re
import logging
import requests
import numpy  as np
import pandas as pd

from datetime   import datetime
from sqlalchemy import create_engine
from bs4        import BeautifulSoup
from datetime   import datetime       as dt

# ===================================================================================== #
#                                     DATA COLLECTION                                   #
# ===================================================================================== #

def data_collection(url, headers):
    # Request to URL
    page = requests.get(url, headers=headers)

    # Beautiful Soup object
    soup = BeautifulSoup(page.text, 'html.parser')

    # Page with all items
    total_item = int(soup.find_all('h2', class_='load-more-heading')[0].get('data-total'))
    # Url showroom with all items
    url_showroom = url + '?page-size=' + str(total_item)

    # Request to URL
    page = requests.get(url_showroom, headers=headers)

    # Beautiful Soup object
    soup = BeautifulSoup(page.text, 'html.parser')


    # ================================== Product Data ==================================
    product_list = soup.find_all('article', class_='hm-product-item')

    # Product id
    product_id = [i.get('data-articlecode') for i in product_list]

    # Product category
    product_category = [i.get('data-category') for i in product_list]

    # Products DataFrame
    data = pd.DataFrame([product_id, product_category]).T
    data.columns = ['product_id', 'product_category']

    # Scrap datetime
    data['scrap_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return data


# ===================================================================================== #
#                                DATA COLLECTION BY PRODUCT                             #
# ===================================================================================== #

def data_collection_by_product(data, headers):
    # Empty dataframe
    df_compositions = pd.DataFrame()

    # Unique columns for all products
    aux = []

    # Creating a dataframe with unique column names
    df_pattern = pd.DataFrame(columns=['Art. No.',
                                       'Composition',
                                       'Fit',
                                       'More sustainable materials',
                                       'Product safety',
                                       'Size'])

    for i in data['product_id']:
        # API Request
        url = 'https://www2.hm.com/en_us/productpage.' + i + '.html'
        logger.debug('Product: %s', url)

        page = requests.get(url, headers=headers)

        # Beautiful Soup object
        soup = BeautifulSoup(page.text, 'html.parser')

        # ================================= Color name =================================
        product_list = soup.find_all('a', class_='filter-option miniature active') + soup.find_all('a', class_='filter-option miniature')
        color_name = [i.get('data-color') for i in product_list]

        # Product id
        product_id = [i.get('data-articlecode') for i in product_list]

        # Creating a dataframe that contains product id + color name
        df_color = pd.DataFrame([product_id, color_name]).T
        df_color.columns = ['product_id', 'color_name']


        for j in df_color['product_id']:
            # API Request
            url = 'https://www2.hm.com/en_us/productpage.' + j + '.html'
            # logger.debug('Color: %s', url)

            page = requests.get(url, headers=headers)

            # Beautiful Soup object
            soup = BeautifulSoup(page.text, 'html.parser')

            # =============================== Product Name =============================
            product_name = soup.find_all('h1', class_='primary product-item-headline')
            product_name = product_name[0].get_text()

            # ============================== Product Price =============================
            product_price = soup.find_all('div', class_='primary-row product-item-price')
            product_price = re.findall(r'\d+\.?\d+', product_price[0].get_text())[0]

            # =============================== Composition ==============================
            product_composition_list = soup.find_all('div', class_='pdp-description-list-item')
            product_composition = [list(filter(None, i.get_text().split('\n'))) for i in product_composition_list]

            # Rename dataframe
            df_composition = pd.DataFrame(product_composition).T
            df_composition.columns = df_composition.iloc[0]

            # Delete first row
            df_composition = df_composition[1:].fillna(method='ffill')

            # Remove pocket lining, shell and lining
            df_composition['Composition'] = df_composition['Composition'].replace('Pocket lining: ', '', regex=True)
            df_composition['Composition'] = df_composition['Composition'].replace('Shell: ', '', regex=True)
            df_composition['Composition'] = df_composition['Composition'].replace('Lining: ', '', regex=True)

            # Garantee the same number of columns
            df_composition = pd.concat([df_pattern, df_composition], axis=0)

            # Rename columns
            df_composition.columns = ['product_id',
                                      'composition',
                                      'fit',
                                      'more_sustainable_materials',
                                      'product_safety',
                                      'size']

            df_composition['product_name'] = product_name
            df_composition['product_price'] = product_price

            # keep new columns if it shows up
            aux = aux + df_composition.columns.tolist()

            # merge data color + composition
            df_composition = pd.merge(df_composition, df_color, how='left', on='product_id')

            # all products
            df_compositions = pd.concat([df_compositions, df_composition], axis=0)

    # Join Showroom data + details
    # Generate style id + color id
    df_compositions['style_id'] = df_compositions['product_id'].apply(lambda x: x[:-3])
    df_compositions['color_id'] = df_compositions['product_id'].apply(lambda x: x[-3:])

    # Scrap datetime
    df_compositions['scrap_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return df_compositions


# ===================================================================================== #
#                                      DATA CLEANING                                    #
# ===================================================================================== #

def data_cleaning(data_product):
    # product_id
    data = data_product.dropna(subset=['product_id'])

    # product_name
    data['product_name'] = data['product_name'].str.replace('\n', '')
    data['product_name'] = data['product_name'].str.replace('\t', '')
    data['product_name'] = data['product_name'].str.replace('  ', '')
    data['product_name'] = data['product_name'].str.replace(' ', '_').str.lower()

    # product_price
    data['product_price'] = data['product_price'].astype(float)

    # color_name
    data['color_name'] = data['color_name'].str.replace(' ', '_').str.lower()

    # fit
    data['fit'] = data['fit'].apply(lambda x: x.replace(' ', '_') \
                                               .replace('/', '_') \
                                               .lower() if pd.notnull(x) else x)

    # size_number
    data['size_number'] = data['size'].apply(lambda x: re.search('\d{3}cm', x).group(0) if pd.notnull(x) else x) \
                                      .apply(lambda x: re.search('\d+', x)    .group(0) if pd.notnull(x) else x)

    # size_model
    data['size_model'] = data['size'].str.extract('(\d+\/\d+)')


    # Break composition by comma
    df1 = data['composition'].str.split(',', expand=True).reset_index(drop=True)

    # cotton | polyester | elastano | elasterell
    df_ref = pd.DataFrame(index=np.arange(len(data)), columns=['cotton', 'polyester', 'elastane', 'elasterell'])


    # ========================= Composition =========================
    # ------- cotton -------
    df_cotton_0 = df1.loc[df1[0].str.contains('Cotton', na=True), 0]
    df_cotton_0.name = 'cotton'

    df_cotton_1 = df1.loc[df1[1].str.contains('Cotton', na=True), 1]
    df_cotton_1.name = 'cotton'

    # Combine
    df_cotton = df_cotton_0.combine_first(df_cotton_1)


    # ------- polyester -------
    df_polyester_0 = df1.loc[df1[0].str.contains('Polyester', na=True), 0]
    df_polyester_0.name = 'polyester'

    df_polyester_1 = df1.loc[df1[1].str.contains('Polyester', na=True), 1]
    df_polyester_1.name = 'polyester'

    # Combine
    df_polyester = df_polyester_0.combine_first(df_polyester_1)


    # ------- elastane -------
    df_elastane_1 = df1.loc[df1[1].str.contains('Elastane', na=True), 1]
    df_elastane_1.name = 'elastane'

    df_elastane_2 = df1.loc[df1[2].str.contains('Elastane', na=True), 2]
    df_elastane_2.name = 'elastane'

    df_elastane_3 = df1.loc[df1[3].str.contains('Elastane', na=True), 3]
    df_elastane_3.name = 'elastane'

    # Combine
    df_elastane_c2 = df_elastane_1.combine_first(df_elastane_2)
    df_elastane = df_elastane_c2.combine_first(df_elastane_3)


    # ------- elasterell -------
    df_elasterell = df1.loc[df1[1].str.contains('Elasterell', na=True), 1]
    df_elasterell.name = 'elasterell'


    # Concatenating aux df
    df_ref = pd.concat([df_ref, df_cotton, df_polyester, df_elastane, df_elasterell], axis=1)

    # Remove duplicated columns
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep='last')]

    # Join of combine with product_id
    df_aux = pd.concat([data['product_id'].reset_index(drop=True), df_ref], axis=1)

    # Format composition data
    df_aux['cotton']     = df_aux['cotton']    .apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)
    df_aux['polyester']  = df_aux['polyester'] .apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)
    df_aux['elastane']   = df_aux['elastane']  .apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)
    df_aux['elasterell'] = df_aux['elasterell'].apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)

    # Final Join - Assuming the highest value
    df_aux = df_aux.groupby('product_id').max().reset_index().fillna(0)
    data = pd.merge(data, df_aux, on='product_id', how='left')

    # Drop columns
    data = data.drop(columns=['size', 'more_sustainable_materials', 'product_safety', 'composition', ], axis=1)

    # Drop duplicates
    data = data.drop_duplicates()

    return data


# ===================================================================================== #
#                                       DATA INSERT                                     #
# ===================================================================================== #

def data_insert(data_product_cleaned):
    # Reordenando as colunas (boas praticas e organização)
    data_insert = data_product_cleaned[[
            'product_id'
        ,   'style_id'
        ,   'color_id'
        ,   'product_name'
        ,   'color_name'
        ,   'fit'
        ,   'product_price'
        ,   'size_number'
        ,   'size_model'
        ,   'cotton'
        ,   'polyester'
        ,   'elastane'
        ,   'elasterell'
        ,   'scrap_datetime'
    ]]

    # Insert data
    conn = create_engine('sqlite:///database_hm.sqlite', echo=False)

    # Data insert
    data_insert.to_sql('tbl_vitrine', con=conn, if_exists='append', index=False)

    return None


# ===================================================================================== #
#                                      MAIN FUNCTION                                    #
# ===================================================================================== #

if __name__ == '__main__':
    # ========== Logging ==========
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Creating datetime log
    datetime_log = dt.now().strftime('%Y-%m-%d')
    file_name = f'logs/webscaping_hm_{datetime_log}.txt'

    logging.basicConfig(
        filename = file_name,
        level = logging.DEBUG,
        format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S'
    )

    logger = logging.getLogger('webscraping_hm')

    # ========== Parameters and constants ==========
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    # URL
    url = 'https://www2.hm.com/en_us/men/products/jeans.html'

    # Data collection
    data = data_collection(url, headers)
    logger.info('data collect done')

    # Data collection by product
    data_product = data_collection_by_product(data, headers)
    logger.info('data collection by product done')

    # Data cleaning
    data_product_cleaned = data_cleaning(data_product)
    logger.info('data product cleaned done')

    # Data insertion
    data_insert(data_product_cleaned)
    logger.info('data insertion done')
