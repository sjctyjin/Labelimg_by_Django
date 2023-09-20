from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,StreamingHttpResponse
from django.views.generic import View
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import xml.etree.ElementTree as ET
import time
from pathlib import Path
import os
from PIL import Image
import traceback
import cv2
import numpy as np
import json as d
import yaml
import pymssql
from appclass.models import Training_cycle
from datetime import datetime
import torch
from urllib.parse import unquote#將中文URL編碼轉回中文
# Create your views here.


menu_bar = f"""
         <nav class="sb-topnav navbar navbar-expand navbar-dark bg-dark">
            <!-- Navbar Brand-->
            <a class="navbar-brand ps-3" href="index">影像工具</a>
            <!-- Sidebar Toggle-->
            <button class="btn btn-link btn-sm order-1 order-lg-0 me-4 me-lg-0" onclick="ajaxRead()" id="sidebarToggle" href="#!">
                <span style="font-family:Comic Sans MS;font-size:14px;">
                    <div class="menu-icon"><i class="fas fa-bars"></i></div>
                </span>
            </button>

            <!-- Navbar Search-->
            <form class="d-none d-md-inline-block form-inline ms-auto me-0 me-md-3 my-2 my-md-0">

<!--                <div class="input-group">-->
<!--                    <input class="form-control" type="text" placeholder="搜尋資料夾" aria-label="Search for..." aria-describedby="btnNavbarSearch" />-->
<!--                    <button class="btn btn-primary" id="btnNavbarSearch" type="button"><i class="fas fa-search"></i></button>-->
<!--                </div>-->

            </form>
            <!-- Navbar-->
            <ul class="navbar-nav ms-auto ms-md-0 me-3 me-lg-4">
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" id="navbarDropdown" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false"><i class="fas fa-user fa-fw"></i></a>
                    <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
                        <li><a class="dropdown-item" href="Augmentation">影像增強</a></li>
                        <li><a class="dropdown-item" href="index">影像標註</a></li>
                        <li><a class="dropdown-item" href="#!">調用測試</a></li>
                        <li><a class="dropdown-item" href="ModelView">模型檢視</a></li>
                        <li><a class="dropdown-item" href="training">模型訓練</a></li>
                        <li><hr class="dropdown-divider" /></li>
                        <li><a class="dropdown-item" href="logout">登出</a></li>
                    </ul>
                </li>
            </ul>
        </nav>

"""

decoded_str = "模型訓練中"



class Message(View):
    global menu_bar

    def get(self,request):
        if not request.user.is_authenticated:
            # return render(request, 'please_login.html')
            return HttpResponse("""
                              <style>
                              .square {

                          /* animation 參數設定 */
                          animation-name: MoveToRight;    /*動畫名稱，需與 keyframe 名稱對應*/
                          animation-duration: 2s;    /*動畫持續時間，單位為秒*/
                          animation-delay: 0s;    /*動畫延遲開始時間*/
                          animation-iteration-count: infinite;    /*動畫次數，infinite 為無限次*/
                      }

                      @keyframes MoveToRight {
                          from { top: 0%;opacity:0;  }
                          to { top: 5%;opacity:1; }
                      }
                              </style>
                             <div class="square" style="padding:20px;position:absolute;top:40%;width:80%;left:10%;
                             border-radius:15px;
                             background-color:#FFB5B5;
                             color:#FF2D2D;
                             font-size:5vmin;text-align:center;">
                               無權操作，請先登入<br/>
                              </div>
                              <script>setTimeout("location.href='login'",2000);</script>""")

        dir_name = "userdata"
        user_name = request.user
        name = request.GET.get('filepath','')

        #找尋filepath目錄位置的照片
        #此為提供給該帳號用戶，瀏覽選擇以建立過的檔案照片
        if(name != ""):#若當前路徑有指定目錄名稱
            save_path = f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{name}/images/'
            dirs = []
            user_dirs = []
            try:
                files = os.listdir(save_path)
                files.sort(key= lambda x:int(x[:-4]))
                tags = []
                try:
                    with open(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{name}/classes.txt', 'r') as f:
                        for text in f.read().split('\n'):
                            if text != "\n" and text != "":
                                tags.append(text)
                except:
                    with open(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{name}/classes.txt', 'w') as f:
                        f.write('')

                for fi in files:
                    dirs.append(f"static/{dir_name}/{user_name}/{name}/images/{fi}".replace("\\","/"))

                sorted_folders = sorted(os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'),
                                        key=extract_datetime, reverse=True)

                for fidir in sorted_folders:
                    #分割檔案名稱並重新組裝後賦值到瀏覽器
                    y = fidir.split('-')[0].split('_')[0][0:4]
                    m = fidir.split('-')[0].split('_')[0][4:6]
                    d = fidir.split('-')[0].split('_')[0][6:8]
                    h = fidir.split('-')[0].split('_')[1][0:2]
                    min = fidir.split('-')[0].split('_')[1][2:4]
                    s = fidir.split('-')[0].split('_')[1][4:6]
                    user_dirs.append([fidir,f'{y}-{m}-{d} {h}:{min}:{s}'])

                return render(request,'index.html',{'dirs':dirs,'user':user_name,'obj_name':name.split('-')[1],'file_dir':user_dirs,'tags':tags,'menu':menu_bar,'dirslen':len(dirs)})
            except:
                print(traceback.format_exc())

                return render(request,'index.html',{'user':user_name,'menu':menu_bar})
        else:
            user_dirs = []

            #如果為初次登入使用者，為其建立資料夾
            if not Path(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}').exists():
                Path(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}').mkdir(parents=True, exist_ok=True)

            sorted_folders = sorted(os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'),
                                    key=extract_datetime, reverse=True)

            for fidir in sorted_folders:
                y = fidir.split('-')[0].split('_')[0][0:4]
                m = fidir.split('-')[0].split('_')[0][4:6]
                d = fidir.split('-')[0].split('_')[0][6:8]
                h = fidir.split('-')[0].split('_')[1][0:2]
                min = fidir.split('-')[0].split('_')[1][2:4]
                s = fidir.split('-')[0].split('_')[1][4:6]
                user_dirs.append([fidir, f'{y}-{m}-{d} {h}:{min}:{s}'])
            return render(request,'index.html',{'user':user_name,'file_dir':user_dirs,'menu':menu_bar})
    # def post(self,request):
    #     file_up = request.FILES.getlist("file[]")#['filename']
    #     print(file_up)

    #     return HttpResponse('success')
    @csrf_exempt
    #標註圖片上傳,上傳
    def post(self,request):
        # print("POST的")
        if not request.user.is_authenticated:
            return render(request, 'please_login.html')
        dir_name = "userdata"
        file_name = request.POST.get("dataset")
        file_up = request.FILES.getlist("file[]")  # ['filename']
        user_name = request.user
        now = (time.strftime("%Y%m%d_%H%M%S"))

        # file_up = request.FILES.get("file[]")#['filename']
        print(file_up)
        save_path = f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{now}-{file_name}/images/'
        #創建資料夾
        if not Path(save_path).exists():
            Path(save_path).mkdir(parents=True, exist_ok=True)

        with open(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{now}-{file_name}/classes.txt', 'w') as f:
            f.write('')
        count_img = 0
        for files in file_up:

            save_paths = os.path.join(save_path,f'{count_img}.jpg').replace("\\","/")
            with open(save_paths,'wb') as f:
                for content in files.chunks():
                    f.write(content)

            count_img +=1
            #print(files.chunks())
            # Article.objects.create(thunmbnial=files)
            #若檔案超過1000px x 1000px 則 resize
            try:
                img = Image.open(save_paths)
                img = exif_transpose(img)
                img = img.convert("RGB")
                dd = img.size
                if 4000000 > dd[0]*dd[1] > 999000:
                    cropped = img.resize((int(dd[0]*0.4),int(dd[1]*0.4)))
                    cropped.save(save_paths)
                elif dd[0]*dd[1] > 4000001:
                    cropped = img.resize((int(dd[0] * 0.2), int(dd[1] * 0.2)))
                    cropped.save(save_paths)
            except:
                print(traceback.format_exc())

        dirs = []
        files = os.listdir(save_path)
        files.sort(key= lambda x:int(x[:-4]))
        for fi in files:
            dirs.append(f"static/{dir_name}/{user_name}/{now}-{file_name}/images/{fi}".replace("\\","/"))

        user_dirs = []
        for fidir in os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'):
            user_dirs.append([fidir,fidir])
        print(dirs)

        return render(request,'index.html',{'dirs':dirs,"urlguide":f"{now}-{file_name}",'obj_name':file_name,'file_dir':user_dirs,'tags':[]})

    @csrf_exempt
    # 標註圖片上傳,上傳
    def speedLabel(request):
        if request.method != 'POST':
            # 判斷當前用戶是否已登入
            if not request.user.is_authenticated:
                return render(request, 'please_login.html')
            else:
                return HttpResponse('我是post请求')

        image_path = request.POST.get("filepath")
        filename = request.POST.get("filename")
        username = request.user
        imgpath = f"static/userdata/{username}/{filename}/images/"
        modelpath = f"static/usermodel/{username}/{filename}"
        modellist = []
        modeldict = {}#當有該名稱模型有多個日期資料夾存在時
        #點擊快速自動標註
        if request.POST.get("mode") == "select":
            # modelpath = ""
            modelpath = []
            #查看usermodel中是否有同名model，如果有則加入路徑
            checkmodel = 0
            #查看是否已存在標註檔
            checklabeled = 0
            print(f"{settings.MEDIA_ROOT[0]}/usermodel/{username}")
            for i in os.listdir(f"{settings.MEDIA_ROOT[0]}/usermodel/{username}"):
                if i.split('-')[1] == filename.split('-')[1]:
                    print("模型",i)
                    checkmodel = 1
                    modelpath.append(f"usermodel/{username}/{i}")
                    print("確認存在模型路徑:",i.split('-')[1])
            if modelpath != []:
                for m in modelpath:
                    modellist = []
                    for i in os.listdir(f"{settings.MEDIA_ROOT[0]}/{m}".replace("\\","/")):
                        print(i)
                        if len(i.split('.')) == 1:
                            print(i)
                            modellist.append(i)
                    modeldict[m] = modellist
            print(unquote("{0}\{1}labels_xml".format(settings.MEDIA_ROOT[0], imgpath[7:-7])))
            if Path(unquote("{0}\{1}labels_xml".format(settings.MEDIA_ROOT[0],imgpath[7:-7]))).exists():
                for b in os.listdir(unquote("{0}\{1}labels_xml".format(settings.MEDIA_ROOT[0],imgpath[7:-7]))):
                    checklabeled = 1
            print("模型 日期 :",modelpath)
            #若當日模型訓練數量超過1個時，需排序
            print(sorted(modellist,key=len))
            """TODO : 把模型路徑導正，前端網頁加入一個模型選項，選擇使用哪個模型做快速標註"""

            return JsonResponse({'status':modeldict,'labeled':checklabeled})
        #送出開始自動標註
        else:
            model = request.POST.get('modelname')
            modelpaths = request.POST.get('modelpath')
            print("模型 ",model)
            print("模型路徑",modelpaths)
            checkpt = 0
            if model == "":
                return JsonResponse({'status': "no data"})

            # for i in os.listdir(f"{settings.MEDIA_ROOT[0]}/usermodel/{username}"):
            #     if i.split('-')[1] == filename.split('-')[1]:
            #         modelpath = f"static/usermodel/{username}/{i}"
            try:
                for pt in os.listdir(f"{settings.MEDIA_ROOT[0]}/{modelpaths}/{model}/weights".replace("\\","/")):
                    if pt.split('.')[1] == "pt":
                        checkpt = 1 #確認是否存在模型
                if checkpt == 0:
                    return JsonResponse({'status': "no data"})
            except:
                return JsonResponse({'status': "no data"})
            print(f"調用模型 : {modelpaths}/{model}")
            model = torch.hub.load('static/yolov5', 'custom',
                                   path=f'static/{modelpaths}/{model}/weights/best.pt',
                                   source='local')
            label_class = {}#存放類別的classes.txt

            for img in os.listdir(imgpath):#遍歷每一張圖片


                frame = cv2.imread(f'{imgpath}/{img}')
                YOLO_Format = ""
                xml_content = f"""
                                      <annotation>
                                          <folder>images</folder>
                                          <filename>{img}</filename>
                                          <path>{imgpath}{img}</path>
                                          <source>
                                              <database>Unknown</database>
                                          </source>
                                          <size>
                                              <width>{frame.shape[1]}</width>
                                              <height>{frame.shape[0]}</height>
                                              <depth>3</depth>
                                          </size>
                                          <segmented>0</segmented>
                                      """

                start = time.time()
                results = model(frame)
                if len(results.pandas().xyxy[0]) > 0:

                    for resultI in range(len(results.pandas().xyxy[0])):

                        x = int(results.pandas().xyxy[0]["xmin"][resultI])
                        y = int(results.pandas().xyxy[0]["ymin"][resultI])
                        w = int(results.pandas().xyxy[0]["xmax"][resultI])
                        h = int(results.pandas().xyxy[0]["ymax"][resultI])
                        confi = int(results.pandas().xyxy[0]["confidence"][resultI] * 100)
                        names_label = results.pandas().xyxy[0]["name"][resultI]
                        label_class[results.pandas().xyxy[0]["class"][resultI]] = names_label

                        # print(x,y)
                        # print(h,w)
                        if confi > 10:

                            cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 5)
                            font = cv2.FONT_HERSHEY_COMPLEX
                            cv2.putText(frame, f'{names_label}_{confi}%', (x + 10, y + 10), font, 1, (255, 255, 255), 1,
                                        cv2.LINE_AA)
                            cv2.putText(frame, f'X : {int((w + x) / 2)},Y:{int((y + h) / 2)}',
                                        (int((w + x) / 2) + 10, int((y + h) / 2) + 10), font, 1, (255, 255, 255), 1,
                                        cv2.LINE_AA)
                            xml_content += f"""<object>
                                                    <name>{names_label}</name>
                                                    <pose>Unspecified</pose>
                                                    <truncated>0</truncated>
                                                    <difficult>0</difficult>
                                                    <bndbox>
                                                        <xmin>{x}</xmin>
                                                        <ymin>{y}</ymin>
                                                        <xmax>{w}</xmax>
                                                        <ymax>{h}</ymax>
                                                    </bndbox>
                                                </object>
                                                """

                            ymin, xmin, ymax, xmax, image_w, image_h = [y, x,
                                                                        h, w,
                                                                        frame.shape[1],
                                                                        frame.shape[0]]
                            (x_iw_ratio, y_ih_ratio) = (
                                ((xmin + xmax) * 0.5) / image_w, ((ymin + ymax) * 0.5) / image_h)
                            tw_iw_ratio = (xmax - xmin) * 1. / image_w
                            th_ih_ratio = (ymax - ymin) * 1. / image_h
                            YOLO_Format += f"""{results.pandas().xyxy[0]["class"][resultI]} {round(x_iw_ratio, 6)} {round(y_ih_ratio, 6)} {round(tw_iw_ratio, 6)} {round(th_ih_ratio, 6)}\n"""

                    xml_content += "</annotation>"
                    save_path = f"{settings.MEDIA_ROOT[0]}{imgpath[6:-7]}labels/".replace('\\','/')
                    save_path_xml = f"{settings.MEDIA_ROOT[0]}{imgpath[6:-7]}labels_xml/".replace('\\','/')

                    # print(save_path)
                    # print(save_path_xml)
                    if not Path(save_path).exists():
                        Path(save_path).mkdir(parents=True, exist_ok=True)
                    if not Path(save_path_xml).exists():
                        Path(save_path_xml).mkdir(parents=True, exist_ok=True)


                    save_paths1 = os.path.join(save_path_xml, f"{img.split('.')[0]}.xml").replace("\\", "/")
                    # print(save_paths1)
                    with open(save_paths1, 'wt') as f:
                        f.write(xml_content)
                    #
                    save_paths2 = os.path.join(save_path, f"{img.split('.')[0]}.txt").replace("\\","/")
                    # print(save_paths2)
                    with open(save_paths2, 'wt') as f:
                        f.write(YOLO_Format)  # return HttpResponse(f'{file_path}')
                    classfile = os.path.join(save_path[:-7], f"classes.txt").replace("\\","/")
                    classtexts = ""
                    for cls in range(len(label_class)):
                        # print(sorted(label_class.items())[cls][1])#列出標註物的排序
                        classtexts += f"{sorted(label_class.items())[cls][1]}\n"
                    with open(classfile, 'wt') as f:
                        f.write(classtexts)
                else:
                    print("NO Labeling")

                # print("第",img,"張圖片 ================================================")
                # print(YOLO_Format)
                # print(xml_content)
                # print(label_class)

            return JsonResponse({'status': "成功"})

#影像標註框
class Label_List(View):

    def get(self,request):
        print(dir(request))
        return HttpResponse('test')
    @csrf_exempt
    #儲存標註框
    def addtest(request):
        if request.method != 'POST':
            # 判斷當前用戶是否已登入
            if not request.user.is_authenticated:
                return render(request, 'please_login.html')
            else:
                return HttpResponse('我是post请求')
        #接收post
        dir_name = "userdata"
        user_name = request.user
        file_path = request.POST.get("filepath")
        imgwidth = request.POST.get("imgwidth")
        imgheight = request.POST.get("imgheight")
        ifpass = request.POST.get("ifpass")
        label_list = request.POST.getlist("label[]")
        label_list_classname = request.POST.getlist("labellist[]")

        # print(file_path)
        # print(imgwidth)
        # print(imgheight)
        # print(label_list_classname)

        labe_list_inPython = []
        coun_list = 0
        little_matrix = []


        #處理所有label的標籤名、xmin,ymin,xmax,ymax,h,w
        for i in label_list:
            if coun_list < 6:
                little_matrix.append(i)
                coun_list += 1
            elif coun_list == 6:
                little_matrix.append(i)
                labe_list_inPython.append(little_matrix)
                little_matrix = []
                coun_list = 0
        # print(labe_list_inPython)

        file_path_slash = file_path.replace("/","\\")
        YOLO_Format = ""
        xml_content = f"""
        <annotation>
            <folder>{file_path.split('/')[4]}</folder>
            <filename>{file_path.split('/')[5]}</filename>
            <path>{file_path_slash}</path>
            <source>
                <database>Unknown</database>
            </source>
            <size>
                <width>{int(round(float(imgwidth),1))}</width>
                <height>{int(round(float(imgheight),1))}</height>
                <depth>3</depth>
            </size>
            <segmented>0</segmented>
        """
        print(labe_list_inPython)
        if labe_list_inPython != []:
            for labels in labe_list_inPython:
                xml_content += f"""<object>
                    <name>{labels[0]}</name>
                    <pose>Unspecified</pose>
                    <truncated>0</truncated>
                    <difficult>0</difficult>
                    <bndbox>
                        <xmin>{labels[1]}</xmin>
                        <ymin>{labels[2]}</ymin>
                        <xmax>{labels[3]}</xmax>
                        <ymax>{labels[4]}</ymax>
                    </bndbox>
                </object>
                """
            # for a in range(0,10):
            #     print("=" * a)
            # print(round(float(imgwidth),1),round(float(imgheight),1))
            for li in range(len(label_list_classname)):
                if labels[0] == label_list_classname[li]:
                    ymin, xmin, ymax, xmax, image_w, image_h = [float(labels[2]),float(labels[1]),float(labels[4]),float(labels[3]),int(round(float(imgwidth),1)),int(round(float(imgheight),1))]
                    (x_iw_ratio, y_ih_ratio) = ( ( (xmin + xmax) * 0.5 ) / image_w, ((ymin + ymax) * 0.5 ) / image_h)
                    tw_iw_ratio = (xmax - xmin) * 1. / image_w
                    th_ih_ratio = (ymax - ymin) * 1. / image_h
                    YOLO_Format +=f"""{li} {round(x_iw_ratio,6)} {round(y_ih_ratio,6)} {round(tw_iw_ratio,6)} {round(th_ih_ratio,6)}\n"""

        xml_content += "</annotation>"


        # print("XML : ")
        # print(xml_content)
        # print("YOLO Format : ")
        # print(YOLO_Format)
        save_path = f"{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{file_path.split('/')[3]}/labels/"
        save_path_xml = f"{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{file_path.split('/')[3]}/labels_xml/"
        print(""*100)
        print(save_path)
        print(save_path_xml)
        print(ifpass)
        print(""*100)

        #創建資料夾
        if labe_list_inPython != []:#防止被寫入空值
            if not Path(save_path).exists():
                Path(save_path).mkdir(parents=True, exist_ok=True)
            if not Path(save_path_xml).exists():
                Path(save_path_xml).mkdir(parents=True, exist_ok=True)
            save_paths1 = os.path.join(save_path_xml,f"{file_path.split('/')[5].split('.')[0]}.xml").replace("\\","/")
            print(save_paths1)
            with open(save_paths1,'wt') as f:
                f.write(xml_content)
            save_paths2 = os.path.join(save_path,f"{file_path.split('/')[5].split('.')[0]}.txt").replace("\\","/")
            with open(save_paths2,'wt') as f:
                f.write(YOLO_Format)
        elif ifpass == "1":
            if not Path(save_path).exists():
                Path(save_path).mkdir(parents=True, exist_ok=True)
            if not Path(save_path_xml).exists():
                Path(save_path_xml).mkdir(parents=True, exist_ok=True)
            save_paths1 = os.path.join(save_path_xml,f"{file_path.split('/')[5].split('.')[0]}.xml").replace("\\","/")
            print(save_paths1)
            with open(save_paths1,'wt') as f:
                f.write(xml_content)
            save_paths2 = os.path.join(save_path,f"{file_path.split('/')[5].split('.')[0]}.txt").replace("\\","/")
            with open(save_paths2,'wt') as f:
                f.write(YOLO_Format)        # return HttpResponse(f'{file_path}')
        return HttpResponse(f'OK')
    @csrf_exempt
    #讀取標註框
    def readtest(request):
        if request.method != 'POST':
            return HttpResponse('我是post请求')
        dir_name = "userdata"
        user_name = request.user
        file_up = request.POST.get("filepath")
        base_path = settings.MEDIA_ROOT[0]
        label_path = f"{file_up.split('/')[1]}/{user_name}/{file_up.split('/')[3]}/labels_xml/{file_up.split('/')[5].split('.')[0]}.xml"
        file_up = os.path.join(base_path,label_path).replace("\\","/")
        # tree = ET.parse(file_up)#中文路徑無法辨識
        with open(file_up, 'r', encoding='GBK') as file:
            tree = ET.parse(file)
        root = tree.getroot()
        print(file_up)


        lbl = []
        # 子節點與屬性
        for child in root:
            if(child.tag == "object"):
                # print(root.find("object").find("name").text)
                labn = child.find("name").text
                xmin = child.find("bndbox").find("xmin").text
                ymin = child.find("bndbox").find("ymin").text
                xmax = child.find("bndbox").find("xmax").text
                ymax = child.find("bndbox").find("ymax").text
                h = int(ymax)-int(ymin)
                w =  int(xmax) - int(xmin)
                lbl.append([labn,xmin,ymin,xmax,ymax,h,w])

        # print(lbl)
        for lb in lbl :
            print(lb)
        data = {
            'data':lbl,
        }
        return JsonResponse(data)

    @csrf_exempt
    #新增標籤進類別檔
    def add_class(request):
        if request.method != 'POST':
            return HttpResponse('我是post请求')
        dir_name = "userdata"
        base_path = settings.MEDIA_ROOT[0]
        user_name = request.user
        file_up = request.POST.get("filepath")
        tagname = request.POST.get("tags")
        label_path = f"{file_up.split('/')[1]}/{user_name}/{file_up.split('/')[3]}/classes.txt"
        file_up = os.path.join(base_path, label_path).replace("\\", "/")
        with open(file_up, 'a') as f:
            f.write(f'{tagname}\n')

        data = {
            'data': '123',
        }
        return JsonResponse(data)

    # return render(request, "login_ajax.html")
    def now(self):
        return str(int(time.time()))

class Model_Training(View):
        global menu_bar
        global decoded_str

        def get(self, request):
            if not request.user.is_authenticated:
                # return render(request, 'please_login.html')
                return HttpResponse("""
                                  <style>
                                  .square {

                              /* animation 參數設定 */
                              animation-name: MoveToRight;    /*動畫名稱，需與 keyframe 名稱對應*/
                              animation-duration: 2s;    /*動畫持續時間，單位為秒*/
                              animation-delay: 0s;    /*動畫延遲開始時間*/
                              animation-iteration-count: infinite;    /*動畫次數，infinite 為無限次*/
                          }

                          @keyframes MoveToRight {
                              from { top: 0%;opacity:0;  }
                              to { top: 5%;opacity:1; }
                          }
                                  </style>
                                 <div class="square" style="padding:20px;position:absolute;top:40%;width:80%;left:10%;
                                 border-radius:15px;
                                 background-color:#FFB5B5;
                                 color:#FF2D2D;
                                 font-size:5vmin;text-align:center;">
                                   無權操作，請先登入<br/>
                                  </div>
                                  <script>setTimeout("location.href='login'",2000);</script>""")

            dir_name = "userdata"
            user_name = request.user
            name = request.GET.get('filepath', '')
            model_path = 'usermodel/{0}/{1}'.format(user_name, name)
            model_check = 0
            # 找尋filepath目錄位置的照片
            # 此為提供給該帳號用戶，瀏覽選擇已建立過的檔案照片
            if (name != ""):  # 若當前路徑有指定目錄名稱
                save_path = f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{name}/images/'
                dirs = []
                user_dirs = []
                try:
                    files = os.listdir(save_path)
                    files.sort(key=lambda x: int(x[:-4]))
                    tags = []
                    try:
                        with open(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{name}/classes.txt', 'r') as f:
                            for text in f.read().split('\n'):
                                if text != "\n" and text != "":
                                    tags.append(text)
                    except:
                        with open(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{name}/classes.txt', 'w') as f:
                            f.write('')

                    for fi in files:
                        dirs.append(f"static/{dir_name}/{user_name}/{name}/images/{fi}".replace("\\", "/"))



                    sorted_folders = sorted(os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'), key=extract_datetime, reverse=True)

                    for fidir in sorted_folders:
                        print(fidir)
                        # 分割檔案名稱並重新組裝後賦值到瀏覽器
                        y = fidir.split('-')[0].split('_')[0][0:4]
                        m = fidir.split('-')[0].split('_')[0][4:6]
                        d = fidir.split('-')[0].split('_')[0][6:8]
                        h = fidir.split('-')[0].split('_')[1][0:2]
                        min = fidir.split('-')[0].split('_')[1][2:4]
                        s = fidir.split('-')[0].split('_')[1][4:6]
                        user_dirs.append([fidir, f'{y}-{m}-{d} {h}:{min}:{s}'])
                    # print(user_dirs)

                    if not Path(f"{settings.MEDIA_ROOT[0]}/{model_path}").exists():
                        print("創建", f"{settings.MEDIA_ROOT[0]}/{model_path}")
                        Path(f"{settings.MEDIA_ROOT[0]}/{model_path}").mkdir(parents=True, exist_ok=True)
                    else:
                        print("HERE")

                        for fidir in os.listdir(f"{settings.MEDIA_ROOT[0]}/{model_path}"):
                            if os.path.isdir(os.path.join(f"{settings.MEDIA_ROOT[0]}/{model_path}", fidir)):
                                print(fidir)
                                model_check = 1#若發現資料夾，表示已執行過訓練
                            else:
                                print("不是資料夾")
                        # print(len(dirs))
                    return render(request, 'training.html',
                                  {'dirs': dirs, 'user': user_name, 'obj_name': name.split('-')[1],
                                   'file_dir': user_dirs, 'tags': tags, 'menu': menu_bar,'check_model':model_check,'dirslen':len(dirs)})
                except:
                    print(traceback.format_exc())

                    # return render(request, 'index.html', {'user': user_name, 'menu': menu_bar})
                    return render(request, 'training.html',{'user': user_name,'menu':menu_bar})
            else:
                user_dirs = []

                # 如果為初次登入使用者，為其建立資料夾
                if not Path(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}').exists():
                    Path(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}').mkdir(parents=True, exist_ok=True)

                sorted_folders = sorted(os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'),
                                        key=extract_datetime, reverse=True)

                for fidir in sorted_folders:
                    y = fidir.split('-')[0].split('_')[0][0:4]
                    m = fidir.split('-')[0].split('_')[0][4:6]
                    d = fidir.split('-')[0].split('_')[0][6:8]
                    h = fidir.split('-')[0].split('_')[1][0:2]
                    min = fidir.split('-')[0].split('_')[1][2:4]
                    s = fidir.split('-')[0].split('_')[1][4:6]
                    user_dirs.append([fidir, f'{y}-{m}-{d} {h}:{min}:{s}'])

                return render(request, 'training.html', {'user': user_name, 'file_dir': user_dirs, 'menu': menu_bar,'dirslen':""})
            # return render(request, 'training.html', {'user': user_name, 'menu': menu_bar})
        def post(self, request):

            filepath = request.POST.get('filepath', '')
            user = request.user
            batch = request.POST.get('batch')
            epoch = request.POST.get('epoch')
            ImageSize = request.POST.get('ImageSize')
            model = request.POST.get('model')
            save_path = 'usermodel/{0}/{1}'.format(user,filepath)
            data_path = 'userdata/{0}'.format(user)
            nc = 1
            if not Path(f"{settings.MEDIA_ROOT[0]}/{save_path}").exists():
                print("創建",f"{settings.MEDIA_ROOT[0]}/{save_path}")
                Path(f"{settings.MEDIA_ROOT[0]}/{save_path}").mkdir(parents=True, exist_ok=True)
            # with open(file_up, 'r', encoding='GBK') as file:

            lab_ptr = []#確認陣列
            unlabel = ""
            try:
                image_file = [line.decode("utf-8") for line in os.listdir(f"{settings.MEDIA_ROOT[0]}/{data_path}/{filepath}/labels".encode("utf-8"))]
                #確認圖片數量
                check_img = len(os.listdir(f"{settings.MEDIA_ROOT[0]}/{data_path}/{filepath}/images"))
                #確認有哪幾張尚未被標註，若發現未標註圖片會記錄到 lab_ptr 陣列
                for imgsfile in range(len(os.listdir(f"{settings.MEDIA_ROOT[0]}/{data_path}/{filepath}/images"))):
                    check = 0
                    #label數量
                    for label_file in image_file:
                        if label_file.split('.')[0] == str(imgsfile):
                            check = 1
                    if check == 0:
                        lab_ptr.append(f"{imgsfile}.jpg")
            except:
                print(traceback.print_exc())

            if lab_ptr != []:
                print("No finish yet")
                for lab in lab_ptr:
                    unlabel += lab+'<br/>'
                # return JsonResponse({'status':f'尚未進行標註，無法執行訓練'})
            elif len(lab_ptr) == check_img:#若未標註數量與圖片數量相同，代表皆未標註
                print("Not Finish at all")
                return JsonResponse({'status':f'尚未進行標註，無法執行訓練'})

                # return HttpResponse(f"尚未進行標註，無法執行訓練")

            #建立training.yaml需要的classname
            labelname = "["
            with open(f"{settings.MEDIA_ROOT[0]}/{data_path}/{filepath}/classes.txt", "r") as f:
                lines = [line.strip() for line in f]
                nc = len(lines)
                for i in lines:
                    labelname += f"'{i}',"
                labelname = labelname[:-1]+"]"

            # print(labelname)

            data = f"path: ../{data_path}\ntrain: {filepath}/images\nval: {filepath}/images\nnc: {nc}\nnames: {labelname}"
            #開始訓練
            try:
                with open(f'{settings.MEDIA_ROOT[0]}/{save_path}/training_data.yaml', "w") as f:
                    f.write(data)

                training_Yolov5(imagesize=ImageSize, batch=batch, epoch=epoch, model=model,
                                data=f"static/{save_path}/training_data.yaml", savepath=f"static/{save_path}", name=filepath.split('-')[1],username=user)
            except:
                print("wrong")
                print(traceback.print_exc())
                return HttpResponse("Fail")

            filtered_books = Training_cycle.objects.filter(userid=request.user.id)
            finish_times = datetime.strptime(str(filtered_books[0].finish_time)[:-6],"%Y-%m-%d %H:%M:%S")
            return JsonResponse({'status': 'success','finish':finish_times,'unlabel':unlabel})


        def get_training_progress(request):
            global decoded_str
            # 從保存的 process 對象中獲取訓練進度
            if not request.user.is_authenticated:
                return HttpResponse("No authenticated")

            progress = ""
            finish_times = ""
            try:
                filtered_books = Training_cycle.objects.filter(userid=request.user.id)
                print(filtered_books[0].progress)

                finish_times = datetime.strptime(str(filtered_books[0].finish_time)[:-6],"%Y-%m-%d %H:%M:%S")

                print(finish_times.timestamp())
                print(datetime.now().timestamp())
                if (datetime.now().timestamp()-finish_times.timestamp()) > 10:

                    progress = filtered_books[0].progress if filtered_books[0].progress!= "100%" else "0%"  # 完成度
                else:
                    progress = filtered_books[0].progress  # 完成度
            except:
                progress = "Waitting...."
                # cuser = Training_cycle.objects.create(userid_id=request.user.id)
                # cuser = Training_cycle.objects.create(progress="0%")
                # cuser.save()
            # progress = decoded_str
            print("進度 : ",progress)
            # struct_time = time.strptime(str(filtered_books[0].finish_time), "%Y-%m-%d %H:%M:%S")  # 轉成時間元組

            return JsonResponse({'status': progress,'finish':finish_times})

class Data_Augmentation(View):

    def get(self, request):

        if not request.user.is_authenticated:
            # return render(request, 'please_login.html')
            return HttpResponse("""
                              <style>
                              .square {

                          /* animation 參數設定 */
                          animation-name: MoveToRight;    /*動畫名稱，需與 keyframe 名稱對應*/
                          animation-duration: 2s;    /*動畫持續時間，單位為秒*/
                          animation-delay: 0s;    /*動畫延遲開始時間*/
                          animation-iteration-count: infinite;    /*動畫次數，infinite 為無限次*/
                      }

                      @keyframes MoveToRight {
                          from { top: 0%;opacity:0;  }
                          to { top: 5%;opacity:1; }
                      }
                              </style>
                             <div class="square" style="padding:20px;position:absolute;top:40%;width:80%;left:10%;
                             border-radius:15px;
                             background-color:#FFB5B5;
                             color:#FF2D2D;
                             font-size:5vmin;text-align:center;">
                               無權操作，請先登入<br/>
                              </div>
                              <script>setTimeout("location.href='login'",2000);</script>""")

        dir_name = "userdata_Augmentation"
        user_name = request.user

        name = request.GET.get('filepath', '')

        # 找尋filepath目錄位置的照片
        # 此為提供給該帳號用戶，瀏覽選擇以建立過的檔案照片
        if (name != ""):  # 若當前路徑有指定目錄名稱

            save_path = f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{name}/images/'
            dirs = []
            user_dirs = []
            try:
                files = os.listdir(save_path)
                files.sort(key=lambda x: int(x[:-4]))
                tags = []
                try:
                    with open(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{name}/classes.txt', 'r') as f:
                        for text in f.read().split('\n'):
                            if text != "\n" and text != "":
                                tags.append(text)
                except:
                    with open(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{name}/classes.txt', 'w') as f:
                        f.write('')

                for fi in files:
                    dirs.append(f"static/{dir_name}/{user_name}/{name}/images/{fi}".replace("\\", "/"))
                sorted_folders = sorted(os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'),
                                        key=extract_datetime, reverse=True)

                for fidir in sorted_folders:
                    # 分割檔案名稱並重新組裝後賦值到瀏覽器
                    y = fidir.split('-')[0].split('_')[0][0:4]
                    m = fidir.split('-')[0].split('_')[0][4:6]
                    d = fidir.split('-')[0].split('_')[0][6:8]
                    h = fidir.split('-')[0].split('_')[1][0:2]
                    min = fidir.split('-')[0].split('_')[1][2:4]
                    s = fidir.split('-')[0].split('_')[1][4:6]
                    user_dirs.append([fidir, f'{y}-{m}-{d} {h}:{min}:{s}'])
                return render(request, 'Data_Augmentation.html',
                              {'dirs': dirs, 'user': user_name, 'obj_name': name.split('-')[1], 'file_dir': user_dirs,
                               'tags': tags, 'menu': menu_bar})
            except:
                print(traceback.format_exc())

                return render(request, 'Data_Augmentation.html', {'user': user_name, 'menu': menu_bar})
        else:
            user_dirs = []
            # 如果為初次登入使用者，為其建立影像增強資料夾
            if not Path(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}').exists():
                Path(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}').mkdir(parents=True, exist_ok=True)

            sorted_folders = sorted(os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'),
                                    key=extract_datetime, reverse=True)
            for fidir in sorted_folders:
                y = fidir.split('-')[0].split('_')[0][0:4]
                m = fidir.split('-')[0].split('_')[0][4:6]
                d = fidir.split('-')[0].split('_')[0][6:8]
                h = fidir.split('-')[0].split('_')[1][0:2]
                min = fidir.split('-')[0].split('_')[1][2:4]
                s = fidir.split('-')[0].split('_')[1][4:6]
                user_dirs.append([fidir, f'{y}-{m}-{d} {h}:{min}:{s}'])
            return render(request, 'Data_Augmentation.html', {'user': user_name, 'file_dir': user_dirs, 'menu': menu_bar})
    # def get(self, request):
    #     return render(request, 'Data_Augmentation.html',{'menu':menu_bar})

    @csrf_exempt
    # 圖片上傳,上傳
    def post(self, request):
        # print("POST的")
        if not request.user.is_authenticated:
            return render(request, 'please_login.html')
        dir_name = "userdata_Augmentation"
        file_name = request.POST.get("dataset")
        user_name = request.user
        now = (time.strftime("%Y%m%d_%H%M%S"))
        file_up = request.FILES.getlist("file[]")  # ['filename']
        # file_up = request.FILES.get("file[]")#['filename']
        print(file_up)
        save_path = f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{now}-{file_name}/images/'
        # print("123",settings.MEDIA_ROOT[0])
        # 創建資料夾
        if not Path(save_path).exists():
            Path(save_path).mkdir(parents=True, exist_ok=True)

        # with open(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{now}-{file_name}/classes.txt', 'w') as f:
        #     f.write('')
        count_img = 0
        for files in file_up:
            save_paths = os.path.join(save_path, f'{count_img}.jpg').replace("\\", "/")
            with open(save_paths, 'wb') as f:
                for content in files.chunks():
                    f.write(content)

            count_img += 1
            # print(files.chunks())
            # Article.objects.create(thunmbnial=files)
            # 若檔案超過1000px x 1000px 則 resize
            try:
                #根據手機exif資訊調整

                img = Image.open(save_paths)
                img = exif_transpose(img)
                img = img.convert("RGB")
                dd = img.size



                if 4000000 > dd[0] * dd[1] > 999000:
                    cropped = img.resize((int(dd[0] * 0.4), int(dd[1] * 0.4)))
                    cropped.save(save_paths)
                elif dd[0] * dd[1] > 4000001:
                    cropped = img.resize((int(dd[0] * 0.2), int(dd[1] * 0.2)))
                    cropped.save(save_paths)
                # img = cv2.imread(save_paths)
                # dd = img.shape[:2]
                # if 4000000 > dd[0] * dd[1] > 999000:
                #     cropped = cv2.resize(img, (int(dd[1] * 0.5), int(dd[0] * 0.5)), interpolation=cv2.INTER_AREA)
                #     cv2.imwrite(save_paths)
                # elif dd[0] * dd[1] > 4000001:
                #     cropped = cv2.resize(img, (int(dd[1] * 0.5), int(dd[0] * 0.5)), interpolation=cv2.INTER_AREA)
                #     cv2.imwrite(save_paths)
            except:
                print(traceback.format_exc())

        dirs = []
        files = os.listdir(save_path)
        files.sort(key=lambda x: int(x[:-4]))
        for fi in files:
            dirs.append(f"static/{dir_name}/{user_name}/{now}-{file_name}/images/{fi}".replace("\\", "/"))

        user_dirs = []
        for fidir in os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'):
            user_dirs.append([fidir, fidir])
        print(dirs)

        return render(request, 'Data_Augmentation.html',
                      {'dirs': dirs, "urlguide": f"{now}-{file_name}", 'obj_name': file_name, 'file_dir': user_dirs,
                       'tags': []})

    @csrf_exempt
    # 圖片上傳,上傳
    def augment(request):

        if request.method == 'POST':
            filepath = request.GET.get('filepath', '')
            user = request.user
            dir_name = "userdata_Augmentation"
            #無資料夾
            if filepath == "":
                return HttpResponse("""
                                            <style>
                                            .square {
    
                                        /* animation 參數設定 */
                                        animation-name: MoveToRight;    /*動畫名稱，需與 keyframe 名稱對應*/
                                        animation-duration: 2s;    /*動畫持續時間，單位為秒*/
                                        animation-delay: 0s;    /*動畫延遲開始時間*/
                                        animation-iteration-count: infinite;    /*動畫次數，infinite 為無限次*/
                                    }
    
                                    @keyframes MoveToRight {
                                        from { top: 0%;opacity:0;  }
                                        to { top: 5%;opacity:1; }
                                    }
                                            </style>
                                           <div class="square" style="padding:20px;position:absolute;top:40%;width:80%;left:10%;
                                           border-radius:15px;
                                           background-color:#FFB5B5;
                                           color:#FF2D2D;
                                           font-size;5vmin;text-align:center;">
                                             無資料，請選擇圖片資料夾或上傳圖片<br/>
                                            </div>
                                            <script>setTimeout("location.href='/Augmentation'",2000);</script>""")

            if not request.user.is_authenticated:
                # return render(request, 'please_login.html')
                return HttpResponse("""
                                  <style>
                                  .square {
    
                              /* animation 參數設定 */
                              animation-name: MoveToRight;    /*動畫名稱，需與 keyframe 名稱對應*/
                              animation-duration: 2s;    /*動畫持續時間，單位為秒*/
                              animation-delay: 0s;    /*動畫延遲開始時間*/
                              animation-iteration-count: infinite;    /*動畫次數，infinite 為無限次*/
                          }
    
                          @keyframes MoveToRight {
                              from { top: 0%;opacity:0;  }
                              to { top: 5%;opacity:1; }
                          }
                                  </style>
                                 <div class="square" style="padding:20px;position:absolute;top:40%;width:80%;left:10%;
                                 border-radius:15px;
                                 background-color:#FFB5B5;
                                 color:#FF2D2D;
                                 font-size:5vmin;text-align:center;">
                                   無權操作，請先登入<br/>
                                  </div>
                                  <script>setTimeout("location.href='login'",2000);</script>""")
            print(filepath)
            print(user)
            #checkbox元素，若未勾選為None，有則回應空字串
            flip = request.POST.get("flip")
            degree = request.POST.get("degree_val")
            scales = request.POST.get("scale_val")
            root_path = settings.MEDIA_ROOT[0]
            # pack_data_augmentation = [root_path,filepath,dir_name,flip,degree,scales,user]
            # if flip != None:
            #     print("不是None",flip)
            print("flip : ",flip)
            print("degree : ",degree)
            print("scale : ",scales)
            print("name : ",filepath)
            scales = int(scales)/10 if scales != None else 1
            degree = int(degree) if degree != None else 0
            now = time.strftime("%Y%m%d_%H%M%S")
            filename_path = f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user}/{filepath}/images/'
            save_path = f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user}/{filepath}/augmentation/{now}/'
            # 創建資料夾
            if not Path(save_path).exists():
                Path(save_path).mkdir(parents=True, exist_ok=True)
            for i in os.listdir(filename_path):
                img2 = cv2.imdecode(np.fromfile(filename_path+i, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                if flip == "true":
                    for a in range(degree * -1, degree + 5, 5):
                        ang = a
                        frame = rotation(img2, angel=ang)  #
                        frame = cv2.flip(frame, 1)
                        if scales != 1:
                            frame = imgresize(frame, scale=scales)
                        name = f"{save_path}/d{a}_s{int(scales*10)}_flip_{str(i.split('.')[0]).zfill(4)}.jpg"
                        cv2.imencode('.jpg', frame)[1].tofile(name)
                for a in range(degree*-1, degree+5, 5):
                    ang = a
                    frame = rotation(img2, angel=ang)
                    if scales != 1:
                        frame = imgresize(frame,scale=scales)
                    name = f"{save_path}/d{a}_s{int(scales*10)}_{str(i.split('.')[0]).zfill(4)}.jpg"
                    cv2.imencode('.jpg', frame)[1].tofile(name)
            # return HttpResponse("OK")
            dirs = []
            files = os.listdir(save_path)
            # files.sort(key=lambda x: int(x[:-4]))
            for fi in files:
                dirs.append(f"static/{dir_name}/{user}/{filepath}/augmentation/{now}/{fi}".replace("\\", "/"))
            json_data = d.dumps(dirs)

            return HttpResponse(json_data, content_type='application/json')
        else:
            return HttpResponse("method forbidden!")

    @csrf_exempt
    def image_label(request):
        if not request.user.is_authenticated:
            return render(request, 'please_login.html')

        if request.method == 'POST':
            json_data = request.body.decode('utf-8')
            data = d.loads(json_data)
            dir_name = "userdata"
            file_name = data['filename']
            user_name = request.user
            now = (time.strftime("%Y%m%d_%H%M%S"))
            # filelisst = request.POST.get('key2')
            # flip = request.POST.get("flip")

            print(data['filelist'])
            save_path = f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{now}-{file_name}/images/'
            # 創建資料夾
            if not Path(save_path).exists():
                Path(save_path).mkdir(parents=True, exist_ok=True)

            with open(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{now}-{file_name}/classes.txt', 'w') as f:
                f.write('')
            for i in range(len(data['filelist'])):
                print(i)
                img = cv2.imread(data['filelist'][i])
                cv2.imwrite(f'{save_path}{i}.jpg',img)
            # print(data[0])
            # print(filelisst)
            dirs = []
            files = os.listdir(save_path)
            files.sort(key=lambda x: int(x[:-4]))
            for fi in files:
                dirs.append(f"static/{dir_name}/{user_name}/{now}-{file_name}/images/{fi}".replace("\\", "/"))

            user_dirs = []
            for fidir in os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'):
                user_dirs.append([fidir, fidir])
            print(dirs)

            return HttpResponse(f'{now}-{file_name}')
        # response = StreamingHttpResponse(generate_frames(), content_type="image/jpeg",mimetype='multipart/x-mixed-replace; boundary=frame')
        # return render(request, 'index.html')
        return render(request, 'index.html')

class Model_Examine(View):
    global menu_bar
    global decoded_str

    def get(self, request):
        if not request.user.is_authenticated:
            # return render(request, 'please_login.html')
            return HttpResponse("""
                              <style>
                              .square {

                          /* animation 參數設定 */
                          animation-name: MoveToRight;    /*動畫名稱，需與 keyframe 名稱對應*/
                          animation-duration: 2s;    /*動畫持續時間，單位為秒*/
                          animation-delay: 0s;    /*動畫延遲開始時間*/
                          animation-iteration-count: infinite;    /*動畫次數，infinite 為無限次*/
                      }

                      @keyframes MoveToRight {
                          from { top: 0%;opacity:0;  }
                          to { top: 5%;opacity:1; }
                      }
                              </style>
                             <div class="square" style="padding:20px;position:absolute;top:40%;width:80%;left:10%;
                             border-radius:15px;
                             background-color:#FFB5B5;
                             color:#FF2D2D;
                             font-size:5vmin;text-align:center;">
                               無權操作，請先登入<br/>
                              </div>
                              <script>setTimeout("location.href='login'",2000);</script>""")

        dir_name = "usermodel"
        user_name = request.user
        name = request.GET.get('filepath', '')
        model_path = 'usermodel/{0}/{1}'.format(user_name, name)
        model_check = 0
        # 找尋filepath目錄位置的照片
        # 此為提供給該帳號用戶，瀏覽選擇已建立過的檔案照片
        if (name != ""):  # 若當前路徑有指定目錄名稱
            save_path = f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}/{name}/'
            print(save_path)
            dirs = []
            user_dirs = []
            try:
                files = os.listdir(save_path)
                #"訓練資料結果"
                subdirectories = [f for f in files if os.path.isdir(os.path.join(save_path, f))]
                sorted_subdirectories = sorted(subdirectories,
                                               key=lambda f: os.path.getctime(os.path.join(save_path, f)), reverse=True)
                print("訓練資料 : ",sorted_subdirectories)

                for fi in sorted_subdirectories:
                    dirs.append(f"static/{dir_name}/{user_name}/{name}/{fi}".replace("\\", "/"))

                sorted_folders = sorted(os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'),
                                        key=extract_datetime, reverse=True)

                for fidir in sorted_folders:
                    print(fidir)
                    # 分割檔案名稱並重新組裝後賦值到瀏覽器
                    y = fidir.split('-')[0].split('_')[0][0:4]
                    m = fidir.split('-')[0].split('_')[0][4:6]
                    d = fidir.split('-')[0].split('_')[0][6:8]
                    h = fidir.split('-')[0].split('_')[1][0:2]
                    min = fidir.split('-')[0].split('_')[1][2:4]
                    s = fidir.split('-')[0].split('_')[1][4:6]
                    user_dirs.append([fidir, f'{y}-{m}-{d} {h}:{min}:{s}'])

                return render(request, 'model.html',
                              {'dirs': dirs, 'user': user_name, 'obj_name': name.split('-')[1],
                               'file_dir': user_dirs, 'menu': menu_bar})
            except:
                print(traceback.format_exc())

                return render(request, 'training.html', {'user': user_name, 'menu': menu_bar})
        else:
            user_dirs = []

            # 如果為初次登入使用者，為其建立資料夾
            if not Path(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}').exists():
                Path(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}').mkdir(parents=True, exist_ok=True)

            sorted_folders = sorted(os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'),
                                    key=extract_datetime, reverse=True)
            print(sorted_folders)
            for fidir in sorted_folders:
                y = fidir.split('-')[0].split('_')[0][0:4]
                m = fidir.split('-')[0].split('_')[0][4:6]
                d = fidir.split('-')[0].split('_')[0][6:8]
                h = fidir.split('-')[0].split('_')[1][0:2]
                min = fidir.split('-')[0].split('_')[1][2:4]
                s = fidir.split('-')[0].split('_')[1][4:6]
                user_dirs.append([fidir, f'{y}-{m}-{d} {h}:{min}:{s}'])
            return render(request, 'model.html', {'user': user_name, 'file_dir': user_dirs, 'menu': menu_bar})
        # return render(request, 'training.html', {'user': user_name, 'menu': menu_bar})

    def post(self, request):
        import pandas as pd

        filepath = request.POST.get('filepath', '')
        modelpath = request.POST.get('modelpath', '')
        print(modelpath)
        user = request.user
        save_path = 'usermodel/{0}/{1}'.format(user, filepath)
        data_path = 'userdata/{0}'.format(user)
        modeldir = f"{settings.MEDIA_ROOT[0]}/{modelpath[7:]}"

        epoch = ["0"]
        precision = ["0"]
        mAP_05 = ["0"]
        mAP_0595 = ["0"]
        training_loss = ["0"]
        dataframe_in_table = []#訓練結果csv
        vali_label = ""#驗證標註結果路徑
        vali_pred = ""#驗證測試結果路徑
        ckeck_csv = 0
        ckeck_label = 0
        ckeck_pred = 0
        for result in os.listdir(modeldir):
            if os.path.isfile(os.path.join(modeldir,result)):
                if result.split('.')[1] == "csv":
                    ckeck_csv = 1
                    selected_cols = [0, 1, 4, 5, 6, 7]
                    df = pd.read_csv(os.path.join(modeldir,result), usecols=selected_cols)
                    for i in df.values.tolist():
                        dataframe_in_table.append({'epcoh':int(i[0]),
                                                   'loss':i[1],
                                                   'precision':i[2],
                                                   'recall':i[3],
                                                   'map05':i[4],
                                                   'map0595':i[5]})
                    epoch = df.iloc[:,0].tolist()
                    precision = df.iloc[:,2].tolist()
                    mAP_05 = df.iloc[:,4].tolist()
                    mAP_0595 = df.iloc[:,5].tolist()
                    training_loss = df.iloc[:,1].tolist()
                    # print()
                    # print(df.iloc[:,0].tolist())
                    # print(df.iloc[:,4].tolist())
                    # print("路徑", result)
                elif result.split('.')[1] == "jpg":
                    if result.split('.')[0] == "val_batch0_labels":
                        vali_label = modelpath+'/'+result
                        ckeck_label = 1
                    elif result.split('.')[0] == "val_batch0_pred":
                        vali_pred  = modelpath+'/'+result
                        ckeck_pred = 1
        if ckeck_csv == 0:#若無result.csv則將數值清空
            epoch = ["0"]
            precision = ["0"]
            mAP_05 = ["0"]
            mAP_0595 = ["0"]
            training_loss = ["0"]

        vali_label = vali_label if ckeck_label == 1 else ""
        vali_pred = vali_pred if ckeck_pred == 1 else ""


        return JsonResponse({'status': 'success', 'finish': save_path,
                             'epoch':epoch,
                             'precision':precision,
                             'mAP_0.5':mAP_05,
                             'mAP_0.5:0.95':mAP_0595,
                             'training_loss':training_loss,
                             'datatable':dataframe_in_table,
                             'vali_label':vali_label,
                             'vali_pred' :vali_pred})
#旋轉圖片
def rotation(src, angel=0, scale=1):
    h, w = src.shape[:2]
    x = int((w - 1) / 2)
    y = int((h - 1) / 2)

    m = cv2.getRotationMatrix2D((x, y), angel, scale)
    img = cv2.warpAffine(src, m, (w, h))
    return img
#縮放圖片
def imgresize(src,w=None,h=None,scale=1):
    if w is None or h is None:
        h,w = src.shape[:2]
        w = int(w*scale)
        h = int(h*scale)
    img = cv2.resize(src,(w,h),interpolation=cv2.INTER_LINEAR)
    return img

#yolov5訓練指令
def training_Yolov5(imagesize=416,batch=5,epoch=10,model="yolov5s",data="static/yolov5/dataset_kumquat_1.yaml",savepath='runs/train',name='exp',username=""):
    # 定义要执行的命令
    command = f"python static/yolov5/train.py " \
              f"--img {imagesize} " \
              f"--batch {batch} " \
              f"--epochs {epoch} " \
              f"--data {data} " \
              f"--cfg static/yolov5/models/{model}.yaml " \
              f"--weights static/yolov5/{model}.pt " \
              f"--device 0 " \
              f"--project {savepath} " \
              f"--name {name} " \
              f"--username {username}"
    print(command)
    os.system(command)

#資料夾排序
def extract_datetime(folder_name):
    # 設定資料夾名稱的格式為 'YYYYMMDD_HHMMSS'
    # 例如 '20230723_150202'
    date_str, time_str = folder_name.split('-')[0].split('_')
    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])
    hour = int(time_str[:2])
    minute = int(time_str[2:4])
    second = int(time_str[4:6])
    return (year, month, day, hour, minute, second)

#依據相片EXIF資訊修正方位
def exif_transpose(img):
    if not img:
        return img

    exif_orientation_tag = 274

    # Check for EXIF data (only present on some files)
    if hasattr(img, "_getexif") and isinstance(img._getexif(),
                                               dict) and exif_orientation_tag in img._getexif():
        exif_data = img._getexif()
        orientation = exif_data[exif_orientation_tag]

        # Handle EXIF Orientation
        if orientation == 1:
            # Normal image - nothing to do!
            pass
        elif orientation == 2:
            # Mirrored left to right
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            # Rotated 180 degrees
            img = img.rotate(180)
        elif orientation == 4:
            # Mirrored top to bottom
            img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 5:
            # Mirrored along top-left diagonal
            img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 6:
            # Rotated 90 degrees
            img = img.rotate(-90, expand=True)
        elif orientation == 7:
            # Mirrored along top-right diagonal
            img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 8:
            # Rotated 270 degrees
            img = img.rotate(90, expand=True)

    return img