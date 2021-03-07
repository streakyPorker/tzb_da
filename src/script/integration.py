import pandas as pd
from src.util import *

data = []
direc = name_entry
sql = "insert into origin_data value ({}%s)".format('%s,' * 46)

cnt = 0
i = 0

for j in range(1, 6):  # iter the file
    file = pd.read_csv('../20200724 V1 Release/data_snapshot_20200724/cfda_records_{}.csv'.format(j))
    print('start load file id {}'.format(j))
    for row_num in range(file.shape[0]):
        data = set_default_val(file.loc[row_num].values.tolist())
        data.insert(0, i)
        i += 1
        # for i in range(len(dir)):
        #     print(i, dir[i], "  ", res[i], "  ", type(res[i]))
        # break
        cursor.execute(sql, data)
        if i % 10000 == 0:
            conn.commit()
    print('file id {} has been loaded!'.format(j))
    conn.commit()
    file.close()
