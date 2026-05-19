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

from flask import Flask, render_template, request, make_response, jsonify
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
    link += "<a href=/movie3>查詢關鍵字</a><hr>"
    link += "<a href=/opendata>臺中市十大肇事路口 </a><hr>"
    link += "<a href=/weather>天氣查詢 </a><hr>"
    link += "<a href=/movie3>查詢關鍵字</a><hr>"
    link += "<a href=/rate>本週新片進DB</a><hr>"
    link += "<a href=/demo>聊天機器人</a><hr>"
    link += "<br><a href=/read>讀取Firestore資料(根據lab遞減排序，取前4)</a><br>"
    link += "<br><a href=/movie2>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    return link

@app.route("/demo")
def demo():
    return render_template("demo.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req["queryResult"]["action"]
    #msg =  req["queryResult"]["queryText"]
    #info = "我是陳楷修設計的電影聊天機器人，動作：" + action + "； 查詢內容：" + msg
    if (action == "rateChoice"):
        rate =  req["queryResult"]["parameters"]["rate"]
        info = "我是陳楷修開發的電影聊天機器人,您選擇的電影分級是：" + rate + "，相關電影：\n"

        db = firestore.client()
        collection_ref = db.collection("本週新片含分級")
        docs = collection_ref.get()
        result = ""
        for doc in docs:
            dict = doc.to_dict()
            if rate in dict["rate"]:
                result += "片名：" + dict["title"] + "\n"
                result += "介紹：" + dict["hyperlink"] + "\n\n"
        info += result
    return make_response(jsonify({"fulfillmentText": info}))



@app.route("/weather", methods=["GET", "POST"])
def weather():
    if request.method == "POST":
        # 從表單獲取使用者輸入的城市
        city = request.form.get("city", "臺中市")
        city = city.replace("台", "臺")
        
        # 氣象局 API 設定
        token = "rdec-key-123-45678-011121314"
        url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={token}&format=JSON&locationName={city}"
        
        try:
            Data = requests.get(url)
            raw_json = json.loads(Data.text)
            
            # 取得氣象資料
            records = raw_json["records"]
            if not records["location"]:
                return f"<h3>找不到「{city}」的資料，請確保輸入正確的縣市名稱（如：臺北市、彰化縣）。</h3><br><a href='/weather'>重新查詢</a>"
            
            WeatherTitle = records["datasetDescription"]
            location_data = records["location"][0]
            
            # 抓取天氣現象 (Wx) 與 降雨機率 (PoP)
            Weather = location_data["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
            Rain = location_data["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
            
            R = f"<h1>{WeatherTitle}</h1>"
            R += f"<h3>查詢城市：{city}</h3>"
            R += f"<p>目前預報：{Weather}</p>"
            R += f"<p>降雨機率：{Rain}%</p>"
            R += "<hr><a href='/weather'>再次查詢</a> | <a href='/'>回首頁</a>"
            return R
            
        except Exception as e:
            return f"查詢出錯：{str(e)} <br><a href='/weather'>返回重試</a>"
            
    else:
        # GET 模式：顯示輸入表單
        html = """
        <h1>氣象即時查詢</h1>
        <form method="POST">
            <label>請輸入縣市名稱（如：臺中市、高雄市）：</label><br>
            <input type="text" name="city" placeholder="例如：臺中市" required>
            <button type="submit">查詢天氣</button>
        </form>
        <br><a href="/">回首頁</a>
        """
        return html

@app.route("/rate")
def rate():
    #本週新片
    url = "https://www.atmovies.com.tw/movie/new/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    lastUpdate = sp.find(class_="smaller09").text[5:]
    print(lastUpdate)
    print()

    result=sp.select(".filmList")

    for x in result:
        title = x.find("a").text
        introduce = x.find("p").text

        movie_id = x.find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw/movie/" + movie_id
        picture = "https://www.atmovies.com.tw/photo101/" + movie_id + "/pm_" + movie_id + ".jpg"

        r = x.find(class_="runtime").find("img")
        rate = ""
        if r != None:
            rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
            if rr == "G":
                rate = "普遍級"
            elif rr == "P":
                rate = "保護級"
            elif rr == "F2":
                rate = "輔12級"
            elif rr == "F5":
                rate = "輔15級"
            else:
                rate = "限制級"

        t = x.find(class_="runtime").text

        t1 = t.find("片長")
        t2 = t.find("分")
        showLength = t[t1+3:t2]

        t1 = t.find("上映日期")
        t2 = t.find("上映廳數")
        showDate = t[t1+5:t2-8]

        doc = {
            "title": title,
            "introduce": introduce,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": int(showLength),
            "rate": rate,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("本週新片含分級").document(movie_id)
        doc_ref.set(doc)
    return "本週新片已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate
    

@app.route("/opendata")
def opendata():
    R = ""
    url = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=a1b899c0-511f-4e3d-b22b-814982a97e41"
    Data = requests.get(url)
    #print(Data.text)

    JsonData = json.loads(Data.text)
    for item in JsonData:
        R += item["路口名稱"] + ",總共發生" + item["總件數"] + "件事故<br>"
    
    return R + "<hr><a href='/'>回首頁</a>"

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
@app.route("/movie2")
def movie2():
  url = "http://www.atmovies.com.tw/movie/next/"
  Data = requests.get(url)
  Data.encoding = "utf-8"
  sp = BeautifulSoup(Data.text, "html.parser")
  result=sp.select(".filmListAllX li")
  lastUpdate = sp.find("div", class_="smaller09").text[5:]

  for item in result:
    picture = item.find("img").get("src").replace(" ", "")
    title = item.find("div", class_="filmtitle").text
    movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
    hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
    show = item.find("div", class_="runtime").text.replace("上映日期：", "")
    show = show.replace("片長：", "")
    show = show.replace("分", "")
    showDate = show[0:10]
    showLength = show[13:]

    doc = {
        "title": title,
        "picture": picture,
        "hyperlink": hyperlink,
        "showDate": showDate,
        "showLength": showLength,
        "lastUpdate": lastUpdate
      }

    db = firestore.client()
    doc_ref = db.collection("電影").document(movie_id)
    doc_ref.set(doc)    
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 


@app.route("/movie3", methods=["GET", "POST"])
def movie3():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        url = "http://www.atmovies.com.tw/movie/next/"
        Data = requests.get(url)
        Data.encoding = "utf-8"
        sp = BeautifulSoup(Data.text, "html.parser")
        result_items = sp.select(".filmListAllX li")
        
        R = f"<h1>電影搜尋結果：{keyword}</h1>"
        found = False
        
        for item in result_items:
            # 取得電影名稱
            img_tag = item.find("img")
            title = img_tag.get("alt") if img_tag else "無標題"
            
            # 只有當關鍵字在標題中時，才顯示
            if keyword in title:
                found = True
                # 取得連結
                a_tag = item.find("a")
                link = "http://www.atmovies.com.tw" + a_tag.get("href") if a_tag else "#"
                
                R += f"<h3><a href='{link}' target='_blank'>{title}</a></h3>"
        
        if not found:
            R += "<p>抱歉，找不到相關電影。</p>"
            
        R += "<hr><a href='/movie3'>重新查詢</a> | <a href='/'>回首頁</a>"
        return R
    
    else:
        # 顯示搜尋表單
        return """
        <h1>電影名稱即時查詢</h1>
        <form method="POST">
            <input type="text" name="keyword" placeholder="請輸入電影名稱關鍵字...">
            <button type="submit">開始爬取與搜尋</button>
        </form>
        <br><a href="/">回首頁</a>
        """

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
