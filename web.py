from flask import Flask, render_template, request
from datetime import datetime
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
    return link

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


if __name__ == "__main__":
    app.run(debug=True)
