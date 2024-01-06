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


original = pd.read_csv('anonQCut.csv', engine='python')
original["id"] = range(len(original))
df = original.loc[original['dbname'].isin(['UKIDSSDR10PLUS', 'UKIDSSDR8PLUS', 'UKIDSSDR7PLUS'])]
df = df.sample(n=30000)
print(df.shape)

train, test = train_test_split(df, test_size=0.3, random_state=42)

train_tagged = train.apply(
    lambda r: TaggedDocument(words=(EX.SqlExtractor(r['queryStr']).tokens), tags=["train_" + str(r["id"])]), axis=1)
print(train_tagged.values[30])

test_tagged = test.apply(
    lambda r: TaggedDocument(words=(EX.SqlExtractor(r['queryStr']).tokens), tags=["test_" + str(r["id"])]), axis=1)

print("Start preparing test corpus...\n")



hyperparams = {
    'min_count': [2,3,5],
    'iter': [50, 100, 150],
    'window': [20,50],
    'alpha': [0.025, 0.01, 0.05],
    'minalpha': [0.025, 0.0001],
  }

'''
      for epoch in iter:
      model_dbow.train(utils.shuffle([x for x in tqdm(corpus.values)]), total_examples=len(corpus.values),
                       epochs=1)
      model_dbow.alpha -= 0.0001  
      model_dbow = Doc2Vec( vector_size=300, min_count = choice(hyperparams['min_count']),
                         window= choice(hyperparams['window']), alpha = choice(hyperparams['alpha']),
                          min_alpha=choice(hyperparams['minalpha']), epochs=choice(hyperparams['iter']),
                         workers=cores)  
  '''

def doc2vecTraining(hyperparams,corpus):
    cores = multiprocessing.cpu_count()
    model_dbow = Doc2Vec( vector_size=300, min_count = choice(hyperparams['min_count']),
                         window= choice(hyperparams['window']), alpha = choice(hyperparams['alpha']),
                          min_alpha=choice(hyperparams['minalpha']), epochs=choice(hyperparams['iter']),
                         workers=cores)  
    print("min_count: ",model_dbow.min_count,
          "\nwindow size: "  ,model_dbow.window,
          "\nalpha: ", model_dbow.alpha,
          "\nmin_alpha: ", model_dbow.min_alpha,
          "\nepochs: ", model_dbow.epochs
          )

    model_dbow.build_vocab([x for x in tqdm(corpus.values)])
    iter=choice(hyperparams['iter'])

    model_dbow.train([x for x in tqdm(corpus.values)], total_examples=len(corpus.values), epochs=model_dbow.epochs)

   # fname = get_tmpfile(str(random.randint(1,1000))+"_model")
   # model_dbow.save(fname)
    return model_dbow
model=doc2vecTraining(hyperparams,train_tagged)


def test_mostsimilar(testSql,model):
    sql = EX.SqlExtractor(testSql).tokens
    print(sql)
    infer_vector = model.infer_vector(sql)
    similar_documents = model.docvecs.most_similar([infer_vector])
    print("Original sql is :\n", testSql, "\n",
          "The similar sqls with scores are the following:\n", "sql:       Scores:",)
    for i in similar_documents:
               print(EX.SqlExtractor(original.iloc[int(i[0][6:])]["queryStr"]).tokens, i[1])




model=doc2vecTraining(hyperparams,train_tagged)
sql= "SELECT * FROM lasSource AS po  WHERE (po.htmID >= 14926756184064)  AND (po.htmID <= 14926760378367) "
test_mostsimilar(sql,model)


sql='SELECT count(*)*0.9*0.0518*0.95 as commonArea FROM (  select distinct frameSetID ' \
    ' from gcsSource s, gcsSourceXDR7PhotoObj as x WHERE s.sourceID=x.masterObjID ) as t '
sql='SELECT   CAST(ROUND(l*6.0,0) AS INT)/6.0 AS lon,           CAST(ROUND(b*6.0,0) AS INT)/6.0 AS lat,      ' \
    '    COUNT(*)                        AS num FROM     gpsSource WHERE    k_1Class BETWEEN -2 AND -1 AND      ' \
    '     k_1ppErrBits < 256         AND /* Make a seamless selection (i.e. exclude     duplicates) in any overlap regions: */  ' \
    '        (priOrSec=0 OR priOrSec=frameSetID) ' \
    '/* Bin up in 10 arcmin x 10 arcmin cells: */ GROUP BY CAST(ROUND(l*6.0,0) AS INT)/6.0,          CAST(ROUND(b*6.0,0) AS INT)/6.0 '
test_mostsimilar(sql,model)


# TSNE visualization--using bokeh  in two different ways for cluster
from sklearn.manifold import TSNE
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
def TSNE_visualize(tsne_d2v_df, outfile):
    output_notebook()
    TSNE_plot = bp.figure(plot_width=1200, plot_height=1000,
                          title="Queries clustered by K-means using T-SNE",
                          tools="pan, wheel_zoom, box_zoom, reset, hover, save",
                          x_axis_type=None, y_axis_type=None, min_border=1)

    Source = ColumnDataSource(data=dict(x=tsne_d2v_df["x"],
                                        y=tsne_d2v_df["y"],
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


# first K-means then T-SNE

TSNE_visualize(tsne_d2v_df, "723firstTSNE.html")
