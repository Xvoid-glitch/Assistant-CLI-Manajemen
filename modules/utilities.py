import os
import shutil
import psutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
import qrcode
import secrets
import string
import re

console = Console()

class Utilities:
    def __init__(self):
        self.console = Console()
    
    def generate_password(self):
        """Buat password acak"""
        console.print("[bold cyan]🔐 Pembuat Password[/bold cyan]")
        
        length = IntPrompt.ask("Panjang password", default=12)
        use_special = Confirm.ask("Gunakan karakter spesial?", default=True)
        
        alphabet = string.ascii_letters + string.digits
        if use_special:
            alphabet += string.punctuation
        
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        
        strength = "Lemah"
        if length >= 12 and use_special:
            strength = "Kuat"
        elif length >= 8:
            strength = "Sedang"
            
        console.print(Panel(
            f"[bold green]{password}[/bold green]\n[yellow]Kekuatan: {strength}[/yellow]",
            title="Password Dibuat",
            border_style="green"
        ))
    
    def generate_qrcode(self):
        """Buat QR Code"""
        console.print("[bold cyan]📱 Pembuat QR Code[/bold cyan]")
        
        data = Prompt.ask("Masukkan teks/URL/data")
        filename = Prompt.ask("Nama file output (tanpa ekstensi)", default="qrcode")
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"{filename}.png")
        
        console.print(f"[green]QR Code disimpan sebagai {filename}.png[/green]")
    
    def unit_converter(self):
        """Konverter Satuan"""
        console.print("[bold cyan]🔄 Konverter Satuan[/bold cyan]")
        
        console.print("1. 📏 Panjang (meter)")
        console.print("2. 🌡️ Suhu (Celsius)")
        console.print("3. ⚖️ Berat (kg)")
        console.print("4. 💾 Penyimpanan (GB)")
        
        mode = Prompt.ask("Pilih konversi", choices=["1", "2", "3", "4"], default="1")
        
        if mode == "1":
            val = float(Prompt.ask("Nilai (meter)"))
            console.print(f"  {val} m = {val*100} cm")
            console.print(f"  {val} m = {val/1000} km")
            console.print(f"  {val} m = {val*3.28084:.2f} feet")
            console.print(f"  {val} m = {val*39.3701:.2f} inch")
            
        elif mode == "2":
            val = float(Prompt.ask("Nilai (Celsius)"))
            console.print(f"  {val}°C = {(val*9/5)+32:.1f}°F")
            console.print(f"  {val}°C = {val+273.15:.1f}K")
            
        elif mode == "3":
            val = float(Prompt.ask("Nilai (kg)"))
            console.print(f"  {val} kg = {val*1000} gram")
            console.print(f"  {val} kg = {val*2.20462:.2f} lbs")
            console.print(f"  {val} kg = {val*35.274:.2f} oz")
            
        elif mode == "4":
            val = float(Prompt.ask("Nilai (GB)"))
            console.print(f"  {val} GB = {val*1024:.0f} MB")
            console.print(f"  {val} GB = {val*(1024**2):.0f} KB")
            console.print(f"  {val} GB = {val/1024:.4f} TB")
    
    def system_info(self):
        """Tampilkan info sistem"""
        import platform
        
        info = {
            "Sistem": platform.system(),
            "Rilis": platform.release(),
            "Versi": platform.version(),
            "Arsitektur": platform.machine(),
            "Prosesor": platform.processor(),
            "Python": platform.python_version()
        }
        
        table = Table(title="💻 Informasi Sistem")
        table.add_column("Properti", style="cyan")
        table.add_column("Nilai", style="green")
        
        for k, v in info.items():
            table.add_row(k, v)
            
        console.print(table)
        
        # Penggunaan Disk
        console.print("\n[bold]💾 Penggunaan Disk:[/bold]")
        try:
            disk = psutil.disk_usage('/')
            total = disk.total / (1024**3)
            used = disk.used / (1024**3)
            free = disk.free / (1024**3)
            percent = disk.percent
            console.print(f"  Total: {total:.2f} GB | Terpakai: {used:.2f} GB | Kosong: {free:.2f} GB ({percent}%)")
        except:
            console.print("  [dim]Tidak dapat membaca informasi disk[/dim]")
        
        # RAM
        console.print("\n[bold]🧠 Penggunaan RAM:[/bold]")
        ram = psutil.virtual_memory()
        ram_total = ram.total / (1024**3)
        ram_used = ram.used / (1024**3)
        console.print(f"  Total: {ram_total:.2f} GB | Terpakai: {ram_used:.2f} GB ({ram.percent}%)")
    
    def safe_link_previewer(self):
        """Pemeriksa keamanan link"""
        console.print("[bold cyan]🔗 Pemeriksa Keamanan Link[/bold cyan]")
        console.print("[dim]Cek apakah sebuah link aman sebelum dibuka[/dim]\n")
        
        url = Prompt.ask("[yellow]Masukkan URL yang ingin dicek[/yellow]")
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        console.print(f"\n[cyan]🔍 Menganalisa: {url}[/cyan]\n")
        
        warnings = []
        safe_signs = []
        
        # Check HTTPS
        if url.startswith('https://'):
            safe_signs.append("✅ Menggunakan HTTPS (koneksi terenkripsi)")
        else:
            warnings.append("⚠️ TIDAK menggunakan HTTPS! Koneksi tidak aman!")
        
        # Check for suspicious patterns
        suspicious_patterns = [
            (r'@', "⚠️ Mengandung karakter '@' — kemungkinan phishing!"),
            (r'\.tk$|\.ml$|\.ga$|\.cf$|\.gq$', "⚠️ Domain gratis yang sering dipakai phishing!"),
            (r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', "⚠️ Menggunakan IP langsung, bukan domain!"),
            (r'login|signin|verify|update|secure|account.*confirm', "⚠️ Mengandung kata-kata yang sering dipakai phishing!"),
            (r'bit\.ly|tinyurl|t\.co|goo\.gl|is\.gd', "⚠️ Link dipendekkan — tidak bisa melihat tujuan asli!"),
        ]
        
        for pattern, msg in suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                warnings.append(msg)
        
        # Check URL length
        if len(url) > 100:
            warnings.append("⚠️ URL sangat panjang — bisa jadi mencurigakan")
        else:
            safe_signs.append("✅ Panjang URL normal")
        
        # Check known safe domains
        safe_domains = ['google.com', 'youtube.com', 'github.com', 'wikipedia.org', 
                       'stackoverflow.com', 'microsoft.com', 'apple.com', 'facebook.com',
                       'instagram.com', 'twitter.com', 'linkedin.com', 'tokopedia.com',
                       'shopee.co.id', 'bukalapak.com', 'gojek.com', 'grab.com']
        
        for domain in safe_domains:
            if domain in url.lower():
                safe_signs.append(f"✅ Domain terpercaya ({domain})")
                break
        
        # Try to connect
        try:
            import requests
            console.print("[dim]Mencoba menghubungi server...[/dim]")
            resp = requests.head(url, timeout=5, allow_redirects=True)
            safe_signs.append(f"✅ Server merespon (status: {resp.status_code})")
            
            if resp.url != url:
                warnings.append(f"⚠️ Redirect ke: {resp.url}")
                
            if resp.status_code >= 400:
                warnings.append(f"⚠️ Server mengembalikan error ({resp.status_code})")
        except:
            warnings.append("⚠️ Server tidak merespon atau tidak dapat dijangkau")
        
        # Display results
        result = ""
        if safe_signs:
            result += "[bold green]🛡️ Tanda Aman:[/bold green]\n"
            for s in safe_signs:
                result += f"  {s}\n"
        
        if warnings:
            result += "\n[bold red]⚠️ Peringatan:[/bold red]\n"
            for w in warnings:
                result += f"  {w}\n"
        
        if len(warnings) == 0:
            result += "\n[bold green]🟢 LINK KEMUNGKINAN AMAN[/bold green]"
        elif len(warnings) <= 2:
            result += "\n[bold yellow]🟡 HATI-HATI — ada beberapa peringatan[/bold yellow]"
        else:
            result += "\n[bold red]🔴 MENCURIGAKAN — jangan buka link ini![/bold red]"
        
        console.print(Panel(result, title="🔗 Hasil Analisa Link", border_style="cyan"))
    
    def password_strength_checker(self):
        """Pemeriksa kekuatan password"""
        console.print("[bold cyan]🔒 Pemeriksa Kekuatan Password[/bold cyan]")
        console.print("[dim]Cek apakah password kamu sudah aman[/dim]\n")
        
        password = Prompt.ask("[yellow]Masukkan password yang ingin dicek[/yellow]")
        
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 16:
            score += 3
            feedback.append("✅ Panjang sangat baik (16+ karakter)")
        elif len(password) >= 12:
            score += 2
            feedback.append("✅ Panjang baik (12+ karakter)")
        elif len(password) >= 8:
            score += 1
            feedback.append("⚠️ Panjang cukup (8+ karakter), idealnya 12+")
        else:
            feedback.append("❌ Terlalu pendek! Minimal 8 karakter")
        
        # Uppercase
        if re.search(r'[A-Z]', password):
            score += 1
            feedback.append("✅ Mengandung huruf besar")
        else:
            feedback.append("❌ Tambahkan huruf besar (A-Z)")
        
        # Lowercase
        if re.search(r'[a-z]', password):
            score += 1
            feedback.append("✅ Mengandung huruf kecil")
        else:
            feedback.append("❌ Tambahkan huruf kecil (a-z)")
        
        # Numbers
        if re.search(r'[0-9]', password):
            score += 1
            feedback.append("✅ Mengandung angka")
        else:
            feedback.append("❌ Tambahkan angka (0-9)")
        
        # Special characters
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            score += 2
            feedback.append("✅ Mengandung karakter spesial")
        else:
            feedback.append("❌ Tambahkan karakter spesial (!@#$%...)")
        
        # Common patterns check
        common = ['password', '123456', 'qwerty', 'abc123', 'admin', 'letmein',
                  '1234', 'pass', 'login', 'welcome', 'master', 'dragon',
                  'monkey', 'shadow', 'sunshine', 'princess', 'football']
        
        if password.lower() in common or any(c in password.lower() for c in common):
            score = max(0, score - 3)
            feedback.append("❌ Mengandung kata umum yang mudah ditebak!")
        
        # Repeated characters
        if re.search(r'(.)\1{2,}', password):
            score = max(0, score - 1)
            feedback.append("⚠️ Mengandung karakter berulang")
        
        # Rating
        if score >= 7:
            rating = "[bold green]🟢 SANGAT KUAT[/bold green]"
            bar_color = "green"
        elif score >= 5:
            rating = "[bold cyan]🔵 KUAT[/bold cyan]"
            bar_color = "cyan"
        elif score >= 3:
            rating = "[bold yellow]🟡 SEDANG[/bold yellow]"
            bar_color = "yellow"
        else:
            rating = "[bold red]🔴 LEMAH[/bold red]"
            bar_color = "red"
        
        # Visual bar
        bar_filled = min(score, 8)
        bar = f"[{bar_color}]{'█' * bar_filled}{'░' * (8 - bar_filled)}[/{bar_color}]"
        
        result = f"Kekuatan: {rating}\n{bar} ({score}/8)\n\n"
        result += "[bold]Detail Analisa:[/bold]\n"
        for f in feedback:
            result += f"  {f}\n"
        
        console.print(Panel(result, title="🔒 Hasil Analisa Password", border_style="cyan"))

    def run(self):
        """Menu utama utilitas"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print("\n[bold cyan]⚡ Utilitas[/bold cyan]")
            
            menu = Table(show_header=False, box=None)
            menu.add_column("Opsi", style="cyan")
            menu.add_column("Keterangan", style="green")
            
            menu_items = [
                ("1", "🔐 Pembuat Password"),
                ("2", "🔒 Cek Kekuatan Password"),
                ("3", "📱 Pembuat QR Code"),
                ("4", "🔄 Konverter Satuan"),
                ("5", "💻 Info Sistem"),
                ("6", "🔗 Cek Keamanan Link"),
                ("0", "🔙 Kembali")
            ]
            
            for item in menu_items:
                menu.add_row(item[0], item[1])
            
            console.print(menu)
            
            choice = Prompt.ask("Pilihan", 
                              choices=["0", "1", "2", "3", "4", "5", "6"], 
                              default="0")
            
            if choice == "0":
                break
            elif choice == "1":
                self.generate_password()
            elif choice == "2":
                self.password_strength_checker()
            elif choice == "3":
                self.generate_qrcode()
            elif choice == "4":
                self.unit_converter()
            elif choice == "5":
                self.system_info()
            elif choice == "6":
                self.safe_link_previewer()
            
            if choice != "0":
                console.print("[dim]Tekan Enter untuk melanjutkan...[/dim]")
                input()