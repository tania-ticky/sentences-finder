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
import pickle
import multiprocessing as mp
from multiprocessing import Process, Manager
output = mp.Queue()
L = mp.Array('b',[])
#for the sake of speed we don't want search through whole text and then show the result, instead we break the first file into smaller files and do the search and show the result for each of the smaller files. this method takes a big text file and write every "line_num" lines in a seperate file
def chop(file,line_num):
    adds = []
    fsize = os.path.getsize(file)
    myfile = open(file, "r")
    i = 0
    j = 0
    directory = os.path.join(os.path.dirname(file),os.path.basename(file).split('.')[0])
    if not os.path.exists(directory):
        os.makedirs(directory)
    fdir = os.path.join(directory,os.path.basename(file).split('.')[0]+"_0.txt")
    adds.append(fdir)
    f = open(fdir,"w")
    for line in myfile:
        f.write(line + "\n")
        i += 1
        if(i>line_num):
            f.close()
            i = 0
            j+= 1
            fdir = os.path.join(directory,os.path.basename(file).split('.')[0] + "_" + str(j) + ".txt")
            f = open(fdir,"w")
            adds.append(fdir)
    return adds

#it takes an array of files and index them all in one directory (using whoosh library)
# adds -> dir
def multi_index(adds):
        import glob
        if not os.path.exists("indexdir"):
           os.mkdir("indexdir")
        i = 0
        names = []
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
    dir = os.path.join('pickles',os.path.basename(file))
    f_list = chop(file,num)
    names = multi_index(f_list)
    with open(dir, "wb") as f:
        pickle.dump(names, f)
    return names

def get_names(file):
    dir = os.path.join('pickles',os.path.basename(file))
    names = []
    with open(dir, "rb") as f:
        names = pickle.load(f)
    return names
    
def search(keyword, n_limit , names , index_n):
    storage = FileStorage("indexdir")
    i = index_n
    result = {"sen_list":[] , "last_i":index_n}
    s = time.time()
    for index in names:
        if(i>len(names)):break
        ix = storage.open_index(names[i])
        query_b = QueryParser('name', ix.schema).parse(keyword)
        with ix.searcher() as srch:
            res = srch.search(query_b,limit=None)
            # print('\n' ,res, '\n')
            for line in res:
                result["sen_list"].append(line['name'].split(" "))
        if(len(result["sen_list"]) < n_limit):
            i+=1
        else:
            break
    result["sen_list"] = result["sen_list"][len(result["sen_list"])//10::]
    result["last_i"] = i + 1
    f = time.time()
    print("time serial search:",f - s )
    return result

def mysearch2(index,keyword):
    storage = FileStorage("indexdir")
    result = []
    s = time.time()
    ix = storage.open_index(index)
    query_b = QueryParser('name', ix.schema).parse(keyword)
    with ix.searcher() as srch:
        res = srch.search(query_b,limit=None)
        # print('\n' ,res,'...........' , index ,'\n' )
        for line in res:
            result.append(line['name'].split(" "))
    f= time.time()
    print("time pool search:", f-s ,'.......',index)
    # print("done")
    return result

def mysearch3(index,keyword,output):
    storage = FileStorage("indexdir")
    result = []
    s = time.time()
    ix = storage.open_index(index)
    query_b = QueryParser('name', ix.schema).parse(keyword)
    with ix.searcher() as srch:
        res = srch.search(query_b,limit=None)
        # print('\n' ,res,'...........' , index ,'\n' )
        for line in res:
            result.append(line['name'].split(" "))
    f= time.time()
    print("time process search:", f-s ,'.......',index)
    output.put(result)
    # print("done")
    return result

def para_search3(names,keyword):
    s= time.time()
    pool = mp.Pool(processes=4)
    results = [pool.apply_async(mysearch2, args=(x,keyword,)) for x in names]
    f1 = time.time()
    outputs = [p.get() for p in results]
    #print(results[0].get())
    f = time.time()
    print("time pool parallel search:  ", f-s)
    return outputs

def para_search4(names,keyword,output):
    s = time.time()
    processes = [mp.Process(target=mysearch3, args=(x, keyword,output)) for x in names]
    for p in processes:
        p.start()
    results = [output.get() for p in processes]
    for p in processes:
        p.join()
    #print(results)

    f = time.time()
    print('time process parallel search:   ', f-s)
    return results

def mysearch30(index,keyword):
    result = []
    storage = FileStorage("indexdir")
    s = time.time()
    ix = storage.open_index(index)
    query_b = QueryParser('name', ix.schema).parse(keyword)
    with ix.searcher() as srch:
        res = srch.search(query_b,limit=None)
        print('\n' ,res,'...........' , index ,'\n' )
        for line in res:
            output.put(line['name'].split(" "))
            #print(line)
    f= time.time()
    print("time mysearch:", f-s ,'.......',index)
    print(output.get())

def para_search(names,keyword):
    from multiprocessing import Pool
    from itertools import repeat
    s = time.time()
    with Pool(10) as p:
        res = p.starmap(mysearch2, zip(names, repeat(keyword)))
        f = time.time()
        print("time:   " , f-s)
    return res

def para_search2(names,keyword):
        s1 = time.time()
        with Manager() as manager:
            L = manager.list()  # <-- can be shared between processes.
            processes = []
            for name in names:
                p = Process(target=mysearch, args=(L,name,keyword))  # Passing the list
                p.start()
                processes.append(p)
            s = time.time()
            for p in processes:
                n = time.time()
                p.join()
                f= time.time()
                print("time:   " ,p,":", f-s)
                print("start time:",p,":",n)
            f1 = time.time()
            print("time:   " , f1-s1)
        return L

def result1(keyword):
    print(keyword)
    search(keyword, 50 , ['test'] , 0)
    print('\n')
    names = ['test_0','test_1','test_2','test_3',]
    a = para_search3(names,keyword)
    print('\n')
    # print('ggggggggggggg')
    # print(a[1][0:2])
    b=para_search4(names,keyword,output)
    print("\n")
    # print(b[1][0:2])
