from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

#網頁顯示內容

#視圖函數

def index(request):
    return HttpResponse('<h1 style="text-align:center;color:red;">Hello django</h1><br/><a style="text-align:center;" href="index2">點此前往</a><script>window.location.href="index2"<script>')
