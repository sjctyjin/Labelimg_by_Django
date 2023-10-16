from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
# Create your views here.
class Index(View):
    def index(self,request):
    #def index(request,name,age):
        name = request.GET.get('name','')
        age = request.GET.get('age',10)
        print(name,age)
        return HttpResponse('hello')
    def get(self,request):
        print(dir(request))
        return render(request,'text.html',{'f':dir(request)})
        #return HttpResponse('hello message{{f}}',{'f':123})
