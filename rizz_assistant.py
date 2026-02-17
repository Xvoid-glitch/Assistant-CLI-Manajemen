#!/usr/bin/env python3
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import click

from config.config_manager import ConfigManager
from modules.database import Database
from modules.jadwal import JadwalManager
from modules.notes import NotesManager
from modules.tasks import TaskManager
from modules.utilities import Utilities
from modules.study_tools import StudyTools
from modules.weather import WeatherInfo
from modules.expense_tracker import ExpenseTracker
from modules.clipboard_manager import ClipboardManager
from modules.habit_tracker import HabitTracker
from modules.network_check import NetworkCheck
from modules.productivity_coach import ProductivityCoach
from modules.life_dashboard import LifeDashboard
from modules.future_you import FutureYou
from modules.financial_survival import FinancialSurvival

console = Console()

def clear_screen():
    """Bersihkan layar terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

class RIzzAssistant:
    def __init__(self):
        self.config_mgr = ConfigManager()
        self.profile = self.config_mgr.load_profile()
        
        if not self.profile:
            self.profile = self.config_mgr.collect_user_profile()
        
        self.db = Database(self.config_mgr.config_dir)
        
        self.modules = {
            'jadwal': JadwalManager(self.db, self.profile),
            'notes': NotesManager(self.db),
            'tasks': TaskManager(self.db),
            'utilities': Utilities(),
            'study': StudyTools(self.db, self.profile),
            'weather': WeatherInfo(),
            'expense': ExpenseTracker(self.db),
            'clipboard': ClipboardManager(self.db),
            'habits': HabitTracker(self.db),
            'network': NetworkCheck(),
            'coach': ProductivityCoach(self.db),
            'dashboard': LifeDashboard(self.db),
            'future': FutureYou(self.db),
            'survival': FinancialSurvival(self.db),
        }
        
        self.running = True
    
    def display_banner(self):
        nickname = self.profile.get('nickname', 'Bro')
        
        banner = f"""
[bold cyan]
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║ [bold magenta]██████╗      █████╗ ███████╗███████╗██╗███████╗████████╗            [/bold magenta] ║
║ [bold magenta]██╔══██╗    ██╔══██╗██╔════╝██╔════╝██║██╔════╝╚══██╔══╝            [/bold magenta] ║
║ [bold magenta]██████╔╝    ███████║███████╗███████╗██║███████╗   ██║               [/bold magenta] ║
║ [bold magenta]██╔══██╗    ██╔══██║╚════██║╚════██║██║╚════██║   ██║               [/bold magenta] ║
║ [bold magenta]██║  ██║    ██║  ██║███████║███████║██║███████║   ██║               [/bold magenta] ║
║ [bold magenta]╚═╝  ╚═╝    ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚══════╝   ╚═╝               [/bold magenta] ║
║                                                                      ║
║                                  [bold yellow]R ASSIST v3.0[/bold yellow]                       ║
║                           [bold green]Selamat datang, {nickname}![/bold green]                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
[/bold cyan]
"""
        console.print(banner)

    
    def display_main_menu(self):
        menu_table = Table(title="🎯 Menu Utama", show_header=False, box=None)
        menu_table.add_column("No", style="cyan", width=5)
        menu_table.add_column("Modul", style="magenta")
        menu_table.add_column("Keterangan", style="green")
        
        menu_items = [
            ("1",  "📅 Jadwal Pelajaran",     "Atur jadwal harian & mingguan"),
            ("2",  "📝 Catatan Pintar",        "Buat & kelola catatan"),
            ("3",  "✅ Manajer Task",          "Target dan deadline"),
            ("4",  "💰 Pencatat Pengeluaran",  "Catat keuangan harian"),
            ("5",  "🔥 Pelacak Kebiasaan",     "Streak & checkin harian"),
            ("6",  "⚡ Utilitas",              "Password, QR, konverter"),
            ("7",  "🎯 Alat Belajar",          "Pomodoro & musik"),
            ("8",  "📋 Manajer Clipboard",     "Simpan & cari teks"),
            ("9",  "🌐 Cek Jaringan",          "Ping, speed, IP publik"),
            ("10", "🧠 Pelatih Produktivitas",  "Analisa & motivasi harian"),
            ("11", "📊 Dashboard Kehidupan",    "Ringkasan satu layar"),
            ("12", "💀 Dirimu di Masa Depan",   "Target 1 tahun & refleksi"),
            ("13", "💸 Mode Bertahan Finansial", "Simulasi keuangan"),
            ("14", "⛅ Info Cuaca",             "Prakiraan cuaca"),
            ("0",  "❌ Keluar",                "Tutup aplikasi"),
        ]
        
        for item in menu_items:
            menu_table.add_row(item[0], item[1], item[2])
        
        console.print(menu_table)
    
    def handle_command(self, command: str):
        cmd = command.strip().lower()
        
        if cmd in ['0', 'exit', 'keluar']:
            self.running = False
            console.print("[yellow]Sampai jumpa! 👋[/yellow]")
            return
        
        try:
            if cmd == '1':
                self.modules['jadwal'].run()
            elif cmd == '2':
                self.modules['notes'].run()
            elif cmd == '3':
                self.modules['tasks'].run()
            elif cmd == '4':
                self.modules['expense'].run()
            elif cmd == '5':
                self.modules['habits'].run()
            elif cmd == '6':
                self.modules['utilities'].run()
            elif cmd == '7':
                self.modules['study'].run()
            elif cmd == '8':
                self.modules['clipboard'].run()
            elif cmd == '9':
                self.modules['network'].run()
            elif cmd == '10':
                self.modules['coach'].run()
            elif cmd == '11':
                self.modules['dashboard'].run()
            elif cmd == '12':
                self.modules['future'].run()
            elif cmd == '13':
                self.modules['survival'].run()
            elif cmd == '14':
                self.modules['weather'].run()
            else:
                console.print("[red]Perintah tidak dikenal! Pilih 0-14[/red]")
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
    
    def run(self):
        clear_screen()
        self.display_banner()
        
        while self.running:
            try:
                clear_screen()
                self.display_banner()
                self.display_main_menu()
                command = Prompt.ask(
                    f"\n[bold cyan]{self.profile.get('nickname', 'User')}[/bold cyan]@rizz>"
                )
                self.handle_command(command)
            except KeyboardInterrupt:
                console.print("\n[yellow]Ketik '0' atau 'keluar' untuk keluar[/yellow]")

@click.command()
@click.option('--setup', is_flag=True, help='Jalankan setup ulang profil')
def main(setup):
    try:
        assistant = RIzzAssistant()
        if setup:
            assistant.profile = assistant.config_mgr.collect_user_profile()
        assistant.run()
    except Exception as e:
        console.print(f"[bold red]Error Fatal: {str(e)}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()