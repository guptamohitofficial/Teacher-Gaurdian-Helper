from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from .__init__ import cursor, conn, sendMail
from creator.models import allot_tg, semister
from .models import profileimage
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
        global sem_info
        global pinfo
        global is_pic
        global class_name
        global sem_send
        global sems_info
        global my_tg
        global all_sem_subs

        uname2db = request.POST['enroll']
        pass2db = request.POST['passwd']
        if uname2db == "" or pass2db == "":
            return render(request,'index.html',{'err':'Empty Feilds'})
        else:   
            if uname2db[0:4] == "0114":
                uname2db = uname2db.upper()
            out = allot_tg.objects.all()
            class_name = ""
            my_tg = "Prof. "
            for i in out:
                query = "select * from " + i.have_class + " where enrollment='" + str(uname2db) + "';"
                cursor.execute(query)
                output_l = cursor.fetchall()
                if output_l:
                    class_name = i.have_class
                    my_tg += i.first_name.title()+" "
                    my_tg += i.last_name.title()
                    break
            try:
                result = output_l[0]
                if pbkdf2_sha256.verify(pass2db,result[6]):
                    
                    query = "select * from " + class_name+ "_pinfo where enrollment='"+result[0]+"';"
                    cursor.execute(query)
                    pinfo = cursor.fetchall() 
                    if pinfo:
                        pinfo = pinfo[0]

                    query = "select profile_image from pinfo_profileimage where profile_image='images/" + uname2db + "';"
                    cursor.execute(query)
                    is_pic = cursor.fetchall()

                    query = "select * from creator_semister where class_name='" + class_name + "';"
                    cursor.execute(query)
                    sems_info = cursor.fetchall()
                    all_sem_subs = []
                    print(sems_info)
                    sem_num = []
                    ccc = 0
                    for temps in sems_info:
                        n = len(temps[3])
                        tem = temps[3]
                        sub = ""
                        subs = []
                        count_local = 1
                        for i in range(0,n):
                            if tem[i] != ',':
                                sub = sub + tem[i]
                            else:
                                subs.append([sub,count_local])
                                count_local += 1
                                sub = ""
                            if i==n-1:
                                subs.append([sub,count_local])
                        all_sem_subs.append({'sub_name':subs,'sem':temps[2]+'_sem'+str(temps[1])})
                        sem_num.append([ccc,temps[1]])
                        ccc += 1
                    print(all_sem_subs)
                    sem_send = [sem_num]

                    query = "select notic from noti where class='"+class_name+"';"
                    cursor.execute(query)
                    notice = cursor.fetchall()
                    messages.info(request,"Welcome "+result[1])
                    messages.info(request,"This is Your Message pannel")
                    return render(request,'student_home.html',{'my_tg':my_tg,'result':result,'class_name':class_name,'noti':notice,'profilepic':is_pic,'sems_info':sem_send,'sub_name':all_sem_subs,'pinfo':pinfo})
                else:
                    return render(request,'index.html',{'err':'Pssword not matched'}) 
            except IndexError:
                output_l = allot_tg.objects.filter(tg_name__exact=uname2db)
                try:
                    result = output_l[0]
                    if pbkdf2_sha256.verify(pass2db,result.password):
                        regis_result = None
                        regis_request = "select * from register_temp where class='" + result.have_class + "' and otp=1;"
                        cursor.execute(regis_request)
                        regis_result = cursor.fetchall()

                        query = "select profile_image from pinfo_profileimage where profile_image='images/" + uname2db + "';"
                        cursor.execute(query)
                        is_pic = cursor.fetchall()
                        messages.info(request,"This is Your Message pannel")
                        return render(request,'tg_home.html',{'work_':'home','result':result,'registrations':regis_result,'profilepic':is_pic})
                    else:
                        return render(request,'index.html',{'err':'Pssword not matched'})  
                except IndexError:
                    try:
                        regis_request = "select * from register_temp where enrollment='" + uname2db + "';"
                        cursor.execute(regis_request)
                        regis_result = cursor.fetchall()
                        result = regis_result[0]
                        if pbkdf2_sha256.verify(pass2db,result[7]):
                            return render(request,'otp.html',{'enroll':result[0]})
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
            sendMail("TG-Diary OTP",email2db,"Hey "+fname2db+"\nWe are very happy to have you here but your email verification is left.\n\nYour OTP is : "+str(otp_reg)+"\n\nPlease submit your OTP So, that we can move your Application forward to your TG\nAfter Email verifiction Please wait for the approval of your request.\n\n\nRegards,\nMohit (Admin)")
            query = "insert into register_temp(enrollment,first_name,last_name,email,phone,class,gender,password,otp) values('" + enroll2db + "','" + fname2db + "','" + lname2db + "','" + email2db + "','" + phone2db + "','" + class2db + "','" + gender2db + "','" + pass_hash + "'," + str(otp_reg) + ");"
            try:
                cursor.execute(query)
                print(query)
                conn.commit()
            except:
                messages.info(request,"User exists")
                return render(request,'signup.html',{'clas':output})
            return render(request,'otp.html',{'enroll':enroll2db})
        else:
            messages.info(request,"Both passwords does not match")
            return render(request,'signup.html',{'clas':output})
    else:
        output = allot_tg.objects.all()
        return render(request,'signup.html',{'clas':output})
        

def VerifyEmail(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        chk_enroll = request.POST['enroll']
        chk_enroll = chk_enroll.upper()
        regis_request = "select * from register_temp where enrollment='" + chk_enroll + "';"
        cursor.execute(regis_request)
        regis_result = cursor.fetchall()
        if str(otp) == str(regis_result[0][8]):
            query = "UPDATE register_temp SET otp=1 where enrollment='"+ chk_enroll +"';"
            cursor.execute(query)
            conn.commit()
            output = allot_tg.objects.all()
            messages.info(request,chk_enroll+" Registered Sucessfully")
            return render(request,'signup.html',{'clas':output}) 
        else:
            return render(request,'index.html',{'err':'OTP Not Match'}) 
    else:
        messages.info(request,"Please Register First")
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
                return render(request,'tg_home.html',{'work_':'home','registrations':regis_result,'profilepic':is_pic,'result':result})            
        else:
            print(result)
            semss = [1,2,3,4,5,6,7,8]
            sem_next = 1
            sem_exist = semister.objects.filter(class_name=result.have_class)
            for i in sem_exist:
                semss.remove(i.sem)
            return render(request,'tg_home.html',{'work_':'add_sem','registrations':regis_result,'profilepic':is_pic,'result':result,'sem_next':semss})
    except NameError:
        return render(request,'index.html',{'err':'Please Login First'})


def UploadImg(request):
    if request.method == 'POST':
        image = request.FILES['img']
        image.name = result[0]
        imgObj = profileimage(profile_Image=image)
        imgObj.save()
        is_pic = profileimage.objects.filter(profile_Image='images/'+result[0])
        messages.info(request,"Profile Sucessfully Uploaded")
        return render(request,'student_home.html',{'result':result,'profilepic':is_pic,'sems_info':sems_info})
    else:
        return render(request,'index.html',{'err':'Please Login First'})


def UploadImgtg(request):
    global is_pic
    if request.method == 'POST':
        image = request.FILES['img']
        image.name = result.tg_name
        imgObj = profileimage(profile_Image=image)
        imgObj.save()
        is_pic = profileimage.objects.filter(profile_Image='images/'+result.tg_name)
        messages.info(request,"Profile Sucessfully Uploaded")
        return render(request,'tg_home.html',{'work_':'home','registrations':regis_result,'result':result,'profilepic':is_pic})
    else:
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
                return render(request,'tg_home.html',{'work_':'home','registrations':regis_result,'result':result})
            else:    
                query = "delete from creator_semister where sem=" + sem + " and class_name='" + class_name + "';"
                print(query)
                cursor.execute(query)
                conn.commit()        
                query = "drop table " + class_name + "_sem" + sem + ";" 
                cursor.execute(query)
                conn.commit()  
                messages.info(request,"Semister "+sem+" for "+class_name+" is Deleted")
                return render(request,'tg_home.html',{'work_':'home','registrations':regis_result,'profilepic':is_pic,'result':result})            
        else:
            print(result)
            sem_have = []
            sem_exist = semister.objects.filter(class_name=result.have_class)
            for i in sem_exist:
                sem_have.append(i.sem)
            return render(request,'tg_home.html',{'work_':'del_sem','registrations':regis_result,'profilepic':is_pic,'result':result,'sem_exist':sem_have})
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
                try:
                    cursor.execute(query,pt)
                    conn.commit()
                except NameError:
                    print()
                count += cursor.rowcount
                print(pt)
                print("Mail Sent to "+pt[1])
            messages.info(request,str(count)+" Students has been added")
            return render(request,'tg_home.html',{'work_':'home','registrations':regis_result,'profilepic':is_pic,'result':result})
        else:
            print(result)
            return render(request,'tg_home.html',{'work_':'add_stu','registrations':regis_result,'profilepic':is_pic,'result':result})
    except IndexError:
        messages.info(request,"Index Error Occured")
        return render(request,'tg_home.html',{'work_':'home','registrations':regis_result,'profilepic':is_pic,'result':result})
    except NameError:
        return render(request,'index.html',{'err':'Please Login First'})


def add_notification(request):
    try:
        if request.method == 'POST':
            notice = request.POST['notification']
            query = "insert into noti(class,notic) values('" + result.have_class + "','" + notice + "');"
            cursor.execute(query)
            conn.commit()
            messages.info(request,"Notification Added")
            return render(request,'tg_home.html',{'work_':'home','registrations':regis_result,'profilepic':is_pic,'result':result})
        else:
            return render(request,'tg_home.html',{'work_':'add_notification','registrations':regis_result,'profilepic':is_pic,'result':result})
    except NameError:
        return render(request,'index.html',{'err':'Please Login First'})


def sendMessage(request):
    if request.method == 'POST':
        mesg = request.POST['notification']
        query = "select first_name,email from "+result.have_class+";"
        cursor.execute(query)
        emails = cursor.fetchall()
        have_mail = 0
        no_mail = 0
        for i in emails:
            if i[1]:
                sendMail("Message - TG",i[1],"Hello " + str(i[0]) + "\n\n" + mesg + "\n\nRegards,\nProf. " + result.first_name + " " + result.last_name + "\nTG - " + result.have_class)
                have_mail += 1
            else:
                no_mail += 1
        messages.info(request,"Mails sent to "+str(have_mail)+" Students")
        messages.info(request,str(no_mail)+" Mails Students don't have Mail")
    else:
        return render(request,'index.html',{'err':'Please Login First'})


def search_stu(request):
    if request.method == 'POST':
        search_res = []
        en = request.POST['search']
        en = en.upper()
        query1 = "select * from " + result.have_class + " where enrollment='" + en + "';"
        query2 = "select * from " + result.have_class + "_pinfo where enrollment='" + en + "';;"
        cursor.execute(query1)
        output = cursor.fetchall()
        if output:
            search_res.append(output[0])
        else:
            search_res.append(0)
        cursor.execute(query2)
        output = cursor.fetchall()
        if output:
            search_res.append(output[0])
        else:
            search_res.append(0)
        query3 = "select * from creator_semister where class_name='" + result.have_class + "';"
        cursor.execute(query3)
        sems_info = cursor.fetchall()
        for temps in sems_info:
            sems_result_temp = []
            sems_result_temp_1 = []
            n = len(temps[3])
            tem = temps[3]
            sub = ""
            subs = []
            for i in range(0,n):
                if tem[i] != ',':
                    sub = sub + tem[i]
                else:
                    subs.append(sub)
                    sub = ""
                if i==n-1:
                    subs.append(sub)
            query = "select * from " + result.have_class + "_sem" + str(temps[1]) + " where enrollment='" + en + "';"
            cursor.execute(query)
            sem_temp_marks = cursor.fetchall()
            if sem_temp_marks:
                j = sem_temp_marks[0]
                jn = len(j)
                for i in range(1,jn):
                    sems_result_temp.append([subs[i-1],j[i]])
            else:
                sems_result_temp.append(0)
            sems_result_temp_1.append(sems_result_temp)
        search_res.append(sems_result_temp_1)
        print(search_res)
        sem_num = []
        for i in sems_info:
            sem_num.append(i[1])                 
        return render(request,'tg_home.html',{'work_':'search_done','search_res':search_res,'registrations':regis_result,'profilepic':is_pic,'result':result})
    else:
        return render(request,'tg_home.html',{'work_':'search_','registrations':regis_result,'profilepic':is_pic,'result':result})


def show_stu(request):
    try:
        if request.method == 'POST':
            query = "select * from " + result.have_class + ";"
            cursor.execute(query)
            stus = cursor.fetchall()
            return render(request,'tg_home.html',{'work_':'show_stu','registrations':regis_result,'result':result,'profilepic':is_pic,'stus':stus})
        else:
            return render(request,'tg_home.html',{'work_':'home','registrations':regis_result,'result':result})
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
        sendMail("Regarding Request",regis_result[0][3],"Congratulations "+regis_result[0][1]+",\nYour request for TG Diary has been approved.\nRegards,\nProf. " + result.first_name + " " + result.last_name + "\nTG - " + result.have_class)
        regis_result = None
        regis_request = "select * from register_temp where class='"+ result.have_class +"';"
        cursor.execute(regis_request)
        regis_result = cursor.fetchall()
        messages.info(request,"Request of "+acc_stu+" accepted")
        return render(request,'tg_home.html',{'work_':'home','result':result,'profilepic':is_pic,'registrations':regis_result})    
    else:
        try:
            regis_result = None
            regis_request = "select * from register_temp where class='"+ result.have_class +"' and otp=1;"
            cursor.execute(regis_request)
            regis_result = cursor.fetchall()
            return render(request,'tg_home.html',{'work_':'home','result':result,'profilepic':is_pic,'registrations':regis_result})       
        except:
            messages.info(request,"Something wrong Happening at no post request")
            return render(request,'tg_home.html',{'work_':'home','result':result,'profilepic':is_pic,'registrations':regis_result})



def reject(request):
    if request.method == 'POST':
        acc_stu = request.POST['requested_stu']
        acc_stu = acc_stu.upper()
        regis_request = "select * from register_temp where enrollment='" + acc_stu + "';"
        cursor.execute(regis_request)
        regis_result = cursor.fetchall()
        query = "delete from register_temp where enrollment='"+ acc_stu +"';"
        cursor.execute(query)
        conn.commit()
        sendMail("Regarding Request",regis_result[0][3],"Sorry "+regis_result[0][1]+",\nYour request for TG Diary has been Rejected.\nRegards,\nProf. " + result.first_name + " " + result.last_name + "\nTG - " + result.have_class)
        regis_result = None
        regis_request = "select * from register_temp where class='"+ result.have_class +"';"
        cursor.execute(regis_request)
        regis_result = cursor.fetchall()
        messages.info(request,"Request of "+acc_stu+" Rejected")
        return render(request,'tg_home.html',{'work_':'home','result':result,'profilepic':is_pic,'registrations':regis_result})    
    else:
        try:
            regis_result = None
            regis_request = "select * from register_temp where class='"+ result.have_class +"' and otp=1;"
            cursor.execute(regis_request)
            regis_result = cursor.fetchall()
            return render(request,'tg_home.html',{'work_':'home','result':result,'profilepic':is_pic,'registrations':regis_result})       
        except:
            messages.info(request,"Something wrong Happening at no post request")
            return render(request,'tg_home.html',{'work_':'home','result':result,'profilepic':is_pic,'registrations':regis_result})




def update_pinof(request):
    if request.method == 'POST':
        try:
            enroll = request.POST['enrollment']
            father_name = request.POST['father_name']
            father_phone = request.POST['father_phone']
            mother_name = request.POST['mother_name']
            perm_addr = request.POST['per_addr']
            local_addr = request.POST['local_addr']
            gaurd_name = request.POST['gaur_name']
            gaurd_addr = request.POST['gaur_addr']
        except IndexError:
            messages.info(request,"Something went wrong with Entries")
            return render(request,'student_home.html',{'my_tg':my_tg,'result':result,'class_name':class_name,'noti':notice,'profilepic':is_pic,'sems_info':sems_info})    
    
        query = "insert into " + class_name + "_pinfo(enrollment,father_name,father_phone,mother_name,permanent_address,local_address,local_gaurdian,gaurdian_phone) values('" + enroll + "','" + father_name + "','" + father_phone + "','" + mother_name + "','" + perm_addr + "','" + local_addr + "','" + gaurd_name + "','" + gaurd_addr + "');"
        cursor.execute(query) 
        conn.commit()
        messages.info(request,"Personal Information Successfully Updated")
        return render(request,'student_home.html',{'my_tg':my_tg,'result':result,'class_name':class_name,'noti':notice,'profilepic':is_pic,'sems_info':sem_send,'sub_name':all_sem_subs,'pinfo':pinfo})
    else:
        messages.info(request,"Not Post Method")
        return render(request,'student_home.html',{'my_tg':my_tg,'result':result,'class_name':class_name,'noti':notice,'profilepic':is_pic,'sems_info':sem_send,'sub_name':all_sem_subs,'pinfo':pinfo})
    
def sem_marks(request):
    if request.method == 'POST':
        enroll_sem = request.POST['enroll']
        class_sem = request.POST['class_name']
        semister_sem = str(request.POST['semister'])
        sub_1_sem = request.POST['sub_1']
        sub_2_sem = request.POST['sub_2']
        sub_3_sem = request.POST['sub_3']
        try:
            sub_7_sem = request.POST['sub_7']
            sub_6_sem = request.POST['sub_6']
            sub_5_sem = request.POST['sub_5']
            sub_4_sem = request.POST['sub_4']
            messages.info(request,"7 Subjects Marks has been added to your Semister "+semister_sem)
            query = "insert into "+semister_sem+" values('"+enroll_sem+"',"+sub_1_sem+","+sub_2_sem+","+sub_3_sem+","+sub_4_sem+","+sub_5_sem+","+sub_6_sem+","+sub_7_sem+");"
        except KeyError:
            try:
                sub_6_sem = request.POST['sub_6']
                sub_5_sem = request.POST['sub_5']
                sub_4_sem = request.POST['sub_4']
                messages.info(request,"6 Subjects Marks has been added to your Semister "+semister_sem)
                query = "insert into "+semister_sem+" values('"+enroll_sem+"',"+sub_1_sem+","+sub_2_sem+","+sub_3_sem+","+sub_4_sem+","+sub_5_sem+","+sub_6_sem+");"
            except KeyError:
                try:
                    sub_5_sem = request.POST['sub_5']
                    sub_4_sem = request.POST['sub_4']
                    messages.info(request,"5 Subjects Marks has been added to your Semister "+semister_sem)
                    query = "insert into "+semister_sem+" values('"+enroll_sem+"',"+sub_1_sem+","+sub_2_sem+","+sub_3_sem+","+sub_4_sem+","+sub_5_sem+");"
                except KeyError:
                    try:
                        sub_4_sem = request.POST['sub_4']
                        messages.info(request,"4 Subjects Marks has been added to your Semister "+semister_sem)
                        query = "insert into "+semister_sem+" values('"+enroll_sem+"',"+sub_1_sem+","+sub_2_sem+","+sub_3_sem+","+sub_4_sem+");"
                    except KeyError:
                        messages.info(request,"3 Subjects Marks has been added to your Semister "+semister_sem)
                        query = "insert into "+semister_sem+" values('"+enroll_sem+"',"+sub_1_sem+","+sub_2_sem+","+sub_3_sem+");"
            cursor.execute(query)
            conn.commit()
            return render(request,'student_home.html',{'my_tg':my_tg,'result':result,'class_name':class_name,'noti':notice,'profilepic':is_pic,'sems_info':sem_send,'sub_name':all_sem_subs,'pinfo':pinfo})
        else:
            messages.info(request,"Method is not POST")
            return render(request,'student_home.html',{'my_tg':my_tg,'result':result,'class_name':class_name,'noti':notice,'profilepic':is_pic,'sems_info':sem_send,'sub_name':all_sem_subs,'pinfo':pinfo})


def about_us(request):
    return render(request,'about.html')

def mid_sem(request):
    try:
        if request.method == 'POST':
            xl_file = request.FILES['mid_sem_file']
            data_frame = pd.read_excel(xl_file,sheet_name="Sheet1")
            l = []
            i = data_frame.columns
            file_name = xl_file.name
            file_name_size = len(file_name)
            file_name = file_name[0:file_name_size-5]
            sent_count = 0
            drop_count = 0
            n_row = len(data_frame)
            regsMsg = "\nRegards\nProf. "+result.first_name+" "+result.last_name+"\nTG - "+result.have_class
            for j in range(0,n_row):
                is_email = ""
                to_message = "Your "+str(file_name)+" Marks are : \n\n"
                for k in i:
                    l = data_frame[k]
                    if k == 'enrollment':    
                        query = "select email from "+result.have_class+" where enrollment='" + l[j].upper() + "';"
                        cursor.execute(query)
                        is_email = cursor.fetchall()
                        continue
                    else:
                        to_message += k+"  :  "+str(l[j])+"\n"
                    
                to_message += regsMsg
                if is_email:
                    sendMail(file_name+" Marks",is_email[0][0],to_message)
                    sent_count += 1
                else:
                    drop_count += 1
            messages.info(request,"Marks Sent to " + str(sent_count) + " Students")
            messages.info(request,"" + str(drop_count) + " Student's Email not Found")
            return render(request,'tg_home.html',{'work_':'home','registrations':regis_result,'profilepic':is_pic,'result':result})
        else:
            return render(request,'tg_home.html',{'work_':'mid_sem','profilepic':is_pic,'result':result})
    except IndexError:
        messages.info(request,"Index Error Occured")
        return render(request,'tg_home.html',{'work_':'mid_sem','profilepic':is_pic,'result':result})
    except NameError:
        return render(request,'index.html',{'err':'Please Login First'})


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









