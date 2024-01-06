import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import Callback

# 数据准备
data = '5564,dfrf,frA'

# 构建字符映射表
chars = sorted(list(set(data)))
char_to_int = {c: i for i, c in enumerate(chars)}
int_to_char = {i: c for i, c in enumerate(chars)}

# 将数据按逗号分隔并压缩为一个字母
compressed_data = ''.join([data_section[0] for data_section in data.split(',')])

# 将字符序列转换为整数序列
encoded_data = [char_to_int[char] for char in compressed_data]

# 构建训练数据
X = []
y = []
seq_length = 3

for i in range(len(encoded_data) - seq_length):
    X.append(encoded_data[i:i+seq_length])
    y.append(encoded_data[i+seq_length])

X = np.reshape(X, (len(X), seq_length, 1))
X = X / float(len(chars))
y = np.array(y)

# 构建LSTM模型
model = Sequential()
model.add(LSTM(32, input_shape=(X.shape[1], X.shape[2])))
model.add(Dense(len(chars), activation='softmax'))

# 编译模型
model.compile(loss='sparse_categorical_crossentropy', optimizer='adam')

# 自定义回调函数
class CustomCallback(Callback):
    def on_epoch_end(self, epoch, logs=None):
        if logs is None:
            logs = {}
        loss = logs.get('loss')
        print(f"Epoch {epoch+1} - Loss: {loss}")

# 训练模型
model.fit(X, y, epochs=100, batch_size=1, callbacks=[CustomCallback()])

# 加密
def encrypt(text):
    compressed_text = ''.join([text_section[0] for text_section in text.split(',')])
    encoded_text = [char_to_int[char] for char in compressed_text]
    encoded_text = np.array(encoded_text)
    encoded_text = np.reshape(encoded_text, (1, len(encoded_text), 1))
    encoded_text = encoded_text / float(len(chars))
    predicted = model.predict(encoded_text)
    predicted_char = int_to_char[np.argmax(predicted)]
    return predicted_char

# 测试加密
encrypted_text = encrypt(data)

print("原始数据:", data)
print("加密结果:", encrypted_text)
