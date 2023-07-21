from django.shortcuts import render,redirect,reverse
from django.views.generic import View
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User,Permission,Group
from  django.contrib.auth import login,logout,authenticate
from django.conf import settings
import os,time
from pathlib import Path

#查找權限
from django.db.models import Q
# Create your views here.

#註冊
class Register(View):
    def get(self,request):
        #判斷用戶當前是否登入 如果登入就直接跳轉首頁
        # if request.user.is_authenticated:
        #     print('12==========='*10)
        #     print(request.user.is_authenticated)
        #     return redirect(reverse('register'))
        return render(request,'register.html')
    def post(self,request):
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        email = request.POST.get('mail','')
        check = request.POST.get('check_password','')
        if password != check:#檢查密碼是否輸入一致
            messages.error(request, '密碼輸入不一致')
            return redirect(reverse('register'))
            # return HttpResponse('密碼輸入不一致')
        #判斷當前註冊帳號是否已存在
        exists = User.objects.filter(username=username).exists()

        if exists:
            messages.error(request, '該帳號已註冊')
            return redirect(reverse('register'))
        #將註冊資料insert到資料表
        User.objects.create_user(username=username,password=password,email=email)
        dir_name = "userdata"
        save_path = f'{settings.STATICFILES_DIRS[0]}/{dir_name}/{username}/'
        # print("123",settings.MEDIA_ROOT[0])
        # 創建資料夾
        if not Path(save_path).exists():
            Path(save_path).mkdir(parents=True, exist_ok=True)

        return HttpResponse("""
        <style>
        .square {

    /* animation 參數設定 */
    animation-name: MoveToRight;    /*動畫名稱，需與 keyframe 名稱對應*/
    animation-duration: 3s;    /*動畫持續時間，單位為秒*/
    animation-delay: 0s;    /*動畫延遲開始時間*/
    animation-iteration-count: infinite;    /*動畫次數，infinite 為無限次*/    
}

@keyframes MoveToRight {
    from { top: 0%;opacity:0; }
    to { top: 10%;opacity:1; }
}
        </style>
       <div class="square" style="padding:20px;position:absolute;top:40%;width:80%;left:10%;border-radius:15px;background-color:#7AFEC6;color:#02C874;font-size;4vmin;text-align:center;">
          註冊成功<br/>3秒後跳轉至登入頁面．．．
        </div>
        <script>setTimeout("location.href='login'",3000);</script>""")
        # return render(request,'login.html')
#登入
class Login(View):
    def get(self,request):
        print("測試登入")
        print(request)
        if request.user.is_authenticated:
            print('12==========='*10)
            print(request.user.is_authenticated)
            return redirect(reverse('index'))
        print("失敗")
        return render(request,'login.html')
    def post(self,request):
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        #判斷當前用戶是否存在，如果不存在，則讓用戶重新註冊
        exists = User.objects.filter(username=username).exists()
        if not exists:
            return HttpResponse('該帳號不存在，請重新註冊')
        #驗證帳戶
        user = authenticate(username=username,password=password)

        if user:
            login(request,user)
            return redirect(reverse('index'))
        else:
            return HttpResponse("""
                    <style>
                    .square {

                /* animation 參數設定 */
                animation-name: MoveToRight;    /*動畫名稱，需與 keyframe 名稱對應*/
                animation-duration: 3s;    /*動畫持續時間，單位為秒*/
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
                      密碼錯誤，請重新輸入<br/>
                    </div>
                    <script>setTimeout("location.href='login'",3000);</script>""")
            # return redirect(reverse('register'))

        pass
#網站首頁
# class Index(View):
#     def get(self,request):
#         return render(request,'index.html')
#     def post(self,request):
#         pass
#用戶登出
class LogoutUser(View):
    def get(self,request):
        logout(request)
        return redirect(reverse('login'))
    def post(self,request):
        pass

#基於類的驗證 直接針對單個用戶
class A(View):
    def get(self,request):

        #判斷當前用戶是否已登入
        if not request.user.is_authenticated:

            return render(request,'please_login.html')
        else:
            a_permissinon = Permission.objects.get(codename='look_a_page')
            #添加權限
            request.user.user_permissions.add(a_permissinon)
            if not request.user.has_perm('loginapp.look_a_page'):
                # return render(request,'a.html',{'error':"當前用戶沒有權限訪問該頁面"})
                return HttpResponse('沒有訪問權限')
            else:
                return  render(request,'a.html',{'error':"pass"})
    def post(self,request):
        pass
#基於用戶組添加相應權限
class B(View):
    def get(self,request):
        #判斷當前用戶是否登陸，如果登陸就添加相應權限
        if not request.user.is_authenticated:

            return render(request,'please_login.html')
        else:
            print(request.user)
            #獲取指定用戶
            user = User.objects.get(username='test')

            #創建和獲取組
            Group.objects.get_or_create(name='b_page_test')

            group = Group.objects.get(name='b_page_test')

            #獲取content_type_id 為9的權限

            permissions = Permission.objects.filter(content_type_id=9)

            #將id為8的權限添加到組

            for per in permissions:
                group.permissions.add(per)

            #
            # #將用戶添加到組當中
            user.groups.add(group)

            #驗證當前用戶有沒有我們自定義權限
            #
            b_permission = Permission.objects.filter(codename='look_b_page').first()

            users = User.objects.filter(Q(groups__permissions=b_permission) | Q(user_permissions=b_permission)).distinct()
            # return HttpResponse(b_permission)
            #
            #判斷當前用戶是否具有指定權限
            if request.user not in users:
                return HttpResponse(f'沒有訪問權限_{users}_{request.user}')
            else:
                return render(request,'b.html')


    def post(self,request):
        pass