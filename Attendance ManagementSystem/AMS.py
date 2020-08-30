import os
import sys
import cv2
import csv
import time
import smtplib
import mimetypes
import datetime
import numpy as np
import pandas as pd
from email import encoders
from PIL import Image,ImageTk
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.message import EmailMessage
from tkinter.filedialog import askopenfilename
from email.mime.multipart import MIMEMultipart

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    top = mainScreen (root)
    root.mainloop()

w = None
def create_mainScreen(root, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w, w_win, rt
    rt = root
    w = tk.Toplevel (root)
    top = mainScreen (w)
    AMS_support.init(w, top, *args, **kwargs)
    return (w, top)


class mainScreen:
    def __init__(self, top=None):
        self.top = top
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        font9 = "-family {SF Pro Display} -size 14 -weight bold -slant"  \
            " roman -underline 0 -overstrike 0"
        font10 = "-family {SF Pro Display} -size 14 -weight bold "  \
            "-slant roman -underline 0 -overstrike 0"
        font11 = "-family {SF Pro Display} -size 14 -weight bold "  \
            "-slant roman -underline 0 -overstrike 0"
        font12 = "-family {SF Pro Display} -size 12 -weight bold "  \
            "-slant roman -underline 0 -overstrike 0"

        
        def destroy_mainScreen():
            self.top.destroy()

        def deleteID():
            self.studentID.delete(first=0, last=30)

        def deleteName():
            self.studentName.delete(first=0, last=30)

        def testVal(inStr, acttyp):
            if acttyp == '1':
                if not inStr.isdigit():
                    return False
            return True

        def takeImage():
            entryOne = self.studentID.get()
            entryTwo = self.studentName.get()
            if entryOne == "":
                self.Notification.configure(background="#800000")
                self.Notification.configure(foreground="#FFFFFF")
                self.Notification.configure(text="Please enter ID!")
            elif entryTwo == "":
                self.Notification.configure(background="#800000")
                self.Notification.configure(foreground="#FFFFFF")
                self.Notification.configure(text="Please enter Name!")
            else:
                try:
                    cam = cv2.VideoCapture(0)
                    detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
                    ID = self.studentID.get()
                    Name = self.studentName.get()
                    sampleNum = 0
                    while (True):
                        ret, img = cam.read()
                        gray = cv2.cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        faces = detector.detectMultiScale(gray, 1.3, 5)
                        for (x, y, w, h) in faces:
                            cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255), 5)
                            sampleNum += 1
                            cv2.imwrite("TrainingImage/ " + Name + "." + ID + "." + str(sampleNum) + ".png", gray[y:y + h, x:x + w])
                            cv2.imshow("Taking images for student " + self.studentName.get(), img)
                        if 0xFF == ord('Q') & cv2.waitKey(1):
                            break
                        elif sampleNum >= 100:
                            break
                    cam.release()
                    cv2.destroyAllWindows()
                    ts = time.time()
                    ######################Check for errors below######################
                    Date = datetime.datetime.fromtimestamp(ts).strftime("%d/%m/%Y")
                    Time = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                    row = [ID, Name, Date, Time]
                    with open("StudentDetails.csv", "a+") as csvFile:
                        writer = csv.writer(csvFile, delimiter=',')
                        writer.writerow(row)
                        csvFile.close()
                    res = "Images Saved for ID : " + ID + " Name : " + Name
                    self.Notification.configure(text=res, bg="#008000", width=64, font=('SF Pro Display', 16, 'bold'))
                    self.Notification.place(x=92, y=430)
                except FileExistsError as F:
                    f = 'Student Data already exists'
                    self.Notification.configure(text=f, bg="Red", width=64)
                    self.Notification.place(x=92, y=430)

        def trainImage():
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            global detector
            detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
            global faces,Id
            faces, Id = getImagesAndLabels("TrainingImage")
            '''except Exception as e:
                l='please make "TrainingImage" folder & put Images'
                self.Notification.configure(text=l, bg="#008000", width=64, font=('SF Pro Display', 16, 'bold'))
                self.Notification.place(x=92, y=430)'''
            recognizer.train(faces, np.array(Id))
            recognizer.write('TrainingImageLabel/Trainer.yml')
            '''except Exception as e:
                q = 'An error was encountered.'#Please make a folder named "TrainingImageLabel"'
                self.Notification.configure(text=q, bg="#008000", width=64, font=('SF Pro Display', 16, 'bold'))
                self.Notification.place(x=92, y=430)'''
            res = "Student has been trained by the software."
            self.Notification.configure(text=res, bg="#008000", width=64, font=('SF Pro Display', 16, 'bold'))
            self.Notification.place(x=92, y=430)

        def getImagesAndLabels(path):
            imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
            faceSamples = []
            IDS = []
            for imagePath in imagePaths:
                pilImage = Image.open(imagePath).convert('L')
                imageNp = np.array(pilImage, 'uint8')
                Id = int(os.path.split(imagePath)[-1].split(".")[1])
                faces = detector.detectMultiScale(imageNp)
                for (x, y, w, h) in faces:
                    faceSamples.append(imageNp[y:y + h, x:x + w])
                    IDS.append(Id)
            return faceSamples, IDS

        def autoAttendance():
            def fillAttendance():
                SubjectEntry = self.subjectEntry.get()
                now = time.time()
                future = now + 25
                if time.time() < future:
                    if SubjectEntry == "":
                        self.welcomeMessageAuto.configure(background="#800000")
                        self.welcomeMessageAuto.configure(foreground="#FFFFFF")
                        self.welcomeMessageAuto.configure(text="Please enter subject!")
                    else:
                        recognizer = cv2.face.LBPHFaceRecognizer_create()
                        try:
                            recognizer.read("TrainingImageLabel\Trainer.yml")
                        except:
                            self.welcomeMessageAuto.configure(text='Please make a folder names "TrainingImage"')
                        harcascadePath = "haarcascade_frontalface_default.xml"
                        faceCascade = cv2.CascadeClassifier(harcascadePath)
                        df = pd.read_csv("StudentDetails.csv")
                        cam = cv2.VideoCapture(0)
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        colNames = ['ID','Date','Time']
                        attendance = pd.DataFrame(columns = colNames)
                        while True:
                            ret, im = cam.read()
                            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                            faces = faceCascade.detectMultiScale(gray, 1.2, 5)
                            for (x, y, w, h) in faces:
                                global Id
                                Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
                                if conf <= 100:
                                    print (conf)
                                    global Subject
                                    global aa
                                    global date
                                    global timeStamp
                                    Subject = self.subjectEntry.get()
                                    ts = time.time()
                                    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                    aa = df.loc[df['ID'] == Id].values
                                    tt = "ID: " + str(Id)
                                    attendance.loc[len(attendance)] = [Id, date, timeStamp]
                                    cv2.rectangle(im, (x,y), (x + w, y + h), (250, 250, 250), 7)
                                    cv2.putText(im, (tt), (x + h, y), font, 1, (255, 255, 0,), 4)
                                else:
                                    ID = "Unknown"
                                    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 25, 255), 7)
                                    cv2.putText(im, str(ID), (x + h, y), font, 1, (0, 25, 255), 4)
                            if time.time() > future:
                                break
                            attendance = attendance.drop_duplicates(['ID'], keep = 'first')
                            cv2.imshow("Filling attendance ...", im)
                            key = cv2.waitKey(30) &0xFF
                            if key == 27:
                                break
                        ts = time.time()
                        date = datetime.datetime.fromtimestamp(ts).strftime("%d_%m_%Y")
                        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                        Hour, Minute, Second = timeStamp.split(":")
                        fileName = "Attendance/" + self.subjectEntry.get() + "_" + date + "_Time_" + Hour + "_" + Second + ".csv"
                        attendance = attendance.drop_duplicates(['ID'], keep = "first")
                        print (attendance)
                        attendance.to_csv(fileName, index = False)
                       

                        self.welcomeMessageAuto.configure(text="Attendance filled Successfully")
                        cam.release()
                        cv2.destroyAllWindows()
                        root = tk.Tk()
                        root.title("Attendance of " + Subject)
                        root.configure(background="#1B1B1B")
                        root.configure(highlightbackground="#d9d9d9")
                        root.configure(highlightcolor="black")
                       
                        root.focus_force()
                        cs =  fileName
                        with open(cs, newline="") as file:
                            reader = csv.reader(file)
                            r = 0
                            for col in reader:
                                c = 0
                                for row in col:
                                    label = tk.Label(root, width=8, height=1, fg="black", font=('SF Pro Display', 15, ' bold '), bg="#008000", text=row)
                                    label.grid(row=r, column=c)
                                    c += 1
                                r += 1
                        root.mainloop()

           

            subjectScreen = tk.Tk()
           
            subjectScreen.title("Enter Subject for Automatic Attendance")
            subjectScreen.geometry("585x325+316+165")
            subjectScreen.resizable(0,0)
            subjectScreen.configure(background="#1B1B1B")
            subjectScreen.focus_force()

            self.welcomeMessageAuto = tk.Message(subjectScreen)
            self.welcomeMessageAuto.place(relx=0.12, rely=0.591, relheight=0.102, relwidth=0.742)
            self.welcomeMessageAuto.configure(background="black")
            self.welcomeMessageAuto.configure(font=font9)
            self.welcomeMessageAuto.configure(foreground="#FFFFFF")
            self.welcomeMessageAuto.configure(highlightbackground="#d9d9d9")
            self.welcomeMessageAuto.configure(highlightcolor="black")
            self.welcomeMessageAuto.configure(text='')
            self.welcomeMessageAuto.configure(width=434)

            self.enterSubject = tk.Label(subjectScreen)
            self.enterSubject.place(relx=0.12, rely=0.431, height=29, width=132)
            self.enterSubject.configure(activebackground="#f9f9f9")
            self.enterSubject.configure(activeforeground="black")
            self.enterSubject.configure(background="#1B1B1B")
            self.enterSubject.configure(disabledforeground="#a3a3a3")
            self.enterSubject.configure(font="-family {SF Pro Display} -size 14 -weight bold")
            self.enterSubject.configure(foreground="#FFFFFF")
            self.enterSubject.configure(highlightbackground="#d9d9d9")
            self.enterSubject.configure(highlightcolor="black")
            self.enterSubject.configure(text='''Enter Subject:''')

            self.subjectEntry = tk.Entry(subjectScreen)
            self.subjectEntry.place(relx=0.41, rely=0.431, height=27, relwidth=0.451)
            self.subjectEntry.configure(background="#D9D9D9")
            self.subjectEntry.configure(disabledforeground="#a3a3a3")
            self.subjectEntry.configure(font="-family {SF Pro Display} -size 14 -weight bold")
            self.subjectEntry.configure(foreground="#000000")
            self.subjectEntry.configure(highlightbackground="#d9d9d9")
            self.subjectEntry.configure(highlightcolor="black")
            self.subjectEntry.configure(insertbackground="black")
            self.subjectEntry.configure(selectbackground="#c4c4c4")
            self.subjectEntry.configure(selectforeground="black")

            self.fillAttendanceBtnAuto = tk.Button(subjectScreen)
            self.fillAttendanceBtnAuto.place(relx=0.12, rely=0.769, height=38, width=460)
            self.fillAttendanceBtnAuto.configure(activebackground="#ececec")
            self.fillAttendanceBtnAuto.configure(activeforeground="#000000")
            self.fillAttendanceBtnAuto.configure(background="#2E2E2E")
            self.fillAttendanceBtnAuto.configure(disabledforeground="#a3a3a3")
            self.fillAttendanceBtnAuto.configure(font="-family {SF Pro Display} -size 14 -weight bold")
            self.fillAttendanceBtnAuto.configure(foreground="#FFFFFF")
            self.fillAttendanceBtnAuto.configure(highlightbackground="#d9d9d9")
            self.fillAttendanceBtnAuto.configure(highlightcolor="black")
            self.fillAttendanceBtnAuto.configure(pady="0")
            self.fillAttendanceBtnAuto.configure(text='''Fill Attendance''')
            self.fillAttendanceBtnAuto.configure(command=fillAttendance)

            

            self.chooseSubject = tk.Message(subjectScreen)
            self.chooseSubject.place(relx=0.0, rely=0.062, relheight=0.194, relwidth=1.009)
            self.chooseSubject.configure(background="#2E2E2E")
            self.chooseSubject.configure(font="-family {SF Pro Display} -size 36 -weight bold")
            self.chooseSubject.configure(foreground="#FFFFFF")
            self.chooseSubject.configure(highlightbackground="#d9d9d9")
            self.chooseSubject.configure(highlightcolor="black")
            self.chooseSubject.configure(text='''Choose Subject''')
            self.chooseSubject.configure(width=590)

            subjectScreen.mainloop()

        def manualAttendance():
            global subName
            subName = tk.Tk()
        
            subName.title("Enter Subject for Manual Attendance")
            subName.geometry("585x325+316+165")
            subName.configure(background='#1B1B1B')
            subName.resizable(0, 0)
            subName.focus_force()

            def fillAttendanceManual():
                ts = time.time()
                Date = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                Time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                Hour, Minute, Second = timeStamp.split(":")
                dateForDB = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
                global subEntryText
                subEntryText = self.subjectEntry.get()
                dbTableName = str(subEntryText + "_" + Date + "_Time_" + Hour + "_" + Minute + "_" + Second)
                import mysql.connector
                try:
                    global cursor
                    connection = mysql.connector.connect(host='localhost', user='root', password='', database='ams')
                    cursor = connection.cursor()
                except Exception as e:
                    print(e)
                sql = "CREATE TABLE " + dbTableName + """(SrNo INT NOT NULL AUTO_INCREMENT, ID varchar(100) NOT NULL, Name VARCHAR(50) NOT NULL, Date VARCHAR(20) NOT NULL, Time VARCHAR(20) NOT NULL, PRIMARY KEY (SrNo)); """
                try:
                    cursor.execute(sql)
                except Exception as e:
                    print(e)
                    print("Add mysql.connector")
                if subEntryText == "":
                    self.welcomeMessageSubject.configure(background="#800000")
                    self.welcomeMessageSubject.configure(foreground="#FFFFFF")
                    self.welcomeMessageSubject.configure(text="Please enter subject!")
                else:
                    subName.destroy()
                    manualFill = tk.Tk()
                  
                    manualFill.title("Manual Attedance for " + str(subEntryText))
                    manualFill.geometry("880x465+231+125")
                    manualFill.configure(background="#1B1B1B")
                    manualFill.resizable(1, 1)
                    manualFill.focus_force()

                    def testVal(inStr, acttyp):
                        if acttyp == '1':
                            if not inStr.isdigit():
                                return False
                        return True

                    def removeID():
                        self.studentIDManualEntry.delete(first=0, last=20)

                    def removeName():
                        self.studentNameManualEntry.delete(first=0, last=20)

                    def enterDataDB():
                        ID = self.studentIDManualEntry.get()
                        Name = self.studentNameManualEntry.get()
                        if ID == "":
                            self.welcomeMessage.configure(background="#800000")
                            self.welcomeMessage.configure(foreground="#FFFFFF")
                            self.welcomeMessage.configure(text="Please enter ID!")
                        elif Name == "":
                            self.welcomeMessage.configure(background="#800000")
                            self.welcomeMessage.configure(foreground="#FFFFFF")
                            self.welcomeMessage.configure(text="Please enter Name!")
                        else:
                            time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                            Hour, Minute, Second = time.split(":")
                           
                            self.studentIDManualEntry.delete(first=0, last=20)
                            self.studentNameManualEntry.delete(first=0, last=20)
                    def createCSV():
                        
                        cursor.execute("select * from " + dbTableName + ";")
                        csvName= dbTableName + '.csv'
                        with open(csvName, "w") as csvFile:
                            csvWriter = csv.writer(csvFile)
                            csvWriter.writerow([i[0] for i in cursor.description])  # write headers
                            csvWriter.writerows(cursor)
                            self.welcomeMessage.configure(background="#008000")
                            self.welcomeMessage.configure(text="CSV file created successfully")
                        root = tk.Tk()
                      
                        root.title("Attendance of " + subEntryText)
                        root.configure(background='#2B2B2B')
                        root.focus_force()
                        with open(csvName, newline="") as file:
                            reader = csv.reader(file)
                            r = 0
                            for col in reader:
                                c = 0
                                for row in col:
                                    label = tk.Label(root, width=13, height=1, fg="black", font=('SF Pro Display', 14, ' bold '), bg="#008000", text=row)
                                    label.grid(row=r, column=c)
                                    c += 1
                                r += 1
                        root.mainloop()

                    def checkSheetsManual():
                        import subprocess
                        subprocess.Popen(r'explorer /select,"\Attendance Management System\Attendance"')

                    self.studentIDManual = tk.Label(manualFill)
                    self.studentIDManual.place(relx=0.068, rely=0.344, height=40, width=250)
                    self.studentIDManual.configure(background="#1B1B1B")
                    self.studentIDManual.configure(disabledforeground="#a3a3a3")
                    self.studentIDManual.configure(font=font10)
                    self.studentIDManual.configure(foreground="#FFFFFF")
                    self.studentIDManual.configure(text='''Student ID:''')

                    self.studentNameManual = tk.Label(manualFill)
                    self.studentNameManual.place(relx=0.068, rely=0.516, height=35, width=300)
                    self.studentNameManual.configure(background="#1B1B1B")
                    self.studentNameManual.configure(disabledforeground="#a3a3a3")
                    self.studentNameManual.configure(font=font10)
                    self.studentNameManual.configure(foreground="#FFFFFF")
                    self.studentNameManual.configure(text=''' Student Name:''')

                    self.mainMessage = tk.Message(manualFill)
                    self.mainMessage.place(relx=0.0, rely=0.043, relheight=0.135, relwidth=1.0)
                    self.mainMessage.configure(background="#2E2E2E")
                    self.mainMessage.configure(font="-family {SF Pro Display} -size 36 -weight bold")
                    self.mainMessage.configure(foreground="#FFFFFF")
                    self.mainMessage.configure(highlightbackground="#d9d9d9")
                    self.mainMessage.configure(highlightcolor="black")
                    self.mainMessage.configure(text='''Manual Attendance''')
                    self.mainMessage.configure(width=880)

                    self.studentIDManualEntry = tk.Entry(manualFill)
                    self.studentIDManualEntry.place(relx=0.42, rely=0.344, height=33, relwidth=0.368)
                    self.studentIDManualEntry.configure(background="white")
                    self.studentIDManualEntry.configure(disabledforeground="#a3a3a3")
                    self.studentIDManualEntry.configure(font=font10)
                    self.studentIDManualEntry.configure(foreground="#000000")
                    self.studentIDManualEntry.configure(insertbackground="black")
                    self.studentIDManualEntry.configure(validate='key')
                    self.studentIDManualEntry['validatecommand'] = (self.studentIDManualEntry.register(testVal), '%P', '%d')

                    self.studentNameManualEntry = tk.Entry(manualFill)
                    self.studentNameManualEntry.place(relx=0.42, rely=0.516, height=33, relwidth=0.368)
                    self.studentNameManualEntry.configure(background="white")
                    self.studentNameManualEntry.configure(disabledforeground="#a3a3a3")
                    self.studentNameManualEntry.configure(font=font10)
                    self.studentNameManualEntry.configure(foreground="#000000")
                    self.studentNameManualEntry.configure(insertbackground="black")

                    self.clearIDManual = tk.Button(manualFill)
                    self.clearIDManual.place(relx=0.864, rely=0.344, height=38, width=66)
                    self.clearIDManual.configure(activebackground="#ececec")
                    self.clearIDManual.configure(activeforeground="#000000")
                    self.clearIDManual.configure(background="#2E2E2E")
                    self.clearIDManual.configure(disabledforeground="#a3a3a3")
                    self.clearIDManual.configure(font=font9)
                    self.clearIDManual.configure(foreground="#FFFFFF")
                    self.clearIDManual.configure(highlightbackground="#d9d9d9")
                    self.clearIDManual.configure(highlightcolor="black")
                    self.clearIDManual.configure(pady="0")
                    self.clearIDManual.configure(text='''Clear''')
                    self.clearIDManual.configure(command=removeID)

                    self.clearNameManual = tk.Button(manualFill)
                    self.clearNameManual.place(relx=0.864, rely=0.516, height=38, width=66)
                    self.clearNameManual.configure(activebackground="#ececec")
                    self.clearNameManual.configure(activeforeground="#000000")
                    self.clearNameManual.configure(background="#2E2E2E")
                    self.clearNameManual.configure(disabledforeground="#a3a3a3")
                    self.clearNameManual.configure(font=font9)
                    self.clearNameManual.configure(foreground="#FFFFFF")
                    self.clearNameManual.configure(highlightbackground="#d9d9d9")
                    self.clearNameManual.configure(highlightcolor="black")
                    self.clearNameManual.configure(pady="0")
                    self.clearNameManual.configure(text='''Clear''')
                    self.clearNameManual.configure(command=removeName)

                    self.enterData = tk.Button(manualFill)
                    self.enterData.place(relx=0.068, rely=0.817, height=38, width=110)
                    self.enterData.configure(activebackground="#ececec")
                    self.enterData.configure(activeforeground="#000000")
                    self.enterData.configure(background="#2E2E2E")
                    self.enterData.configure(disabledforeground="#a3a3a3")
                    self.enterData.configure(font=font9)
                    self.enterData.configure(foreground="#FFFFFF")
                    self.enterData.configure(highlightbackground="#d9d9d9")
                    self.enterData.configure(highlightcolor="black")
                    self.enterData.configure(pady="0")
                    self.enterData.configure(text='''Enter data''')
                    self.enterData.configure(command=enterDataDB)

                    self.convertToCSV = tk.Button(manualFill)
                    self.convertToCSV.place(relx=0.761, rely=0.817, height=38, width=154)
                    self.convertToCSV.configure(activebackground="#ececec")
                    self.convertToCSV.configure(activeforeground="#000000")
                    self.convertToCSV.configure(background="#2E2E2E")
                    self.convertToCSV.configure(disabledforeground="#a3a3a3")
                    self.convertToCSV.configure(font=font9)
                    self.convertToCSV.configure(foreground="#FFFFFF")
                    self.convertToCSV.configure(highlightbackground="#d9d9d9")
                    self.convertToCSV.configure(highlightcolor="black")
                    self.convertToCSV.configure(pady="0")
                    self.convertToCSV.configure(text='''Convert to CSV''')
                    self.convertToCSV.configure(command=createCSV)

                    self.welcomeMessage = tk.Message(manualFill)
                    self.welcomeMessage.place(relx=0.068, rely=0.667, relheight=0.092, relwidth=0.866)
                    self.welcomeMessage.configure(background="black")
                    self.welcomeMessage.configure(font="-family {SF Pro Display} -size 18 -weight bold")
                    self.welcomeMessage.configure(foreground="#FFFFFF")
                    self.welcomeMessage.configure(highlightbackground="#d9d9d9")
                    self.welcomeMessage.configure(highlightcolor="black")
                    self.welcomeMessage.configure(text='')
                    self.welcomeMessage.configure(width=760)

                    manualFill.mainloop()

            self.enterSubject = tk.Label(subName)
            self.enterSubject.place(relx=0.12, rely=0.431, height=29, width=132)
            self.enterSubject.configure(background="#1B1B1B")
            self.enterSubject.configure(disabledforeground="#a3a3a3")
            self.enterSubject.configure(font=font9)
            self.enterSubject.configure(foreground="#FFFFFF")
            self.enterSubject.configure(text='''Enter Subject:''')

            self.subjectEntry = tk.Entry(subName)
            self.subjectEntry.place(relx=0.41, rely=0.431, height=27, relwidth=0.451)
            self.subjectEntry.configure(background="#D9D9D9")
            self.subjectEntry.configure(disabledforeground="#a3a3a3")
            self.subjectEntry.configure(font=font9)
            self.subjectEntry.configure(foreground="#000000")
            self.subjectEntry.configure(insertbackground="black")

            self.fillAttendanceBtn = tk.Button(subName)
            self.fillAttendanceBtn.place(relx=0.598, rely=0.769, height=38, width=154)
            self.fillAttendanceBtn.configure(activebackground="#ececec")
            self.fillAttendanceBtn.configure(activeforeground="#000000")
            self.fillAttendanceBtn.configure(background="#2E2E2E")
            self.fillAttendanceBtn.configure(disabledforeground="#a3a3a3")
            self.fillAttendanceBtn.configure(font=font9)
            self.fillAttendanceBtn.configure(foreground="#FFFFFF")
            self.fillAttendanceBtn.configure(highlightbackground="#d9d9d9")
            self.fillAttendanceBtn.configure(highlightcolor="black")
            self.fillAttendanceBtn.configure(pady="0")
            self.fillAttendanceBtn.configure(text='''Fill Attendance''')
            self.fillAttendanceBtn.configure(command=fillAttendanceManual)

            self.chooseSubject = tk.Message(subName)
            self.chooseSubject.place(relx=0.0, rely=0.062, relheight=0.217, relwidth=1.009)
            self.chooseSubject.configure(background="#2E2E2E")
            self.chooseSubject.configure(font="-family {SF Pro Display} -size 36 -weight bold")
            self.chooseSubject.configure(foreground="#FFFFFF")
            self.chooseSubject.configure(highlightbackground="#d9d9d9")
            self.chooseSubject.configure(highlightcolor="black")
            self.chooseSubject.configure(text='''Choose Subject''')
            self.chooseSubject.configure(width=585)

            self.welcomeMessageSubject = tk.Message(subName)
            self.welcomeMessageSubject.place(relx=0.12, rely=0.591, relheight=0.102, relwidth=0.742)
            self.welcomeMessageSubject.configure(background="#008000")
            self.welcomeMessageSubject.configure(font="-family {SF Pro Display} -size 14 -weight bold")
            self.welcomeMessageSubject.configure(foreground="#FFFFFF")
            self.welcomeMessageSubject.configure(highlightbackground="#d9d9d9")
            self.welcomeMessageSubject.configure(highlightcolor="black")
            self.welcomeMessageSubject.configure(text='')
            self.welcomeMessageSubject.configure(width=434)

            subName.mainloop()

        
        top.geometry("1367x696+-9+0")
        top.minsize(120, 1)
        top.maxsize(1370, 749)
        top.resizable(0, 0)
    
        top.focus_force()
        top.title("Attendance Managment System  ")
        top.configure(background="#1B1B1B")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")

        self.Title = tk.Message(top)
        self.Title.place(relx=-0.007, rely=0.042, relheight=0.134, relwidth=1.005)
        self.Title.configure(background="#2E2E2E")
        self.Title.configure(font="-family {SF Pro Display} -size 30 -weight bold")
        self.Title.configure(foreground="#FFFFFF")
        self.Title.configure(highlightbackground="#D9D9D9")
        self.Title.configure(highlightcolor="black")
        self.Title.configure(text='''Face Recognition Attendance Management System''')
        self.Title.configure(width=1374)

        self.studentID = tk.Entry(top)
        self.studentID.place(relx=0.338, rely=0.345,height=33, relwidth=0.237)
        self.studentID.configure(background="#D9D9D9")
        self.studentID.configure(disabledforeground="#a3a3a3")
        self.studentID.configure(font="-family {SF Pro Display} -size 18 -weight bold")
        self.studentID.configure(foreground="#000000")
        self.studentID.configure(highlightbackground="#d9d9d9")
        self.studentID.configure(highlightcolor="black")
        self.studentID.configure(insertbackground="black")
        self.studentID.configure(relief="flat")
        self.studentID.configure(selectbackground="#007878d7d777")
        self.studentID.configure(selectforeground="black")
        self.studentID.configure(validate='key')
        self.studentID['validatecommand'] = (self.studentID.register(testVal), '%P', '%d')

        self.labelStudentID = tk.Label(top)
        self.labelStudentID.place(relx=0.067, rely=0.348, height=31, width=250)
        self.labelStudentID.configure(activebackground="#f9f9f9")
        self.labelStudentID.configure(activeforeground="black")
        self.labelStudentID.configure(background="#1B1B1B")
        self.labelStudentID.configure(disabledforeground="#a3a3a3")
        self.labelStudentID.configure(font="-family {SF Pro Display} -size 18 -weight bold")
        self.labelStudentID.configure(foreground="#FFFFFF")
        self.labelStudentID.configure(highlightbackground="#d9d9d9")
        self.labelStudentID.configure(highlightcolor="black")
        self.labelStudentID.configure(text='''Enter Student ID:''')

        self.labelStudentName = tk.Label(top)
        self.labelStudentName.place(relx=0.067, rely=0.454, height=35, width=300)
        self.labelStudentName.configure(activebackground="#f9f9f9")
        self.labelStudentName.configure(activeforeground="black")
        self.labelStudentName.configure(background="#1B1B1B")
        self.labelStudentName.configure(disabledforeground="#a3a3a3")
        self.labelStudentName.configure(font="-family {SF Pro Display} -size 18 -weight bold")
        self.labelStudentName.configure(foreground="#FFFFFF")
        self.labelStudentName.configure(highlightbackground="#d9d9d9")
        self.labelStudentName.configure(highlightcolor="black")
        self.labelStudentName.configure(text='''Enter Student Name:''')

        self.studentName = tk.Entry(top)
        self.studentName.place(relx=0.338, rely=0.46,height=33, relwidth=0.237)
        self.studentName.configure(background="#D9D9D9")
        self.studentName.configure(disabledforeground="#a3a3a3")
        self.studentName.configure(font="-family {SF Pro Display} -size 18 -weight bold")
        self.studentName.configure(foreground="#000000")
        self.studentName.configure(highlightbackground="#d9d9d9")
        self.studentName.configure(highlightcolor="black")
        self.studentName.configure(insertbackground="black")
        self.studentName.configure(selectbackground="#c4c4c4")
        self.studentName.configure(selectforeground="black")

        self.clearID = tk.Button(top)
        self.clearID.place(relx=0.636, rely=0.345, height=38, width=66)
        self.clearID.configure(activebackground="#ececec")
        self.clearID.configure(activeforeground="#000000")
        self.clearID.configure(background="#2E2E2E")
        self.clearID.configure(disabledforeground="#a3a3a3")
        self.clearID.configure(font="-family {SF Pro Display} -size 14 -weight bold")
        self.clearID.configure(foreground="#FFFFFF")
        self.clearID.configure(highlightbackground="#d9d9d9")
        self.clearID.configure(highlightcolor="black")
        self.clearID.configure(pady="0")
        self.clearID.configure(text='''Clear''')
        self.clearID.configure(command=deleteID)

        self.clearName = tk.Button(top)
        self.clearName.place(relx=0.636, rely=0.46, height=38, width=66)
        self.clearName.configure(activebackground="#ececec")
        self.clearName.configure(activeforeground="#000000")
        self.clearName.configure(background="#2E2E2E")
        self.clearName.configure(disabledforeground="#a3a3a3")
        self.clearName.configure(font="-family {SF Pro Display} -size 14 -weight bold")
        self.clearName.configure(foreground="#FFFFFF")
        self.clearName.configure(highlightbackground="#d9d9d9")
        self.clearName.configure(highlightcolor="black")
        self.clearName.configure(pady="0")
        self.clearName.configure(text='''Clear''')
        self.clearName.configure(command=deleteName)

        self.Notification = tk.Label(top)
        self.Notification.configure(text="")
        self.Notification.configure(background="black")
        self.Notification.configure(foreground="#FFFFFF")
        self.Notification.configure(width=64, height=2)
        self.Notification.configure(font="-family {SF Pro Display} -size 16 -weight bold")
        self.Notification.place(x=92, y=430)

        self.takeImages = tk.Button(top)
        self.takeImages.place(relx=0.067, rely=0.818, height=38, width=150)
        self.takeImages.configure(activebackground="#ececec")
        self.takeImages.configure(activeforeground="#000000")
        self.takeImages.configure(background="#2E2E2E")
        self.takeImages.configure(disabledforeground="#a3a3a3")
        self.takeImages.configure(font=font10)
        self.takeImages.configure(foreground="#FFFFFF")
        self.takeImages.configure(highlightbackground="#d9d9d9")
        self.takeImages.configure(highlightcolor="black")
        self.takeImages.configure(pady="0")
        self.takeImages.configure(text='''Take Images''')
        self.takeImages.configure(command=takeImage)

        self.quitS = tk.Button(top)
        self.quitS.place(relx=0.800, rely=0.818, height=38, width=133)
        self.quitS.configure(activebackground="#ececec")
        self.quitS.configure(activeforeground="#000000")
        self.quitS.configure(background="#2E2E2E")
        self.quitS.configure(disabledforeground="#a3a3a3")
        self.quitS.configure(font=font10)
        self.quitS.configure(foreground="#FFFFFF")
        self.quitS.configure(highlightbackground="#d9d9d9")
        self.quitS.configure(highlightcolor="black")
        self.quitS.configure(pady="0")
        self.quitS.configure(text='''Quit''')
        self.quitS.configure(command=destroy_mainScreen)
        


        self.trainStudent = tk.Button(top)
        self.trainStudent.place(relx=0.205, rely=0.818, height=38, width=175)
        self.trainStudent.configure(activebackground="#ececec")
        self.trainStudent.configure(activeforeground="#000000")
        self.trainStudent.configure(background="#2E2E2E")
        self.trainStudent.configure(disabledforeground="#a3a3a3")
        self.trainStudent.configure(font=font11)
        self.trainStudent.configure(foreground="#FFFFFF")
        self.trainStudent.configure(highlightbackground="#d9d9d9")
        self.trainStudent.configure(highlightcolor="black")
        self.trainStudent.configure(pady="0")
        self.trainStudent.configure(text='''Train Student''')
        self.trainStudent.configure(command=trainImage)

        self.automaticAttendance = tk.Button(top)
        self.automaticAttendance.place(relx=0.344, rely=0.818, height=38, width=250)
        self.automaticAttendance.configure(activebackground="#ececec")
        self.automaticAttendance.configure(activeforeground="#000000")
        self.automaticAttendance.configure(background="#2E2E2E")
        self.automaticAttendance.configure(disabledforeground="#a3a3a3")
        self.automaticAttendance.configure(font=font11)
        self.automaticAttendance.configure(foreground="#FFFFFF")
        self.automaticAttendance.configure(highlightbackground="#d9d9d9")
        self.automaticAttendance.configure(highlightcolor="black")
        self.automaticAttendance.configure(pady="0")
        self.automaticAttendance.configure(text='''Attendance''')
        self.automaticAttendance.configure(command=autoAttendance)

        self.manualAttendance = tk.Button(top)
        self.manualAttendance.place(relx=0.541, rely=0.818, height=38, width=300)
        self.manualAttendance.configure(activebackground="#ececec")
        self.manualAttendance.configure(activeforeground="#000000")
        self.manualAttendance.configure(background="#2E2E2E")
        self.manualAttendance.configure(disabledforeground="#a3a3a3")
        self.manualAttendance.configure(font=font11)
        self.manualAttendance.configure(foreground="#FFFFFF")
        self.manualAttendance.configure(highlightbackground="#d9d9d9")
        self.manualAttendance.configure(highlightcolor="black")
        self.manualAttendance.configure(pady="0")
        self.manualAttendance.configure(text='''Manual Attendance''')
        self.manualAttendance.configure(command=manualAttendance)

       
        

if __name__ == '__main__':
    vp_start_gui()
