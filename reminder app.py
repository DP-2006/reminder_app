import uuid
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional
import schedule
import time
from plyer import notification
from logging.handlers import RotatingFileHandler
import threading
from abc import ABC, abstractmethod

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('reminder.log', maxBytes=100*1024, backupCount=3, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IDGenerator:
    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

@dataclass
class Reminder:
    title: str
    time: str
    remind_id: str = field(default_factory=IDGenerator.generate_id)
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    def __post_init__(self):
        try:
            datetime.strptime(self.time, "%H:%M")
        except ValueError:
            raise ValueError(f"Invalid time format: {self.time}. Use HH:MM")
        logger.info(f"Reminder created: {self.title} - {self.time}")

class ReminderHandler(ABC):
    @abstractmethod
    def process(self, reminder: Reminder):
        pass

class NotificationHandler(ReminderHandler):
    def process(self, reminder: Reminder):
        try:
            notification.notify(title='Task Reminder', message=reminder.title, timeout=10)
            logger.info(f"Notification sent: {reminder.title}")
        except Exception as e:
            logger.error(f"Notification error: {e}")

class LoggingHandler(ReminderHandler):
    def process(self, reminder: Reminder):
        logger.info(f"Reminder executed: {reminder.title} at {reminder.time}")

class ReminderScheduler:
    def __init__(self):
        self.reminders: List[Reminder] = []
        self.handlers: List[ReminderHandler] = []
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
    def add_handler(self, handler: ReminderHandler):
        self.handlers.append(handler)
    
    def add_reminder(self, reminder: Reminder):
        self.reminders.append(reminder)
        schedule.every().day.at(reminder.time).do(self._execute, reminder).tag(reminder.remind_id)
        logger.info(f"Reminder scheduled: {reminder.title}")
    
    def _execute(self, reminder: Reminder):
        if reminder.is_active:
            for handler in self.handlers:
                try:
                    handler.process(reminder)
                except Exception as e:
                    logger.error(f"Handler error: {e}")
    
    def remove_reminder(self, remind_id: str):
        schedule.clear(remind_id)
        self.reminders = [r for r in self.reminders if r.remind_id != remind_id]
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Scheduler started")
    
    def _run(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def get_active(self) -> List[Reminder]:
        return [r for r in self.reminders if r.is_active]
    
    def deactivate(self, remind_id: str):
        for r in self.reminders:
            if r.remind_id == remind_id:
                r.is_active = False
                break

class InteractiveManager:
    def __init__(self, scheduler: ReminderScheduler):
        self.scheduler = scheduler
    
    def add(self):
        try:
            title = input("Title: ").strip()
            if not title:
                print("Title cannot be empty!")
                return
            time_str = input("Time (HH:MM): ").strip()
            reminder = Reminder(title=title, time=time_str)
            self.scheduler.add_reminder(reminder)
            print(f"✓ Reminder added. ID: {reminder.remind_id}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def list(self):
        reminders = self.scheduler.get_active()
        if not reminders:
            print("\nNo active reminders.")
            return
        print("\n=== Active Reminders ===")
        for i, r in enumerate(reminders, 1):
            print(f"{i}. {r.title} - {r.time} [{r.remind_id[:8]}]")
    
    def run(self):
        while True:
            print("\n" + "="*40)
            print("REMINDER MANAGER")
            print("="*40)
            print("1. Add Reminder")
            print("2. List Reminders")
            print("3. Remove Reminder")
            print("4. Deactivate Reminder")
            print("5. Exit")
            
            choice = input("Choice (1-5): ").strip()
            
            if choice == '1':
                self.add()
            elif choice == '2':
                self.list()
            elif choice == '3':
                rid = input("Reminder ID: ").strip()
                self.scheduler.remove_reminder(rid)
                print("✓ Removed")
            elif choice == '4':
                rid = input("Reminder ID: ").strip()
                self.scheduler.deactivate(rid)
                print("✓ Deactivated")
            elif choice == '5':
                print("Goodbye!")
                break
            else:
                print("✗ Invalid choice!")

def create_scheduler() -> ReminderScheduler:
    s = ReminderScheduler()
    s.add_handler(NotificationHandler())
    s.add_handler(LoggingHandler())
    return s

if __name__ == '__main__':
    scheduler = create_scheduler()
    
    for r in [
        Reminder("Complete Python project", "14:30"),
        Reminder("Team meeting", "16:00"),
    ]:
        scheduler.add_reminder(r)
    
    scheduler.start()
    
    try:
        InteractiveManager(scheduler).run()
    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        scheduler.stop()
        logger.info("Program ended")
