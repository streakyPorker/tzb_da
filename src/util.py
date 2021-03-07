import os
import math
import pymysql as sql
import time
import json
import pandas as pd

"""
const area
"""
name_entry = [
    'manufacturer_name',
    'manufacturer_address',
    'manufacturer_final_county',
    'manufacturer_final_prefecture',
    'manufacturer_final_province',
    'sampled_location_name',
    'sampled_location_address',
    'sampled_location_final_county',
    'sampled_location_final_prefecture',
    'sampled_location_final_province',
    'food_name',
    'specifications_model',
    'production_date',
    'production_year',
    'product_classification',
    'notice_number',
    'announcement_date',
    'announcement_year',
    'task_source_or_project_name',
    'testing_agency',
    'inspection_results',
    'failing_results',
    'adulterant',
    'test_outcome',
    'legal_limit',
    'adulterant_english',
    'adulterant_category',
    'adulterant_category',
    'adulterant_intention',
    'adulterant_possible_source',
    'filename',
    'sheetname',
    'data_source_detailed',
    'data_source_province',
    'data_source_general',
    'inspection_id',
    'prod_category_english',
    'prod_category_english_detailed',
    'prod_category_english_nn',
    'sampled_location_type',
    'manufacturer_type',
    'mandate_level',
    'Failing',
    'fresh_aqua',
    'sampled_date',
    'web_source',
]
focus_aspects = ['fruit_veg', 'aquatic', 'meat']

"""
non-const global
"""
conn = sql.connect(user='root', host='localhost', password='123456', database='tzbv1')
cursor = conn.cursor()
cn_cities = set()


def set_default_val(record):
    """
    process the record from csv to form that is able to be inserted into MySQL database
    :param record:
    :return:
    """
    for i in range(len(record)):
        if type(record[i]) != str:
            record[i] = str(record[i])
        if record[i] == 'nan':
            record[i] = None
        # 转化非字符串类型
        elif name_entry[i].endswith('final_county') \
                or name_entry[i].endswith('final_prefecture') \
                or name_entry[i].endswith('final_province') \
                or name_entry[i].endswith('year') \
                or name_entry[i].endswith('inspection_id') \
                or name_entry[i].endswith('Failing'):
            record[i] = int(float(record[i]))
    return record


def runtime_counter(func):
    def wrapper(*args, **kw):
        start = time.time()
        func(*args, **kw)
        print('runtime of ' + func.__name__ + ':', time.time() - start, "seconds")

    return wrapper


def percent(a, b=1):
    # return "{}%".format(round(a * 100 / b, 1))
    return a / b


def percent2float(pct):
    return float(pct.strip("%")) / 100


@runtime_counter
def load_cn_city_set():
    """
    load all the cn city name to filter the segment of sample name
    :return: None
    """
    global cn_cities
    if len(cn_cities) == 0:
        cn_cities = {'(', ')', '（', '）', '\t', ' '}
        with open('../output/name.json') as f:
            province_list = json.loads(f.read())['provinceList']
            for province in province_list:
                cn_cities.add(province['name'])
                for city in province['cityList']:
                    cn_cities.add(city['name'])
                    for county in city['countyList']:
                        cn_cities.add(county['name'])


def filter_cn_city_name(seg):
    """
    used in the filter function param
    :param seg: seg to be filtered
    :return: if the seg is a city name in China
    """
    for city in cn_cities:
        # if city.find(seg) != -1:
        if city.find(seg) != -1:
            return False
    return True


def get_sample_loc_type(table='origin_data'):
    cursor.execute("select sampled_location_type from {} "
                   "where sampled_location_type is not null "
                   "group by sampled_location_type".format(table))
    return [item[0] for item in cursor.fetchall()]


@runtime_counter
def get_adulterant_category(table='fruit_veg'):
    cursor.execute("select adulterant_category from {} "
                   "where adulterant_category is not null "
                   "group by adulterant_category".format(table))
    rst = cursor.fetchall()
    print([item[0] for item in rst])
    # return [item for item in rst]
    return ['Pesticide and veterinary drug', 'Food additive', 'Environmental contaminant', 'Microbial contamination',
            'Specification', 'Toxin', 'Nutrient supplement']


if __name__ == '__main__':
    print(get_adulterant_category())
