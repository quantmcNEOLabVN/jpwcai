# coding: utf-8
# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')

import csv
import tkinter 

import matplotlib.pyplot as plt
from wordcloud import WordCloud
from bs4 import BeautifulSoup
import requests
import MeCab as mc
import math
import base64 
from io import StringIO
import PIL
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont

from graph_W_TFIDF import *

from pylab import figure, axes, pie, title, show
from flask import Flask, make_response
from io import BytesIO 
app = Flask(__name__)


def gen_wordcloud(freq={}):
    if (freq=={}):
        return ""
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
    
    image=wordcloud.to_image()
    
    buffer = BytesIO()    
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue())
    
    ret=[]
    for x in img_str:
        ret.append(chr(x))
    return "".join(ret)
    
myAI=jpwcai()

@app.route('/')
def mainPage():
    return '''
<p>日本語のキーワードを入力してください: <input id="tfkeywords" type="text" id="keywords"/></p>
<p><Button id=wcbutton> ワードクラウドを表示する</Button></p>
<script>
var textF=document.getElementById("tfkeywords");
var wcbut=document.getElementById("wcbutton");
wcbut.addEventListener("click", function() {
    var kw=textF.value;
    window.location =window.location +"result/"+kw;
  });
</script>
'''   

@app.route('/result/<string:keywords>')
def resultPage(keywords=None):
    if ((keywords==None) or (keywords=="")):
        return'''<p><button onclick="window.history.back()">戻る</button></p>'''
    print("input: %s" %keywords)
    freq=myAI.collectFreq(keywords)
    #print (wordcloud(freq))
    imgtag=""
    if (freq=={}):
        imgtag= '<p> No result for this keywords.</p>'
    else:
        base64_img = gen_wordcloud(freq)
        imgtag= '<img src="data:image/png;base64,%s"/>' % base64_img
    
    capt="<p>This is the result for the input '%s' </p>" %keywords
    html='''
    <p><button id=buttonBack>戻る</button></p>
<script>
var but=document.getElementById("buttonBack");
but.addEventListener("click", function() {
    var link=window.location.href;
    link=link.substring(0,link.indexOf(/result/));
    window.location =link;
  });
</script>
    '''+imgtag
    return html