import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

# --- Config Telegram ---
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

def send_telegram_message(text: str) -> None:
    """Invia un messaggio al gruppo Telegram tramite API"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, data=payload, timeout=20)
    if r.status_code != 200:
        print("Errore Telegram:", r.text)

def load_sent_circulars():
    """Legge i link già inviati da sent.txt"""
    if not os.path.exists(SENT_FILE):
        return set()
    with open(SENT_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_sent_circular(link):
    """Aggiunge un link a sent.txt"""
    with open(SENT_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def get_all_circulars():
    """Scarica la pagina e trova tutte le circolari"""
    r = requests.get(URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    circulars = []

    # Struttura nuova: <a class="presentation-card-link">
    for a in soup.select("a.presentation-card-link"):
        link = urljoin(URL, a.get("href", "").strip())
        title_tag = a.select_one("h2.h3") or a.find("h2")
        title = title_tag.get_text(strip=True) if title_tag else a.get_text(strip=True)
        # Numero circolare
        num_tag = a.select_one("small.h6.text-greendark")
        num = num_tag.get_text(strip=True) if num_tag else "Nessun numero"
        circulars.append((num, title, link))

    # Vecchia struttura come fallback
    if not circulars:
        for box in soup.select("div.wpdm-link-tpl"):
            t = box.select_one("strong.ptitle")
            title = t.get_text(strip=True) if t else "Senza titolo"
            a2 = box.find("a", href=True)
            link = urljoin(URL, a2["href"]) if a2 else None
            num = "Nessun numero"
            if link:
                circulars.append((num, title, link))

    return circulars

if __name__ == "__main__":
    sent_links = load_sent_circulars()
    circolari = get_all_circulars()
    new_circolari = [c for c in circolari if c[2] not in sent_links]

    # Inverti l’ordine: prima le circolari più vecchie tra le nuove
    new_circolari.reverse()

    if not new_circolari:
        print("Nessuna circolare nuova da inviare.")
    else:
        for num, titolo, link in new_circolari:
            message = f"📢 {num}: {titolo}\n🔗 {link}"
            send_telegram_message(message)
            print("Messaggio inviato:", message)
            save_sent_circular(link)

