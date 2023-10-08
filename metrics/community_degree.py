# -*- coding: utf-8 -*-
"""
数据分析：
   总共有546549个仓库既有issueevent事件也有prevent事件,其中 total_volunteer=1 的仓库有27万多个（占总数一半），
   1到50之间的也是有26万多个（占总数一半）；
另外，10<=total_volunteer<50 的仓库有2万3千多个，50<=total_volunteer<100 的仓库有2千多个，
   100<=total_volunteer<=1000 的仓库有809个，total_volunteer>1000 的有9个

@author: Liu
"""
from db.clickhouse import client as ck_client
from weight.weight_analysis import get_weight
import pandas as pd
import numpy as np
import simplejson as json

# 设置pd展示全部列
pd.set_option('display.max_columns', None)
# 仓库中最低志愿者人数要求
min_volunteer_number = 10


def get_basic_data():
    """
    获取必需的基本数据，包括所有仓库的相关数据以及权重
    """
    # 查询所有仓库中的志愿者人数，志愿者完成issue数量和pr数量
    sql = "SELECT repo_name, \
                        COUNT(DISTINCT actor_login) AS total_volunteer, \
                        COUNT(DISTINCT CASE WHEN type = 7 THEN id END) AS issue_number, \
                        COUNT(DISTINCT CASE WHEN type = 10 THEN id END) AS pr_number \
                FROM github_log.events  \
                WHERE type IN (7,10) AND action=2 AND actor_login NOT LIKE '%[bot]' AND \
                        issue_author_association IN (1,2,4) AND  \
                        issue_comment_author_association IN (1,2,4) AND  \
                        pull_review_comment_author_association IN (1,2,4) AND  \
                        commit_comment_author_association IN (1,2,4) \
                GROUP BY repo_name \
                HAVING COUNT(DISTINCT type)=2 AND total_volunteer>={} \
                ORDER BY total_volunteer DESC".format(min_volunteer_number)
    result_df = ck_client.query_df(sql)  # 返回类型 = <class 'pandas.core.frame.DataFrame'>

    # 利用整体数据使用CRITIC方法计算权重
    calc_field = result_df.loc[:, ('issue_number', 'pr_number')]
    weight_list = get_weight(calc_field, normal_method='MMN')

    return result_df, weight_list


def tops_community_degree(top):
    """
    获取社区化程度top的仓库得分
    """
    # 获取所有仓库中的志愿者人数，志愿者完成issue数量和pr数量
    sql = "SELECT repo_name, \
                            COUNT(DISTINCT actor_login) AS total_volunteer, \
                            COUNT(DISTINCT CASE WHEN type = 7 THEN id END) AS issue_number, \
                            COUNT(DISTINCT CASE WHEN type = 10 THEN id END) AS pr_number \
                    FROM github_log.events  \
                    WHERE type IN (7,10) AND action=2 AND actor_login NOT LIKE '%[bot]' AND \
                            issue_author_association IN (1,2,4) AND  \
                            issue_comment_author_association IN (1,2,4) AND  \
                            pull_review_comment_author_association IN (1,2,4) AND  \
                            commit_comment_author_association IN (1,2,4) \
                    GROUP BY repo_name \
                    HAVING COUNT(DISTINCT type)=2 AND total_volunteer>={} \
                    ORDER BY total_volunteer DESC ".format(min_volunteer_number)
    result_df = ck_client.query_df(sql)  # 返回类型 = <class 'pandas.core.frame.DataFrame'>
    # 计算社区化程度
    result_df = calculate_community_degree(result_df)
    # 按照社区化得分倒序排序
    top_result_df = result_df.sort_values(by='community_score', ascending=False)
    return top_result_df.head(top)


def query_community_degree(repo_name):
    """
    获取某个仓库每月的社区化程度
    """
    month_df = pd.DataFrame()
    # 查询某个仓库每月的累计志愿者人数，志愿者完成issue数量和pr数量
    for month in range(1, 13):
        sql = "SELECT repo_name, \
                    COUNT(DISTINCT actor_login) AS total_volunteer,  \
                    COUNT(DISTINCT CASE WHEN type = 7 THEN id END) AS issue_number,  \
                    COUNT(DISTINCT CASE WHEN type = 10 THEN id END) AS pr_number  \
                FROM github_log.events  \
                WHERE type IN (7,10) AND action=2 AND repo_name={} AND \
                    actor_login NOT LIKE '%[bot]' AND toMonth(created_at)<={} AND  \
                    issue_author_association IN (1,2,4) AND  \
                    issue_comment_author_association IN (1,2,4) AND  \
                    pull_review_comment_author_association IN (1,2,4) AND  \
                    commit_comment_author_association IN (1,2,4)  \
                GROUP BY repo_name  \
                HAVING COUNT(DISTINCT type)=2 AND total_volunteer>={}".\
            format("'{}'".format(repo_name), month, min_volunteer_number)
        result_df = ck_client.query_df(sql)  # 返回类型 = <class 'pandas.core.frame.DataFrame'>
        # 如果返回结果为空，就将各字段值设置为0
        if result_df.empty:
            zero_data = {'total_volunteer': [0], 'issue_number': [0], 'pr_number': [0]}
            result_df = pd.DataFrame(zero_data)
            result_df.insert(0, 'repo_name', repo_name)
        # 拼接每月的df
        month_df = pd.concat([month_df, result_df], axis=0)

    # 重新设置索引
    month_df.index = [i for i in range(0, 12)]
    # 计算该仓库每月的社区化程度
    month_result_df = calculate_community_degree(month_df)
    return month_result_df


def calculate_community_degree(data_df):
    """
    利用公式计算社区化程度
    """
    # 1、获取权重列表
    result_df, weight_list = get_basic_data()

    # 2、获取全域志愿者人数
    all_volunteer = get_all_volunteer_number()
    # 3、计算全域人均issue完成量
    issue_mean = result_df['issue_number'].sum() / all_volunteer.loc[0, 'all_volunteer']
    # 4、计算全域人均pr完成量
    pr_mean = result_df['pr_number'].sum() / all_volunteer.loc[0, 'all_volunteer']

    # 5、计算社区化程度得分
    community_score = data_df['issue_number'] / issue_mean * weight_list[0] + \
                      data_df['pr_number'] / pr_mean * weight_list[1]
    data_df['community_score'] = community_score.round(2)
    return data_df


def get_all_volunteer_number():
    """
    查询全域志愿者人数
    """
    all_volunteer_sql = "SELECT COUNT(DISTINCT actor_login) AS all_volunteer FROM github_log.events WHERE repo_name IN (  \
                                    SELECT repo_name  \
                                    FROM github_log.events   \
                                    WHERE type IN (7,10) AND action=2 AND actor_login NOT LIKE '%[bot]' AND  \
                                    issue_author_association IN (1,2,4) AND   \
                                    issue_comment_author_association IN (1,2,4) AND   \
                                    pull_review_comment_author_association IN (1,2,4) AND   \
                                    commit_comment_author_association IN (1,2,4)  \
                                    GROUP BY repo_name  \
                                    HAVING COUNT(DISTINCT type)=2 AND COUNT(DISTINCT actor_login)>={} \
                                ) AND type IN (7,10) AND action=2 AND actor_login NOT LIKE '%[bot]' AND  \
                                issue_author_association IN (1,2,4) AND   \
                                issue_comment_author_association IN (1,2,4) AND   \
                                pull_review_comment_author_association IN (1,2,4) AND   \
                                commit_comment_author_association IN (1,2,4)".format(min_volunteer_number)
    all_volunteer = ck_client.query_df(all_volunteer_sql)
    return all_volunteer


# if __name__ == '__main__':
#     top_num = 50
#     # 获取top排名
#     result = tops_community_degree(top_num)
#     # 将数据写入json文件
#     with open('../data/test_community_degree_top'+str(top_num)+'.json', 'w') as f:
#         json.dump(result.to_dict(orient='records'), f)
#     repo = 'SmartThingsCommunity/SmartThingsPublic'
#     print(query_community_degree(repo))
    # print(query_community_degree(repo)['community_score'].tolist())
    # -----------------------test--------------------------
    # array = [136.53, 275.58, 435.15, 598.59, 752.52, 900.66, 1052.02, 1172.38, 1290.61, 1430.23, 1531.63, 1627.38]
    # result = []
    # for i in range(0, len(array)):
    #     if i == 0:
    #         result.append(array[i])
    #         continue
    #     result.append(array[i] - array[i-1])
    # print(result)
