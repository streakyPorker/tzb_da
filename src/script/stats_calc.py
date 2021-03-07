from src.util import *


@runtime_counter
def calc_total_failing_ratio():
    cursor.execute('select count(id) from fruit_veg')
    total_record_num = cursor.fetchall()[0][0]
    cursor.execute('select count(id) from fruit_veg where Failing is true')
    failing_num = cursor.fetchall()[0][0]
    print(total_record_num, failing_num)


@runtime_counter
def calc_sampling_percentage():
    csv_data = [['', 'Fruit&vegetable Products', '',
                 'Meat Products', '', 'Aquatic Product', ''],
                ['Sampled Location Type'] + ['% of Total Tests', 'Failure Rate'] * 3]
    test_info = {}
    total_failing_dict = {}
    total_line = ['Total']
    for aspect in focus_aspects:

        total_failing_dict[aspect] = 0

        cursor.execute('select count(id) from {} '
                       'where sampled_location_type is not null'.format(aspect))
        total_valid_sample_cnt = cursor.fetchone()[0]

        # print(total_valid_sample_cnt)
        cursor.execute("select sampled_location_type, count(id) from {} "
                       "where sampled_location_type is not null "
                       "group by sampled_location_type"
                       .format(aspect))
        total_valid_samples = dict(cursor.fetchall())  # 统计检测比例

        cursor.execute("select sampled_location_type, count(id) "
                       "from {} "
                       "where sampled_location_type is not null "
                       "and Failing is true "
                       "group by sampled_location_type"
                       .format(aspect))
        failed_samples = dict(cursor.fetchall())  # 统计不合格比例
        for sample_loc in total_valid_samples:  # 汇总一行数据
            if sample_loc not in test_info:
                test_info[sample_loc] = []
            test_info[sample_loc] += [percent(total_valid_samples[sample_loc], total_valid_sample_cnt),
                                      percent(failed_samples[sample_loc], total_valid_samples[sample_loc])]
            total_failing_dict[aspect] += failed_samples[sample_loc]

        total_line += [1, total_failing_dict[aspect] / total_valid_sample_cnt]

    for item in test_info.items():
        csv_data.append([item[0]] + item[1])
    csv_data.append(total_line)

    # total_line = ['Total']
    # for aspect in focus_aspects:
    #     cursor.execute('select count(id) from {} '
    #                    'where sampled_location_type is not null '
    #                    'group by Failing '
    #                    'order by Failing '.format(aspect))
    #     rst = cursor.fetchall()
    #     total_line += ["100.0%", percent(rst[1][0], rst[0][0] + rst[1][0])]
    # csv_data.append(total_line)

    pd.DataFrame(csv_data).to_excel('../output/sampling_percentage.xlsx', header=False, index=False)


@runtime_counter
def calc_adulterant_category_by_sample_loc_type():
    adulterant_category = ['Pesticide and veterinary drug', 'Food additive', 'Environmental contaminant',
                           'Microbial contamination',
                           'Specification', 'Toxin', 'Nutrient supplement']
    csv_data = [['Prod Category', 'Sampled Location Type', ] + adulterant_category]
    for aspect in focus_aspects:
        total_pct = {}
        cursor.execute("select count(id) from {} "
                       "where  Failing is true and "
                       "adulterant_category is not null and "
                       "sampled_location_type is not null".format(aspect))
        aspect_all_failing_num = cursor.fetchone()[0]
        for loc_type in get_sample_loc_type(aspect):
            cursor.execute('select adulterant_category,count(id) '
                           'from {} '
                           'where Failing is true and adulterant_category is not null '
                           "and sampled_location_type like '{}' "
                           'group by adulterant_category'.format(aspect, loc_type))
            temp_dict = dict(cursor.fetchall())
            # cursor.execute('select count(id) '
            #                'from {} '
            #                'where Failing is true and adulterant_category is not null '
            #                "and sampled_location_type like '{}' ".format(aspect, loc_type))
            type_all_failing_num = aspect_all_failing_num
            adder = []
            for cat in adulterant_category:
                if cat not in total_pct:
                    total_pct[cat] = 0
                if cat in temp_dict:
                    adder.append(percent(temp_dict[cat], type_all_failing_num))
                    total_pct[cat] += temp_dict[cat] / type_all_failing_num
                else:
                    adder.append(percent(0, 1))
            csv_data.append([aspect, loc_type] + adder)

        cursor.execute('select adulterant_category, count(id) '
                       'from {} '
                       'where adulterant_category is not null and '
                       "sampled_location_type is not null and "
                       "Failing is true "
                       'group by adulterant_category'.format(aspect))
        aspect_failing_dict = dict(cursor.fetchall())
        total_line = ['Total', 'Total']
        for cat in adulterant_category:
            if cat in aspect_failing_dict:
                total_line.append(percent(aspect_failing_dict[cat], aspect_all_failing_num))
            else:
                total_line.append(percent(0))
        csv_data.append(total_line)

    pd.DataFrame(csv_data).to_excel('../output/adulterant_category_by_sample_loc_type.xlsx', header=False, index=False)


@runtime_counter
def calc_failing_ratio_with_manufacturer_type():
    csv_data = []
    cursor.execute('select distinct manufacturer_type '
                   'from fruit_veg '
                   'where manufacturer_type is not null')
    mtype_list = [i[0] for i in cursor.fetchall()]
    csv_data.append(['aspect', 'sampled location type\\manufacturer type'] + mtype_list)
    for aspect in focus_aspects:
        cursor.execute('select distinct sampled_location_type '
                       'from {} '
                       'where sampled_location_type is not null;'.format(aspect))
        stype_list = [i[0] for i in cursor.fetchall()]

        for stype in stype_list:
            line = [aspect, stype]
            for mtype in mtype_list:
                cursor.execute("select Failing,count(id) from {} "
                               "where sampled_location_type like '{}' and manufacturer_type like '{}' "
                               "group by Failing".format(aspect, stype, mtype))
                rst_dict = dict(cursor.fetchall())
                print(rst_dict.items())
                if len(rst_dict) != 0:
                    if 1 not in rst_dict.keys():
                        line.append(0)

                    elif 0 not in rst_dict.keys():
                        line.append(1)
                    else:
                        line.append(rst_dict[1] / (rst_dict[0] + rst_dict[1]))
                else:
                    line.append('/')
            csv_data.append(line)
    pd.DataFrame(csv_data).to_excel('../output/failing_ratio_group_by_manufacturer_type.xlsx', header=False,
                                    index=False)


@runtime_counter
def calc_failing_ratio_with_data_source():
    csv_data = [['', 'prefecture', 'province', 'central']]
    for aspect in focus_aspects:
        cursor.execute('select data_source_general, Failing, count(id) '
                       'from {} '
                       'group by data_source_general, Failing '
                       'order by data_source_general'.format(aspect))
        triples = cursor.fetchall()
        adder = [aspect] + [0] * 3
        # print(csv_data[0])
        for i in range(3):
            i = 2 * i
            adder[csv_data[0].index(triples[i][0])] = triples[i + 1][2] / (triples[i + 1][2] + triples[i][2])
        csv_data.append(adder)
    pd.DataFrame(csv_data).to_excel('../output/failing_ratio_group_by_data_source.xlsx', header=False, index=False)


@runtime_counter
def calc_failing_ratio_group_by_xxx(xxx):
    """
    :param xxx: param to be grouped by
    :return:
    """
    cursor.execute('select distinct {} from origin_data where {} is not null '.format(xxx, xxx))
    csv_data = [[''] + [item[0] for item in cursor.fetchall()]]
    data_len = len(csv_data[0]) - 1
    for aspect in focus_aspects:
        cursor.execute('select {}, Failing, count(id) '
                       'from {} '
                       'where {} is not null '
                       'group by {}, Failing '
                       'order by {}'.format(xxx, aspect, xxx, xxx, xxx))
        triples = cursor.fetchall()
        adder = [aspect] + ['/'] * data_len
        for i in range(data_len):
            i = 2 * i
            adder[csv_data[0].index(triples[i][0])] = triples[i + 1][2] / (triples[i + 1][2] + triples[i][2])
        csv_data.append(adder)
    pd.DataFrame(csv_data).to_excel('../output/failing_ratio_group_by_{}.xlsx'.format(xxx),
                                    header=False,
                                    index=False)


if __name__ == '__main__':
    # calc_sampling_percentage()
    # calc_adulterant_category_by_sample_loc_type()
    # calc_failing_ratio_with_data_source()
    # re.findall(r'\d+.\d+', 'wergwrg22.4rtge')
    # calc_failing_ratio_with_manufacturer_type()
    calc_failing_ratio_group_by_xxx('data_source_province')
