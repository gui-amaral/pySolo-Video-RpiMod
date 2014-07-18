import urllib.request as urllib
import urllib.parse as parse
import urllib.error as error
import sys, time, subprocess, math, os
import view, socket, webbrowser
import threading
from PySide import QtCore, QtGui

autoSaveIsRunning = False
rpiList=[]
nameList=[]

class AutoSaveData(QtCore.QThread):
    

    def __init__(self):
        QtCore.QThread.__init__(self)
            
    def run(self):
        interval = 60
        lastSave = time.time()
        #print ("lastSave,{}".format(lastSave))
        while autoSaveIsRunning:
            #print(time.time()-lastSave)
            if time.time() - lastSave > interval:
                i=0
                for pi in rpiList:
                    #check if the sleep is recording data
                    if (self.isRecording(pi)):
                        #get data    
                        url = pi+':8088/downloadData/'+parse.quote(nameList[i])
                        
                        downloadChunks(url,nameList[i])
                        #print(url)
                        #try:
                        req = urllib.Request(url=url)
                        data = urllib.urlopen(req)
                        
                        ##Problema de memoria si el archivo es muy grande!
                        message = data.read()
                        try:
                            savedFile = open(nameList[i],'a')
                        except:
                            savedFile = open(nameList[i],'w')
                        if (message):
                            message = message.decode("utf-8")
                            savedFile.write(message)
                        savedFile.close()
                        #except:
                         #   print("error on saving")
                    i=i+1
                lastSave = time.time()
             
            time.sleep(interval)
        print("Thread ended")

        
    def isRecording(self,pi):
        url = pi+':8088/state'
        try:
            req = urllib.Request(url=url)
            f = urllib.urlopen(req, timeout = 0.1)
            message = f.read()       
            if message == b'True':
                return True
            else:
                return False
        except:
            print("error getting state")
 
    def downloadChunks(url,filename):
            """
            Helper to download large files
            the only arg is a url
            this file will go to a temp directory
            the file will also be downloaded
            in chunks and print out how much remains
            """

            baseFile = os.path.basename(url)

            #move the file to a more uniq path
            #os.umask(0002)
            #temp_path = "/tmp/"
            try:
                #file = os.path.join(temp_path,baseFile)
                file = "./dowloadedData"+filename
                req = urllib.urlopen(url)
                total_size = int(req.info().getheader('Content-Length').strip())
                downloaded = 0
                CHUNK = 256 * 10240
                with open(file, 'wb') as fp:
                    while True:
                        chunk = req.read(CHUNK)
                        downloaded += len(chunk)
                        print (math.floor((downloaded / total_size) * 100 ))
                        if not chunk: break
                        fp.write(chunk)
            except error.HTTPError:
                print ("HTTP Error:", url)
                return False
            except urllib.error.URLError:
                print ("URL Error:", url)
                return False

            return file
 
class ControlMainWindow(QtGui.QMainWindow):
    
    
    autosave = AutoSaveData()
    
    def __init__(self, localIp,parent=None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = view.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.loadButton.clicked.connect(self.piDiscover)
        self.ui.ipEdit.setText(str(localIp[0]))
        self.ui.ipEdit_2.setText(str(localIp[1]))
        self.ui.ipEdit_3.setText(str(localIp[2]))
        self.ui.listWidget.itemEntered.connect(self.openPi)
        self.ui.listWidget.itemDoubleClicked.connect(self.openPi)
        self.ui.downloadcheckBox.setCheckState(QtCore.Qt.Checked)
        self.ui.downloadcheckBox.stateChanged.connect(self.autoDownload)
        self.ui.progressBar.hide()
        self.localIp = localIp
    
    @QtCore.Slot()
    def piDiscover(self):
        global rpiList 
        global nameList 
        localIp = self.localIp
        self.ui.progressBar.show()
        port = 80

        for i in range(1,255):
            url = "http://"+localIp[0]+"."+localIp[1]+"."+localIp[2]+"."+str(i)
            #print(url+port)
            try:
                req = urllib.Request(url=url+':8088/pidiscover')
                f = urllib.urlopen(req,timeout = 0.051)
                message = f.read()
                print(message)
               # password = b'yes'
                if (message):
                    message = message.decode("utf-8")
                    nameList.append(message)
                    rpiList.append(url)
                    print ('[%s]' % ', '.join(map(str, rpiList)))
                    
            except:
                pass
                #print("No this one")
                
            #print percentage complete
            sys.stdout.write( "scaning..."+str(int(i/255*100)) + '%\r'),
            self.ui.progressBar.setValue(int(i/255*100))
        print("Ended  ")
        self.ui.listWidget.addItems(nameList)
        self.rpiList = rpiList
        self.ui.progressBar.hide()
        self.autoDownload()
        
    @QtCore.Slot()
    def openPi(self):
        itemId = str(self.ui.listWidget.currentRow())#indexFromItem(self.ui.listWidget.currentItem))
        print (itemId)
        url = self.rpiList[int(itemId)]+":8088"
        webbrowser.open(url, new=2)

    @QtCore.Slot()
    def autoDownload(self):
        global autoSaveIsRunning
        
        if self.ui.downloadcheckBox.checkState():
            if self.autosave.isRunning():
                #restart
                print("stopping")
                autoSaveIsRunning = False
                #self.autoSave.joint()
                time.sleep(3)
                autoSaveIsRunning = True
                self.autosave.start()
            else:
                try:
                    self.autosave = AutoSaveData()
                    print("newinstance")
                except:
                    print("oldinstance")
                    pass
                autoSaveIsRunning = True
                self.autosave.start()
                print("started")
        else:
            #stop the saving
            autoSaveIsRunning = False
            self.autosave.exit()
                
            

        
def askPiId(device, port):
    req = urllib.Request(url='http://'+device+':'+str(port),method='PIID')
    f = urllib.urlopen(req,timeout = 1)
    piId=f.read()
    return piId
    
    
def main():
    localIp = socket.gethostbyname(str(socket.gethostname())).split('.')
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow(localIp)
    mySW.show()
    sys.exit(app.exec_())

            
   
if __name__ == "__main__":
    main()


