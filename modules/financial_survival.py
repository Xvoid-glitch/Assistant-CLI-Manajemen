import os
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt

console = Console()

class FinancialSurvival:
    def __init__(self, db):
        self.db = db
    
    def simulasi_bertahan(self):
        """Simulasi bertahan N hari dengan saldo tersisa"""
        console.print("[bold cyan]💀 Mode Bertahan Hidup Finansial[/bold cyan]")
        console.print("[dim]Simulasi apakah uangmu cukup untuk bertahan[/dim]\n")
        
        saldo = Prompt.ask("[yellow]Saldo/uang yang tersisa (Rp)[/yellow]")
        try:
            saldo = float(saldo.replace('.', '').replace(',', '.'))
        except ValueError:
            console.print("[red]Masukkan angka yang valid![/red]")
            return
        
        hari_target = IntPrompt.ask("[yellow]Berapa hari harus bertahan?[/yellow]", default=30)
        
        # Hitung rata-rata pengeluaran harian dari data
        bulan_ini = datetime.now().strftime("%Y-%m")
        stats = self.db.fetch_one('''
            SELECT COUNT(DISTINCT tanggal) as hari, COALESCE(SUM(jumlah), 0) as total
            FROM expenses 
            WHERE strftime('%Y-%m', tanggal) = ?
        ''', (bulan_ini,))
        
        if stats and stats['hari'] > 0 and stats['total'] > 0:
            rata_rata_harian = stats['total'] / stats['hari']
            console.print(f"[dim]Rata-rata dari data pengeluaranmu: Rp {rata_rata_harian:,.0f}/hari[/dim]")
        else:
            console.print("[yellow]Belum ada data pengeluaran di database.[/yellow]")
            rata_rata_input = Prompt.ask("[yellow]Rata-rata pengeluaran harian kamu (Rp)[/yellow]", default="50000")
            try:
                rata_rata_harian = float(rata_rata_input.replace('.', '').replace(',', '.'))
            except ValueError:
                console.print("[red]Angka tidak valid, menggunakan Rp 50.000[/red]")
                rata_rata_harian = 50000
        
        # Simulasi
        budget_harian = saldo / hari_target if hari_target > 0 else 0
        hari_bisa_bertahan = int(saldo / rata_rata_harian) if rata_rata_harian > 0 else 999
        
        # Detail per kategori
        kategori_stats = self.db.fetch_all('''
            SELECT kategori, AVG(jumlah) as avg_per_transaksi, 
                   SUM(jumlah) as total, COUNT(*) as jml
            FROM expenses 
            WHERE strftime('%Y-%m', tanggal) = ?
            GROUP BY kategori 
            ORDER BY total DESC
        ''', (bulan_ini,))
        
        result = f"""
[bold]💰 Saldo Saat Ini: Rp {saldo:,.0f}[/bold]
[bold]📅 Target Bertahan: {hari_target} hari[/bold]

{'─' * 40}

[bold cyan]📊 Analisa:[/bold cyan]
  💵 Budget Harian Maksimal   : Rp {budget_harian:,.0f}
  📈 Rata-rata Pengeluaran/hari: Rp {rata_rata_harian:,.0f}
  📅 Estimasi Bisa Bertahan   : {hari_bisa_bertahan} hari
"""
        
        if hari_bisa_bertahan >= hari_target:
            result += f"\n[bold green]🟢 AMAN! Kamu bisa bertahan {hari_target} hari.[/bold green]\n"
            result += f"[green]  Bahkan masih bisa bertahan {hari_bisa_bertahan - hari_target} hari lebih![/green]\n"
        elif hari_bisa_bertahan >= hari_target * 0.7:
            result += f"\n[bold yellow]🟡 KETAT! Perlu hemat lebih.[/bold yellow]\n"
            kurang = saldo - (rata_rata_harian * hari_target)
            result += f"[yellow]  Estimasi kurang: Rp {abs(kurang):,.0f}[/yellow]\n"
        else:
            result += f"\n[bold red]🔴 BAHAYA! Uang tidak cukup![/bold red]\n"
            kurang = (rata_rata_harian * hari_target) - saldo
            result += f"[red]  Kekurangan: Rp {kurang:,.0f}[/red]\n"
        
        console.print(Panel(result, title="💀 Hasil Simulasi", border_style="cyan", width=60))
        
        # Saran penghematan
        if hari_bisa_bertahan < hari_target:
            self._saran_hemat(budget_harian, kategori_stats)
    
    def _saran_hemat(self, budget_harian, kategori_stats):
        """Berikan saran penghematan"""
        console.print("\n[bold yellow]💡 Saran Penghematan:[/bold yellow]\n")
        
        saran = [
            "🍳 Masak sendiri — hemat 50-70% biaya makan",
            "🚶 Jalan kaki/sepeda untuk jarak dekat",
            "📱 Kurangi langganan yang tidak perlu",
            "☕ Buat kopi sendiri — hemat Rp 15-25rb/hari",
            "🛒 Buat daftar belanja, hindari impulse buying",
            "💧 Bawa botol minum sendiri",
            "🎮 Cari hiburan gratis (taman, perpustakaan)",
            "🔌 Matikan perangkat tidak terpakai — hemat listrik",
        ]
        
        for s in saran:
            console.print(f"  {s}")
        
        console.print(f"\n  [bold]💰 Target pengeluaran harian: Rp {budget_harian:,.0f}[/bold]")
        
        if kategori_stats:
            console.print("\n[bold cyan]📊 Pengeluaran Terbesar (kurangi ini):[/bold cyan]")
            for i, kat in enumerate(kategori_stats[:3], 1):
                console.print(f"  {i}. {kat['kategori']}: Rp {kat['total']:,.0f} (rata-rata Rp {kat['avg_per_transaksi']:,.0f}/transaksi)")
    
    def estimasi_habis(self):
        """Estimasi kapan saldo habis"""
        console.print("[bold cyan]📉 Estimasi Saldo Habis[/bold cyan]\n")
        
        saldo = Prompt.ask("[yellow]Saldo saat ini (Rp)[/yellow]")
        try:
            saldo = float(saldo.replace('.', '').replace(',', '.'))
        except ValueError:
            console.print("[red]Masukkan angka yang valid![/red]")
            return
        
        # Hitung rata-rata pengeluaran harian
        bulan_ini = datetime.now().strftime("%Y-%m")
        stats = self.db.fetch_one('''
            SELECT COUNT(DISTINCT tanggal) as hari, COALESCE(SUM(jumlah), 0) as total
            FROM expenses 
            WHERE strftime('%Y-%m', tanggal) = ?
        ''', (bulan_ini,))
        
        if stats and stats['hari'] > 0 and stats['total'] > 0:
            rata_rata = stats['total'] / stats['hari']
        else:
            rata_rata = float(Prompt.ask("Rata-rata pengeluaran harian (Rp)", default="50000"))
        
        hari_tersisa = int(saldo / rata_rata) if rata_rata > 0 else 999
        tanggal_habis = datetime.now() + timedelta(days=hari_tersisa)
        
        # Visual countdown
        console.print(Panel(f"""
[bold]💰 Saldo: Rp {saldo:,.0f}[/bold]
[bold]💸 Rata-rata Harian: Rp {rata_rata:,.0f}[/bold]

{'─' * 40}

  📅 Estimasi saldo habis: [bold]{tanggal_habis.strftime('%d %B %Y')}[/bold]
  ⏳ Itu [bold]{hari_tersisa} hari[/bold] lagi dari sekarang

  [dim]Hemat Rp {rata_rata * 0.2:,.0f}/hari → bisa bertahan {int(saldo / (rata_rata * 0.8))} hari[/dim]
  [dim]Hemat Rp {rata_rata * 0.5:,.0f}/hari → bisa bertahan {int(saldo / (rata_rata * 0.5))} hari[/dim]
        """, title="📉 Estimasi Habis Saldo", border_style="red", width=60))
    
    def run(self):
        """Antarmuka utama financial survival"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print("\n[bold cyan]💀 Mode Bertahan Finansial[/bold cyan]")
            
            menu = Table(show_header=False, box=None)
            menu.add_column("Opsi", style="cyan")
            menu.add_column("Keterangan", style="green")
            
            menu_items = [
                ("1", "💀 Simulasi Bertahan"),
                ("2", "📉 Estimasi Saldo Habis"),
                ("0", "🔙 Kembali")
            ]
            
            for item in menu_items:
                menu.add_row(item[0], item[1])
            
            console.print(menu)
            
            choice = Prompt.ask("Pilihan", choices=["0","1","2"], default="0")
            
            if choice == "0":
                break
            elif choice == "1":
                self.simulasi_bertahan()
            elif choice == "2":
                self.estimasi_habis()
            
            if choice != "0":
                console.print("[dim]Tekan Enter untuk melanjutkan...[/dim]")
                input()
