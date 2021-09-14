from src.util import *


@runtime_counter
def calc_stat_by_category():
    tab_data = [['产品类别', '抽检总批次', '不合格批次', '不合格率（%）']]
    cursor.execute(f"select 食品大类,pass,count(食品大类) from test_data "
                   f"group by 食品大类,pass")

    tab_data += build_test_calc(cursor.fetchall())
    pd.DataFrame(tab_data).to_excel(f'../hzda_output/食品大类 .xlsx', header=False,
                                    index=False)


@runtime_counter
def calc_stat_by_agri_category():
    tab_data = [['细分类别', '抽检总批次', '不合格批次', '不合格率（%）']]
    cursor.execute(f"select 食品细类,pass,count(食品细类) from test_data "
                   f"where 食品大类='食用农产品' "
                   f"group by 食品细类,pass")

    tab_data += build_test_calc(cursor.fetchall())
    pd.DataFrame(tab_data).to_excel(f'../hzda_output/食用农产品细分.xlsx', header=False,
                                    index=False)


@runtime_counter
def calc_stat_by_area():
    tab_data = [['区域', '抽检总批次', '不合格批次', '不合格率（%）']]
    cursor.execute(f"select 被抽样单位所在辖区,pass,count(被抽样单位所在辖区) from test_data "
                   f"group by 被抽样单位所在辖区,pass")

    tab_data += build_test_calc(cursor.fetchall())
    pd.DataFrame(tab_data).to_excel(f'../hzda_output/抽样区域.xlsx', header=False,
                                    index=False)


@runtime_counter
def calc_stat_by_position():
    tab_data = [['抽检环节', '抽检总批次', '不合格批次', '不合格率（%）', '抽检场所', '抽检总批次', '不合格批次', '不合格率（%）']]
    cursor.execute(f"select 处室,pass,count(处室) from test_data group by 处室,pass")
    stat_list = build_test_calc(cursor.fetchall())

    for stat in stat_list[:-1]:
        cursor.execute(f"select 抽样地点,pass,count(抽样地点) from test_data "
                       f"where 处室='{stat[0]}' "
                       f"group by 抽样地点,pass")
        for sub_line in build_calc_with_no_sumup(cursor.fetchall()):
            tab_data.append(stat + sub_line)
    sum_up_line = stat_list[-1] * 2
    sum_up_line[4] = '/'
    tab_data.append(sum_up_line)
    pd.DataFrame(tab_data).to_excel(f'../hzda_output/抽样环节.xlsx', header=False,
                                    index=False)


@runtime_counter
def calc_unqualified_category():
    tab_data = [['不合格问题类别', '不合格总批次', '占比（%）']]
    cursor.execute(f"select 不合格项目, count(不合格项目) from test_data "
                   f"where pass = 0 "
                   f"group by 不合格项目 "
                   f"having  count(不合格项目)>0 "
                   f"order by count(不合格项目) desc;")

    for line in cursor.fetchall():
        tab_data.append([line[0], line[1], line[1] / 227])
    pd.DataFrame(tab_data).to_excel(f'../hzda_output/不合格类别分布.xlsx', header=False,
                                    index=False)


def calc_1():
    cursor.execute(f"select * from 不合格物质及其分类")
    type_dict = {}
    for line in cursor.fetchall():
        type_dict[line[0].strip()] = line[1].strip()

    data_dict = {}
    cursor.execute(f"select 不合格项目, 序号, count(不合格项目) from test_data "
                   f"where pass = 0 "
                   f"group by 不合格项目, 序号 "
                   f"order by count(不合格项目) desc")
    rst = cursor.fetchall()
    total_fail_num = {2020: 0, 2021: 0}
    map_list = {}
    for line in rst:
        bad_category = line[0].strip()
        found = False
        total_fail_num[line[1] // 1000000] += 1
        for key in type_dict:
            if key.find(bad_category) != -1 or bad_category.find(key) != -1:
                map_list[bad_category] = type_dict[key]
                data_dict[type_dict[key]] = {2020: 0, 2021: 0}
                found = True
                break
        if not found:
            map_list[bad_category] = "其他"
            data_dict["其他"] = {2020: 0, 2021: 0}
    print(total_fail_num)
    for line in rst:
        data_dict[map_list[line[0].strip()]][line[1] // 1000000] += line[2]
    print(data_dict)

    tab_data = [["不合格项目类别", "不合格记录数", "不合格占比（%）", "不合格记录数", "不合格占比（%）"]]
    for key in data_dict:
        tab_data.append([
            key, data_dict[key][2020], percent(data_dict[key][2020], total_fail_num[2020]),
            data_dict[key][2021], percent(data_dict[key][2021], total_fail_num[2021]),
        ])
    pd.DataFrame(tab_data).to_excel(f'../hzda_output/1_不合格项目与不合格类别对应.xlsx', header=False,
                                    index=False)


def calc_2():
    cursor.execute(f"select 食品大类, 序号, count(食品大类) from test_data "
                   f"where pass = 0 "
                   f"group by 食品大类,序号 order by count(食品大类) desc;")

    total_num = {2020: 0, 2021: 0}
    data_dict = {}
    for line in cursor.fetchall():
        if line[0] not in data_dict:
            data_dict[line[0]] = {2020: 0, 2021: 0}
        data_dict[line[0]][line[1] // 1000000] += line[2]

    cursor.execute("select 序号, count(序号) from test_data "
                   "group by 序号 order by count(序号) desc;")
    for line in cursor.fetchall():
        total_num[line[0] // 1000000] += line[1]

    print(total_num)
    tab_data = [["食品大类", "不合格数", "不合格率（%）", "不合格数", "不合格率（%）", "不合格数", "不合格率（%）", ]]
    for k, v in data_dict.items():
        tab_data.append([
            k,
            v[2020], percent(v[2020], total_num[2020]),
            v[2021], percent(v[2021], total_num[2021]),
            v[2020] + v[2021], percent(v[2021] + v[2020], total_num[2021] + total_num[2020]),
        ])
    pd.DataFrame(tab_data).to_excel(f'../hzda_output/2_按照食品大类划分计算每类食品总的不合格记录频数和不合格率.xlsx', header=False,
                                    index=False)


def calc_3():
    total_num = {2020: 0, 2021: 0}
    data_dict = {}
    cursor.execute("select 序号, count(序号) from test_data "
                   "group by 序号 order by count(序号) desc;")
    for line in cursor.fetchall():
        total_num[line[0] // 1000000] += line[1]
    print(total_num)
    cursor.execute(f"select 食品大类, 序号, count(食品大类) from test_data "
                   f"where pass = 0 "
                   f"group by 食品大类,序号 order by count(食品大类) desc;")
    for line in cursor.fetchall():
        if line[0] not in data_dict:
            data_dict[line[0]] = {2020: 0, 2021: 0}
        data_dict[line[0]][line[1] // 1000000] += line[2]

    fail_rate_list = []
    for k, v in data_dict.items():
        fail_rate_list.append([k, percent(v[2021] + v[2020], total_num[2021] + total_num[2020]), ])
    fail_rate_list = list(
        map(lambda i: i[0], sorted(fail_rate_list, key=lambda i: i[1], reverse=True))
    )[:8]
    cursor.execute(f"select * from 不合格物质及其分类")
    type_dict = {}
    for line in cursor.fetchall():
        type_dict[line[0].strip()] = line[1].strip()

    fail_cat_map_dict = {}
    cursor.execute("select distinct 不合格项目  from test_data where pass=0;")
    for line in cursor.fetchall():
        bad_category = line[0]
        found = False
        for key in type_dict:
            if key.find(bad_category) != -1 or bad_category.find(key) != -1:
                fail_cat_map_dict[bad_category] = key
                found = True
                break
        if not found:
            fail_cat_map_dict[bad_category] = "其他"

    total_fail_dict = {i: 0 for i in fail_rate_list}
    tb_data_dict = {i: {} for i in fail_rate_list}
    cursor.execute(f"select 食品大类,不合格项目,count(食品大类) from test_data "
                   f"where pass=0 "
                   f"group by 食品大类, 不合格项目 order by count(食品大类) desc;")
    for line in cursor.fetchall():
        if line[0] in fail_rate_list:
            total_fail_dict[line[0]] += line[2]
            fail_cat_mapped = fail_cat_map_dict[line[1]]
            if fail_cat_mapped not in tb_data_dict[line[0]]:
                tb_data_dict[line[0]][fail_cat_mapped] = [0, type_dict[fail_cat_mapped]]
            tb_data_dict[line[0]][fail_cat_mapped][0] += line[2]

    tab_data = [["食品类别（不合格率最高的前8类)", "不合格类别", "不合格类别占比"]]
    print(fail_rate_list)
    for big_cate in fail_rate_list:
        for fail_cat, v2 in tb_data_dict[big_cate].items():
            tab_data.append([
                big_cate, fail_cat, v2[0], percent(v2[0], sum([x[0] for x in tb_data_dict[big_cate].values()])), v2[1]
            ])
    # pd.DataFrame(tab_data).to_excel(f'../hzda_output/4_前8类.xlsx', header=False,
    #                                 index=False)

    mid_cat_dict = {i: {} for i in fail_rate_list}
    for big_cate in fail_rate_list:
        for tup in tb_data_dict[big_cate].values():
            mid_cat = tup[1]
            num = tup[0]
            if mid_cat not in mid_cat_dict[big_cate]:
                mid_cat_dict[big_cate][mid_cat] = 0
            mid_cat_dict[big_cate][mid_cat] += num
    tab_data = [["食品类别（不合格率最高的前8类)", "不合格类别", "不合格类别占比"]]
    for big_cate in fail_rate_list:
        for mid_cat in mid_cat_dict[big_cate]:
            tab_data.append([
                big_cate,mid_cat,percent(mid_cat_dict[big_cate][mid_cat],sum(mid_cat_dict[big_cate].values()))
            ])
    pd.DataFrame(tab_data).to_excel(f'../hzda_output/6_前8类占比.xlsx', header=False,
                                    index=False)

@runtime_counter
def alter_postion():
    candidate = ['餐饮', '生产', '流通']
    for cat in candidate:
        cursor.execute(f"update test_data set 处室='{cat}' "
                       f"where 处室 like '%{cat}%'")
    conn.commit()


@runtime_counter
def alter_sample_position():
    candidate = ['餐饮', '流通', '成品库', '（', '）']
    cursor.execute("select 抽样地点,处室 from test_data group by 抽样地点,处室 order by count(抽样地点) desc")
    rst = cursor.fetchall()
    for line in rst:
        bench = line[0]
        pos = line[1]
        for exclude in candidate:
            bench = bench.replace(exclude, "")
        cursor.execute(f"update test_data set 抽样地点='{bench}' where 抽样地点='{line[0]}' and 处室='{pos}' ")
    conn.commit()


def build_test_calc(data):
    rst = build_calc_with_no_sumup(data)
    sum_up = [
        '总计',
        sum([x[1] for x in rst]),
        sum([x[2] for x in rst]),
        sum([x[2] for x in rst]) / sum([x[1] for x in rst])
    ]
    rst.append(sum_up)
    return rst


def build_calc_with_no_sumup(data):
    stat_dict = {}
    for line in data:
        key = line[0]
        if key not in stat_dict:
            stat_dict[key] = [0, 0, 0]
        stat_dict[key][0] += line[2]
        if line[1] == 0:
            stat_dict[key][1] += line[2]
    for key in stat_dict:
        stat_dict[key][2] = stat_dict[key][1] / (stat_dict[key][0] if stat_dict[key][0] != 0 else 1)
    return list(sorted(
        [[key, stat_dict[key][0], stat_dict[key][1], stat_dict[key][2]] for key in stat_dict],
        key=lambda l: l[3],
        reverse=True
    ))


if __name__ == '__main__':
    # calc_stat_by_category()
    # calc_stat_by_area()
    # calc_stat_by_agri_category()
    # calc_stat_by_position()
    # calc_unqualified_category()
    # alter_sample_position()
    # calc_1()
    # calc_2()
    calc_3()
