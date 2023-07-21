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
                        <li><a class="dropdown-item" href="#!">模型檢視</a></li>
                        <li><a class="dropdown-item" href="training">模型訓練</a></li>
                        <li><hr class="dropdown-divider" /></li>
                        <li><a class="dropdown-item" href="logout">登出</a></li>
                    </ul>
                </li>
            </ul>
        </nav>

"""

decoded_str = "123"

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
                             font-size;5vmin;text-align:center;">
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

                for fidir in os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'):
                    #分割檔案名稱並重新組裝後賦值到瀏覽器
                    y = fidir.split('-')[0].split('_')[0][0:4]
                    m = fidir.split('-')[0].split('_')[0][4:6]
                    d = fidir.split('-')[0].split('_')[0][6:8]
                    h = fidir.split('-')[0].split('_')[1][0:2]
                    min = fidir.split('-')[0].split('_')[1][2:4]
                    s = fidir.split('-')[0].split('_')[1][4:6]
                    user_dirs.append([fidir,f'{y}-{m}-{d} {h}:{min}:{s}'])
                return render(request,'index.html',{'dirs':dirs,'user':user_name,'obj_name':name.split('-')[1],'file_dir':user_dirs,'tags':tags,'menu':menu_bar})
            except:
                print(traceback.format_exc())

                return render(request,'index.html',{'user':user_name,'menu':menu_bar})
        else:
            user_dirs = []

            #如果為初次登入使用者，為其建立資料夾
            if not Path(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}').exists():
                Path(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}').mkdir(parents=True, exist_ok=True)

            for fidir in os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'):
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
                img = img.convert("RGB")
                dd = img.size
                if 4000000 > dd[0]*dd[1] > 999000:
                    cropped = img.resize((int(dd[0]*0.5),int(dd[1]*0.5)))
                    cropped.save(save_paths)
                elif dd[0]*dd[1] > 4000001:
                    cropped = img.resize((int(dd[0] * 0.3), int(dd[1] * 0.3)))
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

        print(lbl)
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
                                 font-size;5vmin;text-align:center;">
                                   無權操作，請先登入<br/>
                                  </div>
                                  <script>setTimeout("location.href='login'",2000);</script>""")

            dir_name = "userdata"
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

                    for fidir in os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'):
                        # 分割檔案名稱並重新組裝後賦值到瀏覽器
                        y = fidir.split('-')[0].split('_')[0][0:4]
                        m = fidir.split('-')[0].split('_')[0][4:6]
                        d = fidir.split('-')[0].split('_')[0][6:8]
                        h = fidir.split('-')[0].split('_')[1][0:2]
                        min = fidir.split('-')[0].split('_')[1][2:4]
                        s = fidir.split('-')[0].split('_')[1][4:6]
                        user_dirs.append([fidir, f'{y}-{m}-{d} {h}:{min}:{s}'])
                    return render(request, 'training.html',
                                  {'dirs': dirs, 'user': user_name, 'obj_name': name.split('-')[1],
                                   'file_dir': user_dirs, 'tags': tags, 'menu': menu_bar})
                except:
                    print(traceback.format_exc())

                    # return render(request, 'index.html', {'user': user_name, 'menu': menu_bar})
                    return render(request, 'training.html',{'user': user_name,'menu':menu_bar})
            else:
                user_dirs = []

                # 如果為初次登入使用者，為其建立資料夾
                if not Path(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}').exists():
                    Path(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}').mkdir(parents=True, exist_ok=True)

                for fidir in os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'):
                    y = fidir.split('-')[0].split('_')[0][0:4]
                    m = fidir.split('-')[0].split('_')[0][4:6]
                    d = fidir.split('-')[0].split('_')[0][6:8]
                    h = fidir.split('-')[0].split('_')[1][0:2]
                    min = fidir.split('-')[0].split('_')[1][2:4]
                    s = fidir.split('-')[0].split('_')[1][4:6]
                    user_dirs.append([fidir, f'{y}-{m}-{d} {h}:{min}:{s}'])
                return render(request, 'training.html', {'user': user_name, 'file_dir': user_dirs, 'menu': menu_bar})
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


            image_file = [line for line in os.listdir(f"{settings.MEDIA_ROOT[0]}/{data_path}/{filepath}/labels")]
            lab_ptr = []
            for imgsfile in range(len(os.listdir(f"{settings.MEDIA_ROOT[0]}/{data_path}/{filepath}/images"))):
                check = 0
                for label_file in image_file:
                    if label_file.split('.')[0] == str(imgsfile):
                        check = 1
                if check == 0:
                    lab_ptr.append(f"{imgsfile}.jpg")

            # if lab_ptr != []:
            #     print("No finish yet")
            #     return HttpResponse(f"{lab_ptr}尚未進行標註，無法執行訓練")



            labelname = "["
            with open(f"{settings.MEDIA_ROOT[0]}/{data_path}/{filepath}/classes.txt", "r") as f:
                lines = [line.strip() for line in f]
                nc = len(lines)
                for i in lines:
                    labelname += f"'{i}',"
                labelname = labelname[:-1]+"]"
            # print(labelname)
            if not Path(f"{settings.MEDIA_ROOT[0]}/{save_path}").exists():
                print("創建")
                Path(save_path).mkdir(parents=True, exist_ok=True)
            data = f"path: ../{data_path}\ntrain: {filepath}/images\nval: {filepath}/images\nnc: {nc}\nnames: {labelname}"

            try:
                with open(f'{settings.MEDIA_ROOT[0]}/{save_path}/training_data.yaml', "w") as f:
                    f.write(data)
                training_Yolov5(imagesize=ImageSize, batch=batch, epoch=epoch, model=model,
                                data=f"static/{save_path}/training_data.yaml", savepath=f"static/{save_path}", name=filepath.split('-')[1])
            #     # yaml.dump(data, f)
            except:
                return HttpResponse("Fail")


            return JsonResponse({'status': 'success'})

        def get_training_progress(request):
            global decoded_str
            # 從保存的 process 對象中獲取訓練進度
            progress = decoded_str
            print("測試",progress)

            return JsonResponse({'status': progress})

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
                             font-size;5vmin;text-align:center;">
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

                for fidir in os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'):
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

            for fidir in os.listdir(f'{settings.MEDIA_ROOT[0]}/{dir_name}/{user_name}'):
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
                img = Image.open(save_paths)
                img = img.convert("RGB")
                dd = img.size
                if 4000000 > dd[0] * dd[1] > 999000:
                    cropped = img.resize((int(dd[0] * 0.5), int(dd[1] * 0.5)))
                    cropped.save(save_paths)
                elif dd[0] * dd[1] > 4000001:
                    cropped = img.resize((int(dd[0] * 0.3), int(dd[1] * 0.3)))
                    cropped.save(save_paths)
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
                                 font-size;5vmin;text-align:center;">
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

def training_Yolov5(imagesize=416,batch=5,epoch=10,model="yolov5s",data="static/yolov5/dataset_kumquat_1.yaml",savepath='runs/train',name='exp'):
    import subprocess
    global decoded_str
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
              f"--name {name}"
    command = "ping 192.168.2.105"
    # print(command)
    # 执行命令，并捕获输出
    # output = subprocess.check_output(command, shell=True)
    # process = subprocess.Popen("your_command", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # 逐行讀取命令輸出
    for line in process.stdout:
        decoded_str = line.decode("big5", errors="ignore").strip()
        print(decoded_str)

    # print(k)
    # 等待命令執行完成
    process.wait()
    # decoded_str = os.popen(command).readlines()
    # print(decoded_str)

    # try:
    #     # 尝试使用UTF-8解码
    #     decoded_str = output.decode("utf-8")
    #     print("測試 二 : ",decoded_str)
    # except UnicodeDecodeError:
    #     # 如果解码失败，尝试使用latin1编码
    #     decoded_str = output.decode("latin1")
    #     print(decoded_str)

