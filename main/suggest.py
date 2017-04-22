 # Feature Importance
import csv
import random
import math
import operator

from csv import reader
#from sklearn import datasets
from sklearn import metrics
from sklearn import neighbors
from sklearn import datasets
import numpy as np
from sklearn import svm
from sklearn.externals import joblib 
# load the iris datasets

def load_csv(filename):
    file = open(filename, "rb")
    lines = reader(file)
    dataset = list(lines)
    return dataset

# Convert string column to float
def str_column_to_float(dataset, column):
    for row in dataset:
        row[column] = float(row[column].strip())

def values(l):
    k = []
    n = []
    for i in l:
        k.append(i[0])
        del i[0]
        n.append(i)
    return k,n


def split(t):
    b = []
    a = []
    for i in range(len(t)):
        b.append(t[i][0:len(t[i])])
        a.append(t[i][-1])
    return b,a

def rand(dataset, split, trainingSet=[] , testSet=[]):
    for x in range(len(dataset)):
        for y in range(4):
            dataset[x][y] = float(dataset[x][y])
        if random.random() < split:
            trainingSet.append(dataset[x])
        else:
            testSet.append(dataset[x])

def cmain():
    #dataset = datasets.load_iris()
    # fit an Extra Trees model to the data
    trainingSet=[]
    testSet=[]
    filename = 'storage1.csv'
    file = "main2.csv"

    dataset = load_csv(file)
    set2 = load_csv(filename)

    name,set1 = values(set2)
    n,dataset1 = values(dataset)
    #print set1

    for i in range(0,len(set1[0])):
        str_column_to_float(set1, i)
    testdata, testtarget= split(set1)

    for i in range(0,len(dataset1[0])):
        str_column_to_float(dataset1, i)
    traindata, traintarget= split(dataset1)

    #print "data"+str(len(dataset))
    #print "testdata"+str(len(testdata))
    #print "traindata"+str(len(traindata))

    #clf = joblib.load('rf_recommend.pkl')
    clf = svm.SVC(kernel='linear')
    print clf.fit(traindata, traintarget)  
    joblib.dump(clf, 'rf_recommend.pkl')
    final =[]

    """for i in range(len(testdata)):
        l = []
        k = clf.predict([testdata[i]])
        #print "predict: "+name[i]+" "+str(k)
        #print " actual : "+str(testtarget[i])
        l.append(name[i])
        l.append(str(k))
        final.append(l)"""

    k = clf.predict(testdata)
    print k
    w = []
    for i in range(len(testdata)):
        l = []
        l.append(name[i])
        l.append(str(int(k[i])))
        final.append(l)
    for i in final:
        print i
    #print final
    
    return final

    # 10. Save model for future use
    #joblib.dump(clf, 'rf_recommend.pkl')
    # To load: clf2 = joblib.load('rf_recommend.pkl')

cmain()