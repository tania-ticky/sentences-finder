import os
import sys
from whoosh import index
from whoosh.index import exists_in
from whoosh.index import create_in
import whoosh.index as index
from whoosh.fields import Schema, ID, TEXT ,STORED
from whoosh.qparser import QueryParser
from whoosh.query import *
from whoosh.filedb.filestore import FileStorage
import codecs
import time
from whoosh import scoring

#it takes a text file and write every "line_num" lines in seperate files
def chop(file,line_num):
    adds = []
    fsize = os.path.getsize(file)
    myfile = open(file, "r")
    i = 0
    j = 0
    directory = os.path.join(os.path.dirname(file),os.path.basename(file).split('.')[0])
    if not os.path.exists(directory):
        os.makedirs(directory)
    fdir = os.path.join(directory,os.path.basename(file).split('.')[0]+'0'+'.txt')
    adds.append(fdir)
    f = open(fdir,"w")
    for line in myfile:
        f.write(line + "\n")
        i += 1
        if(i>line_num):
            f.close()
            i = 0
            j+= 1
            fdir = os.path.join(directory,os.path.basename(file).split('.')[0]+str(j)+'.txt')
            f = open(fdir,"w")
            adds.append(fdir)
    return adds

#it takes an array of files and index them all in one directory
def multi_index(adds):
        from whoosh import fields
        from whoosh.analysis import StemmingAnalyzer
        stem_ana = StemmingAnalyzer()
        if not os.path.exists("indexdir"):
           os.mkdir("indexdir")
        i = 0
        names = []
        schema =  Schema(name=TEXT(analyzer=stem_ana,stored=True))
        for file in adds:
            ix = create_in("indexdir", schema=schema , indexname = os.path.basename(file).split('.')[0] )
            names.append(os.path.basename(file).split('.')[0])
            writer = ix.writer(procs=4,limitmb=512,multisegment=True)
            with codecs.open(file, "r","utf-8") as f:
                for line in f:
                    writer.add_document(name=line)
            writer.commit()
        return names

def multi_index_bydir(dir):
        import glob
        if not os.path.exists("indexdir"):
           os.mkdir("indexdir")
        i = 0
        adds = []
        names = []
        adds = glob.glob(dir+'*.txt')
        schema =  Schema(name=TEXT(stored=True))
        for file in adds:
            ix = create_in("indexdir", schema=schema , indexname = os.path.basename(file).split('.')[0] )
            names.append(os.path.basename(file).split('.')[0])
            writer = ix.writer(procs=4,limitmb=512,multisegment=True)
            with codecs.open(file, "r","utf-8") as f:
                for line in f:
                    writer.add_document(name=line)
            writer.commit()
        return names


def Partex(file,num):
    s_time = time.time()
    f_list = chop(file,num)
    names = multi_index(f_list)
    f_time = time.time()
    print("done in",f_time - s_time , "seconds")
    return names

def search(keyword, n_limit , names , index_n):
    s=time.time()
    storage = FileStorage("indexdir")
    i = index_n
    result = {"sen_list":[] , "last_i":index_n}
    for index in names:
        if(i>len(names)):break
        ix = storage.open_index(names[i])
        query_b = QueryParser('name', ix.schema).parse(keyword)
        s=time.time()
        with ix.searcher() as srch:
            res = srch.search(query_b,limit=None)
            print('\n' ,res, '\n')
            for line in res:
                result["sen_list"].append(line['name'].split(" "))
        if(len(result["sen_list"]) < n_limit):
            i+=1
        else:
            break
    f = time.time()
    result["sen_list"] = result["sen_list"][len(result["sen_list"])//5::]
    result["last_i"] = i + 1
    print("done in",f-s , "seconds,  ", "last index file which was searched: ", result['last_i'])
    return result
