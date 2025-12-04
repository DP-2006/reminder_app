import uuid 
import logging 
from datetime import datetime
from dataclasses import dataclass
from typing import List
import schedule
import time
from plyer import notification
from logging.handlers import RotatingFileHandler 


logging.basicConfig(
    handlers=[
        RotatingFileHandler(
            filename='reminder.log',
            maxBytes=100*1024, 
            backupCount=3,    
            encoding='utf-8'  
        ),
        logging.StreamHandler()
    ]
)

class id :
    @staticmethod
    def id():
        return str
    def generate_id():
        pass
@dataclass
class Reminder : 
    title : str 
    time : str 
    remind_id : str  = None

    def __sending_init__(self):
        super.generate()
        if self.remind_id is None:
            self.remind_id == self.generate_id()
    
    
class Handler(Reminder):

    def remind(self):
        super().reminder()
        logging.info(f"{self.title} , {self.time}")

class Meet_Handler_reminding(Reminder):

    def schedule_task(task, time_of_day):
        schedule.every().day.at(time_of_day).do(time_of_day,task)     
        print(f"Task scheduled for {time_of_day}: {task}")

    def start_scheduler(reminder):
        super().time
        while True:
            schedule.run_pending() 
            time.sleep(1)  

    def task_reminder(task):
        notification.notify(
        title='Task Reminder',
        message=task,
        timeout=10 
    )
    
    def schedule_task(task, time_of_day):
        schedule.every().day.at(time_of_day).do(time_of_day, task)
        print(f"Task scheduled for {time_of_day}: {task}")

    def start_scheduler():
        while True:
            schedule.run_pending() 
            time.sleep(1)  
    schedule.every().hour.do(task_reminder, "Check emails")
    schedule.every().monday.at("09:00").do(task_reminder, "Team meeting")


    def schedule_user_task(self):
        task = input("Enter the task description: ")
        time_of_day = input("Enter the time of day (24-hour format, e.g., 14:30): ")
        self.schedule_task(task, time_of_day)
class meering_reminder(Reminder):
    def __init__(self , title : str , time : str ):
        super().__init__(time , title)

    def task_reminder(task):
        notification.notify(
        title='Task Reminder',
        message=task,
        timeout=10  
    )
    def pass_and_secourity(Reminder):
        pass


def schedule_task(task, time_of_day):
    schedule.every().day.at(time_of_day).do(time_of_day, task)
    print(f"Task scheduled for {time_of_day}: {task}")
    time.sleep(1)  

def schedule_task(task, time_of_day):
    schedule.every().day.at(time_of_day).do(lambda: notification.notify(title='Task Reminder', message=task, timeout=10), task)
    print(f"Task scheduled for {time_of_day}: {task}")



if __name__ == '__main__':
    schedule_task("Complete your Python project", "14:30")  
    schedule_task("Attend team meeting", "16:00")  
