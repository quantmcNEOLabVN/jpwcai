# coding: utf-8
# -*- coding: utf-8 -*-
import csv

import matplotlib.pyplot as plt
from wordcloud import WordCloud
from bs4 import BeautifulSoup
import requests
import MeCab as mc
import math

class jpwcai:

    elimination=['\n','\t']
    dataText=[]
    acceptedID=1000*[False]
    gr=[]
    vocab=[]
    index={}
    idf=[]
    
    def readElimination(self,file):
        f=open(file,"r",encoding="utf-8")
        self.elimination=self.elimination+f.read().split("\n")
        f.close()
        
    def __init__(self,mode="LOAD"):
        self.acceptedID=1000*[False]
        for i in [2,3,10,12,29,30,31,36,38,40,41,42,43,44,45,46,47,48,49,50, 55, 56, 58, 59, 60, 67, 68]:
            self.acceptedID[i]=True
        self.elimination=['\n','\t']
        self.dataText=[]
        if (mode=="LOAD"):
            self.loadSavedGraph()
        else:
            self.reConstructGraph()    

    def mecab_analysis(self,text):
        t = mc.Tagger("-d /usr/lib64/mecab/dic/mecab-ipadic-neologd")
        t.parse('')
        node = t.parseToNode(text) 
        output = []        
        while(node):
            if ((node.surface in self.elimination)==False):  # ヘッダとフッタを除外
                #word_typ1e = node.feature.split(",")[0]
                #if (word_type in ["形容詞", "動詞","名詞"]):
                if (self.acceptedID[node.posid]==True):
                    output.append(node.surface)
                #print (node.surface + " : " + word_type+ ";  id="+str(node.posid))
            node = node.next
            if node is None:
                break
        return output
    
    
    def create_wordcloud(self,freq={}):
        if (freq=={}):
            return
        # 環境に合わせてフォントのパスを指定する。
        #fpath = "/System/Library/Fonts/HelveticaNeue-UltraLight.otf"
        fpath = "fonts-japanese-gothic.ttf"
    
        # ストップワードの設定
        stop_words = [ u'てる', u'いる', u'なる', u'れる', u'する', u'ある', u'こと', u'これ', u'さん', u'して', \
                 u'くれる', u'やる', u'くださる', u'そう', u'せる', u'した',  u'思う',  \
                 u'それ', u'ここ', u'ちゃん', u'くん', u'', u'て',u'に',u'を',u'は',u'の', u'が', u'と', u'た', u'し', u'で', \
                 u'ない', u'も', u'な', u'い', u'か', u'ので', u'よう', u'']
    
        wordcloud = WordCloud(background_color="white",font_path=fpath, width=900, height=500, \
                              stopwords=set(stop_words)).generate_from_frequencies(freq)
    
        plt.figure(figsize=(15,12))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.show()
    
    gr=[]
    def addEdges(self,u,v,w):
        def addEdge(u,v,w): #from u to v
            if ((v in self.gr[u])==False):
                self.gr[u][v]=0
            self.gr[u][v]=self.gr[u][v]+w
        addEdge(u,v,w)
        addEdge(v,u,w)
    
    def addVocabToGraph(self,vc):

        if (vc in self.index):
            return
        self.index[vc]=self.n
        self.vocab.append(vc)
        self.gr.append({})
        self.vcCount.append(0)
        self.n=self.n+1
    
    
    
    idf=[]
    tf=[]
    def calcTF(self,sample):
        f={}
        m=len(sample)
        for vc in sample:
            id=self.index[vc]
            if ((id in f)==False):
                f[id]=0
            f[id]=f[id]+(1.0/m)
        self.tf.append(f)
    
    def extractSampleToGraph(self,vocabs,f):
        m=len(vocabs)
        ids=[]
        for vc in vocabs:
            ids.append(self.index[vc])
        ids=sorted(ids)
        m=len(ids)
        for i in range(m-1):
            u=ids[i]
            if (ids[i]!=ids[i+1]):
                for j in range(i+1,m):
                    if (j<(m-1)):
                        if (ids[j]==ids[j+1]):
                            continue;
                    v=ids[j]
                    self.addEdges(u,v,(f[u]*self.idf[u])+(f[v]*self.idf[v]))
    
    def getTop(self,d,topn=100):
        l=d.items()
        l=sorted(l,key=lambda w: -w[1])
        d.clear()
        for it in l[0:min(topn,len(l))]:
            d[it[0]]=it[1]
        return d
    
    def collectFreq(self,msg):
        words=self.mecab_analysis(msg)
        #print(msg +" --->  "+ str(words));
        ret={}
        for word in words:
            if ((word in self.index)==False):
                #print (word +"  was not found in any sample")
                continue;
            u=self.index[word]
            for v,t in self.gr[u].items():
                w=self.vocab[v]
                if((w in ret)==False):
                    ret[w]=1
                ret[w]=ret[w]+t
        ret=self.getTop(ret)
        return ret
    
        
    
        
    def saveGraph(self,fileOut="graph_w_tfidf.sav"):
        
        f=open(fileOut,"w+",encoding="utf-8")
        f.write(str(self.n)+"\n")
        f.write("\n".join(self.vocab))
        f.write("\n")
        svc=[]
        for c in self.vcCount:
            svc.append(str(c))
        f.write(" ".join(svc))
        f.write("\n")
        for u in range(self.n):
            es=self.gr[u]
            for v,c in es.items():
                f.write(str(u)+" "+str(v)+" "+str(c)+"\n")
        f.close()
        print("Graph Saved!")
        
    
    def reConstructGraph(self):
        self.index={}
        self.vcCount=[]
        self.n=0
        self.vocab=[]
        self.gr=[]
        self.dataText=[]
        self.elimination=['\n','\t']
        self.readElimination('elimination.txt')
        self.readElimination('stopwords.txt')
        self.elimination=sorted(elimination,key=lambda w: -len(w))
        fileName="questions-2017-10-16.csv"
        csvfile=open(fileName, newline='', encoding='utf-8')
        reader = csv.DictReader(csvfile)
        for row in reader:
            text=(row['Description']+". "+row['Category']).replace('\n','').replace('\t','')
            self.dataText.append(mecab_analysis(text))
        csvfile.close()
        
        fileName="users-2017-10-16.csv"
        csvfile=open(fileName, newline='', encoding='utf-8')
        reader = csv.DictReader(csvfile, )
        for row in reader:
            text=(row['Profile']+". "+row['Problem']).replace('\n','').replace('\t','')
            self.dataText.append(mecab_analysis(text))
        csvfile.close()
        
        
        for sample in self.dataText:
            for vc in sample:
                self.addVocabToGraph(vc)
                self.vcCount[self.index[vc]]=self.vcCount[self.index[vc]]+1
        N=len(self.dataText)
        for sample in dataText:
            self.calcTF(sample)
        self.idf=self.n*[0]
        for vc,id in  index.items():
            d=1
            for sample in dataText:
                if (vc in sample):
                    d=d+1
                    self.idf[id]=math.log((N+0.1)/d)
                    
        for i in range(len(self.dataText)):
            self.extractSampleToGraph(self.dataText[i],self.tf[i])
        for es in self.gr:
            self.getTop(es)
        print(str(n)+" words accepted! ")
        print('graph constructed!')
        self.saveGraph()
    
    
    
    def loadSavedGraph(self,filesav="graph_w_tfidf.sav"):
        self.elimination=['\n','\t']
        self.readElimination('elimination.txt')
        self.readElimination('stopwords.txt')
        f=open(filesav, "r+", newline='',encoding="utf-8")
        self.n=int(f.readline())
        self.vocab=[]
        self.index={}
        self.gr=[]
        for i in range(self.n):
            self.vocab.append(f.readline().replace("\n",''))
            self.index[self.vocab[i]]=i
            self.gr.append({})
        svc=f.readline().replace("\n",'').split()
        self.vcCount=[]
        for s in svc:
            self.vcCount.append(eval(s))
        while (True):
            inp=f.readline()
            if (inp==''):
                break
            l=inp.split(" ")
            u=int(l[0])
            v=int(l[1])
            k=eval(l[2])
            self.gr[u][v]=k
        f.close()
        print(str(self.n)+" words accepted! ")
        print("Graph loaded!")
    
    
    
    
    def trySampleTestCases(self):
        testSet=[u"退職",u"親子関係",u"結婚",u"再婚",u"化粧",u"元彼",u"仕事",u"離婚",u"子供"]
        for test in testSet:
            self.create_wordcloud(self.collectFreq(test))
    
## Testing
