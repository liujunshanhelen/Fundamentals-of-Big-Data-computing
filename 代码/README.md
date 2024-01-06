###  随机采样、基于聚类的负载压缩

2.py 需要连接mysql数据库

### 基于启发式的负载压缩

Huffman.py 是根据哈夫曼树的压缩算法

Sql.g4,Sql.interp,Sql.tokens,SqlBaseListener.java,SqlBaseVisitor.java,SqlLexer.interp是将sql语句转化为树的代码

### 基于机器学习的负载压缩

Doc2-vec 训练模型

使用 Query2vec 框架来应用查询日志提取、工作负载分析和查询建议。 首先，我们使用 Doc2vec 模型对日志中的所有查询进行矢量化， 然后使用 K-means++ 算法对学习到的查询向量进行聚类 表示语料库中的每个查询

nlp.py,用lstm对sql进行压缩和解压

### 查询向量优化

spark-query-log-plugin-master文件夹

