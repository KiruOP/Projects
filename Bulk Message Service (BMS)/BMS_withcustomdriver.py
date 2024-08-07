import os
from tkinter import Tk, Label, Entry, Button, filedialog, StringVar, Text, Scrollbar, VERTICAL, RIGHT, Y, END
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from datetime import datetime

class WhatsAppMessageSender:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Message Sender")
        self.root.geometry("600x500")

        self.message_file_path = StringVar()
        self.numbers_file_path = StringVar()
        self.image_file_path = StringVar()
        self.delay = 30

        self.create_widgets()
        
    def create_widgets(self):
        # Create and place the widgets
        Label(self.root, text="Message File:").grid(row=0, column=0, pady=5, sticky='e')
        Entry(self.root, textvariable=self.message_file_path, width=50).grid(row=0, column=1, pady=5)
        Button(self.root, text="Browse", command=lambda: self.browse_file(self.message_file_path)).grid(row=0, column=2, pady=5, padx=5)

        Label(self.root, text="Numbers File:").grid(row=1, column=0, pady=5, sticky='e')
        Entry(self.root, textvariable=self.numbers_file_path, width=50).grid(row=1, column=1, pady=5)
        Button(self.root, text="Browse", command=lambda: self.browse_file(self.numbers_file_path)).grid(row=1, column=2, pady=5, padx=5)

        Label(self.root, text="Image File (optional):").grid(row=2, column=0, pady=5, sticky='e')
        Entry(self.root, textvariable=self.image_file_path, width=50).grid(row=2, column=1, pady=5)
        Button(self.root, text="Browse", command=lambda: self.browse_image(self.image_file_path)).grid(row=2, column=2, pady=5, padx=5)

        Button(self.root, text="Prepare", command=self.prepare_script).grid(row=3, column=0, pady=20, columnspan=3)
        Button(self.root, text="Start", command=self.send_messages).grid(row=4, column=0, pady=20, columnspan=3)

        self.output_text = Text(self.root, height=15, width=70)
        self.output_text.grid(row=5, column=0, columnspan=3, pady=10)
        scrollbar = Scrollbar(self.root, orient=VERTICAL, command=self.output_text.yview)
        scrollbar.grid(row=5, column=3, sticky='ns')
        self.output_text.configure(yscrollcommand=scrollbar.set)

    def log_output(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} - {message}"
        self.output_text.insert(END, log_message + '\n')
        self.output_text.see(END)
        with open("log.txt", "a") as log_file:
            log_file.write(log_message + '\n')
        
    def browse_file(self, file_var):
        file_path = filedialog.askopenfilename()
        file_var.set(file_path)

    def browse_image(self, file_var):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")])
        file_var.set(file_path)

    def read_message(self, file_path):
        with open(file_path, "r", encoding="utf8") as f:
            return f.read()

    def read_numbers(self, file_path):
        numbers = []
        with open(file_path, "r") as f:
            for line in f.read().splitlines():
                if line.strip() != "":
                    numbers.append(line.strip())
        return numbers

    def init_driver(self):
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--profile-directory=Default")
        options.add_argument("--user-data-dir=/var/tmp/chrome_user_data")

        try:
            self.log_output("Installing ChromeDriver...")
            chrome_service = ChromeService(".\chromedriver-win64\chromedriver-win64\chromedriver.exe")
            driver = webdriver.Chrome(service=chrome_service, options=options)
            self.log_output(f"Chrome Driver initialized successfully at {chrome_service.path}.")
            return driver
        except Exception as e:
            self.log_output("Failed to initialize Chrome Driver. Error: " + str(e))
            return None

    def prepare_script(self):
        self.driver = self.init_driver()
        if not self.driver:
            return

        self.log_output('Once your browser opens up, sign in to web WhatsApp')
        self.driver.get('https://web.whatsapp.com')
        self.log_output("AFTER logging into WhatsApp Web is complete and your chats are visible, press 'Start'...")

    def send_messages(self):
        message_file = self.message_file_path.get()
        numbers_file = self.numbers_file_path.get()
        image_path = self.image_file_path.get()

        message = self.read_message(message_file)
        numbers = self.read_numbers(numbers_file)
        total_number = len(numbers)
        self.log_output(f'We found {total_number} numbers in the file')

        for idx, number in enumerate(numbers):
            number = number.strip()
            if number == "":
                continue
            self.log_output(f'{idx+1}/{total_number} => Sending message to {number}.')
            try:
                search_box = WebDriverWait(self.driver, self.delay).until(EC.element_to_be_clickable((By.XPATH,
                    "//div[@contenteditable='true'][@data-tab='3']")))
                search_box.clear()
                search_box.send_keys(number)
                search_box.send_keys(Keys.RETURN)
                sleep(3)

                message_box = WebDriverWait(self.driver, self.delay).until(EC.element_to_be_clickable((By.XPATH,
                    "//div[@contenteditable='true'][@data-tab='10']")))
                message_box.send_keys(message)
                sleep(3)
                message_box.send_keys(Keys.RETURN)
                sleep(3)
                self.log_output(f'Message sent to: {number}')
                sleep(3)

                if image_path:
                    try:
                        attach_btn = WebDriverWait(self.driver, self.delay).until(EC.element_to_be_clickable((By.XPATH,
                            "//div[@title='Attach']")))
                        attach_btn.click()
                        image_btn = WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((By.XPATH,
                            "//input[@accept='image/*,video/mp4,video/3gpp,video/quicktime']")))
                        image_btn.send_keys(os.path.abspath(image_path))
                        sleep(3)
                        send_btn = WebDriverWait(self.driver, self.delay).until(EC.element_to_be_clickable((By.XPATH,
                            "//span[@data-icon='send']")))
                        send_btn.click()
                        sleep(3)
                        self.log_output(f'Image sent to: {number}')
                    except Exception as e:
                        self.log_output(f'Failed to send image to {number}. Error: {str(e)}')
            except Exception as e:
                self.log_output(f'Failed to send message to {number}. Error: {str(e)}')
        self.driver.close()

if __name__ == "__main__":
    root = Tk()
    app = WhatsAppMessageSender(root)
    root.mainloop()
