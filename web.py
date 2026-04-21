import os
import json
import firebase_admin
import requests
from bs4 import BeautifulSoup
from firebase_admin import credentials, firestore

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)

from flask import Flask, render_template, request
from datetime import datetime
import firebase_admin
import random
app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>歡迎進入陳楷修的網站首頁!</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>今日日期</a><hr>"
    link += "<a href=/about>關於我</a><hr>"
    link += "<a href=/welcome?u=陳楷修&dep=靜宜資管>welcome</a><hr>"
    link += "<a href=/account>POST傳值</a><hr>"
    link += "<a href=/math>計算機</a><hr>"
    link += "<a href=/cup>擲茭</a><hr>"
    link += "<a href=/read4>查詢</a><hr>"
    link += "<a href=/sp1>爬蟲</a><hr>"
    link += "<a href=/movie>電影查詢</a><hr>"
    link += "<br><a href=/read>讀取Firestore資料(根據lab遞減排序，取前4)</a><br>"
    return link

@app.route("/sp1")
def sp1():
    R = "<h1>爬蟲結果</h1>"
    url = "https://kai-xiu2026-a.vercel.app/about"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    #print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select("td a")


    for item in result:
        R += item.text + "<br>" + item.get("href")+"<br><br>"
    return R

@app.route("/movie")
def movie():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select(".filmListAllX li")
    
    # 建立一個變數來儲存 HTML 結果
    R = "<h1>近期上映電影</h1>"
    
    for item in result:
        # 取得電影名稱
        img_tag = item.find("img")
        title = img_tag.get("alt") if img_tag else "無標題"
        
        # 取得連結
        a_tag = item.find("a")
        link = "http://www.atmovies.com.tw" + a_tag.get("href") if a_tag else "#"
        
        # 組裝成超連結顯示
        R += f"<a href='{link}' target='_blank'>{title}</a><br>"
    
    R += "<hr><a href='/'>回首頁</a>"
    return R

@app.route("/read")
def read():
    Temp = ""
    db = firestore.client()

    collection_ref = db.collection("靜宜資管2026a")
    #docs = collection_ref.where(filter=FieldFilter("mail","==", "tcyang@pu.edu.tw")).get()
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).limit(4).get()
    for doc in docs:
        Temp += str(doc.to_dict()) + "<br>"
    return Temp


@app.route("/read4", methods=["GET", "POST"])
def read4():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        db = firestore.client()
        collection_ref = db.collection("靜宜資管2026a")
        docs = collection_ref.get()
        
        result = f"<h1>查詢結果</h1>"
        result += f"<p>您查詢的關鍵字是：{keyword}</p><hr>"
        
        found = False
        for doc in docs:
            user = doc.to_dict()
            # 實作圖片中的邏輯：判斷關鍵字是否在老師姓名中
            if keyword in user.get("name", ""):
                found = True
                result += f"● {user['name']} 老師的研究室在 {user.get('lab', '未知')}<br>"
        
        if not found:
            result += "抱歉，找不到符合條件的老師。"
            
        result += "<br><br><a href='/read4'>重新查詢</a> | <a href='/'>回首頁</a>"
        return result
    else:
        # 顯示查詢介面
        html = """
        <h1>查詢老師研究室</h1>
        <form method="POST">
            <label>請輸入老師姓名關鍵字：</label>
            <input type="text" name="keyword">
            <button type="submit">查詢</button>
        </form>
        <br><a href="/">回首頁</a>
        """
        return html


@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>回首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    year = str(now.year)
    month = str(now.month)
    day = str(now.day)
    now = year + "年" + month + "月" + day +"日"
    return render_template("today.html", datetime = str(now))

@app.route("/about")
def about():
    return render_template("mis2A.php")

@app.route("/welcome", methods= ["GET"])
def welcome():
    x = request.values.get("u")
    y = request.values.get("dep")
    return render_template("welcome.html",name = x, dep = y)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")
    
@app.route("/math", methods=["GET", "POST"])
def math_action():
    result_text = ""
    
    # 如果使用者是按下按鈕 (POST)
    if request.method == "POST":
        # 從表單 (request.form) 抓取資料
        x = int(request.form.get("x", 0))
        y = int(request.form.get("y", 0))
        opt = request.form.get("opt", "+")
        
        # 搬運你的計算邏輯
        if opt == "/" and y == 0:
            result_text = "除數不得為 0"
        else:
            if opt == "+": result = x + y
            elif opt == "-": result = x - y
            elif opt == "*": result = x * y
            elif opt == "/": result = x / y
            
            result_text = f"{x} {opt} {y} 的結果是：{result}"

    # 最後把結果傳回同一個網頁顯示
    return render_template("math.html", result_text=result_text)

@app.route('/cup', methods=["GET"])
def cup():
    # 檢查網址是否有 ?action=toss
    #action = request.args.get('action')
    action = request.values.get("action")
    result = None
    
    if action == 'toss':
        # 0 代表陽面，1 代表陰面
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)
        
        # 判斷結果文字
        if x1 != x2:
            msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0:
            msg = "笑筊：表示神明一笑、不解，或者考慮中，行事狀況不明。"
        else:
            msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"
            
        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }
        
    return render_template('cup.html', result=result)



if __name__ == "__main__":
    app.run(debug=True)
