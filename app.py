import os
from datetime import datetime
import json
from re import X
import datetime
import random
from math import*
from googlesearch import search
import os
from function import*
import sys
import google.generativeai as palm


from flask import Flask, abort, g, request

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (MessageEvent,
                            TextMessage,
                            AudioMessage,
                            ImageMessage,
                            TextSendMessage,
                            ImageSendMessage,
                            VideoSendMessage,
                            AudioSendMessage,
                            LocationSendMessage,
                            StickerSendMessage,
                            ImagemapSendMessage,
                            TemplateSendMessage,
                            FlexSendMessage,
                            ButtonsTemplate,
                            MessageTemplateAction,
                            PostbackEvent,
                            PostbackTemplateAction)

send_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Connection": "keep-alive",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8"}

app = Flask(__name__)

# os.system('python3 -m playwright install')
# os.system('apt-get install sudo')
# os.system('sudo apt-get update')
# os.system('sudo apt install ffmpeg -y')

# get channel_secret and channel_access_token from your environment variable

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)

if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


Message_counter = 0
Message_container = ''
previous_user_name = ''


@app.route("/", methods=["GET", "POST"])
def callback():

    if request.method == "GET":
        return "Hello"
    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    dt = (datetime.datetime.today() +
          datetime.timedelta(hours=8)).strftime("%Y/%m/%d")
    print(dt)

    get_message = event.message.text.rstrip()
    get_message = get_message.replace('！', '!')
    l_get_message = get_message.strip()
    split = get_message.split()

    id = event.source.user_id
    owner = 'U2290158f54f16aea8c2bdb597a54ff9e'
    try:
        group_id = event.source.group_id
    except:
        group_id = 'N/A'
    group = 'C0862e003396d3da93b9016d848560f29'

    line_bot_api = LineBotApi(channel_access_token)
    try:
        profile = line_bot_api.get_group_member_profile(
            group_id, id)
    except:
        profile = line_bot_api.get_profile(id)
    user_name = profile.display_name

    global Message_counter
    global Message_container
    global previous_user_name
    global palm_response

    if Message_container == get_message:
        Message_counter += 1
    else:
        Message_counter = 1
        Message_container = get_message

    # Send To Line
    print(user_name+id)

    # if group_id == group:
    #     F_countMSG(event)

    if id == owner:
        if split[0] == '!resp':
            F_respManager(split, event)

    with open('json/setting.json', 'r', encoding='utf8') as jfile:
        jdata = json.load(jfile)

    if get_message[:4].lower() == '@bot' or get_message[:4] == '神奇海螺':
        LLM(get_message, event)

    if get_message[:4].lower() == '!bot':
        LLM(get_message, event, mode='chat')

    if split[0].lower() == '!t':
        F_translate(get_message, split, event)

    elif split[0].lower() == '!tts':
        F_TTS(get_message, event)

    elif split[0].lower() == '!tt':
        audio_reply(
            'https://cdn.discordapp.com/attachments/866565785982861322/1082691272051011675/tmp.m4a', event)

    elif get_message[0].isdigit() and get_message[-1].isdigit():
        F_eval(get_message, event)

    elif get_message[:2] == '!抽':
        F_lottery(jdata, group_id, split, event)

    elif '.jpg' in get_message.lower() or '.png' in get_message.lower():
        F_imgSearch(split, jdata, get_message, event)

    elif get_message[:3].lower() == '!yt':
        F_ytSearch(split, get_message, jdata, event)

    elif get_message[:2].lower() == '!s' or get_message[:4] == '有人知道' or (get_message[:1] == '教' and get_message[-1:] == '嗎' and len(get_message) > 2):
        F_GoogleSearch(get_message, event)

    elif l_get_message[:17] == 'https://youtu.be/' or l_get_message[:24] == 'https://www.youtube.com/' or l_get_message[:22] == "https://m.youtube.com/":
        F_ytPreview(l_get_message, jdata, event)

    elif 'ptt' in get_message and '不印出' not in get_message:
        F_pttPreview(get_message, event)

    elif 'twitter.com' in get_message or 'x.com' in get_message:
        F_twitterPreview(get_message, event)

    elif 'forum.gamer.com.tw' in get_message:
        F_bahamutePreview(get_message, event)

    elif 'home.gamer.com.tw' in get_message:
        F_bahamuteHomePreview(get_message, event)

    elif get_message[:5] == '!rand':
        F_randnum(get_message, event)

    elif get_message[:5] == '!rate':
        F_rate(get_message, send_headers, event)

    elif l_get_message.lower() == '!face':
        if group_id == 'N/A':
            F_faceDetect(event, id)
        else:
            F_faceDetect(event, group_id)

    elif l_get_message.lower() == '!rbg':
        if group_id == 'N/A':
            F_removeBG(event, id)
        else:
            F_removeBG(event, group_id)

    elif l_get_message.lower() == '!manga':
        if group_id == 'N/A':
            F_manga(event, id)
        else:
            F_manga(event, group_id)

    elif l_get_message.lower() == '!img':
        if group_id == 'N/A':
            text_reply(uploadIMG(f"{id}.png"), event)
        else:
            text_reply(uploadIMG(f"{group_id}.png"), event)

    elif split[0].lower() == '!f':
        if group_id == 'N/A':
            text_reply(F_searchByIMG(id, split[-1]), event)
        else:
            text_reply(F_searchByIMG(group_id, split[-1]), event)

    elif get_message[:5].lower() == '!vote':
        F_vote(event)

    elif get_message.lower() == '!history':
        F_history(event)

    elif ('line' in get_message.lower() or '賴' in get_message) and '怒' in get_message:
        with open('previous_user_name.txt', 'r') as f:
            previous_user_name = f.read()
        text_reply(f'@{previous_user_name} 😡', event)

    elif get_message[:4] != 'http':

        if '機器人' in get_message or 'bot' in get_message:
            for i in jdata['abuse_words']:
                if i in get_message:
                    L = ['兇三小 幹', '家裡死人嗎？', '是在叫三小', '靠北啥？']
                    word = random.choice(L)
                    text_reply(user_name+word, event)
            for i in jdata['praise_words']:
                if i in get_message:
                    img_reply(
                        'https://cdn.discordapp.com/attachments/856516846144192543/863114640345923604/image0.png', event)

        for i in jdata['echo_words']:
            if i in get_message:
                if get_message[0] == '我':
                    get_message = get_message.replace('我', '你')
                if "不會" not in get_message:
                    get_message = get_message.replace('會', '才會')
                if "會不會" not in get_message:
                    get_message = get_message.replace('會不會', '才會')
                if "你是" in get_message or "妳是" in get_message:
                    get_message = get_message.replace('是', '才是')
                    get_message = get_message.replace('才是不才是', '才是')
                text_reply(get_message, event)
                break

        for i in jdata['full_echo_words']:
            if i == get_message:
                text_reply(get_message, event)
                break

        if '買' in get_message:
            if '會員' in get_message:
                text_reply('買 我叫你買', event)

        if '我' in get_message:
            if '不會' in get_message and len(get_message) < 20:
                L = ['哈哈你又不會了', '你要確定ㄋㄟ', '真假', '喔是喔，真的假的，55555', '好了啦']
                word = random.choice(L)
                text_reply(word, event)

        if '我寶寶' in get_message:
            L = ['恩', '喔是喔，真的假的，55555', 'ㄏ', '好了啦', '多出去走走', '有點可憐', '啊哈哈']
            word = random.choice(L)
            text_reply(word, event)
        if '教嗎' in get_message or '教嘛' in get_message or '教？' in get_message or '教?' in get_message:
            text_reply('不要嘲諷好嗎', event)

        if '加推' in get_message or '我婆' in get_message:
            text_reply('又？', event)

        if '一生' in get_message and '推' in get_message and '不' not in get_message:
            text_reply(user_name+'你真可憐', event)

    if Message_counter == 3:
        text_reply(Message_container, event)

    sheet, resp_names, resp_p, resp_words = resp_reload()

    if user_name in resp_names:
        p = resp_p[resp_names.index(user_name)]
        words = resp_words[resp_names.index(user_name)]
        resp(int(p), words, event)

    with open('previous_user_name.txt', 'w') as f:
        f.write(user_name)


@handler.add(MessageEvent, message=AudioMessage)
def handle_message_Audio(event):
    id = event.source.user_id
    owner = 'U2290158f54f16aea8c2bdb597a54ff9e'
    try:
        group_id = event.source.group_id
    except:
        group_id = 'N/A'

    line_bot_api = LineBotApi(channel_access_token)
    try:
        profile = line_bot_api.get_group_member_profile(
            group_id, id)
    except:
        profile = line_bot_api.get_profile(id)
    user_name = profile.display_name
    # Send To Line
    print(user_name+id)
    F_sound2text(event)


@handler.add(MessageEvent, message=ImageMessage)
def handle_message_Image(event):
    try:
        id = event.source.group_id
    except:
        id = event.source.user_id
    PATH = f'{id}.png'
    image_content = line_bot_api.get_message_content(event.message.id)
    with open(PATH, 'wb') as fd:
        for chunk in image_content.iter_content():
            fd.write(chunk)


@handler.add(PostbackEvent)  # Postback的部分
def handle_postback(event):
    data = event.postback.data
