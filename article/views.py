from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
# Create your views here.
from article import models


class Article(View):

    def get(self, request):
        index_data = {}
        typeid = request.GET.get('typeid')
        goodid = request.GET.get('goodid')
        index = models.Article.objects.filter(id = int(typeid))[0]
        index_data['title'] = index.title
        index_data['author'] = index.author
        con_list = index.content.split('|')
        for it in range(len(con_list)):
            word = 'content' + str(it)
            index_data[word] = con_list[it]
        result = {"code": 200, "data": index_data}


        return JsonResponse(result)

