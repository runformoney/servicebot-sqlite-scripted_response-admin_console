####    some thing to show to the admin about trend :)

# importing modules
import matplotlib.pyplot as plt
import pandas as pd
#import numpy as np
import sqlite3
import os

def vs_connect():
    global con
    #conn = sqlite3.connect("servicebot.sqlite")
    con = sqlite3.connect("servicebot.sqlite")
    tickets_history = pd.read_sql_query("SELECT * from cases", con)
    return(tickets_history)

class Visualization():
    def __init__(self):
        pass # we can keep our connection here
        ####    reading data from database

             
    ####    1 - Bar chart of count of incidents w.r.t department
    def incidents_by_department(self):
        tickets_history = vs_connect()
        tickets_by_department = tickets_history.groupby(['department'],as_index = False).count().iloc[:,[0,1]]
        tickets_by_department.columns = ['Department', 'Count']
        plt.bar(tickets_by_department.iloc[:,0], tickets_by_department.iloc[:,1])
        plt.xlabel("Department")
        plt.ylabel("Count")
        plt.title("Count of Incidents vs Department")
        file_name = "charts//chart_by_department.png"
        os.remove(file_name)
        plt.savefig(file_name)
        plt.close()
        con.close()
        return "success"
    ####    2 - Bar chart of count of incidents w.r.t priority
    def incidents_by_Priority(self):
        tickets_history = vs_connect()
        tickets_by_Priority = tickets_history.groupby(['priority'],as_index = False).count().iloc[:,[0,1]]
        tickets_by_Priority.columns = ['Department', 'Count']
        plt.bar(tickets_by_Priority.iloc[:,0], tickets_by_Priority.iloc[:,1])
        plt.xlabel("Priority")
        plt.ylabel("Count")
        plt.title("Count of Incidents vs Priority")
        file_name = "charts//chart_by_Priority.png"
        os.remove(file_name)
        plt.savefig(file_name)
        plt.close()
        con.close()
        return "success"
    ####    3 - Bar chart of count of incidents w.r.t department for a particular date
    def incidents_by_department_date(self, date):
        tickets_history = vs_connect()
        is_date = tickets_history.iloc[:,1] == date
        tickets_history_date = tickets_history[is_date]
        tickets_by_department = tickets_history_date.groupby(['department'],as_index = False).count().iloc[:,[0,1]]
        tickets_by_department.columns = ['Department', 'Count']
        print(tickets_by_department.head())
        plt.bar(tickets_by_department.iloc[:,0], tickets_by_department.iloc[:,1])
        plt.xlabel("Department")
        plt.ylabel("Count")
        plt.title("Count of Incidents vs Department for {}".format(date))
        file_name = "charts//chart_by_department_for_date.png"
        os.remove(file_name)
        plt.savefig(file_name)
        plt.close()
        con.close()
        return "success"
    ####    4 - Bar chart of count of incidents w.r.t priority for a particular date
    def incidents_by_Priority_date(self, date):
        tickets_history = vs_connect()
        is_date = tickets_history.iloc[:,1] == date
        tickets_history_date = tickets_history[is_date]
        tickets_by_Priority = tickets_history_date.groupby(['priority'],as_index = False).count().iloc[:,[0,1]]
        tickets_by_Priority.columns = ['Priority', 'Count']
        plt.bar(tickets_by_Priority.iloc[:,0], tickets_by_Priority.iloc[:,1])
        plt.xlabel("Priority")
        plt.ylabel("Count")
        plt.title("Count of Incidents vs Priority for {}".format(date))
        file_name = "charts//chart_by_Priority_for_date.png"

        os.remove(file_name)
        plt.savefig(file_name)
        plt.close()
        con.close()
        return "success"
####    5 - Bar chart of count of incidents w.r.t location
####    6 - Stacked bar chart of count of incidents w.r.t department and count
