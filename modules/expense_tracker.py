import os
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt

console = Console()

class ExpenseTracker:
    def __init__(self, db):
        self.db = db
        self.kategori_list = [
            "Makanan", "Transportasi", "Belanja", "Hiburan",
            "Tagihan", "Kesehatan", "Pendidikan", "Lainnya"
        ]
    
    def tambah_pengeluaran(self):
        """Tambah pengeluaran baru"""
        console.print("[bold cyan]💸 Tambah Pengeluaran[/bold cyan]")
        
        jumlah = Prompt.ask("[yellow]Jumlah (Rp)[/yellow]")
        try:
            jumlah = float(jumlah.replace('.', '').replace(',', '.'))
        except ValueError:
            console.print("[red]Jumlah harus angka![/red]")
            return
        
        console.print("\n[cyan]Kategori:[/cyan]")
        for i, kat in enumerate(self.kategori_list, 1):
            console.print(f"  {i}. {kat}")
        
        kat_choice = Prompt.ask("Pilih kategori", default="1")
        try:
            kategori = self.kategori_list[int(kat_choice) - 1]
        except (ValueError, IndexError):
            kategori = "Lainnya"
        
        deskripsi = Prompt.ask("Deskripsi (opsional)", default="")
        
        self.db.execute_query('''
            INSERT INTO expenses (jumlah, kategori, deskripsi)
            VALUES (?, ?, ?)
        ''', (jumlah, kategori, deskripsi))
        
        console.print(f"[green]✓ Pengeluaran Rp {jumlah:,.0f} ({kategori}) berhasil dicatat![/green]")
    
    def lihat_hari_ini(self):
        """Tampilkan pengeluaran hari ini"""
        today = datetime.now().strftime("%Y-%m-%d")
        rows = self.db.fetch_all(
            "SELECT * FROM expenses WHERE tanggal = ? ORDER BY created_at DESC",
            (today,)
        )
        
        if not rows:
            console.print("[yellow]Belum ada pengeluaran hari ini 🎉[/yellow]")
            return
        
        table = Table(title=f"💰 Pengeluaran Hari Ini ({today})")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Jumlah", style="green", justify="right")
        table.add_column("Kategori", style="magenta")
        table.add_column("Deskripsi", style="yellow")
        
        total = 0
        for row in rows:
            total += row['jumlah']
            table.add_row(
                str(row['id']),
                f"Rp {row['jumlah']:,.0f}",
                row['kategori'],
                row['deskripsi'] or "-"
            )
        
        console.print(table)
        console.print(f"\n[bold]Total Hari Ini: [red]Rp {total:,.0f}[/red][/bold]")
    
    def statistik_bulanan(self):
        """Tampilkan statistik bulanan"""
        bulan = datetime.now().strftime("%Y-%m")
        
        rows = self.db.fetch_all('''
            SELECT kategori, SUM(jumlah) as total, COUNT(*) as jumlah_transaksi
            FROM expenses 
            WHERE strftime('%Y-%m', tanggal) = ?
            GROUP BY kategori
            ORDER BY total DESC
        ''', (bulan,))
        
        if not rows:
            console.print("[yellow]Belum ada pengeluaran bulan ini[/yellow]")
            return
        
        grand_total = sum(r['total'] for r in rows)
        
        table = Table(title=f"📊 Statistik Bulan {bulan}")
        table.add_column("Kategori", style="cyan")
        table.add_column("Total", style="green", justify="right")
        table.add_column("Transaksi", style="yellow", justify="right")
        table.add_column("Persentase", style="magenta", justify="right")
        table.add_column("Grafik", style="blue")
        
        for row in rows:
            persen = (row['total'] / grand_total * 100) if grand_total > 0 else 0
            bar_len = int(persen / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            
            table.add_row(
                row['kategori'],
                f"Rp {row['total']:,.0f}",
                str(row['jumlah_transaksi']),
                f"{persen:.1f}%",
                bar
            )
        
        console.print(table)
        console.print(f"\n[bold]Total Pengeluaran Bulan Ini: [red]Rp {grand_total:,.0f}[/red][/bold]")
        
        # Cek budget
        budget = self.db.fetch_one(
            "SELECT * FROM budget WHERE bulan = ? ORDER BY id DESC LIMIT 1",
            (bulan,)
        )
        if budget:
            sisa = budget['budget_bulanan'] - grand_total
            if sisa > 0:
                console.print(f"[green]💰 Sisa Budget: Rp {sisa:,.0f}[/green]")
            else:
                console.print(f"[red]⚠️ Budget TERLAMPAUI! Rp {abs(sisa):,.0f} melebihi budget[/red]")
    
    def set_budget(self):
        """Atur budget bulanan"""
        bulan = datetime.now().strftime("%Y-%m")
        console.print(f"[bold cyan]💰 Atur Budget Bulan {bulan}[/bold cyan]")
        
        jumlah = Prompt.ask("[yellow]Budget bulanan (Rp)[/yellow]")
        try:
            jumlah = float(jumlah.replace('.', '').replace(',', '.'))
        except ValueError:
            console.print("[red]Jumlah harus angka![/red]")
            return
        
        self.db.execute_query(
            "INSERT INTO budget (bulan, budget_bulanan) VALUES (?, ?)",
            (bulan, jumlah)
        )
        console.print(f"[green]✓ Budget bulan {bulan} diset: Rp {jumlah:,.0f}[/green]")
    
    def hapus_pengeluaran(self):
        """Hapus pengeluaran"""
        self.lihat_hari_ini()
        
        try:
            exp_id = int(Prompt.ask("\nID pengeluaran yang akan dihapus"))
        except ValueError:
            console.print("[red]ID harus angka![/red]")
            return
        
        if Confirm.ask(f"Yakin hapus pengeluaran ID {exp_id}?"):
            self.db.execute_query("DELETE FROM expenses WHERE id = ?", (exp_id,))
            console.print("[green]✓ Pengeluaran berhasil dihapus![/green]")
    
    def run(self):
        """Antarmuka utama expense tracker"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print("\n[bold cyan]💰 Pencatat Pengeluaran[/bold cyan]")
            
            menu = Table(show_header=False, box=None)
            menu.add_column("Opsi", style="cyan")
            menu.add_column("Keterangan", style="green")
            
            menu_items = [
                ("1", "💸 Tambah Pengeluaran"),
                ("2", "👀 Pengeluaran Hari Ini"),
                ("3", "📊 Statistik Bulanan"),
                ("4", "💰 Atur Budget"),
                ("5", "🗑️ Hapus Pengeluaran"),
                ("0", "🔙 Kembali")
            ]
            
            for item in menu_items:
                menu.add_row(item[0], item[1])
            
            console.print(menu)
            
            choice = Prompt.ask("Pilihan", choices=["0", "1", "2", "3", "4", "5"], default="0")
            
            if choice == "0":
                break
            elif choice == "1":
                self.tambah_pengeluaran()
            elif choice == "2":
                self.lihat_hari_ini()
            elif choice == "3":
                self.statistik_bulanan()
            elif choice == "4":
                self.set_budget()
            elif choice == "5":
                self.hapus_pengeluaran()
            
            if choice != "0":
                console.print("[dim]Tekan Enter untuk melanjutkan...[/dim]")
                input()
