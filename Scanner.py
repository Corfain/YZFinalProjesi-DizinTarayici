import requests
import sys
import os
from colorama import Fore, Style, init

# Colorama'yı başlat (Windows uyumluluğu için)
init(autoreset=True)

BANNER = f"""
{Fore.CYAN}╔══════════════════════════════════════╗
║         DİZİN TARAMA ARACI           ║
║         Python Final Projesi         ║
╚══════════════════════════════════════╝{Style.RESET_ALL}
"""

def load_wordlist(path: str) -> list[str]:
    """Wordlist dosyasını okur, boş satır ve yorumları atlar."""
    if not os.path.exists(path):
        print(f"{Fore.RED}[HATA] Wordlist dosyası bulunamadı: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        words = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

    return words

def normalize_url(url: str) -> str:
    """URL'nin http/https ile başlamasını sağlar."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")

def scan(base_url: str, wordlist: list[str], timeout: int = 5) -> list[str]:
    """
    Her kelime için URL oluşturur ve HTTP isteği atar.
    200-299 arası durum kodları 'bulundu' sayılır.
    """
    found = []
    total = len(wordlist)

    print(f"\n{Fore.YELLOW}[*] Hedef  : {base_url}")
    print(f"[*] Kelime : {total} adet")
    print(f"[*] Tarama başlıyor...\n{Style.RESET_ALL}")

    for index, word in enumerate(wordlist, start=1):
        target = f"{base_url}/{word}"

        # İlerleme göstergesi (satırı üzerine yazar)
        progress = f"[{index}/{total}] Kontrol ediliyor: {target}"
        print(f"\r{Fore.WHITE}{progress:<80}", end="", flush=True)

        try:
            response = requests.get(
                target,
                timeout=timeout,
                allow_redirects=True,
                headers={"User-Agent": "DirScanner/1.0 (EduProject)"}
            )

            status = response.status_code

            if 200 <= status < 300:
                print(f"\r{Fore.GREEN}[+] BULUNDU  [{status}] → {target}{' ' * 20}")
                found.append((target, status))

            elif status == 403:
                # Yasak — dizin var ama erişim yok, yine de ilginç
                print(f"\r{Fore.YELLOW}[!] YASAK    [{status}] → {target}{' ' * 20}")
                found.append((target, status))

            elif status == 401:
                print(f"\r{Fore.MAGENTA}[!] YETKİ GEREKLİ [{status}] → {target}{' ' * 20}")
                found.append((target, status))

            # 404 ve diğerleri sessizce geçilir

        except requests.exceptions.ConnectionError:
            print(f"\r{Fore.RED}[X] Bağlantı hatası: {target}{' ' * 20}")
        except requests.exceptions.Timeout:
            print(f"\r{Fore.RED}[X] Zaman aşımı   : {target}{' ' * 20}")
        except requests.exceptions.RequestException as e:
            print(f"\r{Fore.RED}[X] İstek hatası  : {e}{' ' * 20}")

    return found

def print_results(found: list[tuple]) -> None:
    """Tarama sonunda bulunan dizinleri özetler."""
    print(f"\n\n{Fore.CYAN}{'═' * 45}")
    print(f"  TARAMA SONUÇLARI")
    print(f"{'═' * 45}{Style.RESET_ALL}")

    if not found:
        print(f"{Fore.RED}  Hiçbir dizin bulunamadı.{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}  Toplam {len(found)} dizin/sayfa tespit edildi:\n{Style.RESET_ALL}")
        for url, status in found:
            if 200 <= status < 300:
                color = Fore.GREEN
                label = "OK     "
            elif status == 403:
                color = Fore.YELLOW
                label = "YASAK  "
            else:
                color = Fore.MAGENTA
                label = "YETKİ  "
            print(f"  {color}[{status}] {label} → {url}{Style.RESET_ALL}")

    print(f"{Fore.CYAN}{'═' * 45}{Style.RESET_ALL}")

def get_user_input() -> tuple[str, str, int]:
    """Kullanıcıdan hedef URL, wordlist yolu ve timeout alır."""
    print(BANNER)

    url = input(f"{Fore.WHITE}Hedef URL girin (örn: example.com): {Style.RESET_ALL}").strip()
    if not url:
        print(f"{Fore.RED}[HATA] URL boş olamaz.")
        sys.exit(1)

    default_wordlist = "wordlist.txt"
    wl_input = input(
        f"Wordlist dosyası [{default_wordlist}]: "
    ).strip()
    wordlist_path = wl_input if wl_input else default_wordlist

    timeout_input = input("Bağlantı zaman aşımı (saniye) [5]: ").strip()
    try:
        timeout = int(timeout_input) if timeout_input else 5
    except ValueError:
        timeout = 5

    return url, wordlist_path, timeout

def main():
    try:
        url, wordlist_path, timeout = get_user_input()
        base_url = normalize_url(url)
        wordlist = load_wordlist(wordlist_path)
        found = scan(base_url, wordlist, timeout)
        print_results(found)

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}[!] Tarama kullanıcı tarafından durduruldu.{Style.RESET_ALL}")
        sys.exit(0)

if __name__ == "__main__":
    main()