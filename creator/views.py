from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from .models import admin_auth, allot_tg
from .__init__ import cursor, conn, sendMail
from passlib.hash import pbkdf2_sha256

# Create your views here.
global result
def home(request):
    global result
    if request.method == 'POST':
        if request.POST['adname'] != " ":
            uname2db = request.POST['adname']
            pass2db = request.POST['passwd']
            output = admin_auth.objects.filter(username__exact=uname2db) 
            try:
                result = output[0]
            except IndexError:
                return render(request,'admin_home.html',{'name':'User not found'})

            if pbkdf2_sha256.verify(pass2db,result.password):
                return render(request,'admin_home.html',{'name':result.name,'user_info':result})
            else:
                print("Password Not Match")
                return render(request,'admin_home.html',{'name':'Password Not Matched'})
        else:
            print("Empty Sell")
            return render(request,'admin_home.html',{'name':'Empty Sells'})
    else:
        return render(request,'admin_home.html',{'name':'Admin login'})

def go(request):
    return render(request,'admin_home.html',{'name':result.name,'user_info':result})


def show_tg(request):
    if request.method == 'POST':
        output = allot_tg.objects.all()
        return render(request,'admin_work.html',{'work_':'show_tg','user_info':result,'name':result.name,'all_tg':output})
    else:
        try:
            return render(request,'admin_work.html',{'work_':'show_tg','name':result.name,'user_info':result})
        except NameError:
            return render(request,'admin_home.html',{'name':'Please login first'})
        
def add_tg(request):
    if request.method == 'POST':
        try:
            tg_username2db = request.POST['tg_username']
            tg_f_name2db = request.POST['tg_first_name']
            tg_f_name2db = tg_f_name2db.title()
            tg_l_name2db = request.POST['tg_last_name']
            tg_l_name2db = tg_l_name2db.title()
            tg_email2db = request.POST['tg_email']
            tg_class_branch = request.POST['class_branch']
            tg_class_batch = request.POST['class_batch']
            tg_class_section = request.POST['class_section']
            tg_class2db = str(tg_class_branch)+str(tg_class_batch)+"_"+str(tg_class_section)
            tg_about2db = request.POST['tg_about']
            tg_passwd12db = request.POST['passwd1']
            tg_passwd22db = request.POST['passwd2']
        except:
            messages.info(request,"Wrong Entries")
            return render(request,'admin_work.html',{'work_':'add_tg','user_info':result})
        try:
            if tg_passwd12db != tg_passwd22db:
                messages.info(request,"Password Does Not Confirmed")
                return render(request,'admin_work.html',{'work_':'add_tg','name':result.name,'user_info':result})
            pass_hash = pbkdf2_sha256.encrypt(tg_passwd12db,rounds=12000,salt_size=32)
            create_tg = allot_tg(tg_name = tg_username2db, first_name = tg_f_name2db, last_name = tg_l_name2db, have_class = tg_class2db, tg_email = tg_email2db, password = pass_hash, description = tg_about2db)
            create_tg.save()
            query = "create table " + tg_class2db + "_pinfo(enrollment varchar(12) PRIMARY KEY, father_name varchar(60) not NULL, father_phone varchar(10) not NULL, mother_name varchar(60) not NULL, permanent_address varchar(250) not NULL, local_address varchar(250) not NULL, local_gaurdian varchar(60) not NULL, gaurdian_phone varchar(10) not NULL);"
            cursor.execute(query) 
            conn.commit() 
            query = "create table " + tg_class2db + "(enrollment varchar(12) PRIMARY KEY, first_name varchar(30) not NULL, last_name varchar(30) not NULL, email varchar(100), phone varchar(10), gender varchar(7) not NULL, password varchar(260) not NULL);"
            cursor.execute(query)
            conn.commit()
            sendMail("TG Allotment",tg_email2db,"Hello Prof."+tg_f_name2db+" "+tg_l_name2db+"\nThis message is to inform you that you are appointed to be the TG of Class : "+tg_class2db+"\nYour Login Credentials at tgtruba.com are :\nYour Username is "+tg_username2db+"\nYour Password is "+tg_passwd12db+"\nRegards,\nMohit(Admin - TG Diary)")
        except IndexError:
            messages.info(request,"Something Went Wrong")    
        messages.info(request,"TG created")
        return render(request,'admin_home.html',{'name':result.name,'name':result.name,'user_info':result})

    else:
        try:
            return render(request,'admin_work.html',{'work_':'add_tg','name':result.name,'user_info':result})        
        except NameError:
            return render(request,'admin_home.html',{'name':'Please login first'})

def show_stu(request):
    if request.method == 'POST':
        show_class_stu = request.POST['to_class']
        cursor.execute("select * from " + str(show_class_stu)+ ";")
        output = cursor.fetchall()
        return render(request,'admin_work.html',{'work_':'show_stu','name':result.name,'class_name':show_class_stu,'user_info':result,'all_students':output})   
    else:
        try:
            output = allot_tg.objects.all()
            return render(request,'admin_work.html',{'work_':'show_stu_cls','name':result.name,'user_info':result,'all_tg':output})        
        except NameError:
            return render(request,'admin_home.html',{'name':'Please login first'})
        except:
            return render(request,'admin_home.html',{'name':'Please login first'})

def logout(request):
    try: 
        del result
        return render(request,'admin_home.html',{'name':'Admin login','err':'Success Loged Out'})
    except UnboundLocalError:
        return render(request,'admin_home.html',{'name':'Admin login','err':'Success Loged Out'})









