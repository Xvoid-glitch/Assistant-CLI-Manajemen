import os
import random
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, BarColumn, TextColumn

console = Console()

class FutureYou:
    def __init__(self, db):
        self.db = db
        self.pertanyaan_refleksi = [
            "Apa yang sudah kamu lakukan hari ini untuk mendekati targetmu?",
            "Hambatan apa yang kamu hadapi? Bagaimana mengatasinya?",
            "Apa yang akan 'dirimu di masa depan' katakan tentang usahamu hari ini?",
            "Kalau kamu sudah mencapai target ini, apa yang akan berubah di hidupmu?",
            "Apa 1 hal kecil yang bisa kamu lakukan sekarang untuk maju selangkah?",
            "Apakah kamu lebih dekat ke targetmu dibanding minggu lalu? Kenapa?",
            "Satu kata untuk menggambarkan perjalananmu sejauh ini?",
            "Apa yang membuatmu tetap termotivasi?",
            "Jika kamu gagal, apa rencana B-mu?",
            "Bayangkan dirimu 1 tahun dari sekarang. Apa nasihatmu untuk dirimu hari ini?",
        ]
    
    def tambah_target(self):
        """Tulis target 1 tahun ke depan"""
        console.print("[bold cyan]🎯 Tambah Target Masa Depan[/bold cyan]")
        
        target = Prompt.ask("[yellow]Apa targetmu?[/yellow]")
        
        console.print("\n[cyan]Deadline:[/cyan]")
        console.print("  1. 3 bulan dari sekarang")
        console.print("  2. 6 bulan dari sekarang")
        console.print("  3. 1 tahun dari sekarang")
        console.print("  4. Custom (pilih sendiri)")
        
        dl_choice = Prompt.ask("Pilih", choices=["1", "2", "3", "4"], default="3")
        
        today = datetime.now().date()
        if dl_choice == "1":
            deadline = today + timedelta(days=90)
        elif dl_choice == "2":
            deadline = today + timedelta(days=180)
        elif dl_choice == "3":
            deadline = today + timedelta(days=365)
        else:
            dl_str = Prompt.ask("Deadline (YYYY-MM-DD)")
            try:
                deadline = datetime.strptime(dl_str, "%Y-%m-%d").date()
            except ValueError:
                console.print("[red]Format tanggal salah![/red]")
                return
        
        catatan = Prompt.ask("Catatan/motivasi awal (opsional)", default="")
        
        self.db.execute_query('''
            INSERT INTO future_goals (target, deadline, progress, catatan)
            VALUES (?, ?, 0, ?)
        ''', (target, deadline.strftime("%Y-%m-%d"), catatan))
        
        console.print(f"\n[bold green]✓ Target berhasil ditambahkan![/bold green]")
        console.print(f"[cyan]🎯 '{target}' — deadline: {deadline.strftime('%d %B %Y')}[/cyan]")
        console.print(f"[dim]Kamu punya {(deadline - today).days} hari. Mulai dari sekarang![/dim]")
    
    def lihat_target(self):
        """Lihat semua target"""
        goals = self.db.fetch_all("SELECT * FROM future_goals ORDER BY deadline")
        
        if not goals:
            console.print("[yellow]Belum ada target. Mulai tentukan tujuanmu![/yellow]")
            return []
        
        today = datetime.now().date()
        
        for goal in goals:
            try:
                deadline = datetime.strptime(goal['deadline'], "%Y-%m-%d").date()
                days_left = (deadline - today).days
                created = datetime.strptime(goal['created_at'][:10], "%Y-%m-%d").date()
                total_days = (deadline - created).days
                days_passed = (today - created).days
                
                time_progress = min(int(days_passed / total_days * 100), 100) if total_days > 0 else 0
            except:
                days_left = 0
                time_progress = 0
            
            progress = goal['progress']
            
            # Progress bar
            bar_len = min(int(progress / 5), 20)
            if progress >= 80:
                bar_color = "green"
            elif progress >= 40:
                bar_color = "yellow"
            else:
                bar_color = "cyan"
            
            progress_bar = f"[{bar_color}]{'█' * bar_len}{'░' * (20 - bar_len)}[/{bar_color}] {progress}%"
            
            # Time bar
            time_bar_len = min(int(time_progress / 5), 20)
            time_bar = f"[red]{'█' * time_bar_len}{'░' * (20 - time_bar_len)}[/red] {time_progress}%"
            
            if days_left > 0:
                days_display = f"[green]{days_left} hari lagi[/green]"
            elif days_left == 0:
                days_display = "[bold red]HARI INI![/bold red]"
            else:
                days_display = f"[red]Terlambat {abs(days_left)} hari![/red]"
            
            content = f"""
[bold]{goal['target']}[/bold]

  📅 Deadline: {goal['deadline']} — {days_display}
  📈 Progress : {progress_bar}
  ⏳ Waktu    : {time_bar}
  """
            if goal['catatan']:
                content += f"\n  💭 Catatan: {goal['catatan']}"
            
            console.print(Panel(content, title=f"🎯 Target #{goal['id']}", border_style="cyan", width=60))
        
        return goals
    
    def update_progress(self):
        """Update progress target"""
        goals = self.lihat_target()
        if not goals:
            return
        
        try:
            goal_id = int(Prompt.ask("\nID target untuk update"))
        except ValueError:
            console.print("[red]ID harus angka![/red]")
            return
        
        goal = self.db.fetch_one("SELECT * FROM future_goals WHERE id = ?", (goal_id,))
        if not goal:
            console.print("[red]Target tidak ditemukan![/red]")
            return
        
        console.print(f"\n[cyan]Progress saat ini: {goal['progress']}%[/cyan]")
        new_progress = IntPrompt.ask("Progress baru (0-100)", default=goal['progress'])
        new_progress = max(0, min(100, new_progress))
        
        catatan = Prompt.ask("Update catatan (opsional, kosongkan untuk skip)", default="")
        
        if catatan:
            self.db.execute_query('''
                UPDATE future_goals SET progress = ?, catatan = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_progress, catatan, goal_id))
        else:
            self.db.execute_query('''
                UPDATE future_goals SET progress = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_progress, goal_id))
        
        if new_progress == 100:
            console.print("\n[bold green]🎉🎉🎉 SELAMAT! TARGET TERCAPAI! 🎉🎉🎉[/bold green]")
            console.print("[bold]Kamu sudah membuktikan bahwa kamu bisa![/bold]")
        elif new_progress > goal['progress']:
            console.print(f"\n[green]✓ Progress diupdate: {goal['progress']}% → {new_progress}%[/green]")
            console.print("[cyan]Terus maju! Kamu semakin dekat![/cyan]")
        else:
            console.print(f"\n[yellow]Progress diupdate: {new_progress}%[/yellow]")
    
    def refleksi_harian(self):
        """Sesi refleksi harian"""
        goals = self.db.fetch_all("SELECT * FROM future_goals WHERE progress < 100 ORDER BY deadline LIMIT 1")
        
        if not goals:
            console.print("[yellow]Belum ada target aktif. Tambah target dulu![/yellow]")
            return
        
        goal = goals[0]
        
        console.print(f"\n[bold cyan]💭 Refleksi Harian[/bold cyan]")
        console.print(f"[dim]Target: {goal['target']}[/dim]\n")
        
        # Pilih pertanyaan acak
        pertanyaan = random.choice(self.pertanyaan_refleksi)
        
        console.print(Panel(
            f"[bold yellow]{pertanyaan}[/bold yellow]",
            title="💬 Pertanyaan dari Dirimu di Masa Depan",
            border_style="yellow",
            width=60
        ))
        
        jawaban = Prompt.ask("\n[cyan]Jawaban kamu[/cyan]")
        
        if jawaban.strip():
            self.db.execute_query('''
                INSERT INTO goal_reflections (goal_id, pertanyaan, jawaban)
                VALUES (?, ?, ?)
            ''', (goal['id'], pertanyaan, jawaban))
            
            console.print("\n[green]✓ Refleksi disimpan![/green]")
            
            # Motivasi
            motivasi = [
                "💪 Setiap langkah kecil membawa kamu lebih dekat!",
                "🌟 Percaya prosesnya. Hasilnya akan datang.",
                "🔥 Dirimu di masa depan akan berterima kasih!",
                "🚀 Kamu lebih kuat dari yang kamu pikir!",
                "✨ Consistency beats intensity. Terus jalan!",
            ]
            console.print(f"\n[bold magenta]{random.choice(motivasi)}[/bold magenta]")
    
    def hapus_target(self):
        """Hapus target"""
        goals = self.lihat_target()
        if not goals:
            return
        
        try:
            goal_id = int(Prompt.ask("\nID target untuk dihapus"))
        except ValueError:
            console.print("[red]ID harus angka![/red]")
            return
        
        if Confirm.ask(f"Yakin hapus target ID {goal_id}?"):
            self.db.execute_query("DELETE FROM goal_reflections WHERE goal_id = ?", (goal_id,))
            self.db.execute_query("DELETE FROM future_goals WHERE id = ?", (goal_id,))
            console.print("[green]✓ Target berhasil dihapus![/green]")
    
    def run(self):
        """Antarmuka utama Future You"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print("\n[bold cyan]💀 Mode \"Dirimu di Masa Depan\"[/bold cyan]")
            
            menu = Table(show_header=False, box=None)
            menu.add_column("Opsi", style="cyan")
            menu.add_column("Keterangan", style="green")
            
            menu_items = [
                ("1", "🎯 Lihat Target"),
                ("2", "➕ Tambah Target"),
                ("3", "📈 Update Progress"),
                ("4", "💭 Refleksi Harian"),
                ("5", "🗑️ Hapus Target"),
                ("0", "🔙 Kembali")
            ]
            
            for item in menu_items:
                menu.add_row(item[0], item[1])
            
            console.print(menu)
            
            choice = Prompt.ask("Pilihan", choices=["0","1","2","3","4","5"], default="0")
            
            if choice == "0":
                break
            elif choice == "1":
                self.lihat_target()
            elif choice == "2":
                self.tambah_target()
            elif choice == "3":
                self.update_progress()
            elif choice == "4":
                self.refleksi_harian()
            elif choice == "5":
                self.hapus_target()
            
            if choice != "0":
                console.print("[dim]Tekan Enter untuk melanjutkan...[/dim]")
                input()
