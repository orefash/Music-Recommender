import sip
sip.setapi('QString', 2)
import eyeD3
from eyed3.id3 import ID3_V1_0, ID3_V1_1, ID3_V2_3, ID3_V2_4
from mutagen import File
from os import listdir
import os.path
from os.path import isfile, join
import sys, re
from string import digits
from fing import FingerTabWidget
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
from PyQt4.QtWebKit import *
from album import gmain
from PyQt4.phonon import Phonon
from t1 import rec
from pool import pool


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


#for music artcover popup
class MyPopup(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.pic = QLabel()
        self.pixmap = QPixmap("img/image1.jpg")
        pixmap2 = self.pixmap.scaledToWidth(500)
        self.pic.setPixmap(pixmap2)
        self.pic.show()
                
#for recommendation table pop-up
class RecPopup(QWidget):
    def __init__(self,rec_list):
        QWidget.__init__(self)
        head = ( "Title", "Artist", "Album", "Time") #table header labels
        print rec_list
        tabstyle2 = """
            QTableWidget{
            padding: 10px 10px 10px 30px;
            background: #f9f9f9;            
            color: #a5aeb2; 
            selection-color: white;
            font-size: 15px;
            margin:0px;

            }
            QTableWidget::item{
            padding: 15px 0px;            
            color: #a5aeb2;
            border-top: 1px solid #eeeded;

            }
            QTableWidget::item:selected{            
            color: #646a6f;
            background: white;
            border-top: 1px solid #eeeded;
            }
            
        """
        #recommendation table definition
        self.recTable = QtGui.QTableWidget(0, 4)
        self.recTable.setHorizontalHeaderLabels(head)
        self.recTable.setShowGrid(False)
        self.recTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.recTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.recTable.setAutoFillBackground(True)
        self.recTable.setAlternatingRowColors(False)
        self.recTable.horizontalHeader().setDefaultSectionSize(200)
        self.recTable.horizontalHeader().setVisible(False)
        self.recTable.verticalHeader().setVisible(False)
        self.recTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.recTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.recTable.sizePolicy().hasHeightForWidth())
        self.recTable.setSizePolicy(sizePolicy)
        self.recTable.setStyleSheet(tabstyle2)
        
        headr = self.recTable.horizontalHeader()
        headr.setResizeMode(0, QtGui.QHeaderView.Stretch)
        headr.setResizeMode(1, QtGui.QHeaderView.Stretch)
        headr.setResizeMode(2, QtGui.QHeaderView.Stretch)
        headr.setResizeMode(3, QtGui.QHeaderView.ResizeToContents)
        titleItem = QtGui.QTableWidgetItem("Title")
        titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)
        
        artistItem = QtGui.QTableWidgetItem("Artist")
        artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)
        artistItem.setTextAlignment(QtCore.Qt.AlignLeft)

        albumItem = QtGui.QTableWidgetItem("Albumm")
        albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)
        
        timeItem = QtGui.QTableWidgetItem("Genre")
        timeItem.setFlags(timeItem.flags() ^ QtCore.Qt.ItemIsEditable)
        timeItem.setTextAlignment(QtCore.Qt.AlignCenter)

        currentRow = 0
        self.recTable.insertRow(currentRow)
        self.recTable.setItem(currentRow, 0, titleItem)
        self.recTable.setItem(currentRow, 1, artistItem)
        self.recTable.setItem(currentRow, 2, albumItem)        
        self.recTable.setItem(currentRow, 3, timeItem)

        self.recTable.setRowHeight(currentRow, 50)
        self.recTable.show()


#main application window start
class MainWindow(QtGui.QMainWindow):    
    def __init__(self):
        super(QtGui.QMainWindow, self).__init__()
        self.setWindowIcon(QtGui.QIcon('img/Musicplayer-256.png'))
        self.setWindowTitle("Test Music Player")
        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.mediaObject = Phonon.MediaObject(self)
        self.metaInformationResolver = Phonon.MediaObject(self)
        self.mediaObject.setTickInterval(1000)
        #self.mediaObject.tick.connect(self.tick)
        self.mediaObject.currentSourceChanged.connect(self.sourceChanged)
        self.mediaObject.aboutToFinish.connect(self.aboutToFinish)
        
        self.mainMenu = self.menuBar() 
        self.count = 0
        self.tclicked = 0
        self.buttons = {}

        Phonon.createPath(self.mediaObject, self.audioOutput)
        self.setupActions()
        self.setupUi()
        self.sources = []
        self.albumsource = []
        self.resource = []
        self.files = []
        self.a_files = []
        self.album_list = []
        self.rec_list = []
        self.index = 0
        self.current_source = "a"
        self.fulltable =[]

    def setupActions(self):
        #application menu bar definition
        self.FileAction = QtGui.QAction("&Open Folder", self)
        self.FileAction.setShortcut("Ctrl+O")
        self.FileAction.setStatusTip('Select Music')
        self.FileAction.triggered.connect(self.ButAction)
        self.playAction = QtGui.QAction(QtGui.QIcon('img/play.png'), "Play",self, shortcut="Space") #shortcut="Ctrl+P", enabled=False,
        self.playAction.triggered.connect(self.PlayAction)

        self.pauseAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaPause),
                "Pause", self, shortcut="Ctrl+A", enabled=False,
                triggered=self.mediaObject.pause)

        self.stopAction = QtGui.QAction(QtGui.QIcon('img/stop.png'), "Stop",
                self)
        self.stopAction.triggered.connect(self.StopAction)

        self.nextAction = QtGui.QAction(QtGui.QIcon('img/forward.png'),
                "Next", self, shortcut="Ctrl+N")
        self.nextAction.triggered.connect(self.next_track)

        self.previousAction = QtGui.QAction(QtGui.QIcon('img/rewind.png'),
                "Previous", self, shortcut="Ctrl+R")
        self.previousAction.triggered.connect(self.previous_track)
        self.exitAction = QtGui.QAction("E&xit", self, shortcut="Ctrl+X",
                triggered=self.close)
    
    def albumL(self,line):
        self.alist = line
        a_dict = {}
        k = len(self.album_list)

    def popup(self, pos):#main table right-click action
        for i in self.musicTable.selectionModel().selection().indexes():
            print i.row(), i.column()
        menu = QMenu()
        quitAction = menu.addAction("Quit")
        recommendAction = menu.addAction("Recommend")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == quitAction:
            qApp.quit()
        else:
            self.reclist()

        
    def ButAction(self, event):#music load to table function
        self.current_source = "main"
        dirs = QtGui.QFileDialog.getExistingDirectory(self, 'Select Folder')        
        files = [dirs+"/"+file for file in listdir(dirs) if  re.match(r'(.*)mp3',file)]
        self.files.extend(files)#add all song path to file list
        for path in files:
            self.sources.append(Phonon.MediaSource(path))
            self.populate_table(path)#load songs into table
        icon_1 = QtGui.QIcon()
        icon_1.addPixmap(QtGui.QPixmap('img/pause.png'))
        self.playAction.setIcon(icon_1)
        self.playAction.setToolTip('Pause')
        self.album_list = gmain(dirs)#get all albums for album tab
        #self.rec_list = pool(dirs)#extract features from songs
        #self.album_test(self.album_list)#load songs to album tab
        
    def titleResolve(self, path):   
        pap = path.split("/")[-1]
        return pap

    def tagGet(self,path):#get music tags to load into music table
        taglist = []
        tag = eyeD3.Tag()

        try:#to get music play duration
            trackInfo = eyeD3.Mp3AudioFile(path)
            Duration = trackInfo.getPlayTimeString()
        except:
            Duration = "Unknown"
        else:
            Duration = trackInfo.getPlayTimeString()

        tag.link(path)

        try:#get music genre
            g = tag.getGenre()
        except:
            Genre = "Unknown Genre"#tag.getGenre()
        else:
            if g == None:
                Genre = "Unknown Genre"
            else:
                junk = tag.getGenre()
                Genre = junk
        g = str(Genre)
        g = g.replace("(","")
        g = g.replace(")","")
        Genre = g.translate(None,digits)

        #get music arist, album, title, year tags
        if tag.getArtist() == "":
            Artist = "Unknown Artist"
        else:
            Artist = tag.getArtist()
        
        if tag.getAlbum() == "":
            Album = "Unknown Album"
        else:
            Album = tag.getAlbum()
        
        if tag.getTitle() == "":

            Title = self.titleResolve(path)
        else:
            Title = tag.getTitle()
        if tag.getYear() == None:
            Year = " "
        else:
            Year = tag.getYear()
        taglist.extend([Title,Artist,Album,Duration,Year,Genre])
        return taglist


    def album_test(self, line):#function to load album tab in app
        print "In album test"
        self.alist = line
        #print line
        a = len(self.album_list)
        print "a: "+str(a)
        l = 0
        n = 0
        if a/6 < 1:
            c = 1
        else:
            c = a/6 +1
        print "c: "+str(c)
        for i in range(c):
            for j in range(6):                
                if l==a:
                    print "break"
                    break
                if l<a:
                    name = 'album/'+str(l)+'.jpg'
                    if os.path.isfile(name):#create album tab buttons
                        self.buttons[(i, j)] = QtGui.QToolButton(self)
                        self.buttons[(i, j)].setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
                        metrics = QtGui.QFontMetrics(self.font())
                        t = self.alist[l][0]
                        st = t
                        width = metrics.width(t)
                        if width > 240:
                            m = 240.0/width
                            k = m * len(t)
                            m = int(k)
                            p = t.rfind(" ",0,m)
                            st = t[:p] + '\n' + t[p+1:]
                            #print st
                        self.buttons[(i, j)].setText(st)
                        self.buttons[(i, j)].setIcon(QtGui.QIcon(name))
                        self.buttons[(i, j)].setIconSize(QtCore.QSize(240,240))
                        self.buttons[(i, j)].setFixedSize(240,285)
                        print "l: "+str(l)
                        self.buttons[(i, j)].clicked.connect(self.album_table(line[l]))#load album table
                        self.buttons[(i, j)].setStyleSheet("padding:1px; background: white;\
                            border: 2px solid grey")
                        self.verticalLayoutScroll.addWidget(self.buttons[(i, j)], i, j)
                        l = l+1
                        
                    else:
                        self.buttons[(i, j)] = QtGui.QToolButton(self)
                        self.buttons[(i, j)].setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
                        metrics = QtGui.QFontMetrics(self.font())
                        t = self.alist[l][0]
                        st = t
                        width = metrics.width(t)
                        if width > 240:
                            m = 240.0/width
                            k = m * len(t)
                            m = int(k)
                            p = t.rfind(" ",0,m)
                            st = t[:p] + '\n' + t[p+1:]
                            #print st
                        self.buttons[(i, j)].setText(st)
                        self.buttons[(i, j)].setIcon(QtGui.QIcon("img/Musicplayer-256.png"))
                        self.buttons[(i, j)].setIconSize(QtCore.QSize(240,240))
                        self.buttons[(i, j)].setFixedSize(240,285)
                        print "l: "+str(l)
                        self.buttons[(i, j)].clicked.connect(self.album_table(line[l]))
                        self.buttons[(i, j)].setStyleSheet("padding:1px; background: white;\
                            border: 2px solid grey")
                        self.verticalLayoutScroll.addWidget(self.buttons[(i, j)], i, j)
                        l = l+1
                else:
                    print "l::"+str(l)
                    break
        if(a < 6):
            self.verticalLayoutScroll.setColumnStretch(a,1)

    def album_table(self, l):#fill albumtable with songs
        def fill():
            print "triggered"
            a = l[1:]#list of songs in album
            self.a_files = a
            self.albumsource = []
            for i in a:
                self.albumsource.append(Phonon.MediaSource(i))
            print "list"
            self.albumTable.setRowCount(0)
            self.albumTable.clearContents()
            currentRow = 0
            for i in range(1,len(l)):
                path = l[i]
                line = self.tagGet(path)#get song tags
                
                titleItem = QtGui.QTableWidgetItem(line[0])
                titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)
                
                artistItem = QtGui.QTableWidgetItem(line[1])
                artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)
                artistItem.setTextAlignment(QtCore.Qt.AlignLeft)

                albumItem = QtGui.QTableWidgetItem(line[2])
                albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)
                
                timeItem = QtGui.QTableWidgetItem(str(line[3]))
                timeItem.setFlags(timeItem.flags() ^ QtCore.Qt.ItemIsEditable)
                timeItem.setTextAlignment(QtCore.Qt.AlignCenter)

                
                self.albumTable.insertRow(currentRow)
                self.albumTable.setItem(currentRow, 0, titleItem)
                self.albumTable.setItem(currentRow, 1, artistItem)
                self.albumTable.setItem(currentRow, 2, albumItem)        
                self.albumTable.setItem(currentRow, 3, timeItem)

                self.albumTable.setRowHeight(currentRow, 50)
                currentRow = currentRow + 1
        return fill

    def populate_table(self, path):#function to load songs into main table
        #adds songs to table
        line = self.tagGet(path)
        self.fulltable.append(line)
       
        titleItem = QtGui.QTableWidgetItem(line[0])
        titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)
      
        artistItem = QtGui.QTableWidgetItem(line[1])
        artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)
        albumItem = QtGui.QTableWidgetItem(line[2])
        albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)
        
        timeItem = QtGui.QTableWidgetItem(str(line[3]))
        timeItem.setFlags(timeItem.flags() ^ QtCore.Qt.ItemIsEditable)
        timeItem.setTextAlignment(QtCore.Qt.AlignCenter)

        yearItem = QtGui.QTableWidgetItem(str(line[4]))
        yearItem.setFlags(yearItem.flags() ^ QtCore.Qt.ItemIsEditable)
        yearItem.setTextAlignment(QtCore.Qt.AlignCenter)

        currentRow = self.musicTable.rowCount()
        self.musicTable.insertRow(currentRow)
        self.musicTable.setItem(currentRow, 0, titleItem)
        self.musicTable.setItem(currentRow, 1, artistItem)
        self.musicTable.setItem(currentRow, 2, albumItem)
        self.musicTable.setItem(currentRow, 3, yearItem)
        self.musicTable.setItem(currentRow, 4, timeItem)
        self.musicTable.setRowHeight(currentRow, 50)

        if not self.musicTable.selectedItems():
            self.musicTable.selectRow(0)
            self.mediaObject.setCurrentSource(self.metaInformationResolver.currentSource())
        self.index = self.index + 1
        if len(self.sources) > self.index:
            self.metaInformationResolver.setCurrentSource(self.sources[index])
        else:
            if self.musicTable.columnWidth(0) > 300:
                self.musicTable.setColumnWidth(0, 300)


    def tableClicked(self, row, column):#when main table is clicked
        print "In click"
        self.current_source = "main"
        print self.current_source
        self.tclicked = 1
        self.count = self.musicTable.currentRow()
        self.mediaObject.stop()
        self.mediaObject.setCurrentSource(self.sources[self.count])
        self.mediaObject.play()


    def atableClicked(self, row, column):#when album table is clicked
        print "In click"
        self.current_source = "album"
        print self.current_source
        self.tclicked = 1
        self.count = self.albumTable.currentRow()
        print self.count
        self.mediaObject.stop()
        self.mediaObject.setCurrentSource(self.albumsource[self.count])
        self.mediaObject.play()

    def rtableClicked(self, row, column):#when recommend table is clicked
        print "In click"
        self.current_source = "recommend"
        print self.current_source
        self.tclicked = 1
        self.count = self.recTable.currentRow()
        print self.count
        self.mediaObject.stop()
        self.mediaObject.setCurrentSource(self.resource[self.count])
        self.mediaObject.play()

    def sourceChanged(self, source):#current playing song is changed
        a = self.current_source
        if a == "main":#main music table
            self.musicTable.selectRow(self.count)
        elif a == "album":
            self.albumTable.selectRow(self.count)
        else:
            self.recTable.selectRow(self.count)
        print 'kk'
        self.setArt()#load song cover art
        self.setLabel()#load song labels
        
    def reclist(self):#recommendation function
        self.count = self.musicTable.currentRow()        
        self.w = RecPopup(self.rec_list)
        self.w.setGeometry(QRect(0, 0,900,900))



    def on_clicked(self):
        print "recommend"
        x = rec()
        for i in self.fulltable:
            print i
        #line = x
        
        currentRow = 0
        for line in x:
            titleItem = QtGui.QTableWidgetItem(line[1])
            titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)
            
            artistItem = QtGui.QTableWidgetItem(line[2])
            artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)
            artistItem.setTextAlignment(QtCore.Qt.AlignLeft)

            albumItem = QtGui.QTableWidgetItem(line[3])
            albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)
            
            timeItem = QtGui.QTableWidgetItem(str(line[4]))
            timeItem.setFlags(timeItem.flags() ^ QtCore.Qt.ItemIsEditable)
            timeItem.setTextAlignment(QtCore.Qt.AlignCenter)

            self.resource.append(Phonon.MediaSource(line[5]))
            #self.resource.append(line[5])
            
            self.recTable.insertRow(currentRow)
            self.recTable.setItem(currentRow, 0, titleItem)
            self.recTable.setItem(currentRow, 1, artistItem)
            self.recTable.setItem(currentRow, 2, albumItem)        
            self.recTable.setItem(currentRow, 3, timeItem)

            self.recTable.setRowHeight(currentRow, 50)
            currentRow = currentRow + 1
   
    def aboutToFinish(self):#to load next song for playing 
        print 'finish'
        index = self.musicTable.currentRow()        
        if index < len(self.sources)-1:
            index += 1
        else:
            index = 0 
        self.count = index
        self.mediaObject.enqueue(self.sources[index])
            

    def PlayAction(self):
        icon_1 = QtGui.QIcon()
        icon_1.addPixmap(QtGui.QPixmap('img/pause.png'))
        icon_2 = QtGui.QIcon()
        icon_2.addPixmap(QtGui.QPixmap('img/play.png'))
        if self.mediaObject.state() == Phonon.PlayingState:
            self.mediaObject.pause()
            self.playAction.setIcon(icon_2)
            self.playAction.setToolTip('Play')
        elif self.mediaObject.state() == Phonon.PausedState or self.mediaObject.state() == Phonon.StoppedState:
            self.mediaObject.play()
            self.playAction.setIcon(icon_1)
            self.playAction.setToolTip('Pause')

    def StopAction(self):
        icon_2 = QtGui.QIcon()
        icon_2.addPixmap(QtGui.QPixmap('img/play.png'))
        self.mediaObject.stop()
        self.playAction.setIcon(icon_2)
        self.playAction.setToolTip('Play')
    
    def getArt(self):#get cover art
        if self.current_source == "main":
            i = self.musicTable.currentRow()
            filepath = self.files[i]
        else:
            i = self.albumTable.currentRow()
            filepath = self.a_files[i]
        file = File(filepath) # mutagen can automatically detect format and type of tags
        try:
            artwork = file.tags['APIC:'].data
        except TypeError:
            p = 0
        except KeyError:
            p = 0
        else:
            p = 1
            with open('img/image1.jpg', 'wb') as img:
                img.write(artwork)
        return p

    def setArt(self):#set art in gui
        print 'king'
        p = self.getArt()

        if p is 1:
            try:
                self.pix = QtGui.QPixmap("img/image1.jpg")
                print 'in'
            except:
                self.pix = QtGui.QPixmap("img/Musicplayer-256.png") 
            else:
                print 'a'
        else:
            self.pix = QtGui.QPixmap("img/Musicplayer-256.png")
        
        self.pixy = self.pix.scaled(70,70) 
        self.pixy1 = self.pix.scaledToWidth(600)       
        self.pic.setPixmap(self.pixy)
        self.bigpic.setPixmap(self.pixy1)


    def artcover(self, event):#popup cover art
        self.w = MyPopup()
        self.w.setGeometry(QRect(0, 0,500,500))

    def setLabel(self):#set song labels in lower portion of ui
        if self.current_source == "main":
            i = self.musicTable.currentRow()
            path = self.files[i]
        else:
            i = self.albumTable.currentRow()
            path = self.a_files[i]
        tag = eyeD3.Tag()
        tag.link(path)
        if tag.getArtist() == "":
            Artist = "Unknown Artist"
        else:
            Artist = tag.getArtist()

        if tag.getTitle() == "":
            Title = self.titleResolve(path)
        else:
            Title = tag.getTitle() 
        self.artist.setText(Artist)#set artist name in ui
        self.title.setText(Title)#set song name in ui           

    def next_track(self, source):#for next button
        if self.current_source == "main":
            index = self.musicTable.currentRow()       
            if index < len(self.sources)-1:
                index += 1
            else:
                index = 0 # start from the beginning of the list
            self.count = index
            self.mediaObject.setCurrentSource(self.sources[index])
        else:
            index = self.albumTable.currentRow()       
            if index < len(self.albumsource)-1:
                index += 1
            else:
                index = 0 # start from the beginning of the list
            self.count = index
            self.mediaObject.setCurrentSource(self.albumsource[index])
        self.mediaObject.play()
        

    def previous_track(self):#for previous button
        if self.current_source == "main":
            index = self.musicTable.currentRow()       
            if index >0:
                index -= 1
            else:
                index = len(self.sources)-1 # start from the beginning of the list
            self.count = index
            self.mediaObject.setCurrentSource(self.sources[index])
        else:
            index = self.albumTable.currentRow()       
            if index >0:
                index -= 1
            else:
                index = len(self.albumsource)-1 # start from the beginning of the list
            self.count = index
            self.mediaObject.setCurrentSource(self.albumsource[index])
        self.mediaObject.play()


    def onResize(self, event):
        print "resized"
        
    def setupUi(self):#set up music gui    
        self.resize(1123, 759)
        self.centralwidget = QtGui.QWidget(self)
        self.fileMenu = self.mainMenu.addMenu('&File')
        self.fileMenu.addAction(self.FileAction)       

        self.HLayout = QtGui.QHBoxLayout(self)

        self.tabs = QtGui.QTabWidget()#for tabs in ui
        self.tabs.setTabBar(FingerTabWidget(width=350,height=50))
        self.tabs.setTabPosition(QtGui.QTabWidget.West)

        styles = """ 
            QTabBar {color: #c2c5c9;
                      font-size: 15px;
                      padding:0px
                      }
            QTabBar::tab:selected {background: #3c4043;
                                   border-left: 4px solid #646a6f;
                                   }
            QTabBar::tab {background: #373b3f;
                          color: white;
                          }
            
            """
        tabstyle = """
            QTableWidget{
            padding: 10px 10px 10px 30px;
            background: #f9f9f9;            
            color: #a5aeb2; 
            selection-color: white;
            font-size: 15px;
            margin:0px;

            }
            QTableWidget::item{
            padding: 15px 0px;            
            color: #a5aeb2;
            border-top: 1px solid #eeeded;

            }
            QTableWidget::item:selected{            
            color: #646a6f;
            background: white;
            border-top: 1px solid #eeeded;
            }
            
        """
        tabstyle2 = """
            QTableWidget{
            padding: 10px 10px 10px 30px;
            background: #f9f9f9;            
            color: #a5aeb2; 
            selection-color: white;
            font-size: 15px;
            margin:0px;

            }
            QTableWidget::item{
            padding: 15px 0px;            
            color: #a5aeb2;
            border-top: 1px solid #eeeded;

            }
            QTableWidget::item:selected{            
            color: #646a6f;
            background: white;
            border-top: 1px solid #eeeded;
            }
            
        """
        self.tabs.setStyleSheet(styles)#style music table
        self.TLayout = QtGui.QHBoxLayout(self)
        bar = QtGui.QToolBar()#create music ui buttons
        bar.addAction(self.playAction)
        bar.addAction(self.previousAction)
        bar.addAction(self.stopAction)
        bar.addAction(self.nextAction)

        headers = ( "Title", "Artist", "Album", "Year", "Time")#main table header labels

        self.musicTable = QtGui.QTableWidget(0, 5)#create main music table in ui
        self.musicTable.setHorizontalHeaderLabels(headers)
        self.musicTable.setShowGrid(False)
        self.musicTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.musicTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.musicTable.setAutoFillBackground(True)
        self.musicTable.setAlternatingRowColors(False)
        self.musicTable.horizontalHeader().setDefaultSectionSize(200)
        self.musicTable.horizontalHeader().setVisible(False)
        self.musicTable.verticalHeader().setVisible(False)
        self.musicTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.musicTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.musicTable.cellDoubleClicked.connect(self.tableClicked)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.musicTable.sizePolicy().hasHeightForWidth())
        self.musicTable.setSizePolicy(sizePolicy)
        self.musicTable.setStyleSheet(tabstyle)
        self.musicTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.musicTable.customContextMenuRequested.connect(self.popup)

        self.tabs.addTab(self.musicTable, 'Tracks')#add to tracks tab in ui
        
        header = self.musicTable.horizontalHeader()#format music table columns
        header.setResizeMode(0, QtGui.QHeaderView.Stretch)
        header.setResizeMode(1, QtGui.QHeaderView.Stretch)
        header.setResizeMode(2, QtGui.QHeaderView.Stretch)
        header.setResizeMode(3, QtGui.QHeaderView.Stretch)
        header.setResizeMode(4, QtGui.QHeaderView.ResizeToContents)
        
        self.TLayout.addWidget(self.tabs)
        
        self.seekSlider = Phonon.SeekSlider(self)#initialize play slider
        self.seekSlider.setMediaObject(self.mediaObject)
        self.seekSlider.setStyleSheet(self.stylesheet())

        self.volumeSlider = Phonon.VolumeSlider(self)#volume slider
        self.volumeSlider.setAudioOutput(self.audioOutput)
        self.volumeSlider.setSizePolicy(QtGui.QSizePolicy.Maximum,
                QtGui.QSizePolicy.Maximum)
        volumeLabel = QtGui.QLabel()

        self.pic = QtGui.QLabel(self)#initialize music cover icon in lower ui
        self.pix = QtGui.QPixmap('img/Musicplayer-256.png')
        self.pixmap = self.pix
        self.pixmap2 = self.pixmap.scaled(70,70)
        self.pic.setPixmap(self.pixmap2)
        self.pic.setStyleSheet("background: grey")
        self.pic.mousePressEvent = self.artcover

        self.nplay = QtGui.QWidget()#initialize now pplaying tab
        self.nplay.setStyleSheet("background: white;")
        self.tabs.addTab(self.nplay, 'Now Playing')
        self.cover_layout = QtGui.QGridLayout()
        self.cover_layout.setColumnStretch(0, 1)
        self.cover_layout.setColumnStretch(3, 1)
        self.cover_layout.setRowStretch(0, 1)
        self.cover_layout.setRowStretch(3, 1)
        self.bigpic = QtGui.QLabel(self)
        self.cover_layout.addWidget(self.bigpic, 1, 1, 2, 2)
        self.nplay.setLayout(self.cover_layout)  

        self.rectab = QtGui.QWidget()
        self.rectab.setStyleSheet("background: white;")
        self.tabs.addTab(self.rectab, 'Recommended')
        self.mLayout = QtGui.QVBoxLayout(self)
        
        head = ( "Title", "Artist", "Album", "Time")

        self.recTable = QtGui.QTableWidget(0, 4)
        self.recTable.setHorizontalHeaderLabels(head)
        self.recTable.setShowGrid(False)
        self.recTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.recTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.recTable.setAutoFillBackground(True)
        self.recTable.setAlternatingRowColors(False)
        self.recTable.horizontalHeader().setDefaultSectionSize(200)
        self.recTable.horizontalHeader().setVisible(False)
        self.recTable.verticalHeader().setVisible(False)
        self.recTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.recTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.recTable.cellDoubleClicked.connect(self.rtableClicked)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.recTable.sizePolicy().hasHeightForWidth())
        self.recTable.setSizePolicy(sizePolicy)
        self.recTable.setStyleSheet(tabstyle2)

        #self.tabs.addTab(self.recTable, 'Tracks')
        
        headr = self.recTable.horizontalHeader()
        headr.setResizeMode(0, QtGui.QHeaderView.Stretch)
        headr.setResizeMode(1, QtGui.QHeaderView.Stretch)
        headr.setResizeMode(2, QtGui.QHeaderView.Stretch)
        headr.setResizeMode(3, QtGui.QHeaderView.ResizeToContents)

        self.inLayout = QtGui.QHBoxLayout(self)
        self.inLayout.addStretch()
        self.button = QtGui.QPushButton("Recommend", self)
        self.button.clicked.connect(self.on_clicked)
        self.inLayout.addWidget(self.button)
        self.mLayout.addLayout(self.inLayout)
        self.mLayout.addWidget(self.recTable)


        self.rectab.setLayout(self.mLayout)

        self.album1 = QtGui.QWidget()#album tab in ui
        self.album1.setStyleSheet("background: white;")
        self.tabs.addTab(self.album1, 'Albums')
        self.albumLayout = QtGui.QVBoxLayout(self)
        self.albumGrid = QtGui.QHBoxLayout(self)
        self.albumList = QtGui.QHBoxLayout(self)  
        self.Xlay = QtGui.QVBoxLayout(self)                     
        self.albumLayout.addLayout(self.albumList)
        
        self.album1.setLayout(self.albumLayout)
        
        head = ( "Title", "Artist", "Album", "Time")

        self.albumTable = QtGui.QTableWidget(0, 4)#initialize album table
        self.albumTable.setHorizontalHeaderLabels(head)
        self.albumTable.setShowGrid(False)
        self.albumTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.albumTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.albumTable.setAutoFillBackground(True)
        self.albumTable.setAlternatingRowColors(False)
        self.albumTable.horizontalHeader().setDefaultSectionSize(200)
        self.albumTable.horizontalHeader().setVisible(False)
        self.albumTable.verticalHeader().setVisible(False)
        self.albumTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.albumTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.albumTable.cellDoubleClicked.connect(self.atableClicked)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.albumTable.sizePolicy().hasHeightForWidth())
        self.albumTable.setSizePolicy(sizePolicy)
        self.albumTable.setStyleSheet(tabstyle2)
        #self.tabs.addTab(self.albumTable, 'Tracks')
        
        headr = self.albumTable.horizontalHeader()
        headr.setResizeMode(0, QtGui.QHeaderView.Stretch)
        headr.setResizeMode(1, QtGui.QHeaderView.Stretch)
        headr.setResizeMode(2, QtGui.QHeaderView.Stretch)
        headr.setResizeMode(3, QtGui.QHeaderView.ResizeToContents)
        
        self.albumGrid.addWidget(self.albumTable)
        self.scrollArea = QtGui.QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFixedHeight(245)
        self.scrollArea.setStyleSheet("background: grey")
        self.scrollAreaWidgetContents = QtGui.QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.Xlay.addWidget(self.scrollArea)

        self.verticalLayoutScroll = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.albumLayout.addWidget(self.scrollArea)
        self.albumLayout.addLayout(self.albumGrid)#end of album tab in ui

        bottom = QtGui.QWidget(self)#bottom widget in ui
        bottom.setStyleSheet("background: #e83c00; margin:0px; padding:0px;")

        self.title = QtGui.QLabel(" ",self)
        self.artist = QtGui.QLabel(" ",self)
        self.title.setStyleSheet("color: #fff; font-size:20px; font-family:Arial;\
         border:0px; padding:0px; margin:0px")
        self.artist.setStyleSheet("color: #fff; font-size:13px; font-family:Arial;\
            border:0px; padding:0px; margin:0px")
        self.title.setFixedWidth(252)
        self.artist.setFixedWidth(252)
        square = QtGui.QWidget(self)
        square.setStyleSheet("background: #373b3f")
        self.BLayout = QtGui.QHBoxLayout(self)
        self.KLayout = QtGui.QHBoxLayout(self)
        square.setLayout(self.KLayout)
        self.TabLayout = QtGui.QHBoxLayout(self)
        self.labLayout = QtGui.QVBoxLayout(self)
        self.labLayout.addWidget(self.title)
        self.labLayout.addWidget(self.artist)
        self.KLayout.addLayout(self.TabLayout)  
        self.TabLayout.addWidget(self.pic)
        self.TabLayout.addLayout(self.labLayout)
        self.TabLayout.addWidget(self.seekSlider)
        self.TabLayout.addWidget(bar) 
        self.TabLayout.addWidget(volumeLabel)  
        self.TabLayout.addWidget(self.volumeSlider)
        self.BLayout.addWidget(square)
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addLayout(self.TLayout)
        mainLayout.addLayout(self.BLayout)
        mainLayout.insertSpacing(1,-30)

        widget = QtGui.QWidget()#add all widgets to main widget
        widget.setStyleSheet("background: #373b3f")
        widget.setLayout(mainLayout)
        widget.setMaximumHeight(1050)
        widget.resizeEvent = self.onResize
        self.setCentralWidget(widget)
    def stylesheet(self):#style sliders
        return """
            QSlider::groove:horizontal {
                background: #f2f2f2;
                height: 3px;
            }

            QSlider::sub-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
                    stop: 0 #66e, stop: 1 #bbf);
                background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
                    stop: 0 #bbf, stop: 1 #55f);
                height: 40px;
            }

            QSlider::handle:horizontal {
                background: #bbf;
                border: 1px solid #bbf;
                height: 19px;
                width: 19px;
                margin: -2px 0;
                margin-top: 0px;
                margin-bottom: 0px;
                border-radius: 9px;
            }
        """   

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Music Player")
    app.setQuitOnLastWindowClosed(True)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


