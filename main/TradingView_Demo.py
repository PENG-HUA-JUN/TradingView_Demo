import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import yfinance as yf
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import mpl_finance as mpf
import talib

def search(keyword):
    # 清空 Listbox 中的結果
    search_list.clear()
    if len(ticker.get()) > 1:
        # 遍歷資料，將符合條件的結果添加到 Listbox 中
        for item in ticker_list:
            if keyword.lower() in item.lower():
                search_list.append(item)
        ticker['values'] = search_list

def entry_event():  # 載入股票資料
    global df1
    if ticker.get() in ticker_list:
        mylabel['text'] = f"{ticker.get()} 載入成功!!"
        df1 = yf.Ticker(ticker.get()).history(period='max').reset_index()
        df1['Date'] = df1['Date'].dt.strftime('%Y-%m-%d')  # 修改日期格式
    elif ticker.get() == '':
        mylabel['text'] = ''
    else:
        mylabel['text'] = '無效的股票代碼!'

def clear_event():  # 清空所有輸入欄
    ticker.delete(0, "end")
    mylabel['text'] = ''
    mode_period_bar.delete(0,'end')
    mode_startend_bar1.delete(0,'end')
    mode_startend_bar2.delete(0,'end')
    MA_cust_entry1.delete(0,"end")
    MA_cust_entry2.delete(0,"end")

def draw():
    global df1,fig,canvas,frame,toolbar,ind_value_total,on_VOL,on_KD,on_MACD,on_RSI,on_BIAS,on_ADX,on_BOL
    if date_mode.get() == 1:
        s,e = df1['Date'].iloc[-int(mode_period_bar.get())], df1['Date'].max()
    elif date_mode.get() == 2:
        s,e = mode_startend_bar1.get(),mode_startend_bar2.get()
    df2 = df1[df1["Date"].between(s,e)].reset_index()
    def candlestick(axe):
        axe.set_xticks(range(0, len(df2.index), 15))
        axe.set_xticklabels(df2['Date'][::15])
        mpf.candlestick2_ochl(axe, df2['Open'], df2['Close'], df2['High'], df2['Low'], width=0.6, colorup='r',
                              colordown='g', alpha=1)
        axe.grid(linestyle='dotted',alpha=0.7)

    def draw_subs(axe,check):
        axe.set_xticks(range(0, len(df2.index), 15))
        axe.set_xticklabels(df2['Date'][::15])
        axe.grid(linestyle='dotted', alpha=0.7)
        if check == 'VOL':
            mpf.volume_overlay(axe, df2['Open'], df2['Close'], df2['Volume'], colorup='r',
                               colordown='g', width=0.6,alpha=1)

        elif check == 'KD':
            df1['k'], df1['d'] = talib.STOCH(df1['High'], df1['Low'], df1['Close'],
                                             fastk_period=9, slowk_period=3,
                                             slowk_matype=1, slowd_period=3, slowd_matype=1)
            df_sub = df1[df1["Date"].between(s,e)].reset_index()
            axe.plot(df_sub['k'], label='K9')
            axe.plot(df_sub['d'], label='D9')
        elif check == 'MACD':
            df1['MACD'], df1['DIF9'], df1['EMA'] = talib.MACD(df1['Close'])
            df_sub = df1[df1["Date"].between(s,e)].reset_index()
            axe.plot(df_sub['MACD'], label='MACD')
            axe.plot(df_sub['DIF9'], label='DIF9')
            up = list(zip(*[(n, i) for n, i in enumerate(df_sub['EMA']) if i >= 0]))
            down = list(zip(*[(n, i) for n, i in enumerate(df_sub['EMA']) if i < 0]))
            axe.bar(up[0], up[1], color='r')
            axe.bar(down[0], down[1], color='g')

        elif check == 'RSI':
            df1['rsi7'] = talib.RSI(df1['Close'], timeperiod=7)
            df1['rsi14'] = talib.RSI(df1['Close'], timeperiod=14)
            df_sub = df1[df1["Date"].between(s,e)].reset_index()
            axe.plot(df_sub['rsi7'], label='rsi7')
            axe.plot(df_sub['rsi14'], label='rsi14')
        elif check == 'BIAS':
            df1['bias_6'] = (df1['Close'] - df1['Close'].rolling(6, min_periods=1).mean()) / df1['Close'].rolling(6,
                                                                                                                  min_periods=1).mean() * 100
            df1['bias_12'] = (df1['Close'] - df1['Close'].rolling(12, min_periods=1).mean()) / df1['Close'].rolling(12,
                                                                                                                    min_periods=1).mean() * 100
            df1['bias_24'] = (df1['Close'] - df1['Close'].rolling(24, min_periods=1).mean()) / df1['Close'].rolling(24,
                                                                                                                    min_periods=1).mean() * 100
            df_sub = df1[df1["Date"].between(s, e)].reset_index()
            axe.plot(round(df_sub['bias_6'], 2), label='bias6')
            axe.plot(round(df_sub['bias_12'], 2), label='bias12')
            axe.plot(round(df_sub['bias_24'], 2), label='bias24')
        elif check == 'ADX':
            df1['adx'] = talib.ADX(df1['High'], df1['Low'], df1['Close'], timeperiod=14)
            df1['pdi'] = talib.PLUS_DI(df1['High'], df1['Low'], df1['Close'], timeperiod=14)
            df1['mdi'] = talib.MINUS_DI(df1['High'], df1['Low'], df1['Close'], timeperiod=14)
            df_sub = df1[df1["Date"].between(s, e)].reset_index()
            axe.plot(df_sub['adx'], label='ADX')
            axe.plot(df_sub['pdi'], label="+DI")
            axe.plot(df_sub['mdi'], label="-DI")

    try:
        # 建立視窗
        fig = plt.figure()   # 清空fig
        fig.suptitle(ticker.get())  # 設定圖表名稱
        ind_dict = {'VOL': on_VOL.get(), 'KD': on_KD.get(), 'MACD': on_MACD.get(), 'RSI': on_RSI.get(), 'BIAS': on_BIAS.get(), 'ADX': on_ADX.get()}
        ind_choice = [i for i, n in ind_dict.items() if n == 1]

        if ind_value_total == 0:  # 1張圖
            ax1 = fig.add_axes([0.05, 0.1, 0.9, 0.85])
            candlestick(ax1)

        elif ind_value_total == 1:  # 2張圖
            ax1 = fig.add_axes([0.05, 0.3, 0.9, 0.65])
            ax2 = fig.add_axes([0.05, 0.1, 0.9, 0.2])
            ax1.sharex(ax2)   # 同時縮放
            candlestick(ax1)
            for i in ind_choice:
                draw_subs(ax2,i)

        elif ind_value_total == 2:   # 三張圖
            ax1 = fig.add_axes([0.05, 0.5, 0.9, 0.45])
            ax2 = fig.add_axes([0.05, 0.3, 0.9, 0.2])
            ax3 = fig.add_axes([0.05, 0.1, 0.9, 0.2])
            ax1.sharex(ax2)
            ax2.sharex(ax3)
            candlestick(ax1)
            for i in ind_choice:
                draw_subs(ax2,i)
                break
            ind_choice.remove(i)
            for i in ind_choice:
                draw_subs(ax3,i)

        elif ind_value_total == 3:  # 四張圖
            ax1 = fig.add_axes([0.05, 0.7, 0.9, 0.25])
            ax2 = fig.add_axes([0.05, 0.5, 0.9, 0.2])
            ax3 = fig.add_axes([0.05, 0.3, 0.9, 0.2])
            ax4 = fig.add_axes([0.05, 0.1, 0.9, 0.2])
            ax1.sharex(ax2)
            ax2.sharex(ax3)
            ax3.sharex(ax4)
            candlestick(ax1)
            for i in ind_choice:
                draw_subs(ax2,i)
                break
            ind_choice.remove(i)
            for i in ind_choice:
                draw_subs(ax3,i)
                break
            ind_choice.remove(i)
            for i in ind_choice:
                draw_subs(ax4,i)

        # 均線
        if MA5_value.get():
            df1['sma_5'] = talib.SMA(np.array(df1['Close']), 5)
            df_sub = df1[(df1['Date'] >= s) & (df1['Date'] <= e)].reset_index()
            ax1.plot(df_sub['sma_5'], label='5日均線', alpha=0.8)
        if MA20_value.get():
            df1['sma_20'] = talib.SMA(np.array(df1['Close']), 20)
            df_sub = df1[(df1['Date'] >= s) & (df1['Date'] <= e)].reset_index()
            ax1.plot(df_sub['sma_20'], label='20日均線', alpha=0.8)
        if MA60_value.get():
            df1['sma_60'] = talib.SMA(np.array(df1['Close']), 60)
            df_sub = df1[(df1['Date'] >= s) & (df1['Date'] <= e)].reset_index()
            ax1.plot(df_sub['sma_60'], label='60日均線', alpha=0.8)
        if MAcust1_value.get():
            d = int(MA_cust_entry1.get())
            df1['sma_cust1'] = talib.SMA(np.array(df1['Close']), d)
            df_sub = df1[(df1['Date'] >= s) & (df1['Date'] <= e)].reset_index()
            ax1.plot(df_sub['sma_cust1'], label=f'{d}日均線', alpha=0.8)
        if MAcust2_value.get():
            d = int(MA_cust_entry2.get())
            df1['sma_cust2'] = talib.SMA(np.array(df1['Close']), d)
            df_sub = df1[(df1['Date'] >= s) & (df1['Date'] <= e)].reset_index()
            ax1.plot(df_sub['sma_cust2'], label=f'{d}日均線', alpha=0.8)
        # 布林通道
        if on_BOL.get():  # https://ithelp.ithome.com.tw/m/articles/10268243
            df1['BU'], df1['BM'], df1['BL'] = talib.BBANDS(df1['Close'],
                                                           timeperiod=5,nbdevup=2,
                                                           nbdevdn=2,matype=0)
            df_sub = df1[(df1['Date'] >= s) & (df1['Date'] <= e)].reset_index()
            ax1.plot(df_sub['BU'], color='b', alpha=0.3, label='布林通道')
            ax1.plot(df_sub['BM'], color='orange', alpha=0.3, label='中線')
            ax1.plot(df_sub['BL'], color='b', alpha=0.3)

        # 添加圖例
        ax1.legend(loc="upper left")
        if ind_value_total >= 1: ax2.legend(loc="upper left")
        if ind_value_total >= 2: ax3.legend(loc="upper left")
        if ind_value_total == 3: ax4.legend(loc="upper left")
        # 更新圖表
        frame.destroy()  # 刪除舊工具列

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.get_tk_widget().place(x=20, y=210, relwidth=0.97, relheight=0.7)
        canvas.draw()
        frame = tk.Frame(root)
        frame.pack(side='bottom', fill='x')
        toolbar = NavigationToolbar2Tk(canvas, frame)
        mylabel['text']=f"{ticker.get()} 輸出成功!!"

    except:
        mylabel['text']='無效的操作!'


# 建立視窗
root = tk.Tk()
root.title("看盤軟體_Demo")
root.geometry('1000x750+200+30')
root.iconbitmap("icon.ico")
# 視窗風格
style = ttk.Style()
style.theme_use('clam')  # 'winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative'

# 股票列表
ticker_list = open("ticker_list.txt").read().split()
search_list = []

# 預設圖表欄
fig = plt.figure()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().place(x=20, y=210, relwidth=0.97, relheight=0.7)
frame = tk.Frame(root)
frame.pack(side='bottom', fill='x')
toolbar = NavigationToolbar2Tk(canvas, frame)

# 設定按鈕選項資料型態
date_mode = tk.IntVar()
MA5_value = tk.IntVar()
MA20_value = tk.IntVar()
MA60_value = tk.IntVar()
MAcust1_value = tk.IntVar()
MAcust2_value = tk.IntVar()
on_VOL = tk.IntVar()
on_KD = tk.IntVar()
on_MACD = tk.IntVar()
on_RSI = tk.IntVar()
on_BIAS = tk.IntVar()
on_ADX = tk.IntVar()
on_BOL = tk.IntVar()
ind_value_total = 0   # 用來判斷選了幾個指標
df1 = []

# 設計tk視窗
# 第一行-輸入股票代碼
ticker = ttk.Combobox(root, width=28,values=search_list)
ticker.bind("<KeyRelease>", lambda event: search(ticker.get()))
ticker.place(x=10,y=14)
ttk.Button(root, text='確認', command=entry_event, width=5).place(x=240,y=8)
ttk.Button(root, text='清除', command=clear_event, width=5).place(x=290,y=8)
# 第二行-提示欄
mylabel = tk.Label(root)
mylabel.place(x=10,y=36)
# 第三行-時間選項(天數)
tk.Radiobutton(root, text="天數", width=30, anchor="w",variable=date_mode,value=1).place(x=10,y=60)
mode_period_bar = tk.Entry(root,width=10)
mode_period_bar.place(x=90,y=60)
# 第四行-時間選項(區間)
tk.Radiobutton(root, text="區間", width=30, anchor='w',variable=date_mode,value=2).place(x=10,y=90)
mode_startend_bar1 = DateEntry(root, width=12, background='darkblue',foreground='white', borderwidth=2,date_pattern='yyyy-mm-dd')
mode_startend_bar1.place(x=90,y=90)
tk.Label(root,text='~').place(x=200,y=90) # 波浪符
mode_startend_bar2 = DateEntry(root, width=12, background='darkblue',foreground='white', borderwidth=2,date_pattern='yyyy-mm-dd')
mode_startend_bar2.place(x=220,y=90)
# 第五行-均線選項
ttk.Label(root, text="均線選項: ").place(x=10,y=120)
tk.Checkbutton(root,text="5日",variable=MA5_value, onvalue=1,offvalue=0).place(x=70,y=130,anchor='w')
tk.Checkbutton(root,text="20日",variable=MA20_value, onvalue=1,offvalue=0).place(x=120,y=130,anchor='w')
tk.Checkbutton(root,text="60日",variable=MA60_value, onvalue=1,offvalue=0).place(x=180,y=130,anchor='w')
tk.Checkbutton(root,text="自訂1(日):",variable=MAcust1_value, onvalue=1,offvalue=0).place(x=240,y=130,anchor='w')
tk.Checkbutton(root,text="自訂2(日):",variable=MAcust2_value, onvalue=1,offvalue=0).place(x=370,y=130,anchor='w')
# 自訂均線輸入框
MA_cust_entry1 = tk.Entry(root,width=5,justify=tk.RIGHT)
MA_cust_entry2 = tk.Entry(root,width=5,justify=tk.RIGHT)
MA_cust_entry1.place(x=320,y=120)
MA_cust_entry2.place(x=450,y=120)
# 第六行-輸出按鈕
output_buttom = ttk.Button(root,text="輸出圖表",command=draw)
output_buttom.place(x=20,y=150,relwidth=0.97,relheight=0.05)
# 技術指標選單
ind_frame = tk.Frame(root,width=410, height=130,highlightbackground="grey", highlightthickness=2)
ind_frame.place(x=550, y=10)

def limit_ind(current):
    global on_VOL,on_KD,on_MACD,on_RSI,on_BIAS,on_ADX,ind_value_total
    if ind_value_total >= 3:
        current.set(0)
    ind_value_total = on_VOL.get()+on_KD.get()+on_MACD.get()+on_RSI.get()+on_BIAS.get()+on_ADX.get()

tk.Label(ind_frame,text="技術指標:", anchor="w").place(x=10,y=10)
tk.Checkbutton(ind_frame, text = "交易量", width=20, anchor="w",variable=on_VOL,onvalue=1,offvalue=0,command=lambda :limit_ind(on_VOL)).place(x=10, y=30)
tk.Checkbutton(ind_frame, text = "KD", width=20, anchor="w",variable=on_KD,onvalue=1,offvalue=0,command=lambda :limit_ind(on_KD)).place(x=10, y=50)
tk.Checkbutton(ind_frame, text = "MACD", width=20, anchor="w",variable=on_MACD,onvalue=1,offvalue=0,command=lambda :limit_ind(on_MACD)).place(x=10, y=70)
tk.Checkbutton(ind_frame, text = "RSI", width=20, anchor="w",variable=on_RSI,onvalue=1,offvalue=0,command=lambda :limit_ind(on_RSI)).place(x=200, y=30)
tk.Checkbutton(ind_frame, text = "BIAS", width=20, anchor="w",variable=on_BIAS,onvalue=1,offvalue=0,command=lambda :limit_ind(on_BIAS)).place(x=200, y=50)
tk.Checkbutton(ind_frame, text = "ADX", width=20, anchor="w",variable=on_ADX,onvalue=1,offvalue=0,command=lambda :limit_ind(on_ADX)).place(x=200, y=70)
tk.Checkbutton(ind_frame, text = "Bollinger Band", width=20, anchor="w",variable=on_BOL,onvalue=1,offvalue=0).place(x=10, y=90)

# 執行主迴圈
root.mainloop()