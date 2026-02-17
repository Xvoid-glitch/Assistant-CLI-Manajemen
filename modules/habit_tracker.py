import os
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

class HabitTracker:
    def __init__(self, db):
        self.db = db
    
    def tambah_kebiasaan(self):
        """Tambah kebiasaan baru"""
        console.print("[bold cyan]➕ Tambah Kebiasaan Baru[/bold cyan]")
        
        nama = Prompt.ask("[yellow]Nama kebiasaan[/yellow]")
        emoji = Prompt.ask("[yellow]Emoji (opsional)[/yellow]", default="✅")
        
        self.db.execute_query(
            "INSERT INTO habits (nama, emoji) VALUES (?, ?)",
            (nama, emoji)
        )
        console.print(f"[green]✓ Kebiasaan '{emoji} {nama}' berhasil ditambahkan![/green]")
    
    def checkin_hari_ini(self):
        """Checkin kebiasaan hari ini"""
        habits = self.db.fetch_all("SELECT * FROM habits ORDER BY id")
        
        if not habits:
            console.print("[yellow]Belum ada kebiasaan. Tambahkan dulu![/yellow]")
            return
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        console.print(f"[bold cyan]📋 Checkin Hari Ini ({today})[/bold cyan]\n")
        
        for habit in habits:
            # Cek apakah sudah checkin hari ini
            existing = self.db.fetch_one(
                "SELECT * FROM habit_logs WHERE habit_id = ? AND tanggal = ?",
                (habit['id'], today)
            )
            
            if existing:
                console.print(f"  {habit['emoji']} {habit['nama']} — [green]✅ Sudah![/green]")
            else:
                done = Confirm.ask(f"  {habit['emoji']} {habit['nama']} — sudah dilakukan?", default=False)
                if done:
                    self.db.execute_query(
                        "INSERT INTO habit_logs (habit_id, tanggal) VALUES (?, ?)",
                        (habit['id'], today)
                    )
                    console.print(f"    [green]✓ Tercatat![/green]")
                else:
                    console.print(f"    [dim]Belum — semangat ya![/dim]")
        
        console.print("\n[bold green]✓ Checkin selesai![/bold green]")
    
    def lihat_streak(self):
        """Tampilkan streak untuk setiap kebiasaan"""
        habits = self.db.fetch_all("SELECT * FROM habits ORDER BY id")
        
        if not habits:
            console.print("[yellow]Belum ada kebiasaan[/yellow]")
            return
        
        console.print("[bold cyan]🔥 Streak Kebiasaan[/bold cyan]\n")
        
        for habit in habits:
            streak = self._hitung_streak(habit['id'])
            
            # Tampilan streak
            if streak >= 30:
                streak_display = f"[bold red]🔥🔥🔥 {streak} HARI! LEGENDARIS![/bold red]"
            elif streak >= 14:
                streak_display = f"[bold yellow]🔥🔥 {streak} hari! HEBAT![/bold yellow]"
            elif streak >= 7:
                streak_display = f"[bold green]🔥 {streak} hari! Bagus![/bold green]"
            elif streak >= 3:
                streak_display = f"[cyan]{streak} hari — terus semangat![/cyan]"
            elif streak >= 1:
                streak_display = f"[white]{streak} hari — awal yang baik![/white]"
            else:
                streak_display = "[dim]0 hari — mulai hari ini![/dim]"
            
            # Visual bar 7 hari terakhir
            week_bar = self._get_week_bar(habit['id'])
            
            console.print(f"  {habit['emoji']} [bold]{habit['nama']}[/bold]")
            console.print(f"     Streak: {streak_display}")
            console.print(f"     7 Hari: {week_bar}\n")
    
    def _hitung_streak(self, habit_id):
        """Hitung streak berturut-turut"""
        today = datetime.now().date()
        streak = 0
        
        current_date = today
        while True:
            log = self.db.fetch_one(
                "SELECT * FROM habit_logs WHERE habit_id = ? AND tanggal = ?",
                (habit_id, current_date.strftime("%Y-%m-%d"))
            )
            if log:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    def _get_week_bar(self, habit_id):
        """Tampilkan bar 7 hari terakhir"""
        today = datetime.now().date()
        bars = []
        
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            log = self.db.fetch_one(
                "SELECT * FROM habit_logs WHERE habit_id = ? AND tanggal = ?",
                (habit_id, date.strftime("%Y-%m-%d"))
            )
            if log:
                bars.append("[green]■[/green]")
            else:
                bars.append("[dim]□[/dim]")
        
        return " ".join(bars)
    
    def statistik_mingguan(self):
        """Statistik mingguan"""
        habits = self.db.fetch_all("SELECT * FROM habits ORDER BY id")
        
        if not habits:
            console.print("[yellow]Belum ada kebiasaan[/yellow]")
            return
        
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        table = Table(title=f"📊 Statistik Minggu Ini ({week_start.strftime('%d/%m')} - {today.strftime('%d/%m')})")
        table.add_column("Kebiasaan", style="cyan")
        table.add_column("Sen", style="green", justify="center", width=3)
        table.add_column("Sel", style="green", justify="center", width=3)
        table.add_column("Rab", style="green", justify="center", width=3)
        table.add_column("Kam", style="green", justify="center", width=3)
        table.add_column("Jum", style="green", justify="center", width=3)
        table.add_column("Sab", style="green", justify="center", width=3)
        table.add_column("Min", style="green", justify="center", width=3)
        table.add_column("Total", style="yellow", justify="right")
        
        for habit in habits:
            row_data = [f"{habit['emoji']} {habit['nama']}"]
            total_done = 0
            
            for day_offset in range(7):
                date = week_start + timedelta(days=day_offset)
                log = self.db.fetch_one(
                    "SELECT * FROM habit_logs WHERE habit_id = ? AND tanggal = ?",
                    (habit['id'], date.strftime("%Y-%m-%d"))
                )
                if log:
                    row_data.append("✅")
                    total_done += 1
                elif date <= today:
                    row_data.append("❌")
                else:
                    row_data.append("·")
            
            row_data.append(f"{total_done}/7")
            table.add_row(*row_data)
        
        console.print(table)
    
    def hapus_kebiasaan(self):
        """Hapus kebiasaan"""
        habits = self.db.fetch_all("SELECT * FROM habits ORDER BY id")
        
        if not habits:
            console.print("[yellow]Belum ada kebiasaan[/yellow]")
            return
        
        table = Table(title="📋 Daftar Kebiasaan")
        table.add_column("ID", style="cyan")
        table.add_column("Kebiasaan", style="green")
        
        for h in habits:
            table.add_row(str(h['id']), f"{h['emoji']} {h['nama']}")
        
        console.print(table)
        
        try:
            h_id = int(Prompt.ask("\nID kebiasaan untuk dihapus"))
        except ValueError:
            console.print("[red]ID harus angka![/red]")
            return
        
        if Confirm.ask(f"Yakin hapus kebiasaan ID {h_id}? (data log juga akan terhapus)"):
            self.db.execute_query("DELETE FROM habit_logs WHERE habit_id = ?", (h_id,))
            self.db.execute_query("DELETE FROM habits WHERE id = ?", (h_id,))
            console.print("[green]✓ Kebiasaan berhasil dihapus![/green]")
    
    def run(self):
        """Antarmuka utama habit tracker"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print("\n[bold cyan]🔥 Pelacak Kebiasaan[/bold cyan]")
            
            menu = Table(show_header=False, box=None)
            menu.add_column("Opsi", style="cyan")
            menu.add_column("Keterangan", style="green")
            
            menu_items = [
                ("1", "📋 Checkin Hari Ini"),
                ("2", "🔥 Lihat Streak"),
                ("3", "📊 Statistik Mingguan"),
                ("4", "➕ Tambah Kebiasaan"),
                ("5", "🗑️ Hapus Kebiasaan"),
                ("0", "🔙 Kembali")
            ]
            
            for item in menu_items:
                menu.add_row(item[0], item[1])
            
            console.print(menu)
            
            choice = Prompt.ask("Pilihan", choices=["0","1","2","3","4","5"], default="0")
            
            if choice == "0":
                break
            elif choice == "1":
                self.checkin_hari_ini()
            elif choice == "2":
                self.lihat_streak()
            elif choice == "3":
                self.statistik_mingguan()
            elif choice == "4":
                self.tambah_kebiasaan()
            elif choice == "5":
                self.hapus_kebiasaan()
            
            if choice != "0":
                console.print("[dim]Tekan Enter untuk melanjutkan...[/dim]")
                input()
