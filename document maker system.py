import requests
import cv2
import numpy as np
import time
from PIL import Image
import PIL.Image
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import tkinter as tk
import mysql.connector
import numpy as np
from tkinter import StringVar
from tkinter import *
from datetime import datetime

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="time table"
)
mycursor = mydb.cursor()

name= ""
file_name="out.pdf"
password=""
list=[]
list2=[]
days= ["monday","tuesday","wednesday","thrusday","friday"]


def update_1():
    del1="DELETE FROM `time table` WHERE 1"
    mycursor.execute(del1)
    mydb.commit()
    print(list)
    for i in range(1,9):
         
         del1="INSERT INTO `time table`(`name`, `slot`) VALUES('" + name + "'," + str(i) + ")"
         
         mycursor.execute(del1)
         
         print(del1+ " " )
    
    for i in range(1,9):
        for j in range(2,7):
            temp=(list[i-1][j-2].get()) 
            if temp.strip():
                print(str(i)+ " " + str(j) + " " + temp)
                string1= "UPDATE `time table` SET `" + days[j-2] +"`='" + temp + "'where name='" + name + "' and slot=" + str(i)
                
                print(string1)
                mycursor.execute(string1)
    
                # myresult = mycursor.fetchone()
                
    mydb.commit()
    
    
    

def show_entry_fields():
    print("IP address: %s\n Name: %s" % (e1.get(), e2.get()))
    url  = "http://" +  e1.get() + ":8080/shot.jpg"
    make(url,e2.get())
    mail(name,password,e2.get())
    


def timetable(): 
      
    master1 = tk.Tk()
    master1.iconbitmap("logo.ico") 
    master1.title("set time table")
    master1.geometry('900x300')
    tk.Label(master1, text="Faculty Name",font=('bold',14)).grid(row=0,column=0)
    tk.Label(master1, text="Slot",font=('bold',14)).grid(row=0,column=1)
    tk.Label(master1, text="Monday",font=('bold',14)).grid(row=0,column=2)
    tk.Label(master1, text="tuesday",font=('bold',14)).grid(row=0,column=3)
    tk.Label(master1, text="Wednesday",font=('bold',14)).grid(row=0,column=4)
    tk.Label(master1, text="Thursday",font=('bold',14)).grid(row=0,column=5)
    tk.Label(master1, text="friday",font=('bold',14)).grid(row=0,column=6)
    
    
    
    tk.Label(master1, text="9-10",font=('bold',14)).grid(row=1,column=1)
    tk.Label(master1, text="10-11",font=('bold',14)).grid(row=2,column=1)
    tk.Label(master1, text="11-12",font=('bold',14)).grid(row=3,column=1)
    tk.Label(master1, text="12-1",font=('bold',14)).grid(row=4,column=1)
    tk.Label(master1, text="2-3",font=('bold',14)).grid(row=5,column=1)
    tk.Label(master1, text="3-4",font=('bold',14)).grid(row=6,column=1)
    tk.Label(master1, text="4-5",font=('bold',14)).grid(row=7,column=1)
    tk.Label(master1, text="5-6",font=('bold',14)).grid(row=8,column=1)
    list.clear()
    list2.clear()
    for i in range(1,9):
        list3=[]
        for j in range(2,7):
            v=StringVar();
            list3.append(v)
        list2.append(list3)
            
    for i in range(1,9):
        list1=[]
        for j in range(2,7):
            e1= tk.Entry(master1, textvariable=list2[i-1][j-2])
            e1.grid(row=i,column=j)
            list1.append(e1);
            string1= "Select `" + days[j-2]+ "` from `time table` where slot=" + str(i) + " AND name= '" + name + "'" 
            # print(string1)
            mycursor.execute(string1)
        
            myresult = mycursor.fetchone()
            # print(type(myresult))
            if myresult is not None:
                if(myresult[0] is not None):
                    print(myresult[0])
                    print( str(i)+ " " + str(j))
                    e1.delete(0,0)
                    e1.insert(0,str(myresult[0]))
        list.append(list1)
                    
        
            
    e1= tk.Entry(master1)
    e1.grid(row=1,column=0)
    e1.insert(END, name)
    
    tk.Button(master1, text='update', command=update_1).grid(row=10, column=10,sticky=tk.W,pady=4)
    tk.Button(master1, text="Quit", command=master1.destroy).grid(row=10,column=11)
    
def make(url,batch_name):
    
    i=1
    print(url)
    while True:
    
        img=  requests.get(url)
        img_arr= np.array(bytearray(img.content),dtype=np.uint8)
        img_cv = cv2.imdecode(img_arr,-1)
    
        cv2.imshow("het",img_cv)
    
        name= str(i) + '.jpg' 
    
        key = cv2.waitKey(1)    
        if  key == 32 :
            cv2.imwrite(name,img_cv)
            i=i+1
    
        if key == 27 :
            break
        
        print(key)
        time.sleep(1)
    cv2.destroyAllWindows()
    
    images = []
    
    for  j in range(1,i) :
        fname = str(j)+ '.jpg'
        im= PIL.Image.open(fname)
    
        if im.mode == "RGBA" :
            im.im.convert("RGB")
        
        images.append(im)
        
    from datetime import date
    global file_name
    today = date.today()
    out_fname=  batch_name + " "+ str(today) + ".pdf"
    file_name=batch_name + " "+ str(today) + ".pdf"
    images[0].save(out_fname, save_all = True, quality=100, append_images = images[1:])
    
    
def mail(sender, pass1, classname):
    send = sender + "@nirmauni.ac.in"
    password = pass1
    receiver = classname+ "@nirmauni.ac.in"
    
    msg = 'PFA'
    message = MIMEMultipart()
    message['From'] = send
    message['To'] = receiver
    message['Subject'] = 'Class notes '
    message.attach(MIMEText(msg, 'plain'))
    
    path= '/Desktop/mp-3'
    print(file_name)
    f=open(file_name,"rb") #het sir add the path of the file / pdf
    
    pay = MIMEBase('application', 'octet-stream')
    pay.set_payload(f.read())
    encoders.encode_base64(pay)
    pay.add_header('Content-Disposition', "attachment; filename= %s" %file_name)
    message.attach(pay)
    f.close()
    
    session = smtplib.SMTP('smtp.gmail.com', 587) 
    session.starttls() 
    session.login(send, password)
    text = message.as_string()
    session.sendmail(send, receiver, text)
    session.quit()
def change(name1, password1):
    
    global name 
    global password
    del1="DELETE FROM `user details` WHERE 1"
    mycursor.execute(del1)
    mydb.commit()
    
    del1="INSERT INTO `user details`(`name`, `password`) VALUES ('"+ name1 +"','"+ password1 + "')"
    print(del1)
    mycursor.execute(del1)
    mydb.commit() 
    
    
    del1 =" UPDATE `time table` set name='"+name1 +"'";
    mycursor.execute(del1)
    mydb.commit() 
    

    
def change_details():
    newWindow = tk.Toplevel(master)
    newWindow.iconbitmap("logo.ico")
    E1 = tk.Entry(newWindow)
    E2 = tk.Entry(newWindow)
    tk.Label(newWindow, text="Enter email id",font=('bold',14)).grid(row=1, column=1,padx=0,sticky=W+E+N+S)
    tk.Label(newWindow, text="Enter password",font=('bold',14)).grid(row=2, column=1,padx=0,sticky=W+E+N+S)
    E1.grid(row=1, column=2)
    E2.grid(row=2, column=2)
    tk.Button(newWindow, text='Quit', command=newWindow.destroy).grid(row=5, column=2,pady=4,padx=5)
    tk.Button(newWindow, text='save', command=lambda: change(E1.get(),E2.get())).grid(row=5, column=3,pady=4,padx=5)
    


master = tk.Tk()
master.title("Document Creater")
master.geometry('650x100')
tk.Label(master, text="Enter IP address",font=('bold',14),background='grey',foreground='white').grid(row=3, column=2,padx=0,sticky=W+E+N+S)
tk.Label(master, text="Enter Batch name",font=('bold',14),background='grey',foreground='white').grid(row=6, column=2,padx=0,sticky=W+E+N+S)
master.configure(background="grey")
master.focus_force()
master.iconbitmap("logo.ico")
e1 = tk.Entry(master)
e2 = tk.Entry(master)

e1.grid(row=3, column=3)
e2.grid(row=6, column=3)

tk.Button(master, text='change login details', command=change_details).grid(row=8, column=7,pady=4,padx=5)
tk.Button(master, text='Quit', command=master.destroy).grid(row=8, column=4,pady=4,padx=5)
tk.Button(master, text='Show', command=show_entry_fields).grid(row=8, column=5,pady=4,padx=5)
tk.Button(master, text = 'change timetable', command=timetable).grid(row=8,column=6,pady=4,padx=5)

del1="SELECT * FROM `user details` "
mycursor.execute(del1)
temp= mycursor.fetchall()
name=  temp[0][0]
password=temp[0][1]

import datetime
now = datetime.datetime.now()
day = (now.strftime("%A"))
time1 = now.strftime("%H:%M:%S")
hour =(time1[:2])
minute =(time1[3:5])

welcome=  "welcome " + name + " " 
message1 = tk.Label(master, text=welcome,font=('bold',14)).grid(row=8, column=2,padx=0,sticky=W+E+N+S)
slot=-1;
hour = int(hour,10)
print(hour)
if(hour==9):
    slot=1
elif(hour==10):
    slot=2
elif(hour==11):
    slot=3 
elif(hour==12):
    slot=4
elif(hour==14):
    slot=5
elif(hour==15):
    slot=6
elif(hour==16):
    slot=7
elif(hour==14):
    slot=8
print(slot)
if( slot!=-1):
    del1="select `" + day+ "` from `time table` where slot=" +(str)(slot); 
    print(del1)
    mycursor.execute(del1)
    temp= mycursor.fetchall()
    print(temp)
    if len(temp)==1:
        e2.insert(END, temp[0])
print((str)(hour)+ " " + minute)
print(day.lower() )
tk.mainloop()

