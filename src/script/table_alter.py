from src.util import *
import json

alter_dict = {
    'wholesale/retail': 'wholesale market',
    'wet market/wholesale market': 'wet market',
    'other supermarket/convenience store': 'chain supermarket',
    'online store': 'chain supermarket',
    'eatery': 'restaurant',
    'cafeteria': 'restaurant',
}


@runtime_counter
def reclassify_sc_type():
    sample_backup_dict = {}
    manu_backup_dict = {}
    cursor.execute('select id,sampled_location_type,manufacturer_type from origin_data '
                   'where sampled_location_type is not null or '
                   'manufacturer_type is not null ')
    rst = cursor.fetchall()
    print(len(rst))
    cnt = 0
    for triple in rst:
        if triple[1] in alter_dict or triple[2] in alter_dict:
            if triple[1] in alter_dict:
                cursor.execute("update origin_data set sampled_location_type='{}' "
                               "where id={}".format(alter_dict[triple[1]], int(triple[0])))
                sample_backup_dict[triple[0]] = triple[1]
            if triple[2] in alter_dict:
                cursor.execute("update origin_data set manufacturer_type='{}' "
                               "where id={}".format(alter_dict[triple[2]], int(triple[0])))
                manu_backup_dict[triple[0]] = triple[2]
            cnt += 1
            if cnt == 1000:
                conn.commit()
                cnt = 0

    print(conn.commit())
    cursor.close()
    with open('../backup/sc_type_bak.json', 'w') as f:
        f.write(json.dumps({'sampled_location_type': sample_backup_dict,
                            'manufacturer_type': manu_backup_dict}))


if __name__ == '__main__':
    reclassify_sc_type()
    # cursor.execute('select distinct sampled_location_type,manufacturer_type from aquatic limit 200;')
    # rst = cursor.fetchall()
    # for t in rst:
    #     print(t)
