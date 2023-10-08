# -*- coding: utf-8 -*-
"""

@author: Liu
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import simplejson as json
from metrics.community_degree import tops_community_degree, query_community_degree

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})      # 解决跨域问题


# 获取仓库社区化程度top25接口
@app.route('/tops', methods=['GET', 'POST'])
def get_tops():
    top_num = 25
    top_result_df = tops_community_degree(top_num)
    # 将df转为json数据返回
    response = jsonify(top_result_df.to_dict(orient='records'))
    # # 解决跨域问题
    # response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# 获取某个仓库每月的社区化程度接口
@app.route('/queryByName', methods=['GET', 'POST'])
def get_by_name():
    repo_name = request.args.get('repoName')
    month_result_df = query_community_degree(repo_name)
    # 将df转为json数据返回
    response = jsonify(month_result_df.to_dict(orient='records'))
    return response


if __name__ == '__main__':
    app.run()
