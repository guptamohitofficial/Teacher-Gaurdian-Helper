from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from .__init__ import cursor, conn, sendMail
from creator.models import allot_tg, semister
import pandas as pd
from random import randint
from passlib.hash import pbkdf2_sha256

# Create your views here.

def home(request):
    if request.method == 'POST':
        
        global result
        global output_l
        global notice
        global regis_result
        result = ""
        output_l = ""
        notice = ""
        regis_result = ""

        uname2db = request.POST['enroll']
        pass2db = request.POST['passwd']

        if uname2db == "" or pass2db == "":
            return render(request,'index.html',{'err':'Empty Feilds'})
        else:   
            if uname2db[0:4] == "0114":
                uname2db = uname2db.upper()
            out = allot_tg.objects.all()
            class_name = ""
            for i in out:
                query = "select * from " + i.have_class + " where enrollment='" + str(uname2db) + "';"
                cursor.execute(query)
                output_l = cursor.fetchall()
                if output_l:
                    class_name = i.have_class
                    break
            try:
                result = output_l[0]
                print(result[6])
                print(pass2db)
                if pbkdf2_sha256.verify(pass2db,result[6]):
                    query = "select notic from noti where class='"+class_name+"';"
                    cursor.execute(query)
                    notice = cursor.fetchall() 
                    return render(request,'student_home.html',{'result':result,'class_name':class_name,'noti':notice})
                else:
                    return render(request,'index.html',{'err':'Pssword not matched'}) 
            except:
                output_l = allot_tg.objects.filter(tg_name__exact=uname2db)
                try:
                    result = output_l[0]
                    if pbkdf2_sha256.verify(pass2db,result.password):
                        regis_result = None
                        regis_request = "select * from register_temp where class='" + result.have_class + "';"
                        cursor.execute(regis_request)
                        regis_result = cursor.fetchall()
                        return render(request,'tg_home.html',{'work_':'home','result':result,'registrations':regis_result})
                    else:
                        return render(request,'index.html',{'err':'Pssword not matched'})  
                except IndexError:
                    return render(request,'index.html',{'err':'user not found'})     
    else:
        return render(request,'index.html')


def signup(request):
    global output
    output = ""
    if request.method == 'POST':
        try:
            output = allot_tg.objects.all()
            enroll2db = request.POST['enroll']
            enroll2db = enroll2db.upper()
            fname2db = request.POST['fname']
            fname2db = fname2db.title()
            lname2db = request.POST['lname']
            lname2db = lname2db.title()
            email2db = request.POST['email']
            phone2db = request.POST['phone']
            class2db = request.POST['to_class']
            gender2db = request.POST['gender']
            passwd2db = request.POST['pass']
            passwd_cnf = request.POST['pass_cnf']
        except:
            output = allot_tg.objects.all()
            messages.info(request,"Something Wrong Happend in INPUTS")
            return render(request,'signup.html',{'clas':output})

        if passwd2db == passwd_cnf:
            pass_hash = pbkdf2_sha256.encrypt(passwd2db,rounds=12000,salt_size=32)
            otp_reg = randint(1000,9999)
            print(otp_reg)
            query = "insert into register_temp(enrollment,first_name,last_name,email,phone,class,gender,password) values('" + enroll2db + "','" + fname2db + "','" + lname2db + "','" + email2db + "','" + phone2db + "','" + class2db + "','" + gender2db + "','" + pass_hash + "');"
            try:
                cursor.execute(query)
                print(query)
                conn.commit()
            except:
                messages.info(request,"User exists")
                return render(request,'signup.html',{'clas':output})
            print("Done !!! Data Saved  !!!")
            messages.info(request,enroll2db+" Registered")
            return render(request,'signup.html',{'clas':output})
        else:
            messages.info(request,"Both passwords does not match")
            return render(request,'signup.html',{'clas':output})
    else:
        output = allot_tg.objects.all()
        return render(request,'signup.html',{'clas':output})
        

def add_sem(request):
    try:
        if request.method == 'POST':
            try:
                sem = request.POST['semister']
                class_name = request.POST['class_name']
                subjects = request.POST['subjects']
            except KeyError:
                messages.info(request,"Inputs Error")
                return render(request,'tg_home.html',{'work_':'add_sem','result':result})                
            if semister.objects.filter(sem=sem).filter(class_name=class_name):
                messages.info(request,"Semister Exists")
                return render(request,'tg_home.html',{'work_':'home','result':result})
            else:
                create_sem = semister(sem = sem,class_name = class_name, subjects = subjects)
                create_sem.save()
                subs = []
                sub = ""
                n = len(subjects)
                for i in range(0,n):
                    if subjects[i] != ',':
                        sub = sub+subjects[i]
                    else:
                        subs.append(sub)
                        sub = ""
                    if i==n-1:
                        subs.append(sub)                        
                query = "create table " + class_name + "_sem" + sem + "(enrollment varchar(12) PRIMARY KEY, " 
                n = len(subs)
                for i in range(0,n):
                    query += subs[i]+" integer"
                    if i != n-1:
                        query += ", "
                query += ");"
                cursor.execute(query)
                conn.commit()
                messages.info(request,"Semister "+sem+" for "+class_name+" is Created")
                return render(request,'tg_home.html',{'work_':'home','result':result})            
        else:
            print(result)
            sem_left = [1,2,3,4,5,6,7,8]
            sem_exist = semister.objects.filter(class_name=result.have_class)
            for i in sem_exist:
                sem_left.remove(i.sem)
            return render(request,'tg_home.html',{'work_':'add_sem','result':result,'sem_exist':sem_left})
    except NameError:
        return render(request,'index.html',{'err':'Please Login First'})


def del_sem(request):
    try:
        if request.method == 'POST':
            try:
                sem = request.POST['semister']
                class_name = request.POST['class_name']  
            except KeyError:
                messages.info(request,"Inputs Error")
                return render(request,'tg_home.html',{'work_':'del_sem','result':result})
            if not semister.objects.filter(sem=sem).filter(class_name=class_name):
                messages.info(request,"Semister Exists")
                return render(request,'tg_home.html',{'work_':'home','result':result})
            else:    
                query = "delete from creator_semister where sem=" + sem + " and class_name='" + class_name + "';"
                print(query)
                cursor.execute(query)
                conn.commit()        
                query = "drop table " + class_name + "_sem" + sem + ";" 
                cursor.execute(query)
                conn.commit()  
                messages.info(request,"Semister "+sem+" for "+class_name+" is Deleted")
                return render(request,'tg_home.html',{'work_':'home','result':result})            
        else:
            print(result)
            sem_have = []
            sem_exist = semister.objects.filter(class_name=result.have_class)
            for i in sem_exist:
                sem_have.append(i.sem)
            return render(request,'tg_home.html',{'work_':'del_sem','result':result,'sem_exist':sem_have})
    except NameError:
        return render(request,'index.html',{'err':'Please Login First'})


def add_stu(request):
    try:
        if request.method == 'POST':
            xl_file = request.FILES['file_stu']
            data_frame = pd.read_excel(xl_file,sheet_name="Sheet1")
            query = "INSERT INTO "+ result.have_class +"(enrollment,first_name,last_name,email,phone,gender,password) VALUES(%s,%s,%s,%s,%s,%s,%s);"
            l = []
            i = data_frame.columns
            count = 0
            n_row = len(data_frame)
            for j in range(0,n_row):
                pt = []
                for k in i:
                    l = data_frame[k]
                    if k == 'enrollment':
                        pt.append(l[j].upper())
                        continue
                    elif k == 'last_name' or k == 'first_name':
                        pt.append(l[j].title())
                        continue
                    elif k == 'email':
                        if l[j]:
                            sendMail("Registraion Success",l[j],data_frame['first_name'][j]+", Welcome to Truba TG Helper Plateform\nYour User ID is : "+data_frame['enrollment'][j]+" \nPassword is : "+data_frame['password'][j])
                    elif k == 'password':
                        pt.append(pbkdf2_sha256.encrypt(l[j],rounds=12000,salt_size=32))
                        continue
                    pt.append(str(l[j]))
                cursor.execute(query,pt)
                conn.commit()
                count += cursor.rowcount
                print(pt)
            messages.info(request,str(count)+" Students has been added")
            return render(request,'tg_home.html',{'work_':'home','result':result})
        else:
            print(result)
            return render(request,'tg_home.html',{'work_':'add_stu','result':result})
    except IndexError:
        return render(request,'index.html',{'err':'Please Login First'})

def add_notification(request):
    try:
        if request.method == 'POST':
            notice = request.POST['notification']
            query = "insert into noti(class,notic) values('" + result.have_class + "','" + notice + "');"
            cursor.execute(query)
            conn.commit()
            messages.info(request,"Notification Added")
            return render(request,'tg_home.html',{'work_':'home','result':result})
        else:
            print(result)
            return render(request,'tg_home.html',{'work_':'add_notification','result':result})
    except NameError:
        return render(request,'index.html',{'err':'Please Login First'})

def show_stu(request):
    try:
        if request.method == 'POST':
            query = "select * from " + result.have_class + ";"
            cursor.execute(query)
            stus = cursor.fetchall()
            return render(request,'tg_home.html',{'work_':'show_stu','result':result,'stus':stus})
        else:
            print(result)
            return render(request,'tg_home.html',{'work_':'home','result':result})
    except NameError:
        return render(request,'index.html',{'err':'Please Login First'})

def accept(request):
    if request.method == 'POST':
        acc_stu = request.POST['requested_stu']
        acc_stu = acc_stu.upper()
        regis_request = "select * from register_temp where enrollment='" + acc_stu + "';"
        cursor.execute(regis_request)
        regis_result = cursor.fetchall()
        query1 = "INSERT INTO "+ result.have_class +"(enrollment,first_name,last_name,email,phone,gender,password) VALUES(%s,%s,%s,%s,%s,%s,%s);"
        hh = [regis_result[0][0],regis_result[0][1],regis_result[0][2],regis_result[0][3],regis_result[0][4],regis_result[0][6],regis_result[0][7]]
        query = "delete from register_temp where enrollment='"+ acc_stu +"';"
        cursor.execute(query)
        conn.commit()
        cursor.execute(query1,hh)
        conn.commit()
        regis_result = None
        regis_request = "select * from register_temp where class='"+ result.have_class +"';"
        cursor.execute(regis_request)
        regis_result = cursor.fetchall()
        messages.info(request,"Request of "+acc_stu+" accepted")
        return render(request,'tg_home.html',{'work_':'home','result':result,'registrations':regis_result})     
    else:
        try:
            regis_result = None
            regis_request = "select * from register_temp where class='"+ result.have_class +"';"
            cursor.execute(regis_request)
            regis_result = cursor.fetchall()
            return render(request,'tg_home.html',{'work_':'home','result':result,'registrations':regis_result})       
        except:
            messages.info(request,"Something wrong Happening at no post request")
            return render(request,'tg_home.html',{'work_':'home','result':result,'registrations':regis_result})

def about_us(request):
    return render(request,'about.html')


def logout(request):
    try: 
        del result
        del output_l
        del output
        del notice
        del regis_result
        return render(request,'index.html',{'err':'Success Loged Out'})
    except UnboundLocalError:
        return render(request,'index.html',{'err':'Success Loged Out'})









































            