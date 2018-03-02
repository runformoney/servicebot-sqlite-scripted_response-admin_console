import json
import requests
import time
import urllib
import datetime
import random
from flask import Flask
#from flask.ext.rq import job
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

from dbhelper import DBHelper
from chat2classconversion import MLhelper
from WHDintegration import APIintegration
from getknowledge import GetKnowledge
from visualization import Visualization

#from logservicerequest import LogRequest

db = DBHelper()
ml = MLhelper()
whdapi = APIintegration()
gk = GetKnowledge()
vis = Visualization()

TOKEN = "540902937:AAFvz9_nV7xagpxiaT_8YZ_TnE2UYSSYSH0"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

correspondent_list = (open('correspondent.txt').read()).split("\n")

application = Flask(__name__)

#cat_resp = pd.read_csv("cat_resp.csv")
cat_resp = pd.read_excel("cat_resp.xlsx")
all_scripted_reply_category = list(cat_resp.Category.unique())
cat_resp = cat_resp.set_index('Category')

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def sendHelptext(chat):
    send_message("If you wish to know what I can do for you, type /menu. Type /stop to exit", chat)

commands = ['Ask a Question','Log Service Request', 'Escalate Request', 'Show Pending Requests', 'Close Request', 'Clear Chat History']
goodbye_messages = ['thanks', 'thank you', 'thank', 'good bye']
action = None
ticket_no = 0

def handle_updates(updates):
    global action
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        firstName = update["message"]["from"]["first_name"]
        print(update)
        if "last_name" in update["message"]["from"]:
            lastName = update["message"]["from"]["last_name"]
        else:
            lastName = ''

        #db.db_connect()()
        items = db.get_items(chat)
        items_lower = [x.lower() for x in items]

        print("action " + str(action))

        if action != None and text[0] != '/':
        #if action != None and action in commands and text[0] != '/':
            if action == 'Log Service Request':
                log_service_request(chat,text,firstName,lastName,ticket_no)
            elif action == 'Close Request':
                close_reuqest(chat,text)
            elif action == 'Escalate Request':
                #print(text)
                escalate_request(chat,text)
            elif action == 'Ask a Question':
                ask_a_question(chat,text)
            elif action == 'Admin':
                admin_check(chat,text)
            elif action == 'Admin Extraction':
                admin_stuff(chat,text)

        elif text in commands:
            command(text,chat,firstName)

        elif text == "/stop" or text.lower() in goodbye_messages:
            #db.db_connect()()
            db.delete_chat(chat)
            msg = 'Thank you, ' +firstName+ " for your time. Good day ahead :)"
            send_message(msg,chat)

        elif text == '/admin':
            admin_value = db.get_admin(chat)
            if len(admin_value) == 0:
                send_message("Sorry, I cannot understand.",chat)
                sendHelptext(chat)
            else:
                send_message("Please reply the pass-key.",chat)
                action = 'Admin'
                #admin_stuff(chat,text)

        elif text == "/start" or text.lower() == "hi" or text.lower() == "hello":
            msg = "Hi " + firstName + "."
            if 'hi' in items_lower or 'hello' in items_lower:
                send_message(msg + " Tell me how can I help you today :)", chat)
                sendHelptext(chat)
            else:
                send_message(msg + " This is OpenHack-ServiceBot. How can I assist you today?", chat)
                sendHelptext(chat)
                #db.db_connect()()
                db.add_item(text, chat)

        elif text.lower() == 'help' or text == "/menu":
            keyboard = build_keyboard(commands)
            send_message("Select an option to continue", chat, keyboard)
            action = None
        else:
            topScoringIntent = gk.get_intent(text)
            if topScoringIntent != None and topScoringIntent in all_scripted_reply_category:
                scripted_resp = cat_resp.loc[topScoringIntent]["Reply"]
                print(scripted_resp)
                send_message(scripted_resp, chat)
                sendHelptext(chat)
            else:
                send_message("Sorry, I cannot understand.",chat)
                sendHelptext(chat)
        if text != '/stop' or text.lower() in goodbye_messages:
            #db.db_connect()()
            db.add_item(text, chat)

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    #print(keyboard)
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def send_message(text, chat_id, reply_markup=None):
    #text = urllib.parse.quote_plus(text)
    text = urllib.parse.quote(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def start():
    print("In Start")
    t_end = time.time() + 25
    #db.db_connect()()
    db.setup()
    last_update_id = None
    #while True:
    while time.time() < t_end:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)
    return "app running"

def command(text,chat,firstName):
    if text.lower() == 'clear chat' or text.lower() == 'cc' or text == 'Clear Chat History':
        #db.db_connect()()
        db.delete_chat(chat)
        message = "Chat history has been cleared from server. Please use 'Clear history' in options button, to clear chat from this window. Thank you."
        send_message(message, chat)
        sendHelptext(chat)

    elif text == 'Ask a Question':
        send_message("I am listening. Shoot.",chat)
        global action
        action = 'Ask a Question'

    elif text == 'Log Service Request':
        message = "Tell me what is the issue."
        send_message(message, chat)
        action
        action = 'Log Service Request'
        global ticket_no
        ticket_no = random.randint(10000, 19999)

    elif text == 'Show Pending Requests':
        #db.db_connect()()
        db.delete_invalid_cases(chat)
        #db.db_connect()()
        case = db.get_pending_case(chat)
        if len(case) != 0:
            for item in case:
                #print(item)
                case_id = item[0]
                case_subject = item[3]
                case_log_date = item[1]
                message = "You have incident #" +str(case_id)+" about '" +str(case_subject)+"' opened on " + str(case_log_date) +"."
                action = None
                send_message(message,chat)
            sendHelptext(chat)
        else:
            send_message("You don't have any pending/active requests.", chat)
            sendHelptext(chat)

    elif text == 'Close Request':
        #global action
        #db.db_connect()()
        db.delete_invalid_cases(chat)
        #db.db_connect()()
        case = db.get_pending_case(chat)
        if len(case) != 0:
            keyboard_layout = []
            for item in case:
                case_id = item[0]
                case_subject = item[3]
                case_log_date = item[1]
                case_matter = "" + str(case_id) + ": " + str(case_subject) + ", opened on " + str(case_log_date)
                #print(case_matter)
                keyboard_layout.append(case_matter)
            keybrd = build_keyboard(keyboard_layout)
            send_message("Select an incident to delete: ",chat,keybrd)
            action = 'Close Request'
        else:
            send_message("You don't have any pending/active requests.",chat)
            sendHelptext(chat)

    elif text == 'Escalate Request':
        #db.db_connect()()
        db.delete_invalid_cases(chat)
        #db.db_connect()()
        case = db.get_pending_case(chat)
        if len(case) != 0:
            keyboard_layout = []
            for item in case:
                case_id = item[0]
                case_subject = item[3]
                case_open_date = item[1]
                case_matter = "" + str(case_id) + ": " + str(case_subject) + " Priority -  " + str(item[12]) + ", Opened On " + str(case_open_date)
                # print(case_matter)
                keyboard_layout.append(case_matter)
            keybrd = build_keyboard(keyboard_layout)
            send_message("Select an incident to escalate: ", chat, keybrd)
            action = 'Escalate Request'
        else:
            send_message("You don't have any pending/active requests.", chat)
            sendHelptext(chat)

def log_service_request(chat,text,firstName,lastName,ticket_no):
    #print(text,chat)
    subject = text

    date_today = datetime.datetime.now().strftime('%Y-%m-%d')
    #db.db_connect()()
    data = db.get_case_subject(ticket_no,chat,date_today)
    print("Case Detail: " + str(data))

    if len(data) == 0:
        db.add_case_subject(ticket_no, text, chat, firstName, lastName, date_today)
        send_message("I am sorry to hear that. Can you please elaborate for me to take the request?", chat)

    elif str(data[0][4]) == 'None':  # logic to check there is no detail
        if len(text) >= 10:
            department = ml.get_department(text)
            # department = 'XYZ'
            db.update_case_detail(text, chat, date_today, ticket_no, department)
            send_message(
                "Ok " + firstName + ", please tell me your location and your phone number to log a request. eg: Pune, 1234569870",
                chat)
        else:
            send_message("Please write a bigger detail. It will help us to serve you better.", chat)

    elif str(str(data[0][9]) == 'None' and str(data[0][11])) == 'None':  # to see if phn number and loc are blank
        # print(text)
        if "," in text:
            text = text.replace(" ", "")
            text = text.split(",")
            # print(text)
            phn_no = str(text[1]).replace(" ", "")
            if len(phn_no) == 10:
                loc = text[0]
                assignee = random.choice(correspondent_list)
                db.update_case_phn_loc(phn_no, loc, chat, date_today, assignee, ticket_no)
                db.update_priority(chat, 1, ticket_no)
                department = db.get_case_department(ticket_no, chat)

                if department == '':
                    department = 'Miscellaneous'
                # assignee = 'Elon Musk'
                message = "Service request has been created under " + department + " department. Please note the request number: " + str(
                    ticket_no) \
                          + "\n\nOur correspondent " + assignee + " will connect with you over " + str(text[1])
                send_message(message, chat)
                global action
                action = None
                whdapi.create_ticket_in_whd(ticket_no, chat, date_today)
                sendHelptext(chat)
            else:
                send_message("Please provide a valid 10-digit mobile number.", chat)
        else:
            send_message("Please provide in below format: \n<location>, <number>", chat)


def close_reuqest(chat,text):
    case_id = text.split(":")[0]
    #print(case_id)
    if any(char.isdigit() for char in case_id):
        #db.db_connect()()
        whd_ticket_id = (db.get_case_whd_ticket_id(case_id,chat)[-1])[0]
        #db.db_connect()()
        db.delete_case(case_id,chat)
        print(whd_ticket_id)
        whdapi.delete_ticket(whd_ticket_id)
        send_message("Incident #" +str(case_id) + " has been purged. Hope we served you well.",chat)
        sendHelptext(chat)
        global action
        action = None
    else:
        send_message("Invalid Selection! Please try again.", chat)


def escalate_request(chat,text):
    case_id = text.split(":")[0]
    priority = text.split(",")[0]
    if any(char.isdigit() for char in case_id):
        priority = int(priority.split(" - ")[1])

        print(case_id,priority)
        log_date = str(text.split(" Opened On ")[-1])
        if priority+1 <= 3:
            #db.db_connect()()
            db.update_priority(chat,priority+1,case_id)
            send_message("Incident #" + str(case_id) + " has been escalated to Priority " + str(priority+1) + " from Priority " + str(priority) +
                         "\n\nWe will reach you as soon as possible.",chat)
            whdapi.escalate_ticket(case_id,chat,log_date)
        else:
            send_message("Incident # " + str(case_id) + " cannot be escalated any further.",chat)
        sendHelptext(chat)
        global action
        action = None
    else:
        send_message("Invalid Selection! Please try again.", chat)

def ask_a_question(chat,text):
    topScoringIntent = gk.get_intent(text)
    print("Type of Query: " + topScoringIntent)

    if topScoringIntent != 'None':
        scripted_resp = cat_resp.loc[topScoringIntent]["Reply"]
        print(scripted_resp)
        send_message(scripted_resp,chat)
        sendHelptext(chat)
    else:
        #send_message("Everyone is an ass hole, Rukhshan. Trust no one.",chat)
        send_message("I am unable to answer your query. I am still learning. Go ahead and log a request.", chat)
        sendHelptext(chat)
    global action
    action = None

def admin_check(owner,text):
    print("In admin stuff!!")
    global action
    admin_value = db.get_admin(owner)[0]
    pass_key = admin_value[1]
    if pass_key != text:
        send_message("You have entered and invalid pass-key. Please try again by replying  /admin",owner)
        action = None
    else:
        #send_message(,owner)
        keyboard_values = ["Incidents By Department", "Incidents By Priority","Incidents By Department - Logged Today","Incidents By Priority - Logged Today"]
        keybrd = build_keyboard(keyboard_values)
        send_message("Pass-key validated.",owner)
        send_message("Choose an option to continue.", owner, keybrd)
        action = 'Admin Extraction'

def sendImage(file_name,chat):
    url = "https://api.telegram.org/bot".format(TOKEN)+ "/sendPhoto"
    print(url)
    files = {'photo': open(file_name, 'rb')}
    data = {'chat_id' : chat}
    r = requests.post(url, files=files, data=data)
    print(r.status_code, r.reason, r.content)

def admin_stuff(chat,text):
    global action
    file_generated = ''
    file_name = ''
    if text == "Incidents By Department":
        file_generated = vis.incidents_by_department()
        file_name = "charts/chart_by_department.png"

    elif  text == "Incidents By Priority":
        file_generated = vis.incidents_by_Priority()
        file_name = "charts/chart_by_Priority.png"

    elif text == "Incidents By Department - Logged Today":
        date_today = datetime.datetime.today().strftime('%Y-%m-%d')
        file_generated = vis.incidents_by_department_date(str(date_today))
        file_name = "charts/chart_by_department_for_date.png"

    elif text == "Incidents By Priority - Logged Today":
        date_today = datetime.datetime.today().strftime('%Y-%m-%d')
        file_generated = vis.incidents_by_Priority_date(str(date_today))
        file_name = "charts/chart_by_Priority_for_date.png"
    else:
        send_message("Sorry, invalid choice. Type /admin to try again.",chat)


    if file_generated == 'success':
        send_message("Generating file and sending.\n\nHang on tight :D",chat)
        sendImage(file_name, chat)
        send_message("Please clear this chat window for security purposes.", chat)
        sendHelptext(chat)
    else:
        send_message("Some issues. Please try again.", chat)
        sendHelptext(chat)
    action = None


@application.route('/')
def call_main_app():
    print("In Call")
    start()
    return("App is running!")

if __name__ == '__main__':
    #start()
    print("In Main")
    application.run()
