import pandas as pd
from bokeh.models import ColumnDataSource
from tqdm import tqdm
import extract as EX
import random
from random import choice
tqdm.pandas(desc="progress-bar")
from gensim.models import Doc2Vec
from sklearn import utils
from sklearn.model_selection import train_test_split
from gensim.models.doc2vec import TaggedDocument
from gensim.test.utils import get_tmpfile
from bokeh.plotting import figure, show, output_notebook, reset_output, save, output_file
import bokeh.plotting as bp
from bokeh.models import HoverTool
import multiprocessing


#original = pd.read_csv('anonQCut.csv', engine='python')
original = pd.read_csv('anonQCut.csv', engine='python')
original["id"] = range(len(original))
df = original.loc[original['dbname'].isin(['UKIDSSDR10PLUS', 'UKIDSSDR8PLUS', 'UKIDSSDR7PLUS'])]
#df = df.sample(n=30000)
#



model=Doc2Vec.load("/lustre/home/d171/s1926539/dissertation/s1926539/Data_code/Dissertationcode/QuerylogExtractionResults/540000/sample")

OutputPath='/lustre/home/d171/s1926539/dissertation/s1926539/Data_code/Dissertationcode/QueryRecommendation/TestQ1/'

def test_mostsimilar(original,testSql,model):
    cluster = pd.DataFrame(columns=["score", 'query'])

    sql = EX.SqlExtractor(testSql).tokens
    infer_vector =  model.infer_vector(doc_words=sql, steps=20, epochs=200,alpha=0.025)
    similar_documents = model.docvecs.most_similar([infer_vector],topn=50)
    iter=0
    for i in similar_documents:
               list_i=[]
               list_i.append(i[1])
               list_i.append(original.iloc[int(i[0][6:])]["queryStr"])
               cluster.loc[iter] = list_i
               iter=iter+1

    cluster.to_csv(OutputPath+"TestQ0_Query2vec.csv")
    return cluster






def DF_similarList(clusternum,test):
    list={}
    list["cluster_id"] =[]
    list["score"] = []
    list["query"] = []
    for i in range(clusternum):

        query = test.loc[test['cluster_id'] == i].sample(1).iloc[0]['queryStr']
        cluster = test_mostsimilar(query, model)
        list["score"].extend(cluster["score"])
        list["query"].extend(cluster["query"])
        for item in range(len(cluster["query"])):
           list["cluster_id"].append(i)

    df = pd.DataFrame(list)

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
 
test_mostsimilar(original,sql,model)
