from ast import NameConstant
from operator import truediv
import os
import profile
from pydoc import doc
import shutil
import glob
from statistics import mode
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

#ボットトークンを使ってアプリを初期化
app = App(token = os.environ.get("SLACK_BOT_TOKEN"))

dir = os.path.dirname(__file__)
if(os.getcwd != dir):
    os.chdir(dir)

#WorkStation名一覧を取得
WSPath = "./WorkStations"
WSName = []
files = os.listdir(WSPath)
files_name = [f for f in files if os.path.isfile(os.path.join(WSPath, f))]
for name in files_name:
    name = name[:-4]
    WSName.append(name)

#グローバル変数
run_stat = True
run_userinfo = True
WSUser = ["none"]*len(WSName)
update_WSUser = False

with open(".\\wsuser.txt", mode="r") as file:
    lines = file.read()
    count_line = 0
    for line in lines.split("\n"):
        WSUser[count_line] = line
        count_line += 1

#以下bot処理

#DM開始
@app.message("opendm")
def open_dm(message):
    user = message['user']
    im = app.client.conversations_open(users=user)
    im_id = im['channel']['id']
    app.client.chat_postMessage(channel=im_id,text="channel open")

#リモートアクセス状況の確認
@app.message("stat")
def stat(body,say):
    global run_stat
    text = body2text(body)
    if(run_stat):
        run_stat = False
        if(text == "stat"):
            for name in WSName:
                stat_say = make_stat(name)
                say(stat_say)
        else:
            for name in WSName:
                if(name in text.lower()):
                    stat_say = make_stat(name)
                    say(stat_say)
        run_stat = True
    else:
        say("他の利用状況の確認を実行中です。もう少ししてから再度実行してください")

#利用開始の記録
@app.message("use")
def start_use(body,message,say):
    global run_userinfo
    global WSName
    global update_WSUser
    if(run_userinfo):
        run_userinfo = False
        user = message['user']
        text = body2text(body)
        if(text == "use"):
            for name in WSName:
                use_ws(name,user,say)
        else:
            for name in WSName:
                if(name in text.lower()):
                    use_ws(name,user,say)
        if(update_WSUser):
            with open(".\\wsuser.txt", mode="w") as file:
                write_list = "\n".join(WSUser)
                file.write(write_list)
            update_WSUser = False
        run_userinfo = True
    else:
        say("他の処理を行っているため、もう少ししてから再度実行してください")

#利用終了の記録
@app.message("end")
def end_use(body,message,say):
    global run_userinfo
    global WSName
    global update_WSUser
    if(run_userinfo):
        run_userinfo = False
        user = message['user']
        text = body2text(body)
        if(text == "end"):
            for name in WSName:
                end_ws(name,user,say)
        else:
            for name in WSName:
                if(name in text.lower()):
                    end_ws(name,user,say)
        if(update_WSUser):
            with open(".\\wsuser.txt", mode="w") as file:
                write_list = "\n".join(WSUser)
                file.write(write_list)
            update_WSUser = False
        else:
            say("他の処理を行っているため、もう少ししてから再度実行してください")

#アクセス情報確認
@app.message("pass")
def view_pass(body,say):
    global run_stat
    global WSName
    if(run_stat):
        run_stat = False
        text = body2text(body)
        if(text == "pass"):
            for name in WSName:
                say_pass = check_pass(name)
                say(say_pass)
        else:
            for name in WSName:
                if(name in text.lower()):
                    say_pass = check_pass(name)
                    say(say_pass)
        run_stat = True
    else:
        say("他の処理を行っているため、もう少ししてから再度実行してください")

#helpを表示
@app.message("help")
def help(say):
    with  open(".\\help.txt", mode="r", encoding="utf-8") as file:
        text = file.read()
    say(text)

#WSのアクセス情報を確認
def check_pass(name):
    move_dir()
    target = ".\\WorkStations\\" + name + ".txt"
    shutil.copy(target,".\\tmp.txt")
    os.system("powershell -Command powershell -ExecutionPolicy RemoteSigned .\\decrypt.ps1")
    with open(".\\tmp.txt", mode="r", encoding="utf-8") as file:
        pass_list = file.read().split("\n")
    text = make_pass_text(name,pass_list[0],pass_list[3],pass_list[4],pass_list[5])
    return text

def make_pass_text(name,hostip,chrome_pin,ws_pin,ws_pass):
    pass_text = "*" + name + "*\n```TailScale ip：" + hostip + "\nWindows PIN：" + ws_pin + "\nWindows Password：" + ws_pass + "\nChrome PIN：" + chrome_pin + "```"
    return pass_text


#WSの利用開始を記録
def use_ws(name,user,say):
    global WSName
    global WSUser
    global update_WSUser
    ws_num = WSName.index(name)
    if(WSUser[ws_num] == "none"):
        WSUser[ws_num] = user
        username = search_username(user)
        say(username + "が" + name + "の利用を開始しました")
        update_WSUser = True
    elif(WSUser[ws_num] == user):
        say("現在、" + name + "はあなたが利用中です。利用を終了する際はend " + name + "コマンドを利用してください")
    else:
        username = search_username(user)
        say(name + "は現在" + username + "が利用中です")

#WSの利用終了を記録
def end_ws(name,user,say):
    global WSName
    global WSUser
    global update_WSUser
    ws_num = WSName.index(name)
    if(WSUser[ws_num] == "none"):
        say("現在、" + name + "を利用中のユーザーはいません。利用を始める際はuse " + name + "コマンドを利用してください")
    elif(WSUser[ws_num] == user):
        WSUser[ws_num] = "none"
        username = search_username(user)
        say(username + "が" + name + "の利用を終了しました")
        update_WSUser = True
    else:
        username = search_username(user)
        say("利用を終了する際は利用開始した時と同じユーザーで操作を行ってください。このパソコンは" + username + "が利用中です")

#リモートアクセス状況を表すメッセージを作成
def make_stat(name):
    chr_sta, win_sta = check_stat(name)
    stat_say = make_stat_text(name,chr_sta,win_sta)
    return stat_say

#ChromeRDとWindowsRDの使用状況を確認
def check_stat(name):
    move_dir()
    target = ".\\WorkStations\\" + name + ".txt"
    shutil.copy(target,".\\tmp.txt")
    os.system("powershell -Command powershell -ExecutionPolicy RemoteSigned .\\decrypt.ps1")
    os.system("powershell -Command powershell -ExecutionPolicy remoteSigned .\\pssession.ps1")
    with open(".\\wsstat.txt", mode="r", encoding="utf-16") as file:
        stat_list = file.read().split("\n")
    return stat_list[0],stat_list[1]

#出力用のテキストを生成
def make_stat_text(name,chrome,windows):
    global WSName
    global WSUser
    if(chrome == "chrome use"):
        chrome_txt = "使用中"
    elif(chrome == "chrome notuse"):
        chrome_txt = "未使用"
    else:
        chrome_txt = "エラー"

    if(windows == "windows use"):
        windows_real_text = "使用中"
        windows_remote_txt = "未使用"
    elif(windows == "windows remote"):
        windows_real_text = "未使用"
        windows_remote_txt = "使用中"
    elif(windows == "windows notuse"):
        windows_real_text = "未使用"
        windows_remote_txt = "未使用"
    else:
        windows_real_text = "エラー"
        windows_remote_txt = "エラー"

    ws_num = WSName.index(name)
    ws_user = WSUser[ws_num]
    if(ws_user != "none"):
        username = search_username(ws_user)
    else:
        username = "---"

    #stat_text = "*" + name + "*\n```利用中ユーザー：" + username + "\n実機：" + windows_real_text + "\nWindowsリモートデスクトップ：" + windows_remote_txt + "\nChromeリモートデスクトップ：" + chrome_txt + "```"
    stat_text = "*" + name + "*\n```利用中ユーザー：" + username + "\nWindowsリモートデスクトップ：" + windows_remote_txt + "\nChromeリモートデスクトップ：" + chrome_txt + "```"
    return stat_text


#bodyからテキスト情報のみを抽出
def body2text(body):
    elements = body['event']['blocks'][0]['elements'][0]['elements']
    text = elements[len(elements)-1]['text'].strip()
    return text

#Slackのidからユーザー名を検索
def search_username(userid):
    list = app.client.users_list()
    for i in list['members']:
        id = i['id']
        if(id == userid):
            profile = i['profile']
            return profile['real_name']


#ユーザー名からSlackのidを検索
def search_userid(username):
    list = app.client.users_list()
    for i in list['members']:
        profile = i['profile']
        real_name = profile['real_name']
        if(real_name == username):
            return i['id']

#実行中ファイルと同じディレクトリに移動
def move_dir():
    dir = os.path.dirname(__file__)
    if(os.getcwd != dir):
        os.chdir(dir)



#アプリを起動
if __name__ == "__main__":
    SocketModeHandler(app,os.environ["SLACK_APP_TOKEN"]).start()