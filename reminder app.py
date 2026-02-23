import uuid
import logging
import time
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Optional
from abc import ABC, abstractmethod

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reminder.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Reminder:
    title: str
    time: str
    repeat_days: int = 0
    remind_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    def __post_init__(self):
        try:
            datetime.strptime(self.time, "%H:%M")
        except ValueError:
            raise ValueError(f"Invalid time format: {self.time}. Use HH:MM")

class NotificationService:
    @staticmethod
    def send(title: str, message: str):
        try:
            print(f"\nReminder: {title} - {message}")
            logger.info(f"Notification sent: {title}")
        except Exception as e:
            logger.error(f"Notification error: {e}")

class Scheduler:
    def __init__(self):
        self.reminders = []
        self.tasks = {}
        self.running = False
        self.thread = None
        
    def add(self, reminder: Reminder):
        self.reminders.append(reminder)
        logger.info(f"Reminder added: {reminder.title} - {reminder.time}")
        
    def remove(self, remind_id: str):
        self.reminders = [r for r in self.reminders if r.remind_id != remind_id]
        if remind_id in self.tasks:
            del self.tasks[remind_id]
        logger.info(f"Reminder {remind_id} removed")
        
    def deactivate(self, remind_id: str):
        for r in self.reminders:
            if r.remind_id == remind_id:
                r.is_active = False
                logger.info(f"Reminder {remind_id} deactivated")
                break
                
    def get_active(self):
        return [r for r in self.reminders if r.is_active]
    
    def check_reminders(self):
        now = datetime.now().strftime("%H:%M")
        
        for reminder in self.reminders:
            if not reminder.is_active:
                continue
                
            if reminder.time == now:
                NotificationService.send(reminder.title, f"Time: {reminder.time}")
                
                if reminder.repeat_days > 0:
                    next_time = datetime.now() + timedelta(days=reminder.repeat_days)
                    reminder.time = next_time.strftime("%H:%M")
                    logger.info(f"Repeating reminder {reminder.remind_id} set for {reminder.time}")
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        print("Scheduler started")
        
    def _run(self):
        while self.running:
            self.check_reminders()
            time.sleep(30)
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("Program ended")

def main():
    scheduler = Scheduler()
    
    scheduler.add(Reminder("Python project deadline", "14:30"))
    scheduler.add(Reminder("Team meeting", "16:00", repeat_days=7))
    scheduler.add(Reminder("Water plants", "09:00", repeat_days=1))
    
    scheduler.start()
    
    commands = {
        '1': ('Add reminder', lambda: add_reminder(scheduler)),
        '2': ('Show list', lambda: show_list(scheduler)),
        '3': ('Remove reminder', lambda: remove_reminder(scheduler)),
        '4': ('Deactivate reminder', lambda: deactivate_reminder(scheduler)),
        '5': ('Exit', lambda: exit_app(scheduler))
    }
    
    try:
        while True:
            print("\n" + "="*40)
            print("REMINDER MANAGER")
            print("="*40)
            for key, (desc, _) in commands.items():
                print(f"{key}. {desc}")
            
            choice = input("\nYour choice: ").strip()
            
            if choice in commands:
                if commands[choice][1]() == False:
                    break
            else:
                print("Invalid choice!")
                
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    finally:
        scheduler.stop()

def add_reminder(scheduler):
    try:
        title = input("Title: ").strip()
        if not title:
            print("Title cannot be empty!")
            return
            
        time_str = input("Time (HH:MM): ").strip()
        
        repeat = input("Repeat (0=none, 1=daily, 7=weekly): ").strip()
        repeat_days = int(repeat) if repeat.isdigit() else 0
        
        reminder = Reminder(title=title, time=time_str, repeat_days=repeat_days)
        scheduler.add(reminder)
        print(f"Reminder added with ID: {reminder.remind_id}")
        
    except Exception as e:
        print(f"Error: {e}")

def show_list(scheduler):
    reminders = scheduler.get_active()
    
    if not reminders:
        print("\nNo active reminders")
        return
        
    print("\nActive Reminders:")
    print("-" * 50)
    for r in reminders:
        repeat_text = ""
        if r.repeat_days == 1:
            repeat_text = "[Daily]"
        elif r.repeat_days == 7:
            repeat_text = "[Weekly]"
        elif r.repeat_days > 0:
            repeat_text = f"[Every {r.repeat_days} days]"
        
        status = "[Active]" if r.is_active else "[Inactive]"
        print(f"ID: {r.remind_id} | {r.title} | {r.time} {repeat_text} {status}")

def remove_reminder(scheduler):
    rid = input("Reminder ID: ").strip()
    scheduler.remove(rid)
    print(f"Reminder {rid} removed")

def deactivate_reminder(scheduler):
    rid = input("Reminder ID: ").strip()
    scheduler.deactivate(rid)
    print(f"Reminder {rid} deactivated")

def exit_app(scheduler):
    scheduler.stop()
    return False

if __name__ == "__main__":
    main()
