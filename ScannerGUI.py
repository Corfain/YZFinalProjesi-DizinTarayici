import requests
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import threading
from datetime import datetime

class CyberScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ADVANCED DIRECTORY SCANNER v3.0 | CYBER-SECURITY TOOL")
        self.root.geometry("900x750")
        self.root.configure(bg="#0a0f14")

        # Tarama sonuçlarını hafızada tutacağımız liste (Raporlama için)
        self.found_items = []

        # Header Alanı
        self.header = tk.Frame(self.root, bg="#111827", height=80)
        self.header.pack(fill=tk.X)
        
        tk.Label(self.header, text="VULNERABILITY RECONNAISSANCE TOOL", bg="#111827", fg="#4ade80", 
                 font=("Orbitron", 18, "bold")).pack(pady=20)

        # Giriş Paneli
        self.input_frame = tk.Frame(self.root, bg="#0a0f14", padx=40, pady=10)
        self.input_frame.pack(fill=tk.X)

        # URL Girişi
        tk.Label(self.input_frame, text="HEDEF DOMAIN / URL", bg="#0a0f14", fg="#94a3b8", 
                 font=("Verdana", 10, "bold")).pack(anchor=tk.W)
        self.url_entry = tk.Entry(self.input_frame, width=60, bg="#1f2937", fg="white", 
                                  insertbackground="white", borderwidth=0, font=("Consolas", 12))
        self.url_entry.pack(fill=tk.X, pady=5, ipady=8)
        self.url_entry.insert(0, "testphp.vulnweb.com")

        # Uzantı Filtreleme Girişi (YENİ EKLENDİ)
        tk.Label(self.input_frame, text="UZANTILAR (Virgülle ayırın, örn: .php, .txt, .bak) - Boş bırakılabilir", 
                 bg="#0a0f14", fg="#94a3b8", font=("Verdana", 9)).pack(anchor=tk.W, pady=(10, 0))
        self.ext_entry = tk.Entry(self.input_frame, width=60, bg="#1f2937", fg="white", 
                                  insertbackground="white", borderwidth=0, font=("Consolas", 11))
        self.ext_entry.pack(fill=tk.X, pady=5, ipady=6)
        self.ext_entry.insert(0, ".php, .zip")

        # Butonlar
        self.btn_frame = tk.Frame(self.input_frame, bg="#0a0f14")
        self.btn_frame.pack(fill=tk.X, pady=15)

        self.start_btn = tk.Button(self.btn_frame, text="TARAMAYI BAŞLAT", command=self.start_thread, 
                                   bg="#059669", fg="white", activebackground="#10b981", 
                                   font=("Verdana", 10, "bold"), borderwidth=0, cursor="hand2", padx=20, pady=10)
        self.start_btn.pack(side=tk.LEFT)

        # Rapor Kaydet Butonu (YENİ EKLENDİ)
        self.report_btn = tk.Button(self.btn_frame, text="HTML RAPOR AL", command=self.save_report, 
                                    bg="#2563eb", fg="white", activebackground="#3b82f6", state=tk.DISABLED,
                                    font=("Verdana", 10, "bold"), borderwidth=0, cursor="hand2", padx=20, pady=10)
        self.report_btn.pack(side=tk.LEFT, padx=10)

        self.clear_btn = tk.Button(self.btn_frame, text="EKRANI TEMİZLE", command=self.clear_screen, 
                                   bg="#374151", fg="white", font=("Verdana", 10), borderwidth=0, padx=15, pady=10)
        self.clear_btn.pack(side=tk.LEFT)

        # Sonuç Ekranı
        self.result_area = scrolledtext.ScrolledText(self.root, bg="#000000", fg="#d1d5db", 
                                                     font=("Consolas", 11), borderwidth=0, padx=15, pady=15)
        self.result_area.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 20))
        
        self.result_area.tag_config("found", foreground="#4ade80")
        self.result_area.tag_config("warn", foreground="#facc15")
        self.result_area.tag_config("info", foreground="#3b82f6")

    def log(self, message, tag="info"):
        self.result_area.insert(tk.END, message + "\n", tag)
        self.result_area.see(tk.END)

    def clear_screen(self):
        self.result_area.delete(1.0, tk.END)
        self.found_items.clear()
        self.report_btn.config(state=tk.DISABLED)

    def save_report(self):
        if not self.found_items:
            messagebox.showwarning("Uyarı", "Raporlanacak bir bulgu yok!")
            return

        # Kullanıcıya raporu nereye kaydedeceğini soran pencere
        file_path = filedialog.asksaveasfilename(defaultextension=".html", 
                                                 initialfile=f"Tarama_Raporu_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                                                 title="Raporu Kaydet",
                                                 filetypes=[("HTML Files", "*.html")])
        if not file_path:
            return

        # HTML Rapor Tasarımı (Şık Kurumsal Şablon)
        html_content = f"""
        <html>
        <head>
            <title>Siber Güvenlik Tarama Raporu</title>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f3f4f6; color: #1f2937; margin: 40px; }}
                .container {{ background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                h1 {{ color: #111827; border-bottom: 3px solid #10b981; padding-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
                th {{ background-color: #111827; color: white; }}
                .status-200 {{ color: #059669; font-weight: bold; }}
                .status-403 {{ color: #d97706; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Web Dizin Tarama Raporu</h1>
                <p><strong>Tarih:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Hedef URL:</strong> {self.url_entry.get()}</p>
                <p><strong>Toplam Bulunan:</strong> {len(self.found_items)} adet</p>
                <table>
                    <tr><th>HTTP Durumu</th><th>Erişim URL'si</th></tr>
        """
        for status, url in self.found_items:
            status_class = "status-200" if status == 200 else "status-403"
            html_content += f"<tr><td class='{status_class}'>{status}</td><td><a href='{url}' target='_blank'>{url}</a></td></tr>"
        
        html_content += """
                </table>
            </div>
        </body>
        </html>
        """

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(html_content)
            messagebox.showinfo("Başarılı", f"Rapor başarıyla kaydedildi!\n{file_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor kaydedilemedi: {e}")

    def scan(self):
        target = self.url_entry.get().strip()
        extensions_input = self.ext_entry.get().strip()
        
        if not target:
            messagebox.showwarning("Uyarı", "Geçerli bir hedef belirtilmedi!")
            return

        if not target.startswith("http"): target = "http://" + target
        
        try:
            with open("wordlist.txt", "r") as f:
                base_words = [line.strip() for line in f if line.strip()]
        except:
            messagebox.showerror("Hata", "wordlist.txt dosyası bulunamadı!")
            return

        # Uzantıları ayarla (Örn: admin, admin.php, admin.zip)
        words_to_scan = []
        exts = [e.strip() for e in extensions_input.split(',')] if extensions_input else []
        
        for word in base_words:
            words_to_scan.append(word) # Önce kelimenin yalın hali
            for ext in exts:
                if ext: # Uzantı boş değilse
                    # Uzantının başında nokta yoksa ekle
                    if not ext.startswith('.'): ext = '.' + ext
                    words_to_scan.append(f"{word}{ext}")

        self.start_btn.config(state=tk.DISABLED, text="TARANIYOR...")
        self.report_btn.config(state=tk.DISABLED)
        self.found_items.clear()
        
        self.log(f"[>] KEŞİF BAŞLATILDI: {target}", "info")
        self.log(f"[>] TARANACAK TOPLAM KOMBİNASYON: {len(words_to_scan)} ADET", "info")
        self.log("-" * 60)

        # Custom User-Agent (WAF Atlatma Taktikleri)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

        for word in words_to_scan:
            full_url = f"{target.rstrip('/')}/{word}"
            try:
                r = requests.get(full_url, timeout=5, allow_redirects=True, headers=headers)
                if 200 <= r.status_code < 300:
                    self.log(f"[+] BULUNDU  [{r.status_code}] -> /{word}", "found")
                    self.found_items.append((r.status_code, full_url))
                elif r.status_code == 403:
                    self.log(f"[!] YASAK    [{r.status_code}] -> /{word}", "warn")
                    self.found_items.append((r.status_code, full_url))
            except:
                pass
        
        self.log("-" * 60)
        self.log(f"[*] TARAMA TAMAMLANDI. ({len(self.found_items)} sonuç bulundu)", "info")
        self.start_btn.config(state=tk.NORMAL, text="TARAMAYI BAŞLAT")
        
        if self.found_items:
            self.report_btn.config(state=tk.NORMAL) # Rapor butonu sadece bir şey bulunursa aktif olur

    def start_thread(self):
        threading.Thread(target=self.scan, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = CyberScannerApp(root)
    root.mainloop()