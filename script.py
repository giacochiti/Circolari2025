import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Config (hard-coded come vuoi tu) ---
CHAT_ID = "-1002309715979"
TOKEN = "7305004967:AAGe1tySkfUANi9yp0Jh2uBNAJeWwHUG2SI"

# --- URL delle circolari ---
URL = "https://www.liceoartisticopistoia.it/circolare/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36"
}

SENT_FILE = "sent.txt"

def make_session():
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=frozenset(['GET','POST']))
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    s.headers.update(HEADERS)
    return s

session = make_session()

def send_telegram_message(text: str) -> bool:
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        r = session.post(url, data=payload, timeout=20)
        r.raise_for_status()
        return True
    except Exception as e:
        print("Errore invio Telegram:", e)
        return False

def get_all_circulars():
    r = session.get(URL, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    circulars = []

    # nuova struttura
    for a in soup.select("a.presentation-card-link"):
        link = urljoin(URL, a.get("href", "").strip())
        title_tag = a.select_one("h2.h3") or a.find("h2")
        title = title_tag.get_text(strip=True) if title_tag else a.get_text(strip=True)
        circulars.append((title, link))

    # fallback vecchia struttura
    if not circulars:
        for box in soup.select("div.wpdm-link-tpl"):
            t = box.select_one("strong.ptitle")
            title = t.get_text(strip=True) if t else "Senza titolo"
            a2 = box.find("a", href=True)
            link = urljoin(URL, a2["href"]) if a2 else None
            if link:
                circulars.append((title, link))

    # rimuovi duplicati mantenendo ordine
    seen = set()
    unique = []
    for t, l in circulars:
        if l and l not in seen:
            seen.add(l)
            unique.append((t, l))
    return unique

def load_sent():
    if not os.path.exists(SENT_FILE):
        return set()
    with open(SENT_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_sent(sent_set):
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        for link in sorted(sent_set):
            f.write(link + "\n")

if __name__ == "__main__":
    try:
        circolari = get_all_circulars()
    except Exception as e:
        print("Errore nel recupero delle circolari:", e)
        raise SystemExit(1)

    if not circolari:
        print("Nessuna circolare trovata.")
        raise SystemExit(0)

    sent = load_sent()
    new = [(t, l) for (t, l) in circolari if l not in sent]

    if not new:
        print("Nessuna circolare nuova da inviare.")
        raise SystemExit(0)

    # Costruisci un singolo messaggio con tutte le nuove (puoi cambiare formato se vuoi)
    msg_lines = ["📢 Elenco nuove circolari:\n"]
    for titolo, link in new:
        msg_lines.append(f"• {titolo}\n{link}\n")

    message = "\n".join(msg_lines)
    ok = send_telegram_message(message)
    if not ok:
        print("Invio fallito.")
        raise SystemExit(1)

    # Aggiorna sent.txt (aggiunge i link inviati)
    for _, l in new:
        sent.add(l)
    save_sent(sent)
    print(f"Inviate {len(new)} nuove circolari.")
