from src.util import *

path = '../../20200724 V1 Release/data_snapshot_20200724/禽肉类产品分类表.xlsx'

df = pd.read_excel(path)

meat_dict = {}
id_dict = {}

for tup in df.values:
    meat_dict[tup[0].strip()] = tup[1]
print(meat_dict)
cursor.execute('SET GLOBAL innodb_buffer_pool_size = 67108864')
conn.commit()
cursor.execute('select id,product_classification from origin_data where product_classification is not null')
while True:
    # 15
    rst = cursor.fetchmany(10000)
    if len(rst) == 0:
        break
    for record in rst:
        if record[1] is not None and str(record[1]).strip() in meat_dict:
            id_dict[record[0]] = meat_dict[str(record[1]).strip()]

print('meat size:', len(id_dict))

with open('../output/id_dict.json', 'w') as f:
    f.write(json.dumps(id_dict))
for key in id_dict:
    cursor.execute('insert into meat select * from origin_data where id = {}'.format(key))
    conn.commit()
