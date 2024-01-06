import extract as EX
import concurrent.futures
import pyodbc
import pandas as pd
import extract as EX
import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

#Connection  configuration
server ='dissertation6539.database.windows.net'
database = 'DissertationClassifier'
username = 'adminNR'
password = 'Qwaszx9e8d7c!'
driver= '{ODBC Driver 17 for SQL Server}'


'''
This is for simple skeleton classifier model's query recommendation task
You can change the testing query at the end of this python script
'''

def Endtime(starttime):
  endtime = datetime.datetime.now()
  timspan = ((endtime - starttime).seconds) / 60
  print(timspan)
  return timspan




def jaccard_similarity(set1, set2):
    result= float(len(set1.intersection(set2)) / len(set1.union(set2)))
    return result



def Endtime(starttime):
  endtime = datetime.datetime.now()
  timspan = ((endtime - starttime).seconds)
  print(timspan)
  return timspan

def Queryrecommendation(query):
    df = pd.DataFrame(columns=["queryStr",'T_id', 'Attri_id','T_features', 'Attri_features','Score'])
    iter = 1
    with pyodbc.connect(
            'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password) as conn:
        with conn.cursor() as cursor:
            print("Start Connecting")
            starttime = datetime.datetime.now()
            firstlayer = str(EX.SqlExtractor(query).triple["table"]).replace("'", "")
            len_first = len(EX.SqlExtractor(query).triple["table"])
            secondlayer = str(EX.SqlExtractor(query).triple["where"]).replace("'", "")
            len_second = len(EX.SqlExtractor(query).triple["where"])
            SearchFirstc="select queryStr,T_id,Attri_id,Attri_features,T_features from SecondLayer S, Firstlayer F,Queryinfo Q where "+\
             "S.Parent_id=F.T_id  and  S.Attri_id=Q.T_layer_id  and T_features='"+firstlayer+"'"+\
             "and  Attri_features='"+ secondlayer+"';"
            result = cursor.execute(SearchFirstc)
            row = len(result.fetchall())
            if row <= 5:
                print("row <= 5")
                SearchAll = "select queryStr,T_id,Attri_id,Attri_features,T_features from SecondLayer S, Firstlayer F,Queryinfo Q where " + \
                               "S.Parent_id=F.T_id  and  S.Attri_id=Q.T_layer_id  and T_features='" + firstlayer + "'" + ";"
                              # "and Attri_feature_num>="+str(len_second) +\

                resultall = cursor.execute(SearchAll)
                iter2=0
                for raw0 in resultall.fetchall():
                    iter2=iter2+1
                    iter = iter + 1
                    setA=set(raw0[3].strip("{").strip("}").replace(" ","").split(","))

                    score=jaccard_similarity(setA,EX.SqlExtractor(query).triple["where"])

                    perrow=list(raw0)
                    perrow.append(score)

                    df.loc[iter] =perrow
                    if(iter2>=500):
                        break;

            if row >5:
                iter2 = 0
                print("row > 5")

                for raw in  cursor.execute(SearchFirstc).fetchall():
                    iter2 = iter2 + 1
                    perraw=list(raw)
                    print(perraw)
                    perraw.append("1")

                    df.loc[iter2] = list(perraw)
                    if (iter2 >= 300):
                        break;
            Endtime(starttime)
            conn.commit()
    return df



sql="select ls.sourceid, ls.framesetid, ls.ra, ls.dec, ls.yapermag3, ls.j_1apermag3, ls.hapermag3, ls.kapermag3, " \
    "ls.yapermag4, ls.j_2apermag3, ls.yapermag3err, ls.j_1apermag3err, ls.hapermag3err, ls.kapermag3err, ls.yapermag4err," \
    " ls.j_2apermag3err, ldy.apermag1 as yapermag1, ldy.apermag1err as yapermag1err,  ls.yclass, ls.j_1class, ls.hclass, " \
    "ls.kclass, ls.mergedclass, ls.mergedclassstat, ls.pstar, ls.pgalaxy,  ls.pnoise, ls.psaturated, ldy.x as yx, ldy.y as yy, " \
    "ls.ypperrbits, ls.j_1pperrbits, ls.hpperrbits, ls.kpperrbits, lml.yenum as yextnum, lml.j_1enum as j_1extnum,  lml.henum as hextnum, " \
    "lml.kenum as kextnum,  rtrim(substring (mfy.filename,charindex('w2',mfy.filename,1),32)) as yfilename,  " \
    "rtrim(substring (mfj.filename,charindex('w2',mfj.filename,-1),32)) as j_1filename,  rtrim(substring " \
    "(mfh.filename,charindex('w2',mfh.filename,-1),32)) as hfilename,  rtrim(substring (mfk.filename,charindex('w2',mfk.filename,-1),32)) " \
    "as kfilename,  mfy.mjdobs as ymjdobs, mfj.mjdobs as j_1mjdobs, mfh.mjdobs as hmjdobs, mfk.mjdobs as kmjdobs from LasSource as ls, Lasmergelog " \
    "as lml, Lasdetection as ldy,  Multiframe as mfy, Multiframe as mfj, Multiframe as mfh, Multiframe as mfk where ls.framesetid=lml.framesetid " \
    "and mfy.multiframeid=lml.ymfid and  lml.yenum=ldy.extnum and lml.ymfid=ldy.multiframeid and  mfj.multiframeid=lml.j_1mfid and mfh.multiframeid=lml.hmfid and  mfk.multiframeid=lml.kmfid and ldy.objid=ls.yobjid and  ls.yppErrBits < 65536 and ls.j_1ppErrBits < 65536 and  ls.hppErrBits < 65536" \
    " and ls.kppErrBits < 65536 and (ls.ra between 329 and 330.001) and (ls.dec between 0 and 1) option (force order) "
 

sql2="SELECT multiframeID FROM gpsDetection WHERE ra between 293.057 and 293.090" \
          " and dec between 12.923 and 12.956 /* Exclude multiple detections of the same source */AND ra > 0 "

 
 
print("Start searching...")

Outputpath='./TestQ1/'
Outputpath2='./TestQ2/'

#Dataframe df is the total recommendation list produced by simple classifier

df=Queryrecommendation(sql)[["queryStr", 'Score']].sort_values(by='Score')[:200]
df.to_csv(Outputpath+"TestQ1_SimpC.csv")

 
df=Queryrecommendation(sql2)[["queryStr", 'Score']].sort_values(by='Score')[:200]
df.to_csv(Outputpath2+"TestQ2_SimpleC.csv")
