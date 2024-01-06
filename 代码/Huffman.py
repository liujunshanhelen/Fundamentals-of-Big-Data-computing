import xlwt
import xlrd
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import os
import os.path

# 2霍夫曼编码
def Huffman():
    Directory = os.path.split(FrequencyPath.get())[0]
    Path = FrequencyPath.get().replace('/', '\\')
    FrequencyName = os.path.split(FrequencyPath.get())[1]
    name = FrequencyName.split('_')[1].split('.')[0]

    workbook1 = xlrd.open_workbook(Path)
    sheet1 = workbook1.sheets()[0]
    nrows1 = sheet1.nrows
    a = []
    a_n = []
    for i in range(nrows1 - 1):
        a.append(sheet1.cell_value(nrows1 - i - 1, 0))
        a_n.append(sheet1.cell_value(nrows1 - i - 1, 1))

    # 对b按b_n排序，后将发生的变动记录到b_s
    def sort(b_zu, b_sum):
        m = b_zu[0]
        n = b_sum[0]

        index = 0
        time = len(b_zu) - 1
        for i in range(time):
            if n > b_sum[i + 1]:
                index = index + 1
            else:
                break
        if index != 0:
            temp_b_zu = b_zu[0]
            temp_b_sum = b_sum[0]
            for j in range(index):
                b_zu[j] = b_zu[j + 1]
                b_sum[j] = b_sum[j + 1]
            b_zu[index] = temp_b_zu
            b_sum[index] = temp_b_sum

    def coding(a, a_n):
        h = []
        b = []
        b_zu = []
        b_n = []
        time = len(a)
        for i in range(time):
            h.append('')
            b.append(a[i])
            b_zu.append([i])
            b_n.append(a_n[i])
        for i in range(time - 1):
            b_sum = []
            for j in range(len(b_zu)):
                temp_sum = 0
                for k in b_zu[j]:
                    temp_sum = temp_sum + b_n[k]
                b_sum.append(temp_sum)
            sort(b_zu, b_sum)
            h_0 = b_zu[0]
            h_1 = b_zu[1]
            for i in h_0:
                h[i] = '0' + h[i]
            for j in h_1:
                h[j] = '1' + h[j]

            b_zu[0] = b_zu[0] + b_zu[1]
            b_zu.pop(1)
        return h

    h = coding(a, a_n)

    workbook2 = xlwt.Workbook()
    sheet2 = workbook2.add_sheet('1')
    sheet2.write(0, 0, '符号')
    sheet2.write(0, 1, '编码')
    for i in range(len(a)):
        sheet2.write(i + 1, 0, a[i])
        sheet2.write(i + 1, 1, h[i])
    workbook2.save(Directory + '/Huffman_code_' + name + '.xls')
    HuffmanCodePath.set(Directory + '/Huffman_code_' + name + '.xls')


# 3压缩
def Compress():
    Directory = os.path.split(HuffmanCodePath.get())[0]
    CompressName = os.path.split(HuffmanCodePath.get())[1]
    name = CompressName.split('_')[2].split('.')[0]
    with open(ToBeCompressPath.get(), 'r') as f1:
        data = f1.read()

    workbook1 = xlrd.open_workbook(HuffmanCodePath.get())
    sheet1 = workbook1.sheets()[0]
    nrows1 = sheet1.nrows

    symbol = []
    code = []
    for i in range(nrows1 - 1):
        symbol.append(sheet1.cell_value(nrows1 - i - 1, 0))
        code.append(sheet1.cell_value(nrows1 - i - 1, 1))

    Compress = ''
    for d in data:
        for i in range(len(symbol)):
            if d == symbol[i]:
                Compress = Compress + code[i]

    # 将二进制字符串转为字节流
    def bitstring2bytes(bs):
        bt = bytearray()
        time = round(len(bs) / 8)
        for i in range(time):
            bs_k = int(bs[i * 8:(i + 1) * 8], 2)
            bt.append(bs_k)
        return bytes(bt)

    CompressData = bitstring2bytes(Compress)
    with open(Directory + '/Compress_' + name, 'wb') as f2:
        f2.write(CompressData)
    CompressPath.set(Directory + '/Compress_' + name)

    # 输出压缩效率
    size_before = os.path.getsize(ToBeCompressPath.get())
    size_after = os.path.getsize(CompressPath.get())
    theta = str(100 * (1 - round(size_after / size_before, 4)))
    labelName = tkinter.Label(root,
                              text=theta + '%',
                              justify=tkinter.RIGHT,
                              anchor='e',
                              width=80)
    labelName.place(x=160, y=270, width=50, height=20)


# 解压缩
def unCompress():
    Directory = os.path.split(CompressPath.get())[0]
    unCompressName = os.path.split(HuffmanCodePath.get())[1]
    name = unCompressName.split('_')[2].split('.')[0]
    with open(CompressPath.get(), 'rb') as f1:
        Compress = f1.read()

    # 将二进制字节流转为字符串
    def bytes2bitstring(byte):
        bs = ''
        for i in byte:
            bs_k = str(bin(i)).split('b')[1]
            while len(bs_k) < 8:
                bs_k = '0' + bs_k
            bs = bs + bs_k
        return bs

    Compress_data = bytes2bitstring(Compress)
    workbook1 = xlrd.open_workbook(HuffmanCodePath.get())
    sheet1 = workbook1.sheets()[0]
    nrows1 = sheet1.nrows

    symbol = []
    code = []
    for i in range(nrows1 - 1):
        symbol.append(sheet1.cell_value(nrows1 - i - 1, 0))
        code.append(sheet1.cell_value(nrows1 - i - 1, 1))

    unCompress_data = ''
    temp = ''
    for c in Compress_data:
        temp = temp + c
        if temp in code:
            index = code.index(temp)
            unCompress_data = unCompress_data + symbol[index]
            temp = ''
    with open(Directory + '/unCompress_' + name + '.txt', 'w', encoding='ANSI') as f2:
        f2.write(unCompress_data)
    unCompressPath.set(Directory + '/unCompress_' + name + '.txt')


##窗口设计
root = tkinter.Tk()

# 窗口大小
root.title('英文文本编码器')
root['height'] = 320
root['width'] = 600

# 放'待压缩文件'
labelName = tkinter.Label(root,
                          text='待压缩文件:',
                          justify=tkinter.RIGHT,
                          anchor='e',
                          width=80)
labelName.place(x=30, y=30, width=80, height=20)

# 放'待压缩文件'后的框
ToBeCompressPath = tkinter.StringVar(root, value='')
entry_ToBeCompressPath = tkinter.Entry(root,
                                       width=80,
                                       textvariable=ToBeCompressPath)
entry_ToBeCompressPath.place(x=120, y=30, width=350, height=20)


# 放'待压缩文件'的'...'钮
def open_file1():
    ToBeCompressPath.set(tkinter.filedialog.askopenfilename())


button_op1 = tkinter.Button(root,
                            text='...',
                            command=open_file1)
button_op1.place(x=470, y=30, width=20, height=20)

# 放'字符频率文件'
labelName = tkinter.Label(root,
                          text='字符频率文件:',
                          justify=tkinter.RIGHT,
                          anchor='e',
                          width=80)
labelName.place(x=30, y=80, width=80, height=20)

# 放'字符频率文件'后的框
FrequencyPath = tkinter.StringVar(root, value='')
entry_FrequencyPath = tkinter.Entry(root,
                                    width=80,
                                    textvariable=FrequencyPath)
entry_FrequencyPath.place(x=120, y=80, width=350, height=20)


# 放'字符频率文件'的'...'钮
def open_file2():
    FrequencyPath.set(tkinter.filedialog.askopenfilename())


button_op2 = tkinter.Button(root,
                            text='...',
                            command=open_file2)
button_op2.place(x=470, y=80, width=20, height=20)



# 放'编码文件'
labelName = tkinter.Label(root,
                          text='编码文件:',
                          justify=tkinter.RIGHT,
                          anchor='e',
                          width=80)
labelName.place(x=30, y=130, width=80, height=20)

# 放'编码文件'后的框
HuffmanCodePath = tkinter.StringVar(root, value='')
entry_HuffmanCodePath = tkinter.Entry(root,
                                      width=80,
                                      textvariable=HuffmanCodePath)
entry_HuffmanCodePath.place(x=120, y=130, width=350, height=20)


# 放'编码文件'的'...'钮
def open_file3():
    HuffmanCodePath.set(tkinter.filedialog.askopenfilename())


button_op3 = tkinter.Button(root,
                            text='...',
                            command=open_file3)
button_op3.place(x=470, y=130, width=20, height=20)

# 放'编码'钮
button_HuffmanCode = tkinter.Button(root,
                                    text='编码',
                                    command=Huffman)
button_HuffmanCode.place(x=520, y=130, width=50, height=20)

# 放'压缩文件'
labelName = tkinter.Label(root,
                          text='压缩文件:',
                          justify=tkinter.RIGHT,
                          anchor='e',
                          width=80)
labelName.place(x=30, y=180, width=80, height=20)

# 放'压缩文件'后的框
CompressPath = tkinter.StringVar(root, value='')
entry_CompressPath = tkinter.Entry(root,
                                   width=80,
                                   textvariable=CompressPath)
entry_CompressPath.place(x=120, y=180, width=350, height=20)


# 放'压缩文件'的'...'钮
def open_file4():
    CompressPath.set(tkinter.filedialog.askopenfilename())


button_op4 = tkinter.Button(root,
                            text='...',
                            command=open_file4)
button_op4.place(x=470, y=180, width=20, height=20)

# 放'压缩'钮
button_Compress = tkinter.Button(root,
                                 text='压缩',
                                 command=Compress)
button_Compress.place(x=520, y=180, width=50, height=20)

# 放'解压缩文件'
labelName = tkinter.Label(root,
                          text='解压缩文件:',
                          justify=tkinter.RIGHT,
                          anchor='e',
                          width=80)
labelName.place(x=30, y=230, width=80, height=20)

# 放'解压缩文件'后的框
unCompressPath = tkinter.StringVar(root, value='')
entry_unCompressPath = tkinter.Entry(root,
                                     width=80,
                                     textvariable=unCompressPath)
entry_unCompressPath.place(x=120, y=230, width=350, height=20)


# 放'解压缩文件'的'...'钮
def open_file5():
    unCompressPath.set(tkinter.filedialog.askopenfilename())


button_op5 = tkinter.Button(root,
                            text='...',
                            command=open_file5)
button_op5.place(x=470, y=230, width=20, height=20)

# 放'解压缩'钮
button_unCompress = tkinter.Button(root,
                                   text='解压缩',
                                   command=unCompress)
button_unCompress.place(x=520, y=230, width=50, height=20)

# 放'压缩效率'
labelName = tkinter.Label(root,
                          text='压缩效率为:',
                          justify=tkinter.RIGHT,
                          anchor='e',
                          width=80)
labelName.place(x=80, y=270, width=80, height=20)

# 放'退出'钮

button_drop_out = tkinter.Button(root,
                                 text='退出',
                                 command=root.destroy)
button_drop_out.place(x=490, y=270, width=60, height=30)

# 开始
root.mainloop()

