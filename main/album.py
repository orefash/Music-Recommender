import eyeD3
from eyed3.id3 import ID3_V1_0, ID3_V1_1, ID3_V2_3, ID3_V2_4
from os import listdir
from os.path import isfile, join
import re
from mutagen import File



def getname(path):
	tag = eyeD3.Tag()
	tag.link(path)
	if tag.getAlbum() == "":
	    Album = "Unknown Album"
	else:
	    Album = tag.getAlbum()
	return Album

def build(a, f):
	list = []
	for i in range(len(a)):
		list.append([])
	#print a
	for i in range(len(a)):
		list[i].append(a[i])
	c = len(list)
	for i in f:
		l = getname(i)
		if l in a:
			x = a.index(l)
			y = f.index(i)
			try:
				kk = str(f[y])#.encode('utf8')
			except:
				#print f[y]				
				pass
			else:
				list[x].append(kk)

	return list

def albumlist(files):
	list = []
	for i in range(len(files)):
		album = getname(files[i])
		#bdir = str(album)
		if album not in list:
			list.append(album)
	return list
def getCover(a, k):
    #a = str(k)
    file = File(a) # mutagen can automatically detect format and type of tags
    try:
        artwork = file.tags['APIC:'].data
    except TypeError:
    	#print "no"
        p = 0
    except KeyError:
        #print "no"
        p = 0
    else:
    	#print 'yes'
        with open('album/%s.jpg' % k, 'wb') as img:
            img.write(artwork)
    k = k+1
    return k



def findMusic(path):
	myPath =  path#"/home/orefash/Music/music"#raw_input()
	files = [myPath+"/"+file for file in listdir(myPath) if  re.match(r'(.*)mp3',file)]
	return files        

def gmain(path):

    k= 0
	#path = '/media/orefash/New Volume/driv'
    print "path in album"
    print  "cover in cover"
    #print path
    files =  findMusic(path)
    albums = albumlist(files)
    c = build(albums, files)
    #print "length c: "+str(len(c))
    #print "done album"
    for i in c:
        #print "index: "+str(i)
        try:
            p = getCover(i[1],k)
            k = p
        except:
            print i
    return c    

gmain("/media/orefash/New Volume/tor")