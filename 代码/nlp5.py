# import tensorflow as tf
# from tensorflow.keras.layers import Embedding, LSTM, Dense
# from tensorflow.keras.preprocessing.text import Tokenizer
# from tensorflow.keras.preprocessing.sequence import pad_sequences
#
# # 假设我们有一些SQL语句数据，这里仅作为示例
# sql_data = [
#     "SELECT * FROM table_name WHERE condition;",
#     "INSERT INTO table_name (column1, column2) VALUES (value1, value2);",
#     "UPDATE table_name SET column1 = value1 WHERE condition;"
# ]
#
# # 构建Token序列
# tokenizer = Tokenizer()
# tokenizer.fit_on_texts(sql_data)
# total_words = len(tokenizer.word_index) + 1  # 加1是因为后面要进行embedding
#
# # 将SQL语句转换为序列
# input_sequences = tokenizer.texts_to_sequences(sql_data)
#
# # 将输入序列填充到相同的长度
# max_sequence_length = max([len(x) for x in input_sequences])
# input_sequences = pad_sequences(input_sequences, maxlen=max_sequence_length, padding='post')
#
# # 构建神经网络模型
# model = tf.keras.Sequential([
#     Embedding(total_words, 64, input_length=max_sequence_length-1),
#     LSTM(100),
#     Dense(total_words, activation='softmax')
# ])
#
# # 编译模型
# model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
#
# # 定义输入和输出
# input_data = input_sequences[:,:-1]
# output_data = input_sequences[:,-1]
#
# # 训练模型
# model.fit(input_data, output_data, epochs=100)
#
# # 保存模型
# model.save('sql_compression_model.h5')
#


#
# import tensorflow as tf
# from tensorflow.keras.preprocessing.text import Tokenizer
# from tensorflow.keras.preprocessing.sequence import pad_sequences
#
# # 加载已训练好的模型
# model = tf.keras.models.load_model('sql_compression_model.h5')
#
# # 假设有一个要压缩的SQL语句
# new_sql = "SELECT column1, column2 FROM table_name WHERE condition;"
#
# # 预处理新的SQL语句
# tokenizer = Tokenizer()
# tokenizer.fit_on_texts([new_sql])
# input_sequences = tokenizer.texts_to_sequences([new_sql])
# max_sequence_length = len(input_sequences[0])
# input_sequences = pad_sequences(input_sequences, maxlen=max_sequence_length, padding='post')
#
# # 使用模型进行预测
# predicted_word_index = model.predict_classes(input_sequences, verbose=0)
#
# # 反向查找词表，获取预测的单词
# word_index_map = tokenizer.word_index
# predicted_word = None
# for word, index in word_index_map.items():
#     if index == predicted_word_index:
#         predicted_word = word
#         break
#
# # 如果预测的单词不为空，则进行替换
# if predicted_word:
#     compressed_sql = new_sql.replace(predicted_word, f'[{predicted_word}]')
#     print("压缩后的SQL语句：", compressed_sql)
# else:
#     print("无法压缩SQL语句，预测的单词为空。")
import tensorflow as tf

import tensorflow as tf
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer

# 原始的SQL语句列表
sql_statements = ['SELECT * FROM table_name WHERE condition;', 'INSERT INTO table2 VALUES (1, "John");','SELECT multiframeID FROM gpsDetection WHERE ra between 293.057 and 293.090" and dec between 12.923 and 12.956 /* Exclude multiple detections of the same source */AND ra > 0']

# 使用词袋模型将SQL语句转换为特征向量
vectorizer = CountVectorizer()
sql_features = vectorizer.fit_transform(sql_statements)

# 划分训练和测试集
X_train, X_test = train_test_split(sql_features.toarray(), test_size=0.2, random_state=42)

# 定义模型
model = Sequential()
model.add(Dense(64, activation='relu', input_dim=X_train.shape[1]))
model.add(Dense(32, activation='relu'))
model.add(Dense(X_train.shape[1], activation='linear'))

# 编译模型
model.compile(optimizer='adam', loss='mean_squared_error')

# 训练模型
model.fit(X_train, X_train, epochs=50, batch_size=32, shuffle=True, validation_data=(X_test, X_test))

# 使用训练好的模型进行推断
compressed_sql = model.predict(X_test)
print(compressed_sql)
