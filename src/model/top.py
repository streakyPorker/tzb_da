from src.util import *
from simulation import *
import numpy as np
import math
import re
import json

aspect = ''
sc_vec = []
adlt_vec = []
sub_adlt_vec = []
sub_adlt_dict = {}
R, A, B, C = np.array([]), np.array([]), np.array([]), np.array([])
xi = 2e-6
default_af = 3

aspc_dict = {}


def simulate_params():
    global R, A, B, C
    R = simulateR(len(sc_vec))
    A, B, C = (simulateA(len(adlt_vec)),
               simulateB(len(sc_vec), len(adlt_vec)),
               simulateC(len(sub_adlt_vec)))


def get_params():
    global R, A, B, C
    R, A, B, C = (getR(len(sc_vec)),
                  getA(len(adlt_vec)),
                  getB(len(sc_vec), len(adlt_vec)),
                  getC(len(sub_adlt_vec)))


@runtime_counter
def setup():
    global sc_vec, adlt_vec, sub_adlt_vec
    cursor.execute('select distinct sampled_location_type from {} '
                   'where sampled_location_type is not null '
                   'order by sampled_location_type'.format(aspect))
    sc_vec = [i[0] for i in cursor.fetchall()]
    # print(sc_vec)
    cursor.execute('select distinct adulterant_category from aquatic '
                   'where adulterant_category is not null '
                   'order by adulterant_category')
    adlt_vec = [i[0] for i in cursor.fetchall()]
    # print(adlt_vec,len(adlt_vec))
    for adlt in adlt_vec:
        cursor.execute('select distinct adulterant_sub_category from {} '
                       'where adulterant_sub_category is not null and '
                       "adulterant_category like '{}'".format(aspect, adlt))
        sub_adlt_dict[adlt] = [i[0] for i in cursor.fetchall()]
    # print(sc_vec, adlt_vec)

    cursor.execute('select distinct adulterant_sub_category from {} '
                   'where adulterant_sub_category is not null '
                   'order by adulterant_sub_category'.format(aspect))
    sub_adlt_vec = [i[0] for i in cursor.fetchall()]
    # simulate_params()
    get_params()


def sig_map(x, xi=1):
    if x < 0:
        return 0
    return 2 / (1 + math.exp(-1 * xi * x))


def calc_r_star_vec(u):
    lst = []
    for m in range(len(adlt_vec)):
        a = calc_sub_adlt_weight(u, m)
        b = calc_avg_excessive_amount_evaluation(u, m)
        # print(a.shape, b.shape)
        lst.append(a @ b)
    # return np.array([
    #     a @ b
    #     for m in range(len(adlt_vec))
    # ])
    return np.array(lst)


def calc_sub_adlt_weight(u, m):
    cursor.execute('select adulterant_sub_category,Failing,count(id) from {} '
                   'where adulterant_sub_category is not null '
                   "and sampled_location_type like '{}' "
                   "and adulterant_category like '{}' "
                   'group by adulterant_sub_category,Failing '
                   'order by adulterant_sub_category'.format(aspect, sc_vec[u], adlt_vec[m]))
    temp_dict = {}
    for triple in cursor.fetchall():
        if triple[0] not in temp_dict:
            temp_dict[triple[0]] = [0, 1]
        temp_dict[triple[0]][triple[1]] += triple[2]

    failing_cnt_vec = np.array([  # fits the bucket of sub cat
        temp_dict[i][1] / sum(temp_dict[i]) if i in temp_dict else 0 for i in sub_adlt_vec
    ])
    if (failing_cnt_vec @ C) != 0:
        return failing_cnt_vec * C / (failing_cnt_vec @ C)
    else:
        return np.array([0] * len(sub_adlt_vec))


def calc_adlt_weight(u):
    cursor.execute('select adulterant_category,Failing,count(id) from {} '
                   'where adulterant_category is not null '
                   "and sampled_location_type like '{}' "
                   'group by adulterant_category,Failing '
                   'order by adulterant_category'.format(aspect, sc_vec[u]))
    temp_dict = {}
    for triple in cursor.fetchall():
        if triple[0] not in temp_dict:
            temp_dict[triple[0]] = [0, 1]
        temp_dict[triple[0]][triple[1]] += triple[2]

    failing_cnt_vec = np.array(  # fits the bucket of cat
        [temp_dict[i][1] / sum(temp_dict[i]) if i in temp_dict else 0 for i in adlt_vec]
    )
    return failing_cnt_vec * B[u] / (failing_cnt_vec @ B[u])


def calc_avg_excessive_amount_evaluation(u, m):
    avg_af_dict = {}
    for sub_adlt in sub_adlt_dict[adlt_vec[m]]:
        cursor.execute("select adulterant,test_outcome,legal_limit from {} "
                       "where Failing is true "
                       "and ((test_outcome is not null and legal_limit is not null)or(adulterant is not null)) "
                       "and sampled_location_type like '{}' "
                       "and adulterant_category like '{}' "
                       "and adulterant_sub_category like '{}' "
                       .format(aspect, sc_vec[u], adlt_vec[m], sub_adlt))
        sub_af_lst = []
        rst = cursor.fetchall()
        # print('sub_adlt len : {}'.format(len(rst)))
        for triple in rst:  # 计算超出的幅度

            try:
                if triple[1] is not None and triple[2] is not None:
                    if triple[2].find('不得') or triple[1].find('不得'):
                        sub_af_lst.append(default_af)
                    elif re.findall(r'-?\d+\.?\d*e?-?\d*?', arr[2])[0] != 0:
                        ratio = (re.findall(r'-?\d+\.?\d*e?-?\d*?', triple[1])[0] /
                                 re.findall(r'-?\d+\.?\d*e?-?\d*?', triple[2])[0])
                        if ratio > 1:
                            sub_af_lst.append(ratio - 1)
                else:
                    arr = []
                    for splitter in ['║', '||', '|']:
                        if len(triple[0].split(splitter)) == 3:
                            arr = triple[0].split(splitter)
                            break
                    if len(arr) != 3:
                        continue
                    if re.findall(r'-?\d+\.?\d*e?-?\d*?', arr[2])[0] != 0:
                        ratio = (re.findall(r'-?\d+\.?\d*e?-?\d*?', arr[1])[0] /
                                 re.findall(r'-?\d+\.?\d*e?-?\d*?', arr[2])[0])
                        if ratio > 1:
                            sub_af_lst.append(ratio - 1)
            except BaseException:
                pass
        if len(sub_af_lst) != 0:
            avg_af_dict[sub_adlt] = sum(sub_af_lst) / len(sub_af_lst)
        else:
            avg_af_dict[sub_adlt] = 0
            # print('this actually happens in {} {} {}'.format(sc_vec[u], adlt_vec[m], sub_adlt))
    return np.array([
        avg_af_dict[i] if i in avg_af_dict else 0 for i in sub_adlt_vec
    ])


#    ||

@runtime_counter
def coRISK(aspect_p):
    global aspc, C
    aspc = aspect_p
    setup()
    sc_index = []
    rst_dict = {}
    for u in range(len(sc_vec)):
        print('processing sc {}...'.format(sc_vec[u]))
        adlt_weight = calc_adlt_weight(u)
        r_star_vec = calc_r_star_vec(u)

        # print(adlt_weight,
        #       r_star_vec,
        #       A)
        independent_index = adlt_weight * r_star_vec @ (A @ (adlt_weight * r_star_vec) + 1)
        sc_index.append(independent_index)
        rst_dict[sc_vec[u]] = independent_index
    sc_co_index = R @ np.array(sc_index)
    print(sc_co_index)
    aspc_dict[aspect_p] = rst_dict


if __name__ == '__main__':
    for aspect in focus_aspects:
        print('calculating aspect : {} ...'.format(aspect))
        coRISK(aspect)
    with open('../output/index_with_xi_{}.json'.format(xi), 'w') as f:
        f.write(json.dumps(aspc_dict))

    csv_data = [[''] + sc_vec]
    for a in focus_aspects:
        csv_data.append([a] + [aspc_dict[a][k] for k in sc_vec])

    pd.DataFrame(csv_data).to_excel('../output/index_with_xi_{}.xlsx'.format(xi), header=False, index=False)






