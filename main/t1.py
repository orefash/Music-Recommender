import eyeD3
from eyed3.id3 import ID3_V1_0, ID3_V1_1, ID3_V2_3, ID3_V2_4
from mutagen import File
from os import listdir
import os.path
from os.path import isfile, join
import sys, re
import ntpath
import csv
import MySQLdb

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def titleResolve(path):   
    pap = path.split("/")[-1]
    key = re.sub(r',',"",pap.split('/')[-1])
    key = re.sub(r';',"",key)
    return pap

def get(path):
    a = path_leaf(path)
    taglist = []
    tag = eyeD3.Tag()
    try:
        trackInfo = eyeD3.Mp3AudioFile(path)
        Duration = trackInfo.getPlayTimeString()
    except:
        Duration = "Unknown"
    else:
        Duration = trackInfo.getPlayTimeString()

    tag.link(path)    

    if tag.getArtist() == "":
        Artist = "Unknown Artist"
    else:
        Artist = tag.getArtist()
    
    if tag.getAlbum() == "":
        Album = "Unknown Album"
    else:
        Album = tag.getAlbum()
    
    if tag.getTitle() == "":

        Title = titleResolve(path)
    else:
        Title = tag.getTitle()
    try:
        g = tag.getGenre()
    except:
        Genre = "Unknown"#tag.getGenre()
    else:
        if g == None:
            Genre = "Unknown"
        else:
            #bdir = dirs.encode('utf-8')
            junk = tag.getGenre()
            Genre = junk
    #print str(Genre)+"1"
    taglist.extend([a,Title,Artist,Album,Duration,str(Genre)])
    #print taglist[5]
    return taglist

def findMusic(path):
    myPath =  path#"/home/orefash/Music/music"#raw_input()
    files = [myPath+"/"+file for file in listdir(myPath) if  re.match(r'(.*)mp3',file)]
    return files 

def rec():
    print 'a'
    #SELECT col1 FROM tbl ORDER BY RAND() LIMIT 10
    #connect to db
    #db = MySQLdb.connect("localhost","id1191920_orefash","AllHail1Me","id1191920_main_db" )
    try:
        #db = MySQLdb.connect("johnny.heliohost.org","orefash","AllHail1Me","orefash_musicdb" )
        db = MySQLdb.connect("localhost","root","AllHail1Me","musicdb" )
        cursor = db.cursor()
        print "yes"
         
        #insert to table
        try:
            #print i[0]
            #print "here is %s"%(i[0])
            print "f"
            #show table
            #a = []
            b = []
            cursor.execute("""SELECT * FROM mytable ORDER BY RAND() LIMIT 10""")

            for row in cursor.fetchall():
                a =[]
                for i in row:
                    a.append(i)
                b.append(a)

                #print row[0]

            #cursor.execute("""#INSERT INTO music_tab(name,title,artist,album,duration) VALUES ('%s','%s','%s','%s','%s') """%(i[0],i[1],i[2],i[3],i[4]))
            #db.commit()
            print len(b)
            
        except Exception, e: 
            print "error: %s" %e   
            db.rollback()

        #print a[0][2]
        #show table
        #cursor.execute("""SELECT * FROM anooog1;""")

        #print cursor.fetchall()
        db.close()
        return b
    except Exception, e:
        print "Unable to connect to database: %s" %e
    #db = MySQLdb.connect("localhost","orefash","AllHail1Me","musicdb" )
    #setup cursor

#print "fash"
##path = '/media/orefash/New Volume/driv'
#print "path in album"
#print path
#files =  findMusic(path)
#l = []
#for i in files:
 #   k = get(i)
  ## l.append(k)