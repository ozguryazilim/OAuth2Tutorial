from flask import Flask, Response, render_template, redirect, request
import json
import requests

app = Flask("BilkentGNU")


@app.route("/")
def hello_web():
   return "Hello web!"
    #return redirect("/menu")


@app.route("/hello/<name>")
def hello_name(name):
    surname = request.args.get("surname")

    person = {
        "name": name,
        "surname": surname
    }

    person["asd"] = "qwe"
   # return "Hello {} {}".format(person["name"],person["surname"])
    return json.dumps(person)

'''
@app.route("/menu")
def menu():
    content = open("templates/menu.html").read()
    return content
    # return Response(content)
    # return Response(content, content_type="text/html")
'''

users = []

CLIENT_ID = "396e02aa06564e70b4cb787540fe8ffa"
CLIENT_SECRET = "7e70fcd139bd4d0f905779ba54ced5ff"
REDIRECT_URI = "http://127.0.0.1/instagram_login"
ACCESS_TOKEN = None


@app.route("/menu")
def menu():
    return render_template("menu.html", authorized=(ACCESS_TOKEN is not None), CLIENT_ID=CLIENT_ID, REDIRECT_URI=REDIRECT_URI)


@app.route("/instagram_login")
def instagram_login():

        code = request.args.get("code")
        oauth_res = requests.post("https://api.instagram.com/oauth/access_token/", data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "code": code
        })

        print(oauth_res.text)
        res = json.loads(oauth_res.text)

        global ACCESS_TOKEN # wanna modify global ACCESS_TOKEN
        ACCESS_TOKEN = res["access_token"]
        print("access token is %s" % ACCESS_TOKEN)

        return redirect("/menu")


@app.route("/logout")
def logout():
    global ACCESS_TOKEN
    ACCESS_TOKEN = None
    return redirect("/menu")


@app.route("/my_photos")
def my_photos():

    res_get = requests.get("https://api.instagram.com/v1/users/self/media/recent/", params = {
        "access_token": ACCESS_TOKEN
    })
    res_json = json.loads(res_get.text)
    data = res_json["data"]
    medias = []
    for media in data:
        m = {"url": media["images"]["thumbnail"]["url"],
             "id": media["id"]}
        medias.append(m)

    return render_template("my_photos.html", medias=medias)


@app.route("/media/<id>", methods=["GET"])
def image(id):
    media_get = requests.get("https://api.instagram.com/v1/media/" + id, params={
        "access_token": ACCESS_TOKEN
    })
    media = json.loads(media_get.text)
    comments_get = requests.get("https://api.instagram.com/v1/media/" + id + "/comments?access_token=" + ACCESS_TOKEN)
    comments = json.loads(comments_get.text)

    data = {
        "url": media["data"]["images"]["standard_resolution"]["url"],
        "id": media["data"]["id"],
        "comments": []
    }
    for comment in comments["data"]:
        data["comments"].append({
            "text": comment["text"],
            "id": comment["id"]
        })
    return render_template("media.html", media=data)


@app.route("/media/<id>", methods=["POST"])
def post_media(id):
    comment = str(request.form["comment"])
    requests.post("https://api.instagram.com/v1/media/" + id + "/comments", data={
        "access_token": ACCESS_TOKEN,
        "text": comment
    })
    return redirect("/media/"+id)


@app.route("/media/<media_id>/comment/<comment_id>/delete")
def delete_comment(media_id, comment_id):
    requests.delete("https://api.instagram.com/v1/media/"+ media_id + "/comments/" + comment_id, params={
        "access_token": ACCESS_TOKEN
    })
    return redirect("/media/"+media_id)


app.debug = True
app.run(port=80)