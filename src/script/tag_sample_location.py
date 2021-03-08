import jieba
from src.util import *

judge_threshold = 600
test_sample_size = 2000
expand_factor = 100
aspect_judgement_dict = {}
specifications_model_info = {}
aspect_loc_type_ratio = {}


@runtime_counter
def init_aspect_loc_type_ratio():
    global aspect_loc_type_ratio
    for aspect in focus_aspects:
        cursor.execute('select count(id) from {} '
                       'where sampled_location_type is not null'.format(aspect))
        aspect_loc_type_ratio[aspect] = {}
        aspect_loc_type_ratio[aspect]['total'] = cursor.fetchone()[0]
        cursor.execute('select sampled_location_type,count(id) from {} '
                       'where sampled_location_type is not null '
                       'group by sampled_location_type'.format(aspect))
        cnt_dict = {}
        for item in cursor.fetchall():
            cnt_dict[item[0]] = item[1] / aspect_loc_type_ratio[aspect]['total']
        aspect_loc_type_ratio[aspect]['ratio'] = cnt_dict

    with open('../output/aspect_loc_type_ratio.json', 'w') as f:
        f.write(json.dumps(aspect_loc_type_ratio))


@runtime_counter
def collect_judgement_set():
    load_cn_city_set()

    for aspect in focus_aspects:
        sql_q = "select sampled_location_name,sampled_location_type from {} " \
                "where sampled_location_name is not null and " \
                "sampled_location_type is not null".format(aspect)
        # print('sql is :', sql_q)
        cursor.execute(sql_q)
        aspc_dict = {}

        for record in cursor.fetchall():
            if record[1] not in aspc_dict:
                aspc_dict[record[1]] = {}
            target = aspc_dict[record[1]]
            filtered_seg_lst = list(
                filter(filter_cn_city_name, jieba.cut(record[0]))
            )  # filter the city name out
            for seg in filtered_seg_lst:  # calc the word frequency
                if seg not in target:
                    target[seg] = 1
                else:
                    target[seg] += 1
        print("finish calculating word frequency list of {}".format(aspect))
        sql_q = "select sampled_location_type,count(id) from {} " \
                "where sampled_location_name is not null and " \
                "sampled_location_type is not null " \
                "group by sampled_location_type ".format(aspect)
        cursor.execute(sql_q)
        specified_sample_num_dict = dict(cursor.fetchall())  # calc the total sample num, to balance the factor

        for key in aspc_dict:  # iter the sampled_location_type
            """
            should be improved
            """
            topk_score_list = list(
                map(
                    lambda item: (item[0], item[1] * expand_factor / specified_sample_num_dict[key]),
                    sorted(aspc_dict[key].items(),
                           key=lambda i: i[1],
                           reverse=True)[:judge_threshold]
                )
            )  # build judgement list
            aspc_dict[key] = topk_score_list

        aspect_judgement_dict[aspect] = aspc_dict
    with open('../output/sample_loc_judge_set.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(aspect_judgement_dict))  # write to file


@runtime_counter
def collect_judgement_set_with_tf_iwf(output_path='../output/sample_loc_tf_iwf_judge_set.json'):
    load_cn_city_set()

    for aspect in focus_aspects:
        print("start calc list of {}".format(aspect))
        sql_q = "select sampled_location_name,sampled_location_type from {} " \
                "where sampled_location_name is not null and " \
                "sampled_location_type is not null".format(aspect)
        # print('sql is :', sql_q)
        cursor.execute(sql_q)
        print('get sql done for {}...'.format(aspect))
        word_dict = {}
        all_word_num = 0

        for record in cursor.fetchall():
            if record[1] not in word_dict:
                word_dict[record[1]] = ''

            word_dict[record[1]] += record[0].strip()  # 将所有文本组合
        print('concat word done for {}...'.format(aspect))
        loc_type_iwf_dict = {}
        loc_type_tf_iwf_dict = {}
        loc_type_set = set(word_dict.keys())

        for loc_type in loc_type_set:
            seg_tf_dict = {}

            seg_list = list(
                filter(filter_cn_city_name,
                       jieba.cut(word_dict[loc_type]))
            )
            all_word_num += len(seg_list)
            # word_dict[loc_type] = seg_list

            for seg in seg_list:
                if seg not in seg_tf_dict:  # calc tf`s 分子
                    seg_tf_dict[seg] = 1
                else:
                    seg_tf_dict[seg] += 1

            for seg in seg_tf_dict:  # 计算iwf的分母
                if seg not in loc_type_iwf_dict:
                    loc_type_iwf_dict[seg] = seg_tf_dict[seg]
                else:
                    loc_type_iwf_dict[seg] += seg_tf_dict[seg]

                seg_tf_dict[seg] = seg_tf_dict[seg] / len(seg_list)  # 完成tf的计算

            loc_type_tf_iwf_dict[loc_type] = seg_tf_dict  # 赋值基于loc_type的tf值

        print("finish calculating tf and half iwf of {}".format(aspect))
        for loc_type in loc_type_set:
            tf_iwf = loc_type_tf_iwf_dict[loc_type]
            for seg in tf_iwf:
                tf_iwf[seg] = tf_iwf[seg] * math.log10(all_word_num / loc_type_iwf_dict[seg]) * expand_factor
            loc_type_tf_iwf_dict[loc_type] = list(  # 排序，取topk
                sorted(tf_iwf.items(),
                       key=lambda i: i[1],
                       reverse=True)[:judge_threshold]
            )

        aspect_judgement_dict[aspect] = loc_type_tf_iwf_dict
        print("finish calc tf-iwf of {}".format(aspect))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(aspect_judgement_dict))  # write to file


@runtime_counter
def load_sample_loc_judgement_set(path='../output/sample_loc_judge_set.json'):
    global aspect_judgement_dict
    if len(aspect_judgement_dict) == 0:
        with open(path, encoding='utf-8') as f:
            aspect_judgement_dict = json.loads(f.read())


def judge_one_sample_name(aspect, sample_loc_name):
    """
    judge one sample of its predicted sample_location_type
    :param aspect: one of focus_aspect
    :param sample_loc_name: name str
    :return: predicted sample_location_type
    """
    score_bench = []
    for item in aspect_judgement_dict[aspect].items():
        score = 0
        for seg in jieba.cut(sample_loc_name):
            score += sum([word_pair[1] if word_pair[0] == seg else 0 for word_pair in item[1]])  # calc score
        score_bench.append((item[0], score))
    return max(score_bench, key=lambda i: i[1])[0]


@runtime_counter
def _test_sample_loc_judgement_accuracy(path='../output/sample_loc_judge_set.json'):
    load_sample_loc_judgement_set(path)
    for aspect in focus_aspects:
        print("checking {} accuracy...".format(aspect))
        sql_q = "select sampled_location_name,sampled_location_type from {} " \
                "where sampled_location_name is not null and " \
                "sampled_location_type is not null".format(aspect)
        cursor.execute(sql_q)

        test_samples = cursor.fetchmany(test_sample_size)
        success_num = 0
        type_all_dict = {}
        type_correct_dict = {}
        type_fail_dict = {}
        for sample in test_samples:
            if sample[1] not in type_all_dict:
                type_all_dict[sample[1]] = 1
            else:
                type_all_dict[sample[1]] += 1

            if sample[1] == judge_one_sample_name(aspect, sample[0]):
                success_num += 1
                if sample[1] not in type_correct_dict:
                    type_correct_dict[sample[1]] = 1
                else:
                    type_correct_dict[sample[1]] += 1
            # else:
            #     if sample[1] not in type_fail_dict:
            #         type_fail_dict[sample[1]] = {}
            #     else:
            #         type_fail_dict
        for key in type_all_dict:
            print("{}`s accuracy rate on type {} is {}".format(aspect, key,
                                                               percent(type_correct_dict[key], type_all_dict[key])))
        print("{}`s accuracy rate is {}".format(aspect, percent(success_num, test_sample_size)))


def predict_sampled_location_type():
    load_sample_loc_judgement_set()
    aspect_absent_dict = {}  # record the absent sample id to leave chance for
    for aspect in focus_aspects:
        print('predicting {}`s sample location name...'.format(aspect))
        absent_list = aspect_absent_dict[aspect] = []
        sql_q = "select sampled_location_name,id from {} " \
                "where sampled_location_name is not null and " \
                "sampled_location_type is null".format(aspect)
        cursor.execute(sql_q)
        predict_list = cursor.fetchall()
        for item in predict_list:
            absent_list.append(item[1])  # record the id
            sql_q = "update {} set sampled_location_type='{}' " \
                    "where id = {}".format(aspect, judge_one_sample_name(aspect, item[0]), item[1])
            cursor.execute(sql_q)
        conn.commit()


if __name__ == '__main__':
    # collect_judgement_set()

    collect_judgement_set_with_tf_iwf()
    _test_sample_loc_judgement_accuracy(path='../output/sample_loc_tf_iwf_judge_set.json')
