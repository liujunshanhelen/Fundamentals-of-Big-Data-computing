import tensorflow as tf
import numpy as np
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.models import Model

# 假设有一个包含文本数据的训练集
training_data = ['SELECT * FROM table_name WHERE condition;', 'INSERT INTO table2 VALUES (1, "John");']

# 构建词汇表，将文本数据转换为词袋模型表示
from tensorflow.keras.preprocessing.text import Tokenizer
tokenizer = Tokenizer()
tokenizer.fit_on_texts(training_data)
vocab_size = len(tokenizer.word_index) + 1
sequences = tokenizer.texts_to_sequences(training_data)

# 在这个简化的示例中，假设所有句子的长度是相同的
maxlen = max([len(seq) for seq in sequences])

# 对文本进行填充，使得每个句子的长度相同
padded_sequences = tf.keras.preprocessing.sequence.pad_sequences(sequences, padding='post', maxlen=maxlen)

# 构建自编码器模型
input_seq = Input(shape=(maxlen,))
encoded = Dense(128, activation='relu')(input_seq)  # 编码层
decoded = Dense(maxlen, activation='sigmoid')(encoded)  # 解码层

autoencoder = Model(input_seq, decoded)
autoencoder.compile(optimizer='adam', loss='binary_crossentropy')

# 训练自编码器模型
autoencoder.fit(padded_sequences, padded_sequences, epochs=50, batch_size=16)

# 使用训练好的自编码器模型进行文本压缩
compressed_data = autoencoder.predict(padded_sequences)

# 打印压缩后的数据
for i in range(len(training_data)):
    print("原始数据：", training_data[i])
    print("压缩后的数据：", compressed_data[i])



import tensorflow as tf
import numpy as np
tf.compat.v1.disable_eager_execution()

# 构建 AutoEncoder 模型
input_dim = 1000
encoding_dim = 100

input_data = tf.compat.v1.placeholder(tf.float32, shape=[None, input_dim])

# 编码器
encoder_weights = tf.Variable(tf.compat.v1.random_normal([input_dim, encoding_dim]))
encoder_biases = tf.Variable(tf.compat.v1.random_normal([encoding_dim]))
encoded = tf.nn.sigmoid(tf.matmul(input_data, encoder_weights) + encoder_biases)

# 解码器
decoder_weights = tf.Variable(tf.compat.v1.random_normal([encoding_dim, input_dim]))
decoder_biases = tf.Variable(tf.compat.v1.random_normal([input_dim]))
decoded = tf.matmul(encoded, decoder_weights) + decoder_biases

# 定义损失函数和优化器
loss = tf.reduce_mean(tf.square(decoded - input_data))
optimizer = tf.compat.v1.train.AdamOptimizer().minimize(loss)

# 创建 TensorFlow 会话并训练模型
with tf.compat.v1.Session() as sess:
    sess.run(tf.compat.v1.global_variables_initializer())

    # 假设 data 是你的文本数据，这里用随机生成的数据代替
    data = np.random.rand(100, input_dim)

    # 训练模型
    for epoch in range(1000):
        _, l = sess.run([optimizer, loss], feed_dict={input_data: data})

        if epoch % 100 == 0:
            print('Epoch {} Loss: {}'.format(epoch, l))

    # 对压缩模型进行测试
    encoded_data = sess.run(encoded, feed_dict={input_data: data})

    # 解压缩数据
    decoded_data = sess.run(decoded, feed_dict={input_data: data})

    print('Original Data:', data[0])
    print('Encoded Data:', encoded_data[0])
    print('Decoded Data:', decoded_data[0])
