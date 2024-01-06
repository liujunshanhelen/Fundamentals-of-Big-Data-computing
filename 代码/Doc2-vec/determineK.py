from tqdm import tqdm
tqdm.pandas(desc="progress-bar")
from gensim.models import Doc2Vec
from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt
import random
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from sklearn import metrics
import matplotlib as plt1

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


model_dbow=Doc2Vec.load("/lustre/home/d171/s1926539/dissertation/s1926539/Data_code/Dissertationcode/QuerylogExtractionResults/540000/sample")

sample= PCA(n_components=2).fit(model_dbow.docvecs.vectors_docs)
X = sample.transform(model_dbow.docvecs.vectors_docs)
K = range(1, 19)


def Elbow(K,X,oufile1,outputfile2):
    distortions = []
    inertias = []
    mapping1 = {}
    mapping2 = {}

    for k in K:
        kmeanModel = KMeans(n_clusters=k, init='k-means++', max_iter=400).fit(X)
        kmeanModel.fit(X)
        distortions.append(sum(np.min(cdist(X, kmeanModel.cluster_centers_,
                                            'euclidean'), axis=1)) / X.shape[0])
        inertias.append(kmeanModel.inertia_)
        mapping1[k] = sum(np.min(cdist(X, kmeanModel.cluster_centers_,
                                       'euclidean'), axis=1)) / X.shape[0]
        mapping2[k] = kmeanModel.inertia_
    for key, val in mapping1.items():
        print(str(key) + ' : ' + str(val))

    fig_PCAElbow = plt.figure()
    plt.plot(K, distortions, 'bx-')
    plt.xlabel('Values of K')
    plt.ylabel('Distortion')
    plt.title('The Elbow Method using Distortion')
    fig_PCAElbow.savefig(oufile1)

    for key, val in mapping2.items():
        print(str(key) + ' : ' + str(val))
    fig_PCAE2 = plt.figure()
    plt.plot(K, inertias, 'bx-')
    plt.xlabel('Values of K')
    plt.ylabel('Inertia')
    plt.title('The Elbow Method using Inertia')
    fig_PCAE2.savefig(outputfile2)
    plt1.rcParams.update({'figure.max_open_warning': 0})
    
    
    
    
#Elbow(K,X,"PCA_Elbow.png","PCA_Elbow_Inertia.png")
outputfile1="/lustre/home/d171/s1926539/dissertation/s1926539/Data_code/Dissertationcode/TrainDoc2vecOutput/determineK/Elbow/PCA_Elbow100.png"
outputfile2="/lustre/home/d171/s1926539/dissertation/s1926539/Data_code/Dissertationcode/TrainDoc2vecOutput/determineK/Elbow/PCA_Elbow_Inertia100.png"
Elbow(K,model_dbow.docvecs.vectors_docs,outputfile1,outputfile2)




Alternative_K=[i for i in range(2,19)]


def Silhouette_Coefficient(Alternative_K,X,outputfile):
    subplot_count = 1
    silhouette=[]
    for k in Alternative_K:
        color = colorList(k)
        subplot_count += 1
        figure = plt.figure()
        kmeans_model = KMeans(n_clusters=k, init='k-means++', max_iter=300).fit(X)
        centroids = kmeans_model.cluster_centers_
        colors = [color[i] for i in kmeans_model.labels_.tolist()]
        if len(X[0])>2:
            sample = PCA(n_components=2).fit(X)
            X = sample.transform(model_dbow.docvecs.vectors_docs)
            centroids = sample.transform(centroids)
        '''
        plt.scatter(X[:, 0], X[:, 1], c=colors, ls='None')
        plt.scatter(centroids[:, 0], centroids[:, 1], marker='^', s=10, c='#000000')
        plt.title('K = %s, Silhouette method = %.03f' % (k, metrics.silhouette_score(X, kmeans_model.labels_, metric='euclidean')))
        figure.savefig(outputfile+str(subplot_count)+".png")
        plt1.rcParams.update({'figure.max_open_warning': 0})
        '''
       
        print('K = %s, Silhouette method = %.03f' % (k, metrics.silhouette_score(X, kmeans_model.labels_, metric='euclidean')))
        silhouette.append(metrics.silhouette_score(X, kmeans_model.labels_, metric='euclidean'))
       
        
    silhouette_figure=plt.figure()
    plt.plot(Alternative_K, silhouette, color='#0047ab', marker='o')
    plt.xlabel("Silhouette_Coefficient")
    plt.ylabel("number of clusters")
    plt.title("Silhouette Coefficient for clusters")
    plt.show()
    silhouette_figure.savefig(outputfile+".png")



'''
Silhouette="/lustre/home/d171/s1926539/dissertation/determineK/SilhouetteC/Silhouette"
Silhouette_Coefficient(Alternative_K,X,Silhouette)
'''

Silhouette="/lustre/home/d171/s1926539/dissertation/s1926539/Data_code/Dissertationcode/TrainDoc2vecOutput/determineK/Silhouette/Silhouette45"
Silhouette_Coefficient(Alternative_K,model_dbow.docvecs.vectors_docs,Silhouette)
