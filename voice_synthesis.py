#-*- coding: utf-8 -*-
import requests
import re
import time
import hashlib
import base64
import struct

URL = "http://api.xfyun.cn/v1/service/v1/tts"
AUE = "raw"
APPID = "5b5ad0ae"
API_KEY = "68f7e89b9180a5135daf9febcb60d405"

def getHeader():
        curTime = str(int(time.time()))
        param = "{\"aue\":\""+AUE+"\",\"auf\":\"audio/L16;rate=16000\",\"voice_name\":\"xiaoyan\",\"engine_type\":\"intp65\"}"
        paramBase64 = base64.b64encode(param)
        m2 = hashlib.md5()
        m2.update(API_KEY + curTime + paramBase64)
        checkSum = m2.hexdigest()
        header ={
                'X-CurTime':curTime,
                'X-Param':paramBase64,
                'X-Appid':APPID,
                'X-CheckSum':checkSum,
                'X-Real-Ip':'202.45.129.183',
                'Content-Type':'application/x-www-form-urlencoded; charset=utf-8',
        }
        return header

def getBody(text):
        data = {'text':text}
        return data

def writeFile(file, content):
    with open(file, 'wb') as f:
        f.write(content)
    f.close()

r = requests.post(URL,headers=getHeader(),data=getBody("科大讯飞是中国最大的智能语音技术提供商"))
contentType = r.headers['Content-Type']
if contentType == "audio/mpeg":
    sid = r.headers['sid']
    if AUE == "raw":
        writeFile("C:/Projects/YianTianChatBot/audio/"+sid+".wav", r.content)
    else :
        writeFile("C:/Projects/YianTianChatBot/audio/"+sid+".mp3", r.content)
    print "success, sid = " + sid
else :
    print r.text 