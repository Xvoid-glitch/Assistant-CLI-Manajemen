import os
import time
import socket
import urllib.request
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

class NetworkCheck:
    def __init__(self):
        pass
    
    def cek_ping(self):
        """Cek ping ke server terkenal"""
        console.print("[bold cyan]📡 Cek Ping[/bold cyan]\n")
        
        servers = [
            ("Google DNS", "8.8.8.8"),
            ("Cloudflare DNS", "1.1.1.1"),
            ("Google", "google.com"),
            ("YouTube", "youtube.com"),
            ("GitHub", "github.com"),
        ]
        
        table = Table(title="📡 Hasil Ping")
        table.add_column("Server", style="cyan")
        table.add_column("Alamat", style="blue")
        table.add_column("Status", style="green")
        table.add_column("Waktu", style="yellow", justify="right")
        
        for name, host in servers:
            try:
                start = time.time()
                socket.setdefaulttimeout(3)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                # Resolve hostname  
                ip = socket.gethostbyname(host)
                result = sock.connect_ex((ip, 80))
                elapsed = (time.time() - start) * 1000
                sock.close()
                
                if result == 0:
                    if elapsed < 50:
                        status = "[green]✅ Sangat Cepat[/green]"
                    elif elapsed < 100:
                        status = "[green]✅ Cepat[/green]"
                    elif elapsed < 200:
                        status = "[yellow]⚡ Normal[/yellow]"
                    else:
                        status = "[red]🐌 Lambat[/red]"
                    table.add_row(name, host, status, f"{elapsed:.0f} ms")
                else:
                    table.add_row(name, host, "[red]❌ Gagal[/red]", "-")
            except Exception as e:
                table.add_row(name, host, "[red]❌ Error[/red]", "-")
        
        console.print(table)
    
    def cek_ip_publik(self):
        """Cek IP publik"""
        console.print("[bold cyan]🌐 IP Publik Kamu[/bold cyan]\n")
        
        services = [
            ("https://api.ipify.org", "IPv4"),
            ("https://ifconfig.me/ip", "Alternatif"),
        ]
        
        for url, label in services:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    ip = response.read().decode().strip()
                    console.print(f"  🌐 {label}: [bold green]{ip}[/bold green]")
                    break
            except:
                continue
        else:
            console.print("[red]Gagal mendapatkan IP publik. Cek koneksi internet.[/red]")
    
    def cek_speed_basic(self):
        """Cek kecepatan internet (basic)"""
        console.print("[bold cyan]⚡ Tes Kecepatan Internet (Basic)[/bold cyan]")
        console.print("[dim]Mendownload file kecil untuk mengukur kecepatan...[/dim]\n")
        
        # Download small file to test speed
        test_urls = [
            ("https://speed.cloudflare.com/__down?bytes=1000000", 1_000_000, "Cloudflare"),
            ("https://proof.ovh.net/files/1Mb.dat", 1_000_000, "OVH"),
        ]
        
        for url, expected_size, name in test_urls:
            try:
                console.print(f"[cyan]Menguji via {name}...[/cyan]")
                
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                start = time.time()
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = response.read()
                elapsed = time.time() - start
                
                size_mb = len(data) / (1024 * 1024)
                speed_mbps = (size_mb * 8) / elapsed
                
                if speed_mbps > 50:
                    rating = "[bold green]🚀 Sangat Cepat![/bold green]"
                elif speed_mbps > 20:
                    rating = "[green]⚡ Cepat[/green]"
                elif speed_mbps > 5:
                    rating = "[yellow]📶 Normal[/yellow]"
                else:
                    rating = "[red]🐌 Lambat[/red]"
                
                result = f"""
  📥 Download: [bold]{speed_mbps:.1f} Mbps[/bold]
  📦 Data: {size_mb:.2f} MB dalam {elapsed:.2f} detik
  📊 Rating: {rating}
                """
                console.print(Panel(result, title="⚡ Hasil Tes Kecepatan", border_style="cyan"))
                return
            except Exception as e:
                continue
        
        console.print("[red]Gagal melakukan tes kecepatan. Cek koneksi internet.[/red]")
    
    def cek_server_online(self):
        """Cek apakah server/domain online"""
        console.print("[bold cyan]🏓 Cek Status Server[/bold cyan]")
        
        domain = Prompt.ask("[yellow]Masukkan domain/URL[/yellow]")
        
        # Clean up domain
        domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        
        console.print(f"\n[cyan]Mengecek {domain}...[/cyan]\n")
        
        try:
            # DNS resolve
            ip = socket.gethostbyname(domain)
            console.print(f"  🌐 IP: [green]{ip}[/green]")
            
            # TCP connection
            start = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip, 80))
            elapsed = (time.time() - start) * 1000
            sock.close()
            
            if result == 0:
                console.print(f"  ✅ Port 80 (HTTP): [green]TERBUKA[/green] ({elapsed:.0f} ms)")
            else:
                console.print(f"  ❌ Port 80 (HTTP): [red]TERTUTUP[/red]")
            
            # HTTPS check
            try:
                start = time.time()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((ip, 443))
                elapsed = (time.time() - start) * 1000
                sock.close()
                
                if result == 0:
                    console.print(f"  ✅ Port 443 (HTTPS): [green]TERBUKA[/green] ({elapsed:.0f} ms)")
                else:
                    console.print(f"  ❌ Port 443 (HTTPS): [red]TERTUTUP[/red]")
            except:
                pass
            
            # HTTP check
            try:
                req = urllib.request.Request(f"https://{domain}", 
                    headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
                with urllib.request.urlopen(req, timeout=5) as response:
                    console.print(f"  ✅ HTTP Status: [green]{response.status} {response.reason}[/green]")
            except Exception as e:
                try:
                    req = urllib.request.Request(f"http://{domain}", 
                        headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
                    with urllib.request.urlopen(req, timeout=5) as response:
                        console.print(f"  ✅ HTTP Status: [green]{response.status}[/green]")
                except:
                    console.print(f"  ⚠️ HTTP: [yellow]Tidak dapat mengakses[/yellow]")
            
            console.print(f"\n[bold green]🟢 Server {domain} ONLINE![/bold green]")
            
        except socket.gaierror:
            console.print(f"[red]❌ Domain '{domain}' tidak ditemukan (DNS gagal)[/red]")
        except socket.timeout:
            console.print(f"[red]❌ Timeout — server mungkin offline[/red]")
        except Exception as e:
            console.print(f"[red]❌ Error: {str(e)}[/red]")
    
    def run(self):
        """Antarmuka utama network check"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print("\n[bold cyan]🌐 Cek Jaringan & Internet[/bold cyan]")
            
            menu = Table(show_header=False, box=None)
            menu.add_column("Opsi", style="cyan")
            menu.add_column("Keterangan", style="green")
            
            menu_items = [
                ("1", "📡 Cek Ping"),
                ("2", "🌐 Cek IP Publik"),
                ("3", "⚡ Tes Kecepatan (Basic)"),
                ("4", "🏓 Cek Status Server"),
                ("0", "🔙 Kembali")
            ]
            
            for item in menu_items:
                menu.add_row(item[0], item[1])
            
            console.print(menu)
            
            choice = Prompt.ask("Pilihan", choices=["0","1","2","3","4"], default="0")
            
            if choice == "0":
                break
            elif choice == "1":
                self.cek_ping()
            elif choice == "2":
                self.cek_ip_publik()
            elif choice == "3":
                self.cek_speed_basic()
            elif choice == "4":
                self.cek_server_online()
            
            if choice != "0":
                console.print("[dim]Tekan Enter untuk melanjutkan...[/dim]")
                input()
