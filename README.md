# LinkedIn Email Recon Tool – Generate Email Addresses from Employee Names

A Python-based GUI tool to perform LinkedIn recon and generate company email addresses from employee name lists. Ideal for red teams, OSINT professionals, and penetration testers.

## 🔍 What It Does

- Extracts employee names from a LinkedIn company "People" page
- Supports common corporate email formats
- Builds a list of likely email addresses (e.g. `john.doe@example.com`) using scraped names
- Lets you review results, preview email structure, and export to CSV
- Fully manual login and scrolling for stealth and realism

---

## 🧩 Key Features

- ✅ Manual login through real browser window (no API, no automation bans)
- ✅ Extracts names of employees from LinkedIn
- ✅ Supports formats: `firstname.lastname`, `firstnamelastname`, `j.doe`, and more
- ✅ Domain input (e.g. `@example.com`)
- ✅ Live email preview and name selection
- ✅ Export to `.csv` for phishing, enumeration, or red teaming
- ✅ Built with tkinter GUI for portability and ease of use

---


### 📦 Setup

```bash
git clone https://github.com/yourusername/linkedin-email-recon.git
cd linkedin-email-recon

python3 -m venv venv
source venv/bin/activate

pip install selenium pandas
sudo apt install chromium-driver
```

---

## 🚀 How to Use

```bash
python3 linkedin-email-recon.py
```

### Workflow

1. Paste the LinkedIn "People" page URL (e.g. `https://www.linkedin.com/company/example/people/`)
2. Launch browser → Log in manually → Scroll to load all names
3. Return to GUI and click **Scrape Names**
4. Select valid names from the list
5. Enter a domain (e.g. `company.com`) and choose a format
6. Preview the generated emails
7. Export the final list to CSV

---

## 📂 Example Output

```
John Doe <john.doe@company.com>
Jane Doe <jane.doe@company.com>
J Doe <j.doe@company.com>
```

---

## 🧠 Use Cases

- Red team email harvesting
- OSINT and LinkedIn-based recon
- Pretexting and phishing simulation
- Username generation for login portals
- Credential stuffing or validation prep

---

## ⚠ Disclaimer

This tool is intended **strictly for authorised security assessments**. Do not use it against any targets without written permission.

---

## 📄 License

MIT License — use freely for ethical hacking and training purposes.
