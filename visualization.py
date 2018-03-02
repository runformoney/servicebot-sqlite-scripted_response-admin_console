####    some thing to show to the admin about trend :)

# importing modules
import matplotlib.pyplot as plt
import pandas as pd
#import numpy as np
import sqlite3
import os

class Visualization():
    def __init__(self):
        pass # we can keep our connection here
        ####    reading data from database
        con = sqlite3.connect("servicebot.sqlite")
        self.tickets_history = pd.read_sql_query("SELECT * from cases", con)
             
    ####    1 - Bar chart of count of incidents w.r.t department
    def incidents_by_department(self):
        tickets_by_department = self.tickets_history.groupby(['department'],as_index = False).count().iloc[:,[0,1]]
        tickets_by_department.columns = ['Department', 'Count']
        plt.bar(tickets_by_department.iloc[:,0], tickets_by_department.iloc[:,1])
        plt.xlabel("Department")
        plt.ylabel("Count")
        plt.title("Count of Incidents vs Department")
        file_name = "charts//chart_by_department.png"
        os.remove(file_name)
        plt.savefig(file_name)
        plt.close()
        return "success"
    ####    2 - Bar chart of count of incidents w.r.t priority
    def incidents_by_Priority(self):
        tickets_by_Priority = self.tickets_history.groupby(['priority'],as_index = False).count().iloc[:,[0,1]]
        tickets_by_Priority.columns = ['Department', 'Count']
        plt.bar(tickets_by_Priority.iloc[:,0], tickets_by_Priority.iloc[:,1])
        plt.xlabel("Priority")
        plt.ylabel("Count")
        plt.title("Count of Incidents vs Priority")
        file_name = "charts//chart_by_Priority.png"
        os.remove(file_name)
        plt.savefig(file_name)
        plt.close()
        return "success"
    ####    3 - Bar chart of count of incidents w.r.t department for a particular date
    def incidents_by_department_date(self, date):
        is_date = self.tickets_history.iloc[:,1] == date
        tickets_history_date = self.tickets_history[is_date]
        tickets_by_department = tickets_history_date.groupby(['department'],as_index = False).count().iloc[:,[0,1]]
        tickets_by_department.columns = ['Department', 'Count']
        plt.bar(tickets_by_department.iloc[:,0], tickets_by_department.iloc[:,1])
        plt.xlabel("Department")
        plt.ylabel("Count")
        plt.title("Count of Incidents vs Department for {}".format(date))
        file_name = "charts//chart_by_department_for_date.png"
        os.remove(file_name)
        plt.savefig(file_name)
        plt.close()
        return "success"
    ####    4 - Bar chart of count of incidents w.r.t priority for a particular date
    def incidents_by_Priority_date(self, date):
        is_date = self.tickets_history.iloc[:,1] == date
        tickets_history_date = self.tickets_history[is_date]
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
        return "success"
####    5 - Bar chart of count of incidents w.r.t location
####    6 - Stacked bar chart of count of incidents w.r.t department and count
