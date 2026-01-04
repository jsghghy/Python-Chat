import random
import threading
from socket import *
from customtkinter import *

class App(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('600x400')
        self.title('My Online chat')
        self.minsize(400, 300)

        self.menux = 0
        self.menu_status = "showing"
        self.menu_width = 150

        self.menu = CTkFrame(self, width=self.menu_width+30, height=1000)
        self.menu.pack_propagate(False)
        self.menu.place(x=self.menux, y=30)

        self.hide_menu_btn = CTkButton(self, text="←", width=30, height=30, corner_radius=2, command=self.toggle_menu)
        self.hide_menu_btn.place(x=0, y=0)

        self.name = f"User №{random.randint(1, 1000)}"
        self.name_label = CTkLabel(self.menu, text=self.name, font=("Arial", 16, "bold"))
        self.name_label.pack(pady=(40, 10))

        self.entry = CTkEntry(self.menu, width=130)
        self.entry.pack()

        self.enter_button = CTkButton(self.menu, text="Change Name", command=self.change_name)
        self.enter_button.pack(pady=10)


        self.right_frame = CTkFrame(self)
        self.update_right_frame()

        self.chat_field = CTkTextbox(self.right_frame, font=('Arial', 14), state='disabled')
        self.chat_field.pack(fill='both', expand=True)

        self.bottom_frame = CTkFrame(self.right_frame)
        self.bottom_frame.pack(fill='x', side='bottom')

        self.message_entry = CTkEntry(self.bottom_frame, placeholder_text='Введіть повідомлення:')
        self.message_entry.pack(side='left', fill='x', expand=True)

        self.send_button = CTkButton(self.bottom_frame, text='>', width=30, height=30, command=self.send_message)
        self.send_button.pack(side='right')
        self.message_entry.bind('<Return>', lambda event: self.send_message())

        self.username = self.name
        self.sock = None

        threading.Thread(target=self.connect_to_server, daemon=True).start()

    def connect_to_server(self):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('192.168.1.101', 8080))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            self.recv_message()
        except:
            self.after(0, lambda: self.add_message(f"Система: Не вдалося підключитися до сервера."))

    def change_name(self):
        new_name = self.entry.get()[:15]
        if new_name:
            self.name = new_name
            self.username = new_name
            self.name_label.configure(text=self.name)

    def toggle_menu(self):
        if self.menu_status == "showing":
            self.menu_status = "moving_to_hide"
            self.animate()
        elif self.menu_status == "closed":
            self.menu_status = "moving_to_show"
            self.animate()

    def animate(self):
        if self.menu_status == "moving_to_hide":
            if self.menux > -self.menu_width:
                self.menux -= 10
                self.menu.place(x=self.menux-30, y=30)
                self.update_right_frame()
                self.after(10, self.animate)
            else:
                self.menu_status = "closed"
                self.hide_menu_btn.configure(text="→")

        elif self.menu_status == "moving_to_show":
            if self.menux < 0:
                self.menux += 10
                self.menu.place(x=self.menux, y=30)
                self.update_right_frame()
                self.after(10, self.animate)
            else:
                self.menu_status = "showing"
                self.hide_menu_btn.configure(text="←")

    def update_right_frame(self):
        self.right_frame.place(x=self.menux + self.menu_width + 30, y=0,
                               relwidth=1, relheight=1,
                               )

    def add_message(self, text):
        self.chat_field.configure(state='normal')
        self.chat_field.insert(END, text + '\n')
        self.chat_field.see(END)
        self.chat_field.configure(state='disabled')

    def send_message(self):
        message = self.message_entry.get().strip()
        if message:
            if self.sock:
                try:
                    data = f"TEXT@{self.username}@{message}\n"
                    self.sock.sendall(data.encode('utf-8'))
                    self.add_message(f"Я: {message}")
                    self.message_entry.delete(0, END)
                except:
                    self.add_message("Система: Помилка відправки.")
            else:
                self.add_message("Система: Немає з'єднання з сервером.")

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk: break
                buffer += chunk.decode('utf-8')
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.after(0, lambda l=line: self.handle_line(l.strip()))
            except:
                break

    def handle_line(self, line):
        if not line: return
        parts = line.split("@", 2) # TEXT @ NAME @ MESSAGE
        if len(parts) >= 3 and parts[0] == "TEXT":
            self.add_message(f"{parts[1]}: {parts[2]}")
        else:
            self.add_message(line)

if __name__ == '__main__':
    app = App()
    app.mainloop()