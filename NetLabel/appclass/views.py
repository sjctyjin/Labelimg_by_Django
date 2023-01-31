from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.generic import View
from django.conf import settings
from .models import Article
from django.views.decorators.csrf import csrf_exempt
import xml.etree.ElementTree as ET
import time
from pathlib import Path
import os
from PIL import Image
import traceback
# Create your views here.

class Message(View):
    def get(self,request):
        # print(dir(request))
        # name = request.GET.get('name','')
        # age = request.GET.get('age',10)
       
        #return HttpResponse('My name is {1},age is {0}'.format(name,age))
        # dirs = []
        # files = os.listdir("D:/PyTest/NebelImg/NetLabel/static/userdata/1673072703")
        # for fi in files:
        #     dirs.append(f"D:/PyTest/NebelImg/NetLabel/static/userdata/1673072703/{fi}".replace("\\","/"))

        # print(dirs)
        dir_name = "userdata"
        name = request.GET.get('filepath','')
        if(name != ""):
            save_path = f'{settings.MEDIA_ROOT[0]}/{dir_name}/{name}/images/'
            dirs = []
            files = os.listdir(save_path)
            files.sort(key= lambda x:int(x[:-4]))
            for fi in files:
                dirs.append(f"static/{dir_name}/{name}/images/{fi}".replace("\\","/"))
            return render(request,'index.html',{'dirs':dirs})
        else:
            return render(request,'index.html')
    # def post(self,request):
    #     file_up = request.FILES.getlist("file[]")#['filename']
    #     print(file_up)

    #     return HttpResponse('success')
    @csrf_exempt
    #圖片上傳
    def post(self,request):
        dir_name = "userdata"
        now = (time.strftime("%Y%m%d_%H%M%S"))
        file_up = request.FILES.getlist("file[]")#['filename']
        # file_up = request.FILES.get("file[]")#['filename']
        print(file_up)
        save_path = f'{settings.MEDIA_ROOT[0]}/{dir_name}/{now}/images/'
        # print("123",settings.MEDIA_ROOT[0])
        #創建資料夾
        if not Path(save_path).exists():
            Path(save_path).mkdir(parents=True, exist_ok=True)
        
        count_img = 0
        for files in file_up:
            
            save_paths = os.path.join(save_path,f'{count_img}.jpg').replace("\\","/")
            with open(save_paths,'wb') as f:
                for content in files.chunks():
                    f.write(content)
            
            count_img +=1
            #print(files.chunks())
            # Article.objects.create(thunmbnial=files)
            try:
                img = Image.open(save_paths)
                img = img.convert("RGB")
                dd = img.size
                if dd[0]*dd[1] > 999000:
                    cropped = img.resize((int(dd[0]*0.7),int(dd[1]*0.7)))
                    cropped.save(save_paths)
            except:
                print(traceback.format_exc())

        dirs = []
        files = os.listdir(save_path)
        files.sort(key= lambda x:int(x[:-4]))
        for fi in files:
            dirs.append(f"static/{dir_name}/{now}/images/{fi}".replace("\\","/"))
        
        print(dirs)

        return render(request,'index.html',{'dirs':dirs,"urlguide":now})
class Label_List(View):
    
    def get(self,request):
        print(dir(request))
        return HttpResponse('test')
    @csrf_exempt
    def addtest(request):
        
        #接收post
        dir_name = "userdata"
        file_path = request.POST.get("filepath")
        imgwidth = request.POST.get("imgwidth")
        imgheight = request.POST.get("imgheight")
        label_list = request.POST.getlist("label[]")
        label_list_classname = request.POST.getlist("labellist[]")

        # print(file_path)
        # print(imgwidth)
        # print(imgheight)
        # print(label_list_classname)

        labe_list_inPython = []
        coun_list = 0 
        little_matrix = []

        print("="*50)
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
            <folder>{file_path.split('/')[3]}</folder>
            <filename>{file_path.split('/')[4]}</filename>
            <path>{file_path_slash}</path>
            <source>
                <database>Unknown</database>
            </source>
            <size>
                <width>{imgwidth}</width>
                <height>{imgheight}</height>
                <depth>3</depth>
            </size>
            <segmented>0</segmented>
        """
        
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
            for li in range(len(label_list_classname)):
                if labels[0] == label_list_classname[li]:
                    ymin, xmin, ymax, xmax, image_w, image_h = [float(labels[2]),float(labels[1]),float(labels[4]),float(labels[3]),int(imgwidth),int(imgheight)]
                    (x_iw_ratio, y_ih_ratio) = ( ( (xmin + xmax) * 0.5 ) / image_w, ((ymin + ymax) * 0.5 ) / image_h)
                    tw_iw_ratio = (xmax - xmin) * 1. / image_w
                    th_ih_ratio = (ymax - ymin) * 1. / image_h
                    YOLO_Format +=f"""{li} {round(x_iw_ratio,6)} {round(y_ih_ratio,6)} {round(tw_iw_ratio,6)} {round(th_ih_ratio,6)}\n"""
                
        xml_content += "</annotation>"
        
        
        # print("XML : ")
        # print(xml_content)
        # print("YOLO Format : ")
        # print(YOLO_Format)
        save_path = f"{settings.MEDIA_ROOT[0]}/{dir_name}/{file_path.split('/')[2]}/labels/"
        #創建資料夾
        if labe_list_inPython != []:
            if not Path(save_path).exists():
                Path(save_path).mkdir(parents=True, exist_ok=True)
            save_paths = os.path.join(save_path,f"{file_path.split('/')[4].split('.')[0]}.xml").replace("\\","/")
            with open(save_paths,'wt') as f:
                f.write(xml_content)
            save_paths = os.path.join(save_path,f"{file_path.split('/')[4].split('.')[0]}.txt").replace("\\","/")
            with open(save_paths,'wt') as f:
                f.write(YOLO_Format)

        return HttpResponse(f'{file_path}')
    @csrf_exempt
    def readtest(request):
        dir_name = "userdata"
        file_up = request.POST.get("filepath")
        base_path = settings.MEDIA_ROOT[0]
        label_path = f"{file_up.split('/')[1]}/{file_up.split('/')[2]}/labels/{file_up.split('/')[4].split('.')[0]}.xml"
        file_up = os.path.join(base_path,label_path).replace("\\","/")
        tree = ET.parse(file_up)
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
                # print(child.find("name").text)
                # print(child.find("bndbox").find("xmin").text)
                # print(child.find("bndbox").find("ymin").text)
                # print(child.find("bndbox").find("xmax").text)
                # print(child.find("bndbox").find("ymax").text)
                # print("H",int(child.find("bndbox").find("ymax").text)-int(child.find("bndbox").find("ymin").text))
                # print("W", int(child.find("bndbox").find("xmax").text) - int(child.find("bndbox").find("xmin").text)
        print(lbl)
        data = {
            'data':lbl,
        }
        return JsonResponse(data)

 
    # return render(request, "login_ajax.html")
    def now():
        return str(int(time.time()))
