import os
import time
import threading
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.layout import Layout
from rich.live import Live
from rich.status import Status
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt

console = Console()

class StudyTools:
    def __init__(self, db, profile):
        self.db = db
        self.profile = profile
        self.is_studying = False
        
    def pomodoro_timer(self):
        """Timer fokus Pomodoro"""
        console.print("[bold cyan]⏱️  Timer Fokus Pomodoro[/bold cyan]")
        
        work_time = IntPrompt.ask("Durasi kerja (menit)", default=25)
        break_time = IntPrompt.ask("Durasi istirahat (menit)", default=5)
        cycles = IntPrompt.ask("Jumlah siklus", default=4)
        
        total_focus_time = 0
        
        try:
            for i in range(cycles):
                console.print(f"\n[bold magenta]🔄 Siklus {i+1}/{cycles}[/bold magenta]")
                
                # Fase Kerja
                console.print(f"[green]💪 Waktu Fokus! ({work_time} menit)[/green]")
                self.run_timer(work_time * 60, "Fokus...", "red")
                total_focus_time += work_time
                
                print("\a")
                
                self.log_study_session(work_time, "Sesi Pomodoro")
                
                # Fase Istirahat
                if i < cycles - 1:
                    console.print(f"[blue]☕ Waktu Istirahat! ({break_time} menit)[/blue]")
                    self.run_timer(break_time * 60, "Istirahat...", "green")
                    print("\a")
            
            console.print(f"\n[bold green]🎉 Pomodoro Selesai! Total fokus: {total_focus_time} menit[/bold green]")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Pomodoro dihentikan.[/yellow]")
    
    def run_timer(self, seconds, description, color):
        """Jalankan timer dengan progress bar"""
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[{color}]{{task.description}}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("⏰ {task.remaining}"),
            transient=True
        ) as progress:
            task = progress.add_task(description, total=seconds)
            
            while not progress.finished:
                time.sleep(1)
                progress.update(task, advance=1)
    
    def music_player(self):
        """Pemutar musik untuk belajar"""
        console.print("[bold cyan]🎵 Pemutar Musik[/bold cyan]")
        console.print("[dim]Pilih playlist favoritmu untuk menemani belajar[/dim]\n")
        
        streams = {
            "1": ("🎸 Lagu Indie Indo", "https://youtu.be/34PUV5pAvHM?si=ZZoxqAbtgDXEbsVm"),
            "2": ("🎧 Lagu Santai Inggris", "https://youtu.be/I4sd4an3020?si=XrVTmIPdTJv-stgB"),
            "3": ("💔 Lagu Galau Inggris", "https://youtu.be/D8APomNQtng?si=a_SUFofOBuwkROOX"),
            "4": ("😢 Lagu Galau Indo", "https://youtu.be/d44iocwNBh0?si=lBQznzWIrqFcyxlk"),
            "5": ("🕰️ Lagu Nostalgia 2019", "https://youtu.be/Lge1lDVgOvA?si=LZlzF4FAaohjioP6"),
        }
        
        console.print("[bold]Pilihan Playlist:[/bold]")
        for key, (name, _) in streams.items():
            console.print(f"  {key}. {name}")
        console.print("  0. 🔙 Kembali")
        
        choice = Prompt.ask("Pilih playlist", choices=["0", "1", "2", "3", "4", "5"], default="1")
        
        if choice == "0":
            return
            
        url = streams[choice][1]
        name = streams[choice][0]
        
        console.print(f"\n[green]🎵 Membuka {name} di browser...[/green]")
        import webbrowser
        webbrowser.open(url)
    
    def log_study_session(self, duration, subject="Belajar Umum"):
        """Catat sesi belajar ke database"""
        try:
            self.db.execute_query('''
                INSERT INTO study_sessions (duration_minutes, subject, productivity_score)
                VALUES (?, ?, ?)
            ''', (duration, subject, 5))
        except:
            pass
            
    def study_stats(self):
        """Tampilkan statistik belajar"""
        rows = self.db.fetch_all('''
            SELECT date, SUM(duration_minutes) as total_mins 
            FROM study_sessions 
            GROUP BY date 
            ORDER BY date DESC 
            LIMIT 7
        ''')
        
        if not rows:
            console.print("[yellow]Belum ada data sesi belajar[/yellow]")
            return
            
        table = Table(title="📊 Statistik Belajar (7 Hari Terakhir)")
        table.add_column("Tanggal", style="cyan")
        table.add_column("Durasi (menit)", style="green")
        table.add_column("Jam", style="yellow")
        
        total_week = 0
        for row in rows:
            hours = row['total_mins'] / 60
            table.add_row(
                row['date'],
                str(row['total_mins']),
                f"{hours:.1f} jam"
            )
            total_week += row['total_mins']
            
        console.print(table)
        console.print(f"\n[bold]Total minggu ini: {total_week} menit ({total_week/60:.1f} jam)[/bold]")

    def run(self):
        """Antarmuka utama alat belajar"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print("\n[bold cyan]🎯 Alat Belajar[/bold cyan]")
            
            menu = Table(show_header=False, box=None)
            menu.add_column("Opsi", style="cyan")
            menu.add_column("Keterangan", style="green")
            
            menu_items = [
                ("1", "⏱️  Timer Pomodoro"),
                ("2", "🎵 Pemutar Musik"),
                ("3", "📊 Statistik Belajar"),
                ("0", "🔙 Kembali")
            ]
            
            for item in menu_items:
                menu.add_row(item[0], item[1])
            
            console.print(menu)
            
            choice = Prompt.ask("Pilihan", default="0")
            
            if choice == "0":
                break
            elif choice == "1":
                self.pomodoro_timer()
            elif choice == "2":
                self.music_player()
            elif choice == "3":
                self.study_stats()
            
            if choice != "0":
                console.print("[dim]Tekan Enter untuk melanjutkan...[/dim]")
                input()
