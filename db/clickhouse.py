import clickhouse_connect

client = clickhouse_connect.get_client(host='111.47.28.118', port=9123, username='default', \
                                       password='hubu88661126', database='github_log')

# if __name__ == '__main__':
#     # result = client.query_df('SELECT login,activation FROM github_log.tests limit 3')
#     result = client.query_df('select count() as total_repo from (select DISTINCT repo_id,repo_name from github_log.events)')
#     print(result)
