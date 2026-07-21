
# Lumos Email Automation

Automated cold email outreach for Lumos Learning, using Selenium to send personalized HTML emails through SiteGround's Roundcube webmail interface.

---

## About Me

**Name:**  Sathwik N H 

**Role:**  BDA( as of now -- Referrals are most welcome) 

**Company:** Lumos Learning

**Linked in :** https://www.linkedin.com/in/sathwiknh1/ 

Contact:sathwiknh@gmail.com 


---

## Features

- **Reply-to-thread** — finds the last sent email in Sent folder and replies, preserving the conversation history
- **Fallback compose** — if no previous thread exists, composes a fresh email automatically
- **HTML body** — injects custom HTML messages directly into the TinyMCE editor
- **PDF attachment** — attaches a file per recipient when specified in the CSV
- **Bulk send** — processes an entire CSV list with success/failure tracking

## Files

| File | Purpose |
|---|---|
| `send_emails_html.py` | Original script — clicks Compose, fills To/Subject/Body, sends (simplest flow) |
| `send_emails1.py` | Refined version of above with counters and better error handling |
| `followup.py` | **Primary script** — searches Sent folder for previous thread → replies if found, composes fresh if not |
| `emails.csv` | Recipient list with columns: `name, email, subject, custom_message, attachment_path` |

## How to use

### 1. Prepare your CSV

```csv
name,email,subject,custom_message,attachment_path
John,john@school.org,Your Quote Inside,"<p>Dear John,</p><p>Here is your quote.</p>",C:\Users\you\Docs\quote.pdf
Jane,jane@district.gov,Follow Up,"<p>Dear Jane,</p><p>Checking in.</p>",
```

- `custom_message` — full HTML body (inline styles work best)
- `attachment_path` — optional, leave blank if no attachment

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Run

```powershell
python followup.py
```

### 4. Login

A Chrome window opens. **Log in manually** to the webmail, wait for the inbox to load, then press **Enter** in the terminal. The script takes over from there.

## Which script to use

| You want to… | Use |
|---|---|
| Reply to your last sent email, or compose new if none exists | `followup.py` |
| Always compose a fresh email (ignore sent history) | `send_emails_html.py` |
| Bulk send with success/fail summary | `send_emails1.py` |

## Timing

| Scenario | Per email | Per hour |
|---|---|---|
| Reply with attachment | ~30s | ~120 |
| Reply without attachment | ~25s | ~144 |
| Compose fresh with attachment | ~35s | ~102 |

## ⚠️ Important

- **Manual login required** — credentials are never stored or automated
- **CSV is .gitignored** — recipient data stays local
- **One email at a time** — sends sequentially with delays to avoid spam detection
- **Browser stays open** — and waits for Enter before closing, so you can verify sends

## Troubleshooting

| Problem | Likely fix |
|---|---|
| `element not interactable` | Increase the `time.sleep()` before the failing step |
| No thread found, always composes new | Check that a sent email to that recipient exists in your Sent folder |
| Attachment not attached | Verify the file path exists and remove extra quotes from CSV |
| Send button not found | The script tries inside the iframe first, then falls back to the main page |

## Tech Stack

- Python 3.12+
- Selenium + ChromeDriver
- pandas
- webdriver-manager
- SiteGround Webmail (Roundcube)

---

## License

MIT — see [LICENSE](LICENSE)

---

*Built by --- Sathwik  --- | --- MONTH YEAR (e.g., July 2026) -