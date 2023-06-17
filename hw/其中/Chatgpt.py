#!/usr/bin/env python
# coding: utf-8

# In[1]:


from tkinter import *
import ctypes
import time
import numpy as np
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt, animation
import pyaudio
import wave
import threading
import speech_recognition as sr
import openai
import pyttsx3 
import whisper
import inspect
import sys
import pygame
pygame.init()
pygame.mixer.init()
stop_event = threading.Event()
class SoundThread(threading.Thread):
    def __init__(self, stop_event):
        threading.Thread.__init__(self)
        self.stop_event = stop_event
        self.sound = pygame.mixer.Sound('try.wav')
        
    def run(self):
        self.sound.play()
        #while not self.stop_event.is_set():
        while not self.stop_event.is_set() and pygame.mixer.get_busy():
            time.sleep(0.1)
        self.sound.stop()
class basic_player():    
    def __init__(self, root):
        # BUILD ROOT 
        self.root = root
        root.geometry('1000x500')
        root.resizable(width=0, height=0)
        root.title('Playback')
        self.sound_thread = SoundThread(stop_event)
        self.stream_thread = threading.Thread(target = self.llk)
        self.audio_thread = threading.Thread(target = self.play_audio)
        self.a = StringVar()   # 文字互動內容
        self.a.set('聽音')
        self.b = StringVar()   # 對話文字紀錄
        self.b.set('')
        self.kk=False
        self.di=False
        self.messages=[
            {"role": "system", "content": "#zh-tw You are a chatbot"},
        ]
        #左半區
        button_frame_ = Frame(self.root,height=500)
        button_frame_.grid(column = 0, row =0,sticky = 'nsew')
        button_frame = Frame(button_frame_,bg='yellow')
        button_frame.grid(column = 0, row =0, sticky = 'nw')
        
        #self.stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)
        #self.anim.event_source.stop()        
        self.val = StringVar()  # 語音辨識選擇區
        self.val.set(1)
        # 放入第一個 Radiobutton
        radio_btn1 = Radiobutton(button_frame, text='Google(較快)',variable=self.val, value=1)
        radio_btn1.grid(column = 0, row =0)
        radio_btn1.select()   # 選擇第一個 Radiobutton
        radio_btn2 =Radiobutton(button_frame, text='Whisper(較準)',variable=self.val, value=2)
        radio_btn2.grid(column = 1, row =0)
        
        self.opengpt = StringVar()  # 語音回答選擇區
        self.opengpt.set(1)
        radio_btn1 = Radiobutton(button_frame, text='Gpt3.0(較快)',variable=self.opengpt, value=1)
        radio_btn1.grid(column = 0, row =1)
        radio_btn1.select()   # 選擇第一個 Radiobutton
        radio_btn2 =Radiobutton(button_frame, text='Gpt3.5(較準)',variable=self.opengpt, value=2)
        radio_btn2.grid(column = 1, row =1)
        
        
        btn_play = Button(button_frame,text = '直接對話',command = self.buttons_command_play,state = 'normal',width = 10)
        btn_play.grid(column = 0, row =2, sticky = 'nsew', padx = 10, pady = 10)#位置
        btn_play = Button(button_frame,text = '多對話測試',command = self.aaa,state = 'normal',width = 10)
        btn_play.grid(column = 0, row =3, sticky = 'nsew', padx = 10, pady = 10)#位置
        btn_play = Button(button_frame,text = '終止',command = self.oo,state = 'normal',width = 10)
        btn_play.grid(column = 0, row =4, sticky = 'nsew', padx = 10, pady = 10)#位置
        btn_play = Button(button_frame,text = '終止功能測試',command = self.listenn,state = 'normal',width = 10)
        btn_play.grid(column = 0, row =5, sticky = 'nsew', padx = 10, pady = 10)#位置
        btn_play = Button(button_frame,text = '執行緒測試',command = self.thread_now,state = 'normal',width = 10)
        btn_play.grid(column = 0, row =6, sticky = 'nsew', padx = 10, pady = 10)#位置
        btn_play = Button(button_frame,text = '對話歸零',command = self.zero,state = 'normal',width = 10)
        btn_play.grid(column = 0, row =7, sticky = 'nsew', padx = 10, pady = 10)#位置
        btn_play = Button(button_frame,text = '最新對話刪除',command = self.cut,state = 'normal',width = 10)
        btn_play.grid(column = 0, row =8, sticky = 'nsew', padx = 10, pady = 10)#位置
        
        mylabel =Label(button_frame_, textvariable=self.a,font=('Arial',18),bg='red')   # 內容是 a 變數
        mylabel.grid(column = 0, row =1,pady=50,padx = 10,sticky = 'NSW')
        
        
        
        # 建立 Frame(右半區)
        
        dialogue_frame = Frame(self.root, width = 500,bg='blue')
        dialogue_frame.grid(column = 1, row =0,padx =20, sticky = 'NE')
        self.myentry = Entry(dialogue_frame,width=50)#密鑰輸入
        self.myentry.grid(column=0,row=0)
        ''''''
        mylabel_c = Label(dialogue_frame, text='對話語錄')
        mylabel_c.grid(column =0, row =1)
        
        frame =Frame(dialogue_frame,width = 500)   # 建立 Frame(對話區)
        frame.grid(column =0, row =2,sticky = 'nw')
        
        canvas = Canvas(frame, width=500, height=300, scrollregion=(0, 0,600, 800))
        canvas.grid(row=0, column=0)        
        scrollbar =Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="NS")
       
        mylabel_b=Message(canvas,width=450 ,textvariable=self.b, font=('Arial',15))   # 內容是 b 變數(對話內容)
        
        mylabel_b.grid()

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=mylabel_b, anchor="nw")
        
    def cut(self):
        self.messages.pop()
        self.oo()
        e=self.dialogue()
    def dialogue(self):
        #print(self.messages)
        aa=''
        dd=''
        for i in range(1,len(self.messages)):
            e=self.messages[i]['role']
            cc=self.messages[i]['content']            
            if cc!="":
                if e=="user":
                    dd+="Q:"
                else:                
                    dd+="A:"
                aa+=cc
                aa+="\n"
                dd+=cc
                dd+="\n"
            else:
                pass
        self.b.set(dd)
        return aa
    def zero(self):
        self.messages=[
            {"role": "system", "content": "#zh-tw You are a chatbot"},
        ]        
        self.oo()
        e=self.dialogue()    
    def thread_now(self):
        '''
        rr=""
        for thread in threading.enumerate():
            t= "Running thread: " + thread.getName() + " ID: " + str(thread.ident)
            rr+="\n"
            rr+=t
        '''
        rr="sound_thread:"+str(self.sound_thread.is_alive())        
        rr+='\n'
        rr+="stream_thread:"+str(self.stream_thread.is_alive())
        rr+='\n' 
        rr+="audio_thread:"+str(self.audio_thread.is_alive())
        self.a.set(rr)
        

        
    def aaa(self):
        ee="依絲在清晨起床，匆匆洗漱之後便出門前往工作。她是一名小名氣自媒體，每天都會到各處採訪新聞。"
        #ee+="\ndskfnejbievon eihr voehvp ehvisbiobvapoeh\naieubvribbvribviaehjfiorv"
        self.b.set(ee) 
        self.talk(ee)     
    def oo(self):
        if self.sound_thread.is_alive():
            stop_event.set()
            self.sound_thread.join()
                

    def listenn(self):
        self.a.set("收音中...")
        self.kk=True
        self.stream_thread = threading.Thread(target = self.llk)
        self.stream_thread.start()
        #self.llk()

    def llk(self):
        if not self.sound_thread.is_alive() and self.di:
            self.kk=False
            self.audio_thread = threading.Thread(target = self.play_audio)
            self.audio_thread.start()
        if self.kk:            
            p = pyaudio.PyAudio()
            self.stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)
            frames = []                      # 建立聲音串列
            for i in range(0, int(fs / chunk * 3)):
                datta = self.stream.read(chunk)                
                frames.append(datta)          # 將聲音記錄到串列中
            wf = wave.open(filename, 'wb')   # 開啟聲音記錄檔
            wf.setnchannels(channels)        # 設定聲道
            wf.setsampwidth(p.get_sample_size(sample_format))  # 設定格式
            wf.setframerate(fs)              # 設定取樣頻率
            wf.writeframes(b''.join(frames)) # 存檔
            wf.close() 

        
            r = sr.Recognizer()
            WAV = sr.AudioFile("oxxostudio.wav" )
            self.stream.close()
            p.terminate
            try:
                with WAV as source:
                    audio = r.record(source)
                    txt=r.recognize_google(audio,language="zh-TW")
                    self.a.set(txt)
                    if "天氣" in txt:
                        self.oo()
                        
                    elif "魔鏡"in txt or"郭靜" in txt:
                        self.oo()
                        #self.sound_thread.join() 
                        self.talk(completed_text="為您服務")                   
                        self.a.set("為您服務")
                        if not self.audio_thread.is_alive():
                            self.audio_thread = threading.Thread(target = self.play_audio)
                            self.audio_thread.start()
                    #self.llk()
                    
                    elif "結束" in txt:
                        self.oo()
                    else:          
                        self.llk()
                    
                    
            except sr.UnknownValueError:    
                self.llk()
        else:
            pass
       
            
            
    def buttons_command_play(self):#錄音按鈕
        self.messages=[
            {"role": "system", "content": "#zh-tw You are a chatbot"},
        ]
        self.audio_thread = threading.Thread(target = self.play_audio)
        self.audio_thread.start()
    def play_audio(self):#錄音程式 
        if self.sound_thread.is_alive():
            self.sound_thread.join()
        self.a.set("開始錄音...")
        r = sr.Recognizer()
        self.kk=False
# set the microphone as the audio source
        with sr.Microphone() as source:
            audio = r.listen(source)

# save the audio as a WAV file
        with open("output.wav", "wb") as f:
                f.write(audio.get_wav_data())        
        self.a.set("錄音結束")
        
        if self.val.get()=='1':
            self.google_stt()
        else:####
            self.whisper_stt()
        
    def whisper_stt(self):
        self.a.set("語音辨識中...")
        result = model.transcribe("output.wav",fp16=False)
        txt=result["text"]
        if "結束" in txt:
            self.talk(completed_text="掰掰")
            self.messages.append({
            "role":"system",
            "content":"掰掰"
         })
            self.di=False
            tt=self.dialogue() 
        else:######
            self.openaii(txt=txt)
    def google_stt(self):
        self.a.set("語音辨識中...")
        r = sr.Recognizer()
        WAV = sr.AudioFile("output.wav" )
        try:
            with WAV as source:
                audio = r.record(source)
                txt=r.recognize_google(audio,language="zh-TW")
                if "結束" in txt:
                    self.talk(completed_text="掰掰")
                    self.messages.append({"role":"system","content":"掰掰"})
                    self.di=False
                    tt=self.dialogue() 
                else:#77
                    self.openaii(txt=txt)
        except sr.UnknownValueError:
            self.a.set("語音無法辨識\n")
            self.play_audio()
        except sr.RequestError as e:
            self.a.set("沒有語音輸入\{0}n".format(e))
            self.play_audio()
                #self.a.set('錄音結束...')
            '''
        finally:
            self.stream.stop_stream()
            self.stream.close()
            p.terminate()
        #if
        ''' 
    def openaii(self,txt=''):
        self.messages.append({
            "role":"user",
            "content":txt
         })
        tt=self.dialogue()
        try:
            self.a.set("語音生成中...\n")
            if self.myentry.get()=="":
                self.a.set("無openai金鑰")
            else:            
                openai.api_key =self.myentry.get()
                
           
                #openai.api_key =self.myentry.get() 
                
            
                if self.opengpt.get()=='1':
                    response = openai.Completion.create(engine="text-davinci-003",prompt="#zh-tw"+tt,
                                                    max_tokens=100,temperature=0.6,)
                    completed_text = response["choices"][0]["text"]
                else:
                    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                            messages=self.messages,
                                                            temperature=0.6,max_tokens=100,n=1)
                    
                    completed_text=response['choices'][0]['message']['content']
                self.messages.append({
            "role":"system",
            "content":completed_text
         })                
                
                tt=self.dialogue()    
                self.talk(completed_text=completed_text)
                self.kk=True
                self.di=True
                if self.kk:
                    self.listenn()
                #self.sound_thread.join()
                #self.a.set("語音結束")
                #self.play_audio()
        except openai.error.RateLimitError:
            self.a.set("網路錯誤\n")
            
        except openai.error.AuthenticationError or openai.error.APIConnectionError:
            self.a.set("金鑰錯誤\n")
            
        
    def talk(self,completed_text=""):
        teacher = pyttsx3.init() 
        voices = teacher.getProperty('voices') 
        teacher.setProperty('voice', voices[0].id)
        teacher.save_to_file(completed_text , 'try.wav')
        #teacher.say(completed_text)
        teacher.runAndWait()
        stop_event.clear()
        self.sound_thread = SoundThread(stop_event)
        self.sound_thread.start()

            
root = Tk()
root.title("tkinter and matplotlib")
matplotlib.use('TkAgg')        

chunk = 1024*16                     # 記錄聲音的樣本區塊大小
sample_format = pyaudio.paInt16  # 樣本格式，可使用 paFloat32、paInt32、paInt24、paInt16、paInt8、paUInt8、paCustomFormat
channels = 1                     # 聲道數量
fs = 44100                       # 取樣頻率，常見值為 44100 ( CD )、48000 ( DVD )、22050、24000、12000 和 11025。
#seconds = 3                      # 錄音秒數
filename = "oxxostudio.wav"      # 錄音檔名
            # 建立 pyaudio 物件
model = whisper.load_model("base")
basic_player(root)
root.mainloop()


# In[ ]:


import tkinter as tk
import random
def add_rectangle_and_text():
    # 隨機生成方框位置和文字內容
    x1 = random.randint(50, 350)
    y1 = random.randint(50, 350)
    x2 = x1 + 100
    y2 = y1 + 50
    text_content = "Text"

    # 在畫布上追加方框
    rectangle = canvas.create_rectangle(x1, y1, x2, y2, fill="blue")

    # 在方框中追加文字
    text = canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=text_content, fill="white")

# 建立主視窗
root = tk.Tk()

# 建立Canvas
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()

# 在畫布上追加方框和文字按鈕
button = tk.Button(root, text="Add Rectangle and Text", command=add_rectangle_and_text)
button.pack()

# 執行主迴圈
root.mainloop()


# In[ ]:


import tkinter as tk

def toggle_buttons():
    # 迭代所有按鈕，除了toggle_button以外，進行顯示或隱藏的切換
    for button in buttons:
        if button != toggle_button:
            if button.winfo_exists():  # 確認按鈕是否存在
                if button.winfo_viewable():  # 檢查按鈕是否可見
                    button.grid_remove()  # 隱藏按鈕
                else:
                    button.grid()  # 顯示按鈕

# 建立主視窗
root = tk.Tk()

# 建立按鈕列表
buttons = []

# 建立一個按鈕，觸發toggle_buttons函式
toggle_button = tk.Button(root, text="Toggle Buttons", command=toggle_buttons)
toggle_button.grid(row=0, column=0)
buttons.append(toggle_button)

# 建立其他按鈕
button1 = tk.Button(root, text="Button 1")
button1.grid(row=1, column=0)
buttons.append(button1)

button2 = tk.Button(root, text="Button 2")
button2.grid(row=2, column=0)
buttons.append(button2)

# 建立其他元素
label = tk.Label(root, text="Other Elements")
label.grid(row=3, column=0)

# 執行主迴圈
root.mainloop()


# In[5]:


import tkinter as tk

def toggle_buttons():
    # 迭代所有按鈕，除了toggle_button以外，進行顯示或隱藏的切換
    for button in buttons:
        if button != toggle_button:
            if button.winfo_exists():  # 確認按鈕是否存在
                if button.winfo_viewable():  # 檢查按鈕是否可見
                    button.grid_remove()  # 隱藏按鈕
                else:
                    button.grid()  # 顯示按鈕

# 建立主視窗
root = tk.Tk()

# 建立按鈕列表
buttons = []

# 建立其他按鈕
button1 = tk.Button(root, text="Button 1")
button1.grid(row=0, column=0)
buttons.append(button1)

button2 = tk.Button(root, text="Button 2")
button2.grid(row=1, column=0)
buttons.append(button2)

# 建立一個按鈕，觸發toggle_buttons函式
toggle_button = tk.Button(root, text="Toggle Buttons", command=toggle_buttons)
toggle_button.grid(row=2, column=0)
buttons.append(toggle_button)

# 建立其他元素
label = tk.Label(root, text="Other Elements")
label.grid(row=3, column=0)

# 執行主迴圈
root.mainloop()


# In[ ]:




