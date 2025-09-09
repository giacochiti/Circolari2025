import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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

def send_telegram_message(text: str) -> None:
    """Invia un messaggio al gruppo Telegram tramite API"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, data=payload, timeout=20)
    if r.status_code != 200:
        print("Errore Telegram:", r.text)

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
        circulars.append((title, link))

    # Se non trova nulla, prova con la vecchia struttura
    if not circulars:
        for box in soup.select("div.wpdm-link-tpl"):
            t = box.select_one("strong.ptitle")
            title = t.get_text(strip=True) if t else "Senza titolo"
            a2 = box.find("a", href=True)
            link = urljoin(URL, a2["href"]) if a2 else None
            if link:
                circulars.append((title, link))

    return circulars

if __name__ == "__main__":
    circolari = get_all_circulars()
    if not circolari:
        print("Nessuna circolare trovata.")
    else:
        # Costruiamo un messaggio unico con tutte
        msg_lines = ["📢 Elenco circolari trovate:\n"]
        for titolo, link in circolari:
            msg_lines.append(f"• {titolo}\n🔗 {link}\n")
        message = "\n".join(msg_lines)

        send_telegram_message(message)
        print("Messaggio inviato con tutte le circolari.")
