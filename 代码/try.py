# import pandas as pd
#
# # 读取并展示SQL查询日志数据
# log_data = pd.read_csv('./sql_log.csv')
# print(log_data.head())
# import re
#
# # 提取关键字特征
# log_data['keywords'] = log_data['query'].apply(lambda x: re.findall(r'(?:^|\s)(\w+)', x))
#
# # 提取表名特征
# log_data['table_name'] = log_data['query'].apply(lambda x: re.findall(r'FROM\s+(\w+)', x))
#
# # 提取字段名特征
# log_data['column_name'] = log_data['query'].apply(lambda x: re.findall(r'SELECT\s+(.*)\s+FROM', x))
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.feature_extraction.text import CountVectorizer
#
# # 特征向量化
# vectorizer = CountVectorizer()
# X = vectorizer.fit_transform(log_data['query'])
#
# # 构建模型并训练
# model = RandomForestRegressor()
# model.fit(X, log_data['execution_time'])
#
# # 定义压缩函数
# def compress_query(query):
#     query_vector = vectorizer.transform([query])
#     compressed_time = model.predict(query_vector)
#     return compressed_time[0]
#
# # 测试压缩效果
# query = 'SELECT * FROM table WHERE column = value;'
# compressed_time = compress_query(query)
# print(f'压缩前执行时间：{compressed_time}秒')



from antlr4 import *
from SqlLexer import SqlLexer
from SqlParser import SqlParser

class TreeShapeListener(ParseTreeListener):
    def enterEveryRule(self, ctx):
        for i in range(ctx.depth()):
            print('  ', end='')
        print(ctx.getText())

lexer = SqlLexer(InputStream('SELECT * FROM table WHERE column = value'))
tokens = CommonTokenStream(lexer)
parser = SqlParser(tokens)
tree = parser.query()

# 遍历AST并打印
listener = TreeShapeListener()
walker = ParseTreeWalker()
walker.walk(listener, tree)