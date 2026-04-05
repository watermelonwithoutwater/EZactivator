import customtkinter as ctk
import pyautogui
import time
import os
import pygetwindow as gw
import webbrowser
import stripe
from database import sign_up, login_in

stripe.api_key = "sk_test_51TIv44RF77RBnyjJRDcMY4SUqtEOYF78OBe9vSV3HwiBYyHCrQPMcAN8R9ldTOGJXZT4xN9K6GaQ6C0EWBptVthJ00KZC02gJ4"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("EZactivator PRO - API Edition")
        self.geometry("450x650")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.show_login_screen()

    def clear_screen(self):
        for child in self.container.winfo_children():
            child.destroy()

    def show_login_screen(self):
        self.clear_screen()
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        frame.pack(expand=True)

        ctk.CTkLabel(frame, text="EZactivator", font=("Arial", 32, "bold")).pack(pady=20)

        self.email_input = ctk.CTkEntry(frame, placeholder_text="Email", width=300, height=45)
        self.email_input.pack(pady=10)

        self.password_input = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=300, height=45)
        self.password_input.pack(pady=10)

        self.msg = ctk.CTkLabel(frame, text="", text_color="red")
        self.msg.pack(pady=5)

        ctk.CTkButton(frame, text="Login", command=self.handle_login, width=300, height=45).pack(pady=10)
        ctk.CTkButton(frame, text="Create Account", command=self.handle_signup,
                      fg_color="transparent", border_width=1, width=300, height=45).pack()

    def show_payment_screen(self):
        self.clear_screen()
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        frame.pack(expand=True)

        ctk.CTkLabel(frame, text="Activation Required", font=("Arial", 24, "bold")).pack(pady=20)
        ctk.CTkLabel(frame, text="Pay via Stripe API to Unlock PRO", text_color="gray").pack()

        self.promo_input = ctk.CTkEntry(frame, placeholder_text="Enter Promo Code (EZ2026)", width=300, height=45)
        self.promo_input.pack(pady=20)

        self.pay_msg = ctk.CTkLabel(frame, text="", text_color="red")
        self.pay_msg.pack()

        ctk.CTkButton(frame, text="Verify Promo Code", command=self.verify_promo,
                      fg_color="#3498db", width=300, height=45).pack(pady=10)

        ctk.CTkLabel(frame, text="OR", text_color="gray").pack(pady=5)

        ctk.CTkButton(frame, text="Pay $10.00 (Stripe)", command=self.process_api_payment,
                      width=300, height=45, fg_color="#e67e22").pack()

    def show_main_menu(self):
        self.clear_screen()
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(frame, text="Main Menu", font=("Arial", 28, "bold")).pack(pady=40)

        self.active_btn = ctk.CTkButton(frame, text="ACTIVE NOW!",
                                        fg_color="#2ecc71", hover_color="#27ae60",
                                        font=("Arial", 22, "bold"), width=280, height=100,
                                        corner_radius=50, command=self.start_smart_activation)
        self.active_btn.place(relx=0.5, rely=0.5, anchor="center")

        self.status_label = ctk.CTkLabel(frame, text="Status: Ready", text_color="gray")
        self.status_label.pack(side="bottom", pady=20)

    def process_api_payment(self):
        try:
            self.pay_msg.configure(text="Creating Checkout Session...", text_color="cyan")
            self.update()

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': 'EZactivator PRO License'},
                        'unit_amount': 1000,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='https://checkout.stripe.com/test/success',
                cancel_url='https://checkout.stripe.com/test/cancel',
            )

            webbrowser.open(session.url)
            self.check_payment_loop(session.id)

        except Exception as e:
            self.pay_msg.configure(text=f"API Error: {str(e)[:50]}...", text_color="red")

    def check_payment_loop(self, session_id):
        self.pay_msg.configure(text="Waiting for Stripe Confirmation...", text_color="yellow")
        self.update()

        for _ in range(120):
            try:
                session = stripe.checkout.Session.retrieve(session_id)
                if session.payment_status == 'paid':
                    self.pay_msg.configure(text="Payment Verified!", text_color="green")
                    self.update()
                    time.sleep(2)
                    self.show_main_menu()
                    return
            except:
                pass
            time.sleep(5)

        self.pay_msg.configure(text="Timeout. Please try again.", text_color="red")

    def start_smart_activation(self):
        self.active_btn.configure(text="WORKING...", state="disabled", fg_color="#e67e22")
        self.status_label.configure(text="Status: Launching PowerShell...")
        self.update()

        os.system("start powershell -Command \"irm https://get.activated.win | iex\"")

        found = False
        timeout = 30
        start_time = time.time()

        while not found and (time.time() - start_time) < timeout:
            all_windows = gw.getAllTitles()
            for title in all_windows:
                if "Administrator" in title or "Windows PowerShell" in title:
                    try:
                        win = gw.getWindowsWithTitle(title)[0]
                        win.activate()
                        found = True
                        break
                    except:
                        continue
            time.sleep(0.5)

        if found:
            self.status_label.configure(text="Status: Tool Found! Executing...")
            self.update()

            time.sleep(1.5)
            pyautogui.press('1')
            time.sleep(2)
            pyautogui.press('1')
            time.sleep(1)
            pyautogui.press('0')
            time.sleep(0.5)
            pyautogui.press('0')

            self.active_btn.configure(text="SUCCESS!", state="normal", fg_color="#2ecc71")
            self.status_label.configure(text="Status: Done. Restart Required.")
            self.update()
            self.ask_for_restart()
        else:
            self.status_label.configure(text="Error: Tool not detected.", text_color="red")
            self.active_btn.configure(text="RETRY", state="normal")

    def ask_for_restart(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Restart")
        dialog.geometry("350x180")
        dialog.attributes("-topmost", True)
        ctk.CTkLabel(dialog, text="Activation Success!\nRestart PC now?").pack(pady=20)
        btn_f = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_f.pack()
        ctk.CTkButton(btn_f, text="Yes", fg_color="#e74c3c", width=100,
                      command=lambda: os.system("shutdown /r /t 0")).pack(side="left", padx=10)
        ctk.CTkButton(btn_f, text="Later", fg_color="gray", width=100, command=dialog.destroy).pack(side="left",
                                                                                                    padx=10)

    def handle_login(self):
        s, e = login_in(self.email_input.get(), self.password_input.get())
        if s:
            self.show_payment_screen()
        else:
            self.msg.configure(text=e)

    def handle_signup(self):
        s, e = sign_up(self.email_input.get(), self.password_input.get())
        if s:
            self.msg.configure(text="Account Created!", text_color="green")
        else:
            self.msg.configure(text=e)

    def verify_promo(self):
        if self.promo_input.get() == "shawrma":
            self.show_main_menu()
        else:
            self.pay_msg.configure(text="Invalid Code!", text_color="red")


if __name__ == "__main__":
    app = App()
    app.mainloop()