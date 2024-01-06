import numpy as np
import pyodbc
import pandas as pd
import extract as EX
import datetime
import matplotlib.pyplot as plt
server ='dissertation6539.database.windows.net'
database = 'DissertationClassifier'
username = 'adminNR'
password = 'Qwaszx9e8d7c!'
driver= '{ODBC Driver 17 for SQL Server}'

def Endtime(starttime):
  endtime = datetime.datetime.now()
  timspan = ((endtime - starttime).seconds) / 60
  print(timspan)
  return timspan




original = pd.read_csv('anonQCut.csv', engine='python')
original["id"] = range(len(original))
df = original.loc[original['dbname'].isin(['UKIDSSDR10PLUS', 'UKIDSSDR8PLUS', 'UKIDSSDR7PLUS'])]
df = df.sample(n=1000)
second=[]
timspans=[]
Test_sample=[100,150,200,250,300,350,450,500]
iter=0
with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
    with conn.cursor() as cursor:
      starttime = datetime.datetime.now()
      for index, row in df.iterrows():

        Query_id = index
        queryStr = row["queryStr"]
        time = row["time"]
        cpu_sec = row["cpu_sec"]
        elapsed_time = row["elapsed_time"]
        physical_IO = row["physical_IO"]
        row_count = row["row_count"]
        ipaddress = row["ipaddress"]
        dbname = row["dbname"]
        row_size = row["row_size"]
        userID = row["userID"]
        writeintoQuery = "INSERT INTO Queryinfo (time ,cpu_sec,elapsed_time,physical_IO , row_count,ipaddress,dbname,row_size , userID , queryStr) " \
                         "values(?,?,?,?,?,?,?,?,?,?)"
        cursor.execute(writeintoQuery, time, cpu_sec, elapsed_time,physical_IO,row_count,ipaddress,dbname,row_size,userID,queryStr)
        findQid = "select MAX(Query_id) from Queryinfo"
        Q_id = cursor.execute(findQid).fetchall()[0][0]
        search="select * from Firstlayer where T_features= '"+str(EX.SqlExtractor(queryStr).triple["table"]).replace("'","")+"';"
        result = cursor.execute(search)
        row = len(result.fetchall())
        if row<=0:
           insert="INSERT INTO Firstlayer (T_features, T_feature_num) " \
                  " VALUES('"+str(EX.SqlExtractor(queryStr).triple["table"]).replace("'","")+"', "\
                  +str(len(EX.SqlExtractor(queryStr).triple["table"]))+"); "


           queryinsert=cursor.execute(insert)
           findTid="select MAX(T_id) from Firstlayer"
           T_id=cursor.execute(findTid).fetchall()[0][0]


           insertSecond = "INSERT INTO SecondLayer (Attri_features,Parent_id, Attri_feature_num)  VALUES('" + str(
             EX.SqlExtractor(queryStr).triple["where"]).replace("'", "") + "', " + str(T_id) + "," + str(
             len(EX.SqlExtractor(queryStr).triple["where"])) + "); "
           try:
              resultSecondI = cursor.execute(insertSecond)
           except:
             print("Insert fail")
           findSid = "select MAX(Attri_id) from SecondLayer"
           S_id = cursor.execute(findSid).fetchall()[0][0]

           UpdateQuery = "UPDATE Queryinfo SET T_layer_id=" + str(S_id) + " WHERE Query_id=" + str(Q_id) + ";"
           cursor.execute(UpdateQuery)

           second.append(S_id)
           conn.commit()


        if row >0:

           T_id = cursor.execute(search).fetchall()[0][0]

           searchSecond = "select * from SecondLayer where Parent_id= " +str(T_id) + " and Attri_features='"\
                   +str(EX.SqlExtractor(queryStr).triple["where"]).replace("'","")+\
                   "';"

           resultSecond = cursor.execute(searchSecond)

           countSecond=len(resultSecond.fetchall())


           if countSecond<=0:
             insertSecond= "INSERT INTO SecondLayer (Attri_features,Parent_id, Attri_feature_num)  VALUES('" + str(
               EX.SqlExtractor(queryStr).triple["where"]).replace("'", "") + "', " +str(T_id)+","+ str(
               len(EX.SqlExtractor(queryStr).triple["where"])) + "); "
             try:
                resultSecondI=cursor.execute(insertSecond)
             except:
               print("Insert fail")
             conn.commit()
             findSid = "select MAX(Attri_id) from SecondLayer"
             S_id = cursor.execute(findSid).fetchall()[0][0]
             UpdateQuery="UPDATE Queryinfo SET T_layer_id="+str(S_id)+" WHERE Query_id="+str(Q_id)+";"
             cursor.execute(UpdateQuery)
             second.append(S_id)
           else:
             S_id = cursor.execute(searchSecond).fetchall()[0][0]
             UpdateQuery = "UPDATE Queryinfo SET T_layer_id=" + str(S_id) + " WHERE Query_id=" + str(Q_id) + ";"
             cursor.execute(UpdateQuery)
             second.append(S_id)
        conn.commit()
        iter=iter+1
        if iter in Test_sample:
           timspans.append(Endtime(starttime))



Test_samples=np.array(Test_sample)
print(Test_samples)
trainfig=plt.figure()
plt.plot(Test_samples, timspans,label='Skeleton classifier model',marker='o', markersize=5)
plt.ylabel('Total training time (secs)', fontsize=12)
plt.xlabel('Input Query log size (#queries)', fontsize=12)
plt.title("Simple Classifier Model Training Time")
plt.xticks(rotation=45)
plt.show();
plt.legend()
OutPath = '/lustre/home/d171/s1926539/dissertation/s1926539/Data_code/Dissertationcode/try/'
trainfig.savefig("Traintime.png")
#trainfig.savefig(OutPath+"/Traintime.png")




