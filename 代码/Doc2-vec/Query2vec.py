import pandas as pd
from bokeh.io import export_png
from bokeh.models import ColumnDataSource
from tqdm import tqdm
import extract as EX

import datetime
tqdm.pandas(desc="progress-bar")
from gensim.models import Doc2Vec
from sklearn import utils
from sklearn.model_selection import train_test_split
from gensim.models.doc2vec import TaggedDocument
from gensim.test.utils import get_tmpfile
from bokeh.plotting import figure, show, output_notebook, reset_output, save, output_file
import bokeh.plotting as bp
from bokeh.models import HoverTool
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import numpy as np
from scipy import spatial
import time
import multiprocessing
import random
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import os
import seaborn as sns


# read corpus in CSV format
# anonQCut

#if file path does not exists, create one 
def mkdir(path):
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)




#label all queries inside corpus
def label_sentences(corpus, label_type):
    """
    Gensim's Doc2Vec implementation requires each document/paragraph to have a label associated with it.
    We do this by using the TaggedDocument method. The format will be "TRAIN_i" or "TEST_i" where "i" is
    a dummy index of the complaint narrative.
    """
    labeled = []
    for i, v in enumerate(corpus):
        label = label_type + '_' + str(i)
        labeled.append(TaggedDocument(v.split(), [label]))
    return labeled


# train_tagged = label_sentences(train.queryStr, 'Train')
# test_tagged = label_sentences(test.queryStr, 'Test')

# Doc2vec model
def doc2vecTraining(corpus):
    cores = multiprocessing.cpu_count()
    model = Doc2Vec(vector_size=300, min_count=3,
                    window=50, alpha=0.05,
                    min_alpha=0.0001, epochs=200,
                    workers=cores)
    print("min_count: ", model.min_count,
          "cores: ", cores,
          "\nwindow size: ", model.window,
          "\nalpha: ", model.alpha,
          "\nmin_alpha: ", model.min_alpha,
          "\nepochs: ", model.epochs
          )

    model.build_vocab([x for x in tqdm(corpus.values)])  # corpus.values
    model.train([x for x in tqdm(corpus.values)], total_examples=len(corpus.values), epochs=model.epochs)
    return model


def Doc2vecmodel(outputname,sample_num):
    original = pd.read_csv('anonQCut.csv', engine='python')
    original["id"] = range(len(original))
    df = original.loc[original['dbname'].isin(['UKIDSSDR10PLUS', 'UKIDSSDR8PLUS', 'UKIDSSDR7PLUS'])]
    df = df.sample(n=sample_num)
    print(df)
    print(df.shape)

    # tag corpus
    #start = datetime.datetime.now()
    start = time.time()
    train, test = train_test_split(df, test_size=0.02, random_state=42)
    train_tagged = train.apply(
        lambda r: TaggedDocument(words=(EX.SqlExtractor(r['queryStr']).tokens), tags=["train_" + str(r["id"])]), axis=1)
    ''' 
    test_tagged = test.apply(
        lambda r: TaggedDocument(words=(EX.SqlExtractor(r['queryStr']).tokens), tags=["test_" + str(r["id"])]), axis=1)
    '''
    print("Start preparing test corpus...\n")
    model=doc2vecTraining(train_tagged)
   
    #end = datetime.datetime.now()
    end = time.time()
    timespan=(end-start)/60
    print(timespan)
    #if len(train) >300000 and len(train) <450000:
        


    return train,test,model,timespan

 



# generate cluster colors in visualization

def randomcolor():
    colorArr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0, 14)]
    return "#" + color


def colorList(number):
    label = []
    for i in range(number):
        if randomcolor() not in label:
            label.append(randomcolor())
        if len(label) == number:
            break
    return label

def Color(labels,k):
    label1 = colorList(k)  # NOTE:same number with n_clusters
    color = [label1[i] for i in labels]
    return color




# NOTE: using QueryVec algorithm
# Clustering using K-means++

def K_means(k, vector):
    kmeans_model = KMeans(n_clusters=k, init='k-means++', max_iter=400)
    X = kmeans_model.fit(vector)
    labels = kmeans_model.labels_.tolist()
    centroids = kmeans_model.cluster_centers_
    color = Color(labels, k)
    return labels, centroids,color


def calculate_representativeQuery(vector, train, K, centroids,outputname,outputname2):
    All_cosine = []
    for id in range(K):
        cluster_cosine = pd.DataFrame(columns=['query_id', 'cosine_similarity'])
        cluster_queries = train[train["cluster_id"] == id]
        for i in range(len(cluster_queries)):
            query = cluster_queries.iloc[i]
            index = query["vector_id"]
            result = 1 - spatial.distance.cosine(vector[index], centroids[id])
            cluster_cosine.loc[i] = [str(query["id"])] + [result]
        cluster_cosine.sort_values(by="cosine_similarity", ascending=False)
        All_cosine.append(int(cluster_cosine.iloc[0]["query_id"]))
        cluster_num=train['cluster_id'].value_counts()

        represent_list = train[train["id"].isin(All_cosine)]
        figureBar=plt.figure(figsize=(10, 4))
        sns.barplot(cluster_num.index, cluster_num.values, alpha=0.8)
        plt.ylabel('Number of queries', fontsize=12)
        plt.xlabel('cluster id name', fontsize=12)
        plt.show();
        figureBar.savefig(outputname2)
        
        represent_list.to_csv(outputname)
       
          
    return All_cosine

#visualize it using T-SNE algorithm and output interactive figures that show the queries of dots using Bokeh module
def Visualize(labels,model_vector,color,train,outputname):

    tsne_model = TSNE(n_jobs=4,
                      early_exaggeration=4,
                      n_components=2,
                      verbose=1,
                      perplexity=50,
                      random_state=2018,
                      n_iter=1200)

    tsne_d2v = tsne_model.fit_transform(model_vector)  # model_dbow
    tsne_d2v_df = pd.DataFrame(data=tsne_d2v, columns=["x", "y"])
    tsne_d2v_df["id"] = train["id"].values
    tsne_d2v_df["queryStr"] = train["queryStr"].values
    tsne_d2v_df["cluster_id"] = labels
    tsne_d2v_df["cpu_sec"] = train["cpu_sec"].values
    tsne_d2v_df["dbname"] = train["dbname"].values
    train["cluster_id"] = labels
    fig_PCA = plt.figure()

    plt.scatter(tsne_d2v_df["x"], tsne_d2v_df["y"], c=color,s=2)
    plt.title('Query embeddings using raw query string', fontsize=10)
    plt.show()
    fig_PCA.savefig(outputname)
#Perform workload summarization and query log extraction
def Workload_sum(K,sample_num,OutPath,model_name,CSV_name,Image_name,Bar_name):
    train, test, model_dbow, timespan = Doc2vecmodel(OutPath + model_name, sample_num)
    labels, centroids, color = K_means(K, model_dbow.docvecs.vectors_docs)
    train["cluster_id"] = labels
    train["vector_id"] = range(len(train))
    calculate_representativeQuery(model_dbow.docvecs.vectors_docs, train, K, centroids,OutPath+CSV_name,OutPath+Bar_name)
    Visualize(labels,model_dbow.docvecs.vectors_docs, color, train, OutPath + Image_name)
    print("Cluster number is :",K,"\n Workload running time is ",timespan)
    fname = get_tmpfile(OutPath + model_name)
    model_dbow.save(fname)
    train.to_csv(OutPath+"120000Traindata00.csv")
    return timespan

 

 
Test_sample=[100000,150000,200000,250000,300000,350000,400000,450000,500000,540000]

 
timespan_s = []
timespan_ss=pd.DataFrame(columns=['sample', 'timepan'])
for i in Test_sample:
    OutPath = './'+str(i)+"/"
    model_name = 'sample'
    CSV_name = 'sample.csv'
    Image_name = "sample.png"
    Bar_name = "Bar.png"
    k = 16
    #OutPath=OutPath+str(i)+"/"
    model_name=model_name
    CSV_name=CSV_name
    Image_name=Image_name
    Bar_name=Bar_name
    mkdir(OutPath)
    print(OutPath)

    if  i ==150000:  k = 14
    if i == 200000:  k =15
    if i == 250000:  k =15
    if i == 300000:   k = 16
    if i == 350000:   k = 16
    if i == 450000:   k = 16
 


    print(k,i,Test_sample.index(i),OutPath, model_name, CSV_name, Image_name, Bar_name)
    timespan=Workload_sum(k, i, OutPath, model_name, CSV_name, Image_name,Bar_name)
    timespan_s.append(timespan)
    timespan_ss.loc[Test_sample.index(i)]=[int(i),timespan]


'''
timespan_ss.to_csv("try.csv")
timespan_s=np.array(timespan_s)
Test_samples=np.array(Test_sample)
trainfig=plt.figure()
plt.plot(Test_samples, timespan_s,label='Query2vec model',marker='o', markersize=5)
plt.ylabel('Total training time (secs)', fontsize=12)
plt.xlabel('Input query log size (#queries)', fontsize=12)
plt.title("Query2vec Model Training Time")
plt.xticks(rotation=45)
plt.show();
plt.legend()
trainfig.savefig(OutPath+"/Traintime.png")

'''





