#tf.compat.v1.disable_eager_execution()
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import LSTM, Embedding, Dense, Input
from tensorflow.keras.models import Model
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
tf.compat.v1.disable_eager_execution()
#SQL语句列表
sql_statements = ['SELECT * FROM table_name WHERE condition;', 'INSERT INTO table2 VALUES (1, "John");']

# 创建一个Tokenizer对象，用于将文本转换为序列
tokenizer = Tokenizer()
tokenizer.fit_on_texts(sql_statements)

# 将SQL语句转换为序列
sequences = tokenizer.texts_to_sequences(sql_statements)

# 获取词汇表大小和最大序列长度
vocab_size = len(tokenizer.word_index) + 1
max_length = max([len(seq) for seq in sequences])

# 对序列进行填充，使其长度一致
padded_sequences = pad_sequences(sequences, maxlen=max_length, padding='post')

# 划分训练和测试集
X_train, X_test = train_test_split(padded_sequences, test_size=0.2, random_state=42)

# 将标签进行one-hot编码
y_train = to_categorical(X_train[:, -1], num_classes=vocab_size)
y_test = to_categorical(X_test[:, -1], num_classes=vocab_size)

# 构建LSTM模型
input_layer = Input(shape=(max_length,))
embedding_layer = Embedding(vocab_size, 64)(input_layer)
lstm_layer = LSTM(64)(embedding_layer)
output_layer = Dense(vocab_size, activation='softmax')(lstm_layer)

model = Model(input_layer, output_layer)

# 编译模型
model.compile(optimizer='adam', loss='categorical_crossentropy')

# 训练模型
model.fit(X_train, y_train, epochs=50, batch_size=32, shuffle=True, validation_data=(X_test, y_test))

# 使用训练好的模型进行推断
compressed_sql = model.predict(X_test)
print(compressed_sql)