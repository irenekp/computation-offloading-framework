
import numpy as np
import pandas as pd
import networkx as nx
import nltk
import string
import random
from nltk.corpus import stopwords
import re
from nltk.tokenize import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity
import timeit

#write to file
def dictToFile(filename, dic):
  target = open(filename, 'w')
  target.write(str(dic))
  target.close()

def fileToDict(filename):
  dic = eval(open(filename, 'r').read())
  return dic

def toFileNpArray(filename, arr):
  a_file = open(filename, "w")
  for row in arr:
      np.savetxt(a_file, row)
  a_file.close()
  return arr.shape

def fromFileList(filename):
  with open(filename) as f:
    lines = f.read().splitlines()
  return lines
def fromFileNpArray(filename,shape):
  arr = np.loadtxt(filename).reshape(*shape)
  return arr

def generate_id(size=7, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def append_id(filename):
    return "{0}_{2}.{1}".format(*filename.rsplit('.', 1) + [generate_id()])

def getWordEmbeddings():
  # Extract word vectors
  word_embeddings = {}
  f = open('Trails/glove.6B.100d.txt', encoding='utf-8')
  for line in f:
      values = line.split()
      word = values[0]
      coefs = np.asarray(values[1:], dtype='float32')
      word_embeddings[word] = coefs
  f.close()
  return word_embeddings

#offloadable
def textPreprocessing(filename):
  sentences=fromFileList(filename)
  # remove punctuations, numbers and special characters
  clean_sentences = pd.Series(sentences).str.replace("[^a-zA-Z]", " ")

  # make alphabets lowercase
  clean_sentences = [s.lower() for s in clean_sentences]
  #remove stop words
  stop_words = stopwords.words('english')
  x=list()
  for sen in clean_sentences:
    sen=sen.split()
    sen_new = " ".join([i for i in sen if i not in stop_words])
    x.append(sen_new)
  cleanFileName=append_id(filename)
  ret=dict()
  ret['clean_sentences']=clean_sentences
  ret['sentences']=sentences
  dictToFile(cleanFileName,ret)
  return cleanFileName

#offloadable
def MLmath(cleanFileName):
  ip=fileToDict(cleanFileName)
  clean_sentences=ip['clean_sentences']
  sentences=ip['sentences']
  sentence_vectors = []
  word_embeddings = getWordEmbeddings()
  for i in clean_sentences:
    if len(i) != 0:
      v = sum([word_embeddings.get(w, np.zeros((100,))) for w in i.split()])/(len(i.split())+0.001)
    else:
      v = np.zeros((100,))
    sentence_vectors.append(v)
    # similarity matrix
  sim_mat = np.zeros([len(sentences), len(sentences)])
  for i in range(len(sentences)):
    for j in range(len(sentences)):
      if i != j:
        sim_mat[i][j] = cosine_similarity(sentence_vectors[i].reshape(1,100), sentence_vectors[j].reshape(1,100))[0,0]
  nx_graph = nx.from_numpy_array(sim_mat)
  scores = nx.pagerank(nx_graph)
  ranked_sentences = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)
  res=dict()
  res['ranked_sentences']=ranked_sentences
  sumFileName=append_id(cleanFileName)
  dictToFile(sumFileName,res)
  return sumFileName

#offloadable
def writeSummary(filename, outfile):
  res=fileToDict(filename)
  ranked_sentences=res['ranked_sentences']
  outfile = open(outfile, 'w')
  for i in range(10):
    print(ranked_sentences[i][1])
    outfile.write(ranked_sentences[i][1])

def summarizerMain(filename, outfile):
  cleanFileName = textPreprocessing(filename)
  sumFileName = MLmath(cleanFileName)
  writeSummary(sumFileName, outfile)

#main
if __name__ == "__main__":
  start_time = timeit.default_timer()
  filename= '../../nyt_small.txt'
  cleanFileName = textPreprocessing(filename)
  sumFileName = MLmath(cleanFileName)
  writeSummary(sumFileName)
  print("Elapsed: " + str(timeit.default_timer()-start_time))



