import top
import numpy as np
import pandas as pd

data = pd.read_excel('../model/manual.xlsx', sheet_name=None)


def simulateR(u):
    bench = [([0] * u) for _ in range(u)]
    for i in range(u):
        bench[i][i] = 1
    return np.array(bench)


def simulateA(m):
    return np.array([[0] * m] * m)


def simulateB(u, m):
    rst = np.array([[1] * m] * u)
    assert rst.shape == (u, m)
    return rst


def simulateC(n):
    return np.array([1] * n)


def getR(u):
    # return np.array([
    #     [1, 0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #
    # ])
    return data['R'].values[:u, 1:u + 1]


def getA(m):
    rst = data['A'].values[:m, 1:]
    assert rst.shape == (m, m)
    return rst


def getB(u, m):
    rst = data['B'].values[:u, 1:m + 1]
    assert rst.shape == (u, m)
    return rst


def getC(n):
    return np.array([1] * n)
