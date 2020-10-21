from django.shortcuts import render
from django.http import HttpResponse
from . import forms
from django.http import JsonResponse
import re
from itertools import islice
import nltk
from nltk.corpus import wordnet
import pickle
import partex
import json
# this method is used to remove all the lines belong to other conversations
def extract_conv(lines):
    j = 2
    i = 2
    while i >= 0 :
        if int(lines[i].split("      ")[0]) == int(lines[i-1].split("      ")[0]) + 1 :
            i = i-1
        else :
            break
    while j < 5 :
        if int(lines[j].split("    ")[0]) == int(lines[j+1].split("    ")[0]) - 1 :
            j = j+1
        else :
            break
    return lines[i:j+1]
# finding usage in spoken english
def search_conv(keyword):
    sen_list = []
    conv_list = []
    before = []
    conv=[]
    searchfile = open("/home/termeh/myfiles/datasets/movies.txt", "r")
    for i,line in enumerate(searchfile,1):
        #saving 3 lines before the line which contains keyword
        before.append(line.rstrip())
        if len(before) > 3:
            before.pop(0)
        if keyword in line:
            sen_list.append(line.split("    ")[1].split(' ')[3:])
            #adding 3 lines after the line which contains keyword
            conv = before + list(islice(searchfile,3))
            conv_list.append(extract_conv(conv))
            conv = []
            if (len(sen_list) == 50 ):
              break
    searchfile.close()
    conv_list = zip(sen_list,conv_list)
    #print(conv_list[2])
    return conv_list
# finding usage in written english.
def search_news(keyword,index):
    #list of index files' names
    names = ['booksummaries_0', 'booksummaries_1', 'booksummaries_2', 'booksummaries_3', 'booksummaries_4']
    result = partex.search(keyword,30,names,index)
    return result
#when users press loadmore this method is called
def printmore(request):
    if 'keyword' in request.GET:
        keyword  = request.GET['keyword']
        if 'line' in request.GET:
            line1 = int(request.GET['line'])
            more_news = search_news(keyword,line1)
    else:
        print("missing keyword")
    return JsonResponse({'last_index':more_news['last_i'] , 'more' : more_news['sen_list'] })

def see_also(keyword):
    suggestion = set()
    word = wordnet.synsets(keyword)
    for i in word:
        for j in i.also_sees():
            suggestion.add(j.name().split(".")[0].replace("_"," "))
        for j in i.similar_tos():
            suggestion.add(j.name().split(".")[0].replace("_"," "))
    return suggestion

def search_word(request):
    keyword = ""
    last_index = 0
    news = []
    news_list = {'sen_list' : [] , 'last_i' : 0}
    conv_list = []
    also = set()
    POST = False
    form = forms.search_form
    if request.method == 'GET':

        if 'keyword' in request.GET and request.GET['keyword']:
            POST = True
            keyword = request.GET['keyword']
            also = see_also(keyword)
            keyword = " " + keyword + " "
            conv_list = search_conv(keyword)
            news_list = search_news(keyword,0)
            news = json.dumps(news_list['sen_list'][30::])
            last_index = news_list['last_i']
    my_dict = { 'sth2':conv_list, 'news':news, 'see_also':also, 'POST' : POST, 'form':form , 'last_index' : last_index , 'keyword':keyword , 'f_news':news_list['sen_list'][0:29] }
    return render(request,'searchm/index2.html',context = my_dict)

#this method writes selected sentences and keywords to the favorite file. it also prevents duplication of the sentence by checking if it already exists in the favorite file
def add_sen(sentence , keyword):
    sen = keyword + ' ' + sentence +'\n'
    if sen in open('favorite.txt').read():
        return False
    else:
        f = open("favorite.txt" ,"a")
        f.write(keyword + ' ' + sentence + '\n')
    f.close()

#this method removes selected sentences and keywords from the file
def del_sen(sentence , keyword):
    print('delete')
    sen = keyword + ' ' + sentence +'\n'
    f = open("favorite.txt","r+")
    lines = f.readlines()
    f.close()
    f = open("favorite.txt","w")
    for line in lines:
      if line!= sen:
        f.write(line)
    f.close()
def del_sen_req(request):
    if 'keyword' in request.POST:
        keyword  = request.POST['keyword']
    if 'sentence' in request.POST:
        sentence = request.POST['sentence']
    del_sen(sentence , keyword)
    return HttpResponse('done')
#this method is called when the star icon is pressed and decides whether to add or remove sentence.
def fav(request):
    exist = True
    if 'keyword' in request.POST:
        keyword  = request.POST['keyword']
    if 'sentence' in request.POST:
        sentence = request.POST['sentence']
    if 'which' in request.POST:
        which = request.POST['which']
    if (which == 'true'):
        del_sen(sentence , keyword)
    else:
        exist = add_sen(sentence , keyword)
    return HttpResponse(exist)

#this method is used to show saved sentences
def extract_fav(request):
    faves = dict()
    fav_by_date = []
    f = open("favorite.txt","r")
    lines = f.readlines()
    for line in lines:
        word = line.split('   ')[0].lstrip()
        sentence = line.split('   ')[1].split(' ')
        fav_by_date.append(sentence)
        if word in faves:
            faves[word].append(sentence)
        else:
            faves[word] = [sentence]
    my_dict = { 'faves':faves,'bydate':fav_by_date}
    return render(request,'searchm/favorites.html',context = my_dict)
