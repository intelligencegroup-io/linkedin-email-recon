import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import threading
import pandas as pd

class LinkedInScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Email Scraper")

        self.driver = None
        self.names = set()
        self.name_vars = []
        self.final_names = []
        self.emails = []

        self.build_gui()

    def build_gui(self):
        frame_top = tk.Frame(self.root)
        frame_top.pack(pady=10, padx=10, fill="x")

        tk.Label(frame_top, text="LinkedIn People Page URL:").pack(side="left")
        self.url_entry = tk.Entry(frame_top, width=80)
        self.url_entry.pack(side="left", padx=5)

        self.start_button = tk.Button(frame_top, text="Launch Browser", command=self.launch_browser)
        self.start_button.pack(side="left", padx=5)

        self.scrape_button = tk.Button(frame_top, text="Scrape Names", command=self.start_scraping, state="disabled")
        self.scrape_button.pack(side="left", padx=5)

        self.checklist_frame = tk.Frame(self.root)
        self.canvas = tk.Canvas(self.checklist_frame)
        self.names_container = tk.Frame(self.canvas)
        self.scrollbar = tk.Scrollbar(self.checklist_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0, 0), window=self.names_container, anchor='nw')
        self.names_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        email_frame = tk.Frame(self.root)
        email_frame.pack(pady=10)

        tk.Label(email_frame, text="Email domain:").pack(side="left")
        self.domain_entry = tk.Entry(email_frame, width=30)
        self.domain_entry.pack(side="left", padx=5)

        tk.Label(email_frame, text="Format:").pack(side="left")
        self.format_option = tk.StringVar()
        self.format_option.set("firstname.lastname")
        format_menu = tk.OptionMenu(email_frame, self.format_option,
            "firstname.lastname",
            "firstnamelastname",
            "firstnameinitial.lastname",
            "firstnameinitiallastname",
            command=lambda _: self.generate_emails())
        format_menu.pack(side="left")

        self.confirm_btn = tk.Button(self.root, text="Confirm Names", command=self.confirm_selection, state="disabled")
        self.confirm_btn.pack(pady=5)

        self.export_btn = tk.Button(self.root, text="Export to CSV", command=self.export_to_csv, state="disabled")
        self.export_btn.pack(pady=5)

        self.preview_list = scrolledtext.ScrolledText(self.root, height=12, state='disabled', font=("Courier", 10))
        self.preview_list.pack(fill="both", padx=10, pady=10, expand=True)

    def log_preview(self, message):
        self.preview_list.configure(state='normal')
        self.preview_list.insert("end", message + "\n")
        self.preview_list.see("end")
        self.preview_list.configure(state='disabled')

    def launch_browser(self):
        url = self.url_entry.get().strip()
        if "linkedin.com/company/" not in url or "/people" not in url:
            messagebox.showerror("Invalid URL", "Please enter a valid LinkedIn company People page URL.")
            return
        threading.Thread(target=self._launch_browser_thread, args=(url,), daemon=True).start()

    def _launch_browser_thread(self, url):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        service = Service("/usr/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        self.driver.get(url)
        messagebox.showinfo("Login Required", "Log in to LinkedIn and scroll through the employee list.\nThen return to this window and click 'Scrape Names'.")
        self.scrape_button.configure(state="normal")

    def start_scraping(self):
        self.scrape_button.configure(state="disabled")
        threading.Thread(target=self.scrape_names, daemon=True).start()

    def scrape_names(self):
        links = self.driver.find_elements(By.CSS_SELECTOR, 'a[aria-label^="View "]')
        for link in links:
            try:
                name_element = link.find_element(By.TAG_NAME, 'div')
                name = name_element.text.strip()
                if name and name.lower() != "linkedin member":
                    self.names.add(name)
            except:
                continue
        self.driver.quit()
        self.display_checklist()

    def display_checklist(self):
        for widget in self.names_container.winfo_children():
            widget.destroy()
        self.name_vars = []

        for name in sorted(self.names):
            var = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(self.names_container, text=name, variable=var, anchor="w", justify="left")
            cb.pack(fill="x", padx=5, pady=2, anchor="w")
            self.name_vars.append((var, name))

        self.checklist_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.confirm_btn.configure(state="normal")

    def confirm_selection(self):
        self.final_names = [name for var, name in self.name_vars if var.get()]
        if not self.final_names:
            messagebox.showerror("No names selected", "Please select at least one name.")
            return
        self.generate_emails()
        self.export_btn.configure(state="normal")

    def generate_emails(self):
        domain = self.domain_entry.get().strip()
        fmt = self.format_option.get()

        self.preview_list.configure(state='normal')
        self.preview_list.delete("1.0", tk.END)
        self.preview_list.configure(state='disabled')
        self.emails = []

        for name in self.final_names:
            parts = name.strip().lower().split()
            if not parts or len(parts) < 2:
                continue
            fname, lname = parts[0], parts[-1]
            mi = parts[1][0] if len(parts) > 2 else ""

            if fmt == "firstname.lastname":
                email = f"{fname}.{lname}@{domain}"
            elif fmt == "firstnamelastname":
                email = f"{fname}{lname}@{domain}"
            elif fmt == "firstnameinitial.lastname":
                email = f"{fname[0]}.{lname}@{domain}"
            elif fmt == "firstnameinitiallastname":
                email = f"{fname[0]}{lname}@{domain}"
            else:
                continue

            full_email = f"{name} <{email}>"
            self.log_preview(full_email)
            self.emails.append((name, email))

    def export_to_csv(self):
        if not self.emails:
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            df = pd.DataFrame(self.emails, columns=["Name", "Email"])
            df.to_csv(path, index=False)
            messagebox.showinfo("Exported", f"Saved to {path}")


# Launch the tkinter app in full screen (cross-platform safe)
root = tk.Tk()
try:
    root.attributes('-zoomed', True)  # Linux/Windows fullscreen
except:
    root.state('normal')  # fallback
app = LinkedInScraperApp(root)
root.mainloop()
