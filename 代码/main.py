import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import pymysql
import random
mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="123456",
    database="dbkmeans"
)

mycursor = mydb.cursor()

# get the x data
mycursor.execute("SELECT spending from tblData")
i=random.randint(0,1)

spendingQuerry = mycursor.fetchall()
spending = [row[0] for row in spendingQuerry]
print(len(spending))
data =[]
for i in range(len(spending)):
    a=random.randint(0,1)
    if a==0:
        data.append(spending[i])

#plt画图

plt.hist(data, bins=20, color='steelblue', edgecolor='k', alpha=0.8)
plt.show()