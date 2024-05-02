import pytesseract 
import numpy as np 
import pandas as pd
from flask import Flask , request, abort
from flask_cors import CORS
import cv2
import base64
import os
from PIL import Image
# from google.cloud import datastore
import pickle
# import tempfile
# import struct
# import os
# from embedchain import App

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    MessagingApiBlob
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent
)


app = Flask(__name__) 
CORS(app)
# client = datastore.Client()
# print(pytesseract.__version__)

configuration = Configuration(access_token='kgM8kCIFBA0Eb+suDBnxQGazzw1MW9pjB3ZJoOWnUtOhzeNwMZsIWEl4KDM2c3ed9KERxJgLpuAeFe2sytzyobjWN7SlYO/bDkdRY++Q/e+taXXeNauKrwBFupKXw/wMZvyyqlYcSZXesC3/36UwpQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('005e71877b21820807de29bf82954146')

arrayThaLang = ['๑','๒','๓','ภ','๔','ถ','ู','ุ','ึ','๕','ค','๖','ต','๗','จ','๘','ข','๙','ช','ๆ','๐','ไ','ำ','ฎ','พ','ฑ','ะ','ธ','ั','ํ','ี','๊','ณ','ร','ฯ','น','ญ','ย','ฐ','บ','ล','ฟ','ฤ','ห','ฆ','ฏ','ก','ด','โ','เ','ฌ','็','้','่','๋','า','ษ','ส','ศ','ว','ซ','ง','ผ','ป','ฉ','แ','อ','ฮ','ิ','ื','์','ท','ม','ฒ','ใ','ฬ','ฦ','ฝ']
arrayEngLang = ['q','w','e','r','t','y','u','i','o','p','a','s','d','f','g','h','j','k','l','z','x','c','v','b','n','m','Q','W','E','R','T','Y','U','I','O','P','A','S','D','F','G','H','J','K','L','Z','X','C','V','B','N','M']
arrayNumLang = ['1','2','3','4','5','6','7','8','9','0']
arraySymLang = ['!','@','#','$','%','^','&','*','(',')','-','_','=','+','{','}','[',']',';',':','<','>',',','.','?','/','฿','',' ']
feature_col = []
dataFrame = []


def image_to_text(base64_img):
    image_data_base64 = base64.b64encode(base64_img)
    # print(image_data_base64)
    # np_array = np.frombuffer(image_data_base64, np.uint8)
    with open("imageToSave.png", "wb") as fh:
        fh.write(base64.decodebytes(image_data_base64))

    BANK = "kbank"
    word = ""
    word_left = []
    word_top = []
    word_width = []
    word_height = []
    page_num = []
    block_num = []
    par_num = []
    line_num = []
    word_num = []
    conf = []
    # img = cv2.imdecode(base64_img, cv2.IMREAD_UNCHANGED)
    # imgGry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # print(img)
    img = Image.open("./imageToSave.png")
    raw_data = pytesseract.image_to_data(img, lang='tha+eng', output_type='data.frame')
    for idx,i in enumerate(raw_data.conf):
        if raw_data['level'][idx] == 5:
            word = word + raw_data['text'][idx]
            word_left.append(raw_data['left'][idx])
            word_top.append(raw_data['top'][idx])
            word_width.append(raw_data['width'][idx])
            word_height.append(raw_data['height'][idx])
            page_num.append(raw_data['page_num'][idx])
            block_num.append(raw_data['block_num'][idx])
            par_num.append(raw_data['par_num'][idx])
            line_num.append(raw_data['line_num'][idx])
            word_num.append(raw_data['word_num'][idx])
            conf.append(raw_data['conf'][idx])
        else:
            if word != "":
                average_word_left = round(sum(word_left) / len(word_left),2)
                average_word_top = round(sum(word_top) / len(word_top), 2)
                average_word_width = round(sum(word_width) / len(word_width),2)
                average_word_height = round(sum(word_height) / len(word_height), 2)
                average_page_num = round(sum(page_num)/ len(page_num), 2)
                average_block_num = round(sum(block_num) / len(block_num), 2)
                average_par_num = round(sum(par_num) / len(par_num), 2)
                average_line_num = round(sum(line_num) / len(line_num), 2)
                average_word_num = round(sum(word_num) / len(word_num), 2)
                average_conf = round(sum(conf) / len(conf), 2)
                warp = {
                    'bank':BANK,
                    'level':5,
                    'page_num': average_page_num,
                    'block_num': average_block_num,
                    'par_num': average_par_num,
                    'line_num': average_line_num,
                    'word_num': average_word_num,
                    'left' : average_word_left,
                    'top': average_word_top,
                    'width': average_word_width,
                    'height': average_word_height,
                    'conf': average_conf,
                    'word': word
                }

                dataFrame.append(warp)
                word = ""
                word_left.clear()
                word_top.clear()
                word_width.clear()
                word_height.clear()
                page_num.clear()
                block_num.clear()
                par_num.clear()
                line_num.clear()
                word_num.clear()
                conf.clear()

    featureName = ['bank','level','page_num','block_num','par_num','line_num','word_num','left','top','width','height','conf','word']
    df = pd.DataFrame(dataFrame, columns= featureName)
    # df.to_csv(raw_data_file_name+'.csv')
    return df


def set_feature():
    for i in arrayThaLang:
        if i == "๑":
            thaiNum = '1th'
            feature_col.append(thaiNum)
        elif i == "๒":
            thaiNum = '2th'
            feature_col.append(thaiNum)
        elif i == "๓":
            thaiNum = '3th'
            feature_col.append(thaiNum)
        elif i == "๔":
            thaiNum = '4th'
            feature_col.append(thaiNum)
        elif i == "๕":
            thaiNum = '5th'
            feature_col.append(thaiNum)
        elif i == "๖":
            thaiNum = '6th'
            feature_col.append(thaiNum)
        elif i == "๗":
            thaiNum = '7th'
            feature_col.append(thaiNum)
        elif i == "๘":
            thaiNum = '8th'
            feature_col.append(thaiNum)
        elif i == "๙":
            thaiNum = '9th'
            feature_col.append(thaiNum)
        elif i == "๐":
            thaiNum = '10th'
            feature_col.append(thaiNum)
        else:
            feature_col.append(i)

    for i in arrayEngLang:
        feature_col.append(i)

    for i in arrayNumLang:
        feature_col.append(i)

    for i in arraySymLang:
        if i == "=":
            sym = "equal_sym"
            feature_col.append(sym)
        elif i == "":
            sym = "blank"
            feature_col.append(sym)
        elif i == " ":
            sym = "double_blank"
            feature_col.append(sym)
        else:
            feature_col.append(i)




def counting_word(data, arrayThaLang, arrayEngLang, arrayNumLang, arraySymLang):

    countingWord =[]
    data = data.word
    # print(data)
    for word in data:
        word = str(word)  
        T0=0
        T1=0
        T2=0
        T3=0
        T4=0
        T5=0
        T6=0
        T7=0
        T8=0
        T9=0
        T10=0
        T11=0
        T12=0
        T13=0
        T14=0
        T15=0
        T16=0
        T17=0
        T18=0
        T19=0
        T20=0
        T21=0
        T22=0
        T23=0
        T24=0
        T25=0
        T26=0
        T27=0
        T28=0
        T29=0
        T30=0
        T31=0
        T32=0
        T33=0
        T34=0
        T35=0
        T36=0
        T37=0
        T38=0
        T39=0
        T40=0
        T41=0
        T42=0
        T43=0
        T44=0
        T45=0
        T46=0
        T47=0
        T48=0
        ## รวมสระ ##
        T49=0
        T50=0
        T51=0
        T52=0
        T53=0
        T54=0
        T55=0
        T56=0
        T57=0
        T58=0
        T59=0
        T60=0
        T61=0
        T62=0
        T63=0
        T64=0
        T65=0
        T66=0
        T67=0
        T68=0
        T69=0
        T70=0
        T71=0
        T72=0
        T73=0
        T74=0
        T75=0
        T76=0
        T77=0
        
        E0=0
        E1=0
        E2=0
        E3=0
        E4=0
        E5=0
        E6=0
        E7=0
        E8=0
        E9=0
        E10=0
        E11=0
        E12=0
        E13=0
        E14=0
        E15=0
        E16=0
        E17=0
        E18=0
        E19=0
        E20=0
        E21=0
        E22=0
        E23=0
        E24=0
        E25=0

        E26=0
        E27=0
        E28=0
        E29=0
        E30=0
        E31=0
        E32=0
        E33=0
        E34=0
        E35=0
        E36=0
        E37=0
        E38=0
        E39=0
        E40=0
        E41=0
        E42=0
        E43=0
        E44=0
        E45=0
        E46=0
        E47=0
        E48=0
        E49=0
        E50=0
        E51=0

        N0=0
        N1=0
        N2=0
        N3=0
        N4=0
        N5=0
        N6=0
        N7=0
        N8=0
        N9=0

        S0=0
        S1=0
        S2=0
        S3=0
        S4=0
        S5=0
        S6=0
        S7=0
        S8=0
        S9=0
        S10=0
        S11=0
        S12=0
        S13=0
        S14=0
        S15=0
        S16=0
        S17=0
        S18=0
        S19=0
        S20=0
        S21=0
        S22=0
        S23=0
        S24=0
        S25=0
        S26=0
        S27=0
        S28=0
        
        for elemnt2 in word:
            ### counting Tha element 
            if elemnt2 == arrayThaLang[0]:
                T0 += 1
            elif elemnt2 == arrayThaLang[1]:
                T1 += 1
            elif elemnt2 == arrayThaLang[2]:
                T2 += 1
            elif elemnt2 == arrayThaLang[3]:
                T3 += 1
            elif elemnt2 == arrayThaLang[4]:
                T4 += 1
            elif elemnt2 == arrayThaLang[5]:
                T5 += 1
            elif elemnt2 == arrayThaLang[6]:
                T6 += 1
            elif elemnt2 == arrayThaLang[7]:
                T7 += 1
            elif elemnt2 == arrayThaLang[8]:
                T8 += 1
            elif elemnt2 == arrayThaLang[9]:
                T9 += 1
            elif elemnt2 == arrayThaLang[10]:
                T10 += 1
            elif elemnt2 == arrayThaLang[11]:
                T11 += 1
            elif elemnt2 == arrayThaLang[12]:
                T12 += 1
            elif elemnt2 == arrayThaLang[13]:
                T13 += 1
            elif elemnt2 == arrayThaLang[14]:
                T14 += 1
            elif elemnt2 == arrayThaLang[15]:
                T15 += 1
            elif elemnt2 == arrayThaLang[16]:
                T16 += 1
            elif elemnt2 == arrayThaLang[17]:
                T17 += 1
            elif elemnt2 == arrayThaLang[18]:
                T18 += 1
            elif elemnt2 == arrayThaLang[19]:
                T19 += 1
            elif elemnt2 == arrayThaLang[20]:
                T20 += 1
            elif elemnt2 == arrayThaLang[21]:
                T21 += 1
            elif elemnt2 == arrayThaLang[22]:
                T22 += 1
            elif elemnt2 == arrayThaLang[23]:
                T23 += 1
            elif elemnt2 == arrayThaLang[24]:
                T24 += 1
            elif elemnt2 == arrayThaLang[25]:
                T25 += 1
            elif elemnt2 == arrayThaLang[26]:
                T26 += 1
            elif elemnt2 == arrayThaLang[27]:
                T27 += 1
            elif elemnt2 == arrayThaLang[28]:
                T28 += 1
            elif elemnt2 == arrayThaLang[29]:
                T29 += 1
            elif elemnt2 == arrayThaLang[30]:
                T30 += 1
            elif elemnt2 == arrayThaLang[31]:
                T31 += 1
            elif elemnt2 == arrayThaLang[32]:
                T32 += 1
            elif elemnt2 == arrayThaLang[33]:
                T33 += 1
            elif elemnt2 == arrayThaLang[34]:
                T34 += 1
            elif elemnt2 == arrayThaLang[35]:
                T35 += 1
            elif elemnt2 == arrayThaLang[36]:
                T36 += 1
            elif elemnt2 == arrayThaLang[37]:
                T37 += 1
            elif elemnt2 == arrayThaLang[38]:
                T38 += 1
            elif elemnt2 == arrayThaLang[39]:
                T39 += 1
            elif elemnt2 == arrayThaLang[40]:
                T40 += 1
            elif elemnt2 == arrayThaLang[41]:
                T41 += 1
            elif elemnt2 == arrayThaLang[42]:
                T42 += 1
            elif elemnt2 == arrayThaLang[43]:
                T43 += 1
            elif elemnt2 == arrayThaLang[44]:
                T44 += 1
            elif elemnt2 == arrayThaLang[45]:
                T45 += 1
            elif elemnt2 == arrayThaLang[46]:
                T46 += 1
            elif elemnt2 == arrayThaLang[47]:
                T47 += 1
            elif elemnt2 == arrayThaLang[48]:
                T48 += 1
            elif elemnt2 == arrayThaLang[49]:
                T49 += 1
            elif elemnt2 == arrayThaLang[50]:
                T50 += 1
            elif elemnt2 == arrayThaLang[51]:
                T51 += 1
            elif elemnt2 == arrayThaLang[52]:
                T52 += 1
            elif elemnt2 == arrayThaLang[53]:
                T53 += 1
            elif elemnt2 == arrayThaLang[54]:
                T54 += 1
            elif elemnt2 == arrayThaLang[55]:
                T55 += 1
            elif elemnt2 == arrayThaLang[56]:
                T56 += 1
            elif elemnt2 == arrayThaLang[57]:
                T57 += 1
            elif elemnt2 == arrayThaLang[58]:
                T58 += 1
            elif elemnt2 == arrayThaLang[59]:
                T59 += 1
            elif elemnt2 == arrayThaLang[60]:
                T60 += 1
            elif elemnt2 == arrayThaLang[61]:
                T61 += 1
            elif elemnt2 == arrayThaLang[62]:
                T62 += 1
            elif elemnt2 == arrayThaLang[63]:
                T63 += 1
            elif elemnt2 == arrayThaLang[64]:
                T64 += 1
            elif elemnt2 == arrayThaLang[65]:
                T65 += 1
            elif elemnt2 == arrayThaLang[66]:
                T66 += 1
            elif elemnt2 == arrayThaLang[67]:
                T67 += 1
            elif elemnt2 == arrayThaLang[68]:
                T68 += 1
            elif elemnt2 == arrayThaLang[69]:
                T69 += 1
            elif elemnt2 == arrayThaLang[70]:
                T70 += 1
            elif elemnt2 == arrayThaLang[71]:
                T71 += 1
            elif elemnt2 == arrayThaLang[72]:
                T72 += 1
            elif elemnt2 == arrayThaLang[73]:
                T73 += 1
            elif elemnt2 == arrayThaLang[74]:
                T74 += 1
            elif elemnt2 == arrayThaLang[75]:
                T75 += 1
            elif elemnt2 == arrayThaLang[76]:
                T76 += 1
            elif elemnt2 == arrayThaLang[77]:
                T77 += 1
            
            
            #### counting element Eng
            elif elemnt2 == arrayEngLang[0]:
                E0 += 1
            elif elemnt2 == arrayEngLang[1]:
                E1 += 1
            elif elemnt2 == arrayEngLang[2]:
                E2 += 1
            elif elemnt2 == arrayEngLang[3]:
                E3 += 1
            elif elemnt2 == arrayEngLang[4]:
                E4 += 1
            elif elemnt2 == arrayEngLang[5]:
                E5 += 1
            elif elemnt2 == arrayEngLang[6]:
                E6 += 1
            elif elemnt2 == arrayEngLang[7]:
                E7 += 1
            elif elemnt2 == arrayEngLang[8]:
                E8 += 1
            elif elemnt2 == arrayEngLang[9]:
                E9 += 1
            elif elemnt2 == arrayEngLang[10]:
                E10 += 1
            elif elemnt2 == arrayEngLang[11]:
                E11 += 1
            elif elemnt2 == arrayEngLang[12]:
                E12 += 1
            elif elemnt2 == arrayEngLang[13]:
                E13 += 1
            elif elemnt2 == arrayEngLang[14]:
                E14 += 1
            elif elemnt2 == arrayEngLang[15]:
                E15 += 1
            elif elemnt2 == arrayEngLang[16]:
                E16 += 1
            elif elemnt2 == arrayEngLang[17]:
                E17 += 1
            elif elemnt2 == arrayEngLang[18]:
                E18 += 1
            elif elemnt2 == arrayEngLang[19]:
                T19 += 1
            elif elemnt2 == arrayEngLang[20]:
                E20 += 1
            elif elemnt2 == arrayEngLang[21]:
                E21 += 1
            elif elemnt2 == arrayEngLang[22]:
                E22 += 1
            elif elemnt2 == arrayEngLang[23]:
                E23 += 1
            elif elemnt2 == arrayEngLang[24]:
                E24 += 1
            elif elemnt2 == arrayEngLang[25]:
                E25 += 1

            elif elemnt2 == arrayEngLang[26]:
                E26 += 1
            elif elemnt2 == arrayEngLang[27]:
                E27 += 1
            elif elemnt2 == arrayEngLang[28]:
                E28 += 1
            elif elemnt2 == arrayEngLang[29]:
                E29 += 1
            elif elemnt2 == arrayEngLang[30]:
                E30 += 1
            elif elemnt2 == arrayEngLang[31]:
                E31 += 1
            elif elemnt2 == arrayEngLang[32]:
                E32 += 1
            elif elemnt2 == arrayEngLang[33]:
                E33 += 1
            elif elemnt2 == arrayEngLang[34]:
                E34 += 1
            elif elemnt2 == arrayEngLang[35]:
                E35 += 1
            elif elemnt2 == arrayEngLang[36]:
                E36 += 1
            elif elemnt2 == arrayEngLang[37]:
                E37 += 1
            elif elemnt2 == arrayEngLang[38]:
                E38 += 1
            elif elemnt2 == arrayEngLang[39]:
                E39 += 1
            elif elemnt2 == arrayEngLang[40]:
                E40 += 1
            elif elemnt2 == arrayEngLang[41]:
                E41 += 1
            elif elemnt2 == arrayEngLang[42]:
                E42 += 1
            elif elemnt2 == arrayEngLang[43]:
                E43 += 1
            elif elemnt2 == arrayEngLang[44]:
                E44 += 1
            elif elemnt2 == arrayEngLang[45]:
                E45 += 1
            elif elemnt2 == arrayEngLang[46]:
                E46 += 1
            elif elemnt2 == arrayEngLang[47]:
                E47 += 1
            elif elemnt2 == arrayEngLang[48]:
                E48 += 1
            elif elemnt2 == arrayEngLang[49]:
                E49 += 1
            elif elemnt2 == arrayEngLang[50]:
                E50 += 1
            elif elemnt2 == arrayEngLang[51]:
                E51 += 1

            ### COUNT NUM ELEMENT 
            elif str(elemnt2) == str(arrayNumLang[0]):
                N0 += 1
            elif str(elemnt2) == str(arrayNumLang[1]):
                N1 += 1
            elif str(elemnt2) == str(arrayNumLang[2]):
                N2 += 1
            elif str(elemnt2) == str(arrayNumLang[3]):
                N3 += 1
            elif str(elemnt2) == str(arrayNumLang[4]):
                N4 += 1
            elif str(elemnt2) == str(arrayNumLang[5]):
                N5 += 1
            elif str(elemnt2) == str(arrayNumLang[6]):
                N6 += 1
            elif str(elemnt2) == str(arrayNumLang[7]):
                N7 += 1
            elif str(elemnt2) == str(arrayNumLang[8]):
                N8 += 1
            elif str(elemnt2) == str(arrayNumLang[9]):
                N9 += 1
            ### Counting Symbol

            if elemnt2 == arraySymLang[0]:
                S0 += 1
            elif elemnt2 == arraySymLang[1]:
                S1 += 1
            elif elemnt2 == arraySymLang[2]:
                S2 += 1
            elif elemnt2 == arraySymLang[3]:
                S3 += 1
            elif elemnt2 == arraySymLang[4]:
                S4 += 1
            elif elemnt2 == arraySymLang[5]:
                S5 += 1
            elif elemnt2 == arraySymLang[6]:
                S6 += 1
            elif elemnt2 == arraySymLang[7]:
                S7 += 1
            elif elemnt2 == arraySymLang[8]:
                S8 += 1
            elif elemnt2 == arraySymLang[9]:
                S9 += 1
            elif elemnt2 == arraySymLang[10]:
                S10 += 1
            elif elemnt2 == arraySymLang[11]:
                S11 += 1
            elif elemnt2 == arraySymLang[12]:
                S12 += 1
            elif elemnt2 == arraySymLang[13]:
                S13 += 1
            elif elemnt2 == arraySymLang[14]:
                S14 += 1
            elif elemnt2 == arraySymLang[15]:
                S15 += 1
            elif elemnt2 == arraySymLang[16]:
                S16 += 1
            elif elemnt2 == arraySymLang[17]:
                S17 += 1
            elif elemnt2 == arraySymLang[18]:
                S18 += 1
            elif elemnt2 == arraySymLang[19]:
                S19 += 1
            elif elemnt2 == arraySymLang[20]:
                S20 += 1
            elif elemnt2 == arraySymLang[21]:
                S21 += 1
            elif elemnt2 == arraySymLang[22]:
                S22 += 1
            elif elemnt2 == arraySymLang[23]:
                S23 += 1
            elif elemnt2 == arraySymLang[24]:
                S24 += 1
            elif elemnt2 == arraySymLang[25]:
                S25 += 1
            elif elemnt2 == arraySymLang[26]:
                S26 += 1
            elif elemnt2 == arraySymLang[27]:
                S27 += 1
            elif elemnt2 == arraySymLang[28]:
                S28 += 1
                

        # countingWord.append([T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10,
        # T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21,
        # T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32,
        # T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43,
        # E0, E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, 
        # E13, E14, E15, E16, E17, E18, E19, E20, E21, E22, E23, E24, E25,
        # E26,E27,E28,E29,E30,E31,E32,E33,E34,E35,E36,E37,E38,E39,E40,E41,
        # E42,E43,E44,E45,E46,E47,E48,E49,E50,E51,
        # N0, N1, N2, N3, N4, N5, N6, N7, N8, N9,
        # S0, S1, S2, S3, S4, S5, S6, S7, S8, S9, S10,
        # S11, S12, S13, S14, S15, S16, S17, S18, S19, S20, S21,
        # S22, S23, S24, S25, S26, S27])
        
        countingWord.append([T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10,
        T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21,
        T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32,
        T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43,
        T44,T45,T46,T47,T48,T49,T50,T51,T52,T53,T54,T55,T56,T57,
        T58,T59,T60,T61,T62,T63,T64,T65,T66,T67,T68,T69,T70,T71,
        T72,T73,T74,T75,T76,T77,
        E0, E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, 
        E13, E14, E15, E16, E17, E18, E19, E20, E21, E22, E23, E24, E25,
        E26,E27,E28,E29,E30,E31,E32,E33,E34,E35,E36,E37,E38,E39,E40,E41,
        E42,E43,E44,E45,E46,E47,E48,E49,E50,E51,
        N0, N1, N2, N3, N4, N5, N6, N7, N8, N9,
        S0, S1, S2, S3, S4, S5, S6, S7, S8, S9, S10,
        S11, S12, S13, S14, S15, S16, S17, S18, S19, S20, S21,
        S22, S23, S24, S25, S26, S27, S28])
    
    return countingWord

def machine_detect_data(df):
    with open('./model/model_knn.pkl', 'rb') as f:
        clf2 = pickle.load(f)
    predict = clf2.predict(df)
    df['predict'] = predict
    return df

def controller_save_db(df):
    set_save_data = {
        'timing': '',
        'account': '',
        'name': '',
        'amount': '',
        'refcode': ''
    }
    try:
        for idx, el in enumerate(df.predict):
            # print(el)
            if el == 'timing':
                # print(el)
                set_save_data['timing'] = df.word[idx]
            elif el == 'account':
                # print(el)
                set_save_data['account'] = df.word[idx]
            elif el == 'name':
                # print(el)
                set_save_data['name'] = df.word[idx]
            elif el == 'amount':
                # print(el)
                set_save_data['amount'] = df.word[idx]
            elif el == 'refcode':
                # print(el)
                set_save_data['refcode'] = df.word[idx]
        print("set_save_data => ", set_save_data)
        return "Inserted"
    except:
        print("can't insert into datastore.")
        return "can't insert into datastore."


@app.route('/api/debug', methods = ['GET'])
def debuging():
    if request.method == 'GET':
        return "OK"
    

def handle_content_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_blob_api = MessagingApiBlob(api_client)
        message_content = line_bot_blob_api.get_message_content(message_id=event['message']['id'])
    return message_content


@app.route('/api/savedb', methods = ['POST'])
def set_struct():
    if request.method == 'POST':
        req = request.get_json(force=True)
        # print("req => ", req['events'])
        if req['events'][0]['message']['type'] == "image":
            try:
                base64_img = handle_content_message(req['events'][0])
                is_bank = "kbank"
                df = image_to_text(base64_img)
                testing = counting_word(df, arrayThaLang, arrayEngLang, arrayNumLang, arraySymLang)
                set_feature()
                print(testing)
                df_count = pd.DataFrame(data= testing, columns=feature_col)
                
                if is_bank == "kbank":
                    df_count['bank_bll'] = False
                    df_count['bank_kbank'] = True
                    df_count['bank_krungsri'] = False
                    df_count['bank_scb'] = False
                elif is_bank == "krungsri": 
                    df_count['bank_bll'] = False
                    df_count['bank_kbank'] = False
                    df_count['bank_krungsri'] = True
                    df_count['bank_scb'] = False
                elif is_bank == "scb":
                    df_count['bank_bll'] = False
                    df_count['bank_kbank'] = False
                    df_count['bank_krungsri'] = False
                    df_count['bank_scb'] = True
                else:
                    df_count['bank_bll'] = True
                    df_count['bank_kbank'] = False
                    df_count['bank_krungsri'] = False
                    df_count['bank_scb'] = False
                data_predict = machine_detect_data(df_count)
                data_predict['word'] = df.word
                set_per_save = data_predict[['word', 'predict']]
                print("set_per_save => ",set_per_save)
                # status = controller_save_db(set_per_save)
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    line_bot_api.reply_message_with_http_info(
                        ReplyMessageRequest(
                            replyToken=req['events'][0]['replyToken'],
                            messages=[TextMessage(text="Hello image")]
                        )
                    )

            except InvalidSignatureError:
                app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
                abort(400)
        else:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        replyToken=req['events'][0]['replyToken'],
                        messages=[TextMessage(text="Hello world")]
                    )
                )
    return "ok"


if __name__ == '__main__':
    # print(os.environ['HOME'])
    app.run(host="0.0.0.0",port=8085)