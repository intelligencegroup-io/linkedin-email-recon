import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import threading
import pandas as pd
import subprocess

class LinkedInScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Email Scraper")
        self.root.configure(bg="#0F111A")
        self.driver = None
        self.names = set()
        self.name_vars = []
        self.final_names = []
        self.emails = []
        self.build_gui()

    def build_gui(self):
        bg = "#0F111A"
        input_bg = "#1E212B"
        fg = "#C5C8C6"

        container = tk.Frame(self.root, bg=bg)
        container.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        left_frame = tk.Frame(container, bg=bg)
        right_frame = tk.Frame(container, bg=bg)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right_frame.grid(row=0, column=1, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        def label(frame, text):
            return tk.Label(frame, text=text, bg=bg, fg=fg)

        label(left_frame, "LinkedIn People Page URL:").pack(anchor="w")
        self.url_entry = tk.Entry(left_frame, width=50, bg=input_bg, fg=fg, insertbackground=fg)
        self.url_entry.pack(fill="x", pady=5)

        self.start_button = tk.Button(left_frame, text="Launch Browser", command=self.launch_browser, width=25,
                                      bg=input_bg, fg=fg)
        self.start_button.pack(pady=(5, 2))

        self.scrape_button = tk.Button(left_frame, text="Scrape Names", command=self.start_scraping,
                                       state="disabled", width=25, bg=input_bg, fg=fg)
        self.scrape_button.pack(pady=2)

        label(left_frame, "Email Domain:").pack(anchor="w", pady=(10, 0))
        self.domain_entry = tk.Entry(left_frame, bg=input_bg, fg=fg, insertbackground=fg)
        self.domain_entry.pack(fill="x", pady=5)

        label(left_frame, "Email Format:").pack(anchor="w", pady=(10, 0))
        self.format_option = tk.StringVar(value="firstname.lastname")
        format_menu = tk.OptionMenu(left_frame, self.format_option,
            "firstname.lastname", "firstnamelastname", "firstnameinitial.lastname", "firstnameinitiallastname",
            command=lambda _: self.generate_emails())
        format_menu.config(width=30, bg=input_bg, fg=fg, activebackground="#303641", activeforeground=fg)
        format_menu["menu"].config(bg=input_bg, fg=fg)
        format_menu.pack(pady=5)

        self.confirm_btn = tk.Button(left_frame, text="Confirm Names", command=self.confirm_selection,
                                     state="disabled", width=25, bg=input_bg, fg=fg)
        self.confirm_btn.pack(pady=(10, 2))

        self.export_btn = tk.Button(left_frame, text="Export to CSV", command=self.export_to_csv,
                                    state="disabled", width=25, bg=input_bg, fg=fg)
        self.export_btn.pack(pady=2)

        checklist_container = tk.LabelFrame(left_frame, text="Employee Names", padx=5, pady=5,
                                            bg=bg, fg=fg, bd=1)
        checklist_container.pack(fill="both", expand=True, pady=(10, 0))

        self.checklist_frame = tk.Frame(checklist_container, bg=bg)
        self.canvas = tk.Canvas(self.checklist_frame, bg=bg, highlightthickness=0)
        self.names_container = tk.Frame(self.canvas, bg=bg)
        self.scrollbar = tk.Scrollbar(self.checklist_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0, 0), window=self.names_container, anchor='nw')
        self.names_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.checklist_frame.pack(fill="both", expand=True)

        label(right_frame, "Email Preview").pack(anchor="w")
        self.preview_list = scrolledtext.ScrolledText(right_frame, height=30, state='disabled', font=("Courier", 10),
                                                      bg=bg, fg=fg, insertbackground=fg)
        self.preview_list.pack(fill="both", expand=True)

        # Footer
        footer = tk.Label(self.root, text="💻 Coded with ❤️ by Intelligence Group", font=("Helvetica", 9),
                          fg="#888", bg=bg)
        footer.pack(side="bottom", pady=(5, 10))

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
        window_width = 1100
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))

        chrome_options = Options()
        chrome_options.add_argument(f"--window-size={window_width},{window_height}")
        chrome_options.add_argument(f"--window-position={x},{y}")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        service = Service("/usr/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get(url)
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
            cb = tk.Checkbutton(self.names_container, text=name, variable=var, anchor="w", justify="left",
                                bg="#0F111A", fg="#C5C8C6", selectcolor="#303641", activebackground="#1E212B")
            cb.pack(fill="x", padx=5, pady=2, anchor="w")
            self.name_vars.append((var, name))
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
            if len(parts) < 2:
                continue
            fname, lname = parts[0], parts[-1]
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
            try:
                subprocess.Popen(["libreoffice", "--calc", "--norestore", path])
            except Exception as e:
                messagebox.showwarning("Open Failed", f"Export succeeded but LibreOffice could not be opened:\n{e}")

# Launch GUI centered
root = tk.Tk()
window_width = 1100
window_height = 700
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

app = LinkedInScraperApp(root)
root.mainloop()
