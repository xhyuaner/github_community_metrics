# -*- coding: utf-8 -*-
"""

@author: Liu
"""
from matplotlib import pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd


# 获取分段
def get_section_data(df, column_name, section):
    # 不同分段的数据集合
    sec_data_sum = []
    # 根据指定列对应的分段依据section对数据进行分段
    sec_column = df[column_name]
    for i in range(len(section) - 1):
        # 一个分段的数据
        sec_data = df[(sec_column > section[i]) & (sec_column <= section[i + 1])]
        sec_data_sum.append(sec_data)
    return sec_data_sum


# 权重计算（参考CRITIC赋权方法）
def get_weight(df, normal_method='MMN'):
    columns_list = df.columns.tolist()
    # 1、数据规范化
    if normal_method == 'MMN':          # 最小最大值规范化
        scaler = lambda x: (x - np.min(x)) / (np.max(x) - np.min(x))
        one_sec_data = df[columns_list].apply(scaler)
    elif normal_method == 'ZSN':        # 零均值规范化
        scaler = lambda data: (data - data.mean()) / data.std()
        one_sec_data = df[columns_list].apply(scaler)
    elif normal_method == 'DSN':        # 小数定标规范化
        # 记录小数定标规范化公式的分母
        denominator = []
        for col_index in columns_list:
            denominator.append(10 ** len(str(int(np.max(df[col_index])))))
        one_sec_data = df[columns_list] / denominator
    else:
        return "规范化参数错误！"
    # 2、计算各维度的数据变异性（标准差）
    indices_std = np.std(one_sec_data)
    # 3、计算各维度的数据冲突性
    corr_coef = np.corrcoef(one_sec_data.T)     # 获取各维度的相关系数矩阵
    indices_conflict = np.array(1-corr_coef).sum(axis=1)
    # 4、计算信息量
    information = []
    for x in range(len(indices_conflict)):
        information.append(indices_std[x] * indices_conflict[x])
    # print("信息量：", information)
    # 5、计算权重
    sec_weight = []
    for y in information:
        sec_weight.append(y/np.array(information).sum())
    # return indices_std, indices_conflict, information, sec_weight
    return sec_weight


# 绘制各分段仓库数量统计图
def get_figure(section, dep_number):
    # 设置中文显示
    my_font = font_manager.FontProperties(fname="C:/Windows/Fonts/msyh.ttc", size=15)
    plt.figure(figsize=(12, 8), dpi=80)
    plt.bar(range(len(section) - 1), dep_number)
    plt.xticks(range(len(section) - 1), list(f"{section[i]}-{section[i + 1]}" for i in range(len(section) - 1)))
    plt.xlabel("志愿者完成issue数量", fontproperties=my_font)
    plt.ylabel("仓库数量", fontproperties=my_font)
    plt.title("各段志愿者完成issue数量所含的仓库数量图", fontproperties=my_font, pad=30)
    plt.grid(alpha=0.3)
    plt.show()
    return


# if __name__ == '__main__':
#     # 读取文件
#     # df = pd.read_csv("./data/new_data3.csv")
#     df = pd.read_excel("./data/total_info.xlsx")
#     df = df.loc[:, ("myItems", "watches", "forks", "parItems", "pr_count", "pr_merged_count", "pr_review_count", "followers")]
#     # df = df.loc[1:, ("志愿者完成issue数量", "志愿者完成pr数量")]
#     # print(df.head(5))
#     sec_weight = get_weight(df, normal_method='MMN')
    # indices_std, indices_conflict, information, sec_weight = get_weight(df, normal_method='MMN')
    # print("指标变异性：")
    # print(indices_std)
    # print("指标冲突性：")
    # print(indices_conflict)
    # print("信息量：")
    # print(information)
    # print("各分段权重：")
    # print(sec_weight)

    # # 设置"志愿者人数"字段分段依据
    # # section = [0, 10, 100, 500, 1000, 5000, 20000]
    # # 设置"志愿者完成issue数量"字段分段依据
    # section = [0, 10, 50, 100, 500, 1000, 50000]
    # # 设置"志愿者完成pr数量"字段分段依据
    # # section = [0, 10, 50, 100, 500, 5000, 70000]
    # # 按照指定列对应的分段依据获取分段后的各段数据
    # sec_data_sum = get_section_data(df, column_name="志愿者完成issue数量", section=section)
    # # print(sec_data_sum)
    # dep_number = [len(element) for element in sec_data_sum]
    # print("各段完成issue数所包含的仓库数量:", dep_number)

    # # 计算各分段的不同维度的权重
    # weight = []
    # for i in range(len(sec_data_sum)):
    #     one_sec_data = sec_data_sum[i]
    #     # 如果该分段所包含的仓库数量 大于 该分段间距，则采用“ 零均值规范化(ZSN) ”
    #     if dep_number[i] > (section[i + 1] - section[i]):
    #         sec_weight = get_weight(one_sec_data, normal_method='ZSN')
    #     # 如果该分段所包含的仓库数量 小于 该分段间距，则采用“ 最小最大值规范化(MMN) ”
    #     else:
    #         sec_weight = get_weight(one_sec_data, normal_method='MMN')
    #     weight.append(sec_weight)
    # print("志愿者完成issue数量各分段权重：", weight)

    # # 画图统计各段所包含的仓库数量
    # get_figure(section, dep_number)

