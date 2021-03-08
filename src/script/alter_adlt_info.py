from src.util import *

info_path = '../newiter/数据处理相关分类表.xlsx'
data = pd.read_excel(info_path, sheet_name=None)  # sheet_name=None时可读取全部表，并用名字索引


@runtime_counter
def parition_of_meat():
    map_dict = {}
    meat_classification = data['畜禽肉产品分类表']
    for item in meat_classification.values:
        map_dict[item[0].strip()] = item[1].strip()

    for item in map_dict.items():
        cursor.execute("update meat set prod_category_english_nn = '{}' "
                       "where product_classification like '{}' ".format(item[1], item[0]))
    conn.commit()

def risk_source_alter():
    risk_info = data['风险来源表']


if __name__ == '__main__':
    parition_of_meat()

    # print(meat_classification.values)
