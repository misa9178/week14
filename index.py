
import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

from datetime import datetime,timezone, timedelta
from flask import Flask, render_template, request,make_response, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    homepage = "<h1>芦田紗羽Python讀取Firestore</h1>"
    homepage += "<a href=/account>網頁表單輸入實列</a><br><br>"
    homepage += "<a href=/search>課程查詢</a><br><br>"
    homepage += "<br><a href=/movie>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    homepage += "<a href=/input>影片查詢</a><br><br>"
    return homepage

@app.route("/account", methods=["GET" , "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是:" + user + "; 密碼為 :" + pwd
        return result
    else:
        return render_template("account.html")

@app.route("/search", methods=["GET" , "POST"])
def search():
    if request.method == "POST":
        cond = request.form["keyword"]
        result = "您輸入的課程關鍵字是:" + cond

        db = firestore.client()
        collection_ref = db.collection("111")
        docs = collection_ref.get()
        result = ""
        for doc in docs:
            dict = doc.to_dict()
            if cond in dict["Course"]:
                result += dict["Leacture"] + "老師開的" + dict["Course"] + "課程，每週"
                result += dict["Time"] + "於" + dict["Room"] + "上課<br>"

        if result == "":
            result = "抱歉，查無相關條件的選修課程"


        return result
    else:
        return render_template("search.html")

@app.route("/movie")
def movie():
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

        doc_ref = db.collection("電影").document(movie_id)
        doc_ref.set(doc)
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 

@app.route("/input", methods=["POST","GET"])
def input():
    if request.method == "POST":
        MovieTitle = request.form["MovieTitle"]
        info = ""     
        collection_ref = db.collection("電影")
        #docs = collection_ref.where("title","==", "夜鷹的單戀").get()
        docs = collection_ref.order_by("showDate").get()
        for doc in docs:
            if MovieTitle in doc.to_dict()["title"]: 
                info += "片名：" + doc.to_dict()["title"] + "<br>" 
                info += "海報：" + doc.to_dict()["picture"] + "<br>"
                info += "影片介紹：" + doc.to_dict()["hyperlink"] + "<br>"
                info += "片長：" + doc.to_dict()["showLength"] + " 分鐘<br>" 
                info += "上映日期：" + doc.to_dict()["showDate"] + "<br><br>"           
        return info
    else:  
        return render_template("input.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req.get("queryResult").get("action")
    msg =  req.get("queryResult").get("queryText")
    info = "動作：" + action + "； 查詢內容：" + msg
    return make_response(jsonify({"fulfillmentText": info}))

if __name__ == "__main__":
    app.run()

