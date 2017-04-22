 #!/usr/bin/python
from essentia.standard import MonoLoader
from essentia.standard import LowLevelSpectralEqloudExtractor
from essentia.standard import LowLevelSpectralExtractor
from essentia.standard import Loudness
from essentia.standard import RhythmExtractor2013
from essentia.standard import KeyExtractor
from essentia.standard import LogAttackTime
import essentia.streaming
import numpy as np
from math import sqrt
import re
from os import listdir
from multiprocessing import Pool,Lock
from random import randint
import csv
from suggest1 import smain

dataset = {}
lock = Lock()


#LOAD THE CSV WITH DATA ALREADY BEEN EXTRACTED SO WE DONT HAVE TO EXTRACT THEM AGAIN
def load():
    print "\n\tLoading Files....."
    line = csv.reader(open("data.csv","r"))
    datas  =  list(line)
    global dataset
    for i in datas:
        try:
            dataset[i[0]] = [float(x) for x in i[1:]]
        except ValueError:
            print "error"

    print "\tLoading Complete...."  
    return dataset

#FIND DISTANCE BETWEEN SONGS
def euclidieanDistance(listOne,listTwo):
	distance = 0
	length = len(listOne)
	for i in range(length):
		distance += (listOne[i]-listTwo[i])*(listOne[i]-listTwo[i])
	return sqrt(distance)

#EXTRACT FEATURES
def lowLevel(songName):
	global dataset
	global lock
	print songName
	#REMOVE ; AND , FROM SONGNAMES
	key = re.sub(r',',"",songName.split('/')[-1])
	key = re.sub(r';',"",key)
	#DONT HAVE TO EXTRACT IF IT IS ALREADY EXTRACTED
	if key in dataset.keys():
		feature = dataset[key]
		return feature
	else:
		loader = MonoLoader(filename = songName)
		audio = loader()
		extractor = LowLevelSpectralEqloudExtractor()
		feature =list(extractor(audio))
		del feature[1];del feature[1]
		extractor =LowLevelSpectralExtractor()
		featureTwo = list(extractor(audio))
		del  featureTwo[0]
		del featureTwo[-2]
		featureTwo[4] = feature[4][1]
		feature.extend(featureTwo)
		extractor = Loudness()
		feature.append(extractor(audio))
		extractor = LogAttackTime()
		feature.append(extractor(audio)[0])
		extractor = KeyExtractor()
		feature.append(extractor(audio)[2])
		extractor = RhythmExtractor2013()
		data = extractor(audio)
		feature.append(data[0])
		feature.append(data[2])
		for x in  range(len(feature)) :
			if type(feature[x]) is  np.ndarray :
				#feature[x] = avg(feature[x])
				mean,std =stdDev(feature[x])
				feature[x] = mean
				feature.append(std) 
		arr = key+","+str(feature)[1:-1]+"\n"
 		f=  open('data.csv','a')
 		lock.acquire()
 		f.write(arr)
 		lock.release()
 		f.close()
		return feature

def avg(arr):
    return sum(arr)/len(arr)

#Find standard deviation
def stdDev(arr):
	mean = avg(arr)
	diff = sum([(x-mean)**2 for x in arr])
	return mean,sqrt(diff/len(arr))


#TO RANGE 0.1 and 100   
def normalize(val,norm):
 	for i in range(len(val)):
    		val[i] = ((val[i]- norm[i][1])/(norm[i][0]-norm[i][1]))*(1-0.1)+0.1
    	return val

#COST FOR CLUSTERS
def findCost(medoid,names,distance):
	cost = 0
	for i in range(len(names)):
		temp = distance[medoid[0]][i]
		for x in medoid:
			if distance[x][i] < temp:
				temp = distance[x][i]
		cost += temp
	return cost

#FIND NEW MEDOIDS 
def recluster(medoid,names,distance,numCluster,clusters):
	medNum = 0
	newMedoids = []
	newMedoids.extend(medoid)
	newCost = 0
	rMedoid = []
	while(medNum < len(medoid)):
		arr=clusters[medoid[medNum]]
		for start in range(len(arr)):
			newMedoids[medNum] = arr[start]
			cost = findCost(newMedoids,names,distance)
			if  cost < newCost or newCost == 0: 
				newCost = cost
				rMedoid = []
				rMedoid.extend(newMedoids)
			start += 1
		for x in range(len(newMedoids)):
			newMedoids[x] = medoid[x]
		medNum += 1
	return newCost,rMedoid

#SONGS ARE CLUSTERED BASED ON MEDOIDS
def cluster(medoid,names,distance,numCluster):
	clusters = {}
	for med in medoid:
		clusters[med] = []
	cost=0;
	for i in range(len(names)):
		temp = distance[medoid[0]][i]
		closestMedoid = medoid[0]
		for x in medoid:
			if distance[x][i] < temp:
				temp = distance[x][i]
				closestMedoid = x
		cost += temp
		clusters[closestMedoid].append(names[i])
	newCost,newMedoids = recluster(medoid,names,distance,numCluster,clusters)
	if newCost < cost:
		cost,clusters = cluster(newMedoids,names,distance,numCluster)
	return cost,clusters

#OPEN FOLDER AND SCAN FOR mp3
def findMusic(myPath):
	print "Enter The path : example /home/swaraj/Music \n"
	#myPath = raw_input()
	#myPath = "/home/oem/Music"
	#myPath = "/media/orefash/New Volume/down/Bruno Mars - 24K Magic/uk top"
	files = [myPath+"/"+file for file in listdir(myPath) if  re.match(r'(.*)mp3',file)]
	return files
    	
def pool(path):
	global dataset
	dataset = load()
	names = []
	extract = Pool(8)
	featureList = {}
	songList = findMusic(path)
	extractedList = extract.map(lowLevel,songList)
	norm = []
	for i in zip(*extractedList):
		norm.append([max(i),min(i)])
	for x in range(len(songList)):
		randomTemp = re.sub(r',',"",songList[x].split("/")[-1])
		names.append(re.sub(r';',"",randomTemp))
		featureList[names[-1]] =  normalize(extractedList[x],norm)
	distance = {}
	#Find euclidiean Distances
	for song in names:
		distance[song] = []
		current = featureList[song]
		for songitem in  names:
			if songitem == song :
				distance[song].append(0)
			else:
				value = featureList[songitem]
				distance[song].append(euclidieanDistance(current,value))
	#CLUSTERING
	bestCluster = {}
	bestCost = 0
	numCluster = 1
	#CHOOSE MEDOIDS RANDOMLY FOR THE FIRST TIME
	medoid = []
	while(len(medoid) < numCluster):
		temp = randint(0,len(names)-1)
		if names[temp] not in medoid:
			medoid.append(names[temp])	
	#CALL CLUSTER METHOD
	bestCost,bestCluster = cluster(medoid,names,distance,numCluster)
	#PRINTING THE OUTPUT
	print "\n\n",bestCost
	# WRITE TO CSV FILE
	className = 0
	result = str()
	for key,value in bestCluster.iteritems():
			print "\n",key,":",value
			#ADD EACH VALUE TO FILE
			for itr in value:
				index = names.index(itr)
				result += itr
				for item in extractedList[index]:
					result += "," +str(item)
				result += "," + str(className)+"\n"
			className += 1
	with open("storage.csv","wb") as fp:
		fp.write(result)

	k = smain()
	return k
#pool("/media/orefash/700EF6AE0EF66C8A/Users/orefa/Downloads/Billboard 2016 Year End Hot 100 Songs Top Charts")
