import pandas as pd
from bokeh.models import ColumnDataSource
from tqdm import tqdm
import extract as EX
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
import multiprocessing
import random
from sklearn.manifold import TSNE


OutPath='/lustre/home/d171/s1926539/dissertation/s1926539/Data_code/Dissertationcode/TrainDoc2vecOutput/'

#read corpus in CSV format
original = pd.read_csv('anonQCut.csv', engine='python')
original["id"] = range(len(original))
df = original.loc[original['dbname'].isin(['UKIDSSDR10PLUS', 'UKIDSSDR8PLUS', 'UKIDSSDR7PLUS'])]
df = df.sample(n=30000)
print(df)
print(df.shape)
#tag corpus
train, test = train_test_split(df, test_size=0.2, random_state=42)

train_tagged = train.apply(
    lambda r: TaggedDocument(words=(EX.SqlExtractor(r['queryStr']).tokens), tags=["train_" + str(r["id"])]), axis=1)
print(train_tagged.values[30])
test_tagged = test.apply(
    lambda r: TaggedDocument(words=(EX.SqlExtractor(r['queryStr']).tokens), tags=["test_" + str(r["id"])]), axis=1)

print("Start preparing test corpus...\n")




#Doc2vec model 
def doc2vecTraining(corpus):
    cores = multiprocessing.cpu_count()
    model = Doc2Vec(vector_size=300, min_count=3,
                         window=50, alpha=0.05,
                         min_alpha=0.0001, epochs=150,
                         workers=cores)
    print("min_count: ",model.min_count,
          "\nwindow size: "  ,model.window,
          "\nalpha: ", model.alpha,
          "\nmin_alpha: ", model.min_alpha,
          "\nepochs: ", model.epochs
          )
  
    model.build_vocab([x for x in tqdm(corpus.values)])
    model.train([x for x in tqdm(corpus.values)], total_examples=len(corpus.values), epochs=model.epochs)
    return model
    
    
    
model_dbow=doc2vecTraining(train_tagged)
fname = get_tmpfile(OutPath+"model/window50model")
print(fname)
model_dbow.save(fname)

#generate cluster colors in visualization

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




#NOTE: using QueryVec algorithm
# Clustering using K-means++

def K_means(k,vector):
    kmeans_model = KMeans(n_clusters=k, init='k-means++', max_iter=400)
    X = kmeans_model.fit(vector)
    labels = kmeans_model.labels_.tolist()
    centroids = kmeans_model.cluster_centers_
    return labels,centroids
labels,centroids=K_means(14,model_dbow.docvecs.vectors_docs)



#PCA visualization
pca = PCA(n_components=2).fit(model_dbow.docvecs.vectors_docs)
datapoint = pca.transform(model_dbow.docvecs.vectors_docs)

# PCA visualization--using matplotlib


import matplotlib.pyplot as plt

fig_PCA = plt.figure()
label1 = colorList(16)  # NOTE:same number with n_clusters
color = [label1[i] for i in labels]
plt.scatter(datapoint[:, 0], datapoint[:, 1], c=color)

centroidpoint = pca.transform(centroids)
plt.scatter(centroidpoint[:, 0], centroidpoint[:, 1], marker='^', s=20, c='#000000')
plt.show()
fig_PCA.savefig(OutPath+"outputfigure/PCA/plt_window50.png")

# PCA visualization--using bokeh
output_notebook()
PCA = bp.figure(plot_width=1200, plot_height=1000,
                title="Queries clustered by K-means using PCA",
                tools="pan, wheel_zoom, box_zoom, reset, hover, save",
                x_axis_type=None, y_axis_type=None, min_border=1)


source = ColumnDataSource(data=dict(x=datapoint[:, 0],
                                    y=datapoint[:, 1],
                                    color=color,
                                    queryStr=train["queryStr"].values,
                                    id=train["id"].values,
                                    tags=labels))
PCA.scatter(x="x",
            y="y",
            color="color",
            legend_label="tags",
            source=source,
            alpha=0.5)

PCA.diamond_cross(x=centroidpoint[:, 0],
                  y=centroidpoint[:, 1],
                  color="#000000",
                  legend_label="centroids",
                  alpha=1,
                  size=20)

hover = PCA.select(dict(type=HoverTool))

hover.tooltips = {"id": "@id",
                  "queryStr": "@queryStr",
                  "tags": "@tags"}

output_file(OutPath+"outputfigure/PCA/window50.html")

save(PCA)
reset_output()




# TSNE visualization--using bokeh 
tsne_model = TSNE(n_jobs=4,
                  early_exaggeration=4,
                  n_components=2,
                  verbose=1,
                  perplexity=50,
                  random_state=2018,
                  n_iter=5000)
tsne_d2v = tsne_model.fit_transform(model_dbow.docvecs.vectors_docs)  # model_dbow
tsne_d2v_df = pd.DataFrame(data=tsne_d2v, columns=["x", "y"])
tsne_d2v_df["id"] = train["id"].values
tsne_d2v_df["queryStr"] = train["queryStr"].values
tsne_d2v_df["cluster_id"] = labels
tsne_d2v_df["cpu_sec"] = train["cpu_sec"].values
tsne_d2v_df["dbname"] = train["dbname"].values


train["vector_id"]=range(len(train))
train["cluster_id"]=labels

def TSNE_visualize(tsne_d2v_df,colormap,outfile):
    output_notebook()
    TSNE_plot = bp.figure(plot_width=1200, plot_height=1000,
                          title="Queries clustered by K-means using T-SNE",
                          tools="pan, wheel_zoom, box_zoom, reset, hover, save",
                          x_axis_type=None, y_axis_type=None, min_border=1)


    Source = ColumnDataSource(data=dict(x=tsne_d2v_df["x"],
                                        y=tsne_d2v_df["y"],
                                        color=colormap[tsne_d2v_df["cluster_id"]],
                                        queryStr=tsne_d2v_df["queryStr"],
                                        id=tsne_d2v_df["id"],
                                        tags=tsne_d2v_df["cluster_id"]))
    TSNE_plot.scatter(x="x",
                      y="y",
                      color="color",
                      legend_label="tags",
                      source=Source,
                      alpha=0.6)

    Hover = TSNE_plot.select(dict(type=HoverTool))

    Hover.tooltips = {"cluster id": "@tags",
                      "id": "@id",
                      "queryStr": "@queryStr",
                      }

    output_file(outfile)
    save(TSNE_plot)

#Output the most representative Query 
def calculate_representativeQuery(vector,train,K,centroids):
   All_cosine=[]
   for id in range(K):
       cluster_cosine= pd.DataFrame(columns=['query_id','cosine_similarity'])
       cluster_queries=train[train["cluster_id"]==id]
       for i in range(len(cluster_queries)):
           query=cluster_queries.iloc[i]
           index=query["vector_id"]
           result = 1 - spatial.distance.cosine(vector[index], centroids[id])
           cluster_cosine.loc[i]=[str(query["id"])]+[result]
       cluster_cosine.sort_values(by="cosine_similarity", ascending=False)
       All_cosine.append(int(cluster_cosine.iloc[0]["query_id"]))
   return All_cosine


#first K-means then T-SNE
colormap = np.array(label1)
TSNE_visualize(tsne_d2v_df,colormap,OutPath+"outputfigure/TSNE/window50TSNE.html")
vector = model_dbow.docvecs.vectors_docs
centroidslist=calculate_representativeQuery(vector,train,14,centroids)


#save every cluster representative point with its other attributes
represent_list=train[train["id"].isin(centroidslist)]
represent_list.to_csv(OutPath+"outputcsv/firstTSNE/represent.csv")



#save train and test corpus
train.to_csv(OutPath+"outputcsv/traindata/Tata.csv")
test.to_csv(OutPath+"outputcsv//window50data.csv")


#save doc2vec model
