import os
import random
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

class ProductivityCoach:
    def __init__(self, db):
        self.db = db
    
    def analisa_hari_ini(self):
        """Analisa produktivitas hari ini"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now()
        
        console.print(f"\n[bold cyan]🧠 Analisa Produktivitas Hari Ini[/bold cyan]")
        console.print(f"[dim]{now.strftime('%A, %d %B %Y %H:%M')}[/dim]\n")
        
        # === Task Analysis ===
        tasks_today = self.db.fetch_all(
            "SELECT * FROM tasks WHERE status != 'completed' ORDER BY priority"
        )
        completed_today = self.db.fetch_all(
            "SELECT * FROM tasks WHERE status = 'completed' AND DATE(updated_at) = ?",
            (today,)
        )
        
        total_active = len(tasks_today)
        total_completed = len(completed_today)
        
        # === Expense Analysis ===
        expense_today = self.db.fetch_one(
            "SELECT COALESCE(SUM(jumlah), 0) as total FROM expenses WHERE tanggal = ?",
            (today,)
        )
        expense_total = expense_today['total'] if expense_today else 0
        
        # === Habit Analysis ===
        habits = self.db.fetch_all("SELECT * FROM habits")
        habits_done = 0
        for h in habits:
            log = self.db.fetch_one(
                "SELECT * FROM habit_logs WHERE habit_id = ? AND tanggal = ?",
                (h['id'], today)
            )
            if log:
                habits_done += 1
        
        total_habits = len(habits)
        habit_rate = (habits_done / total_habits * 100) if total_habits > 0 else 0
        
        # === Study Analysis ===
        study = self.db.fetch_one(
            "SELECT COALESCE(SUM(duration_minutes), 0) as total FROM study_sessions WHERE date = ?",
            (today,)
        )
        study_mins = study['total'] if study else 0
        
        # === SKOR PRODUKTIVITAS ===
        score = 0
        max_score = 0
        
        # Task completion
        if total_active + total_completed > 0:
            task_rate = total_completed / (total_active + total_completed) * 100
            if task_rate >= 50: score += 25
            elif task_rate >= 25: score += 15
            elif total_completed > 0: score += 10
            max_score += 25
        
        # Habit completion
        if total_habits > 0:
            if habit_rate >= 80: score += 25
            elif habit_rate >= 50: score += 15
            elif habit_rate > 0: score += 10
            max_score += 25
        
        # Study time
        if study_mins >= 60: score += 25
        elif study_mins >= 30: score += 15
        elif study_mins > 0: score += 10
        max_score += 25
        
        # Financial awareness
        if expense_total > 0:
            score += 10  # At least tracking
            max_score += 25
            
            bulan = now.strftime("%Y-%m")
            budget = self.db.fetch_one(
                "SELECT * FROM budget WHERE bulan = ? ORDER BY id DESC LIMIT 1",
                (bulan,)
            )
            if budget:
                daily_budget = budget['budget_bulanan'] / 30
                if expense_total <= daily_budget:
                    score += 15
        else:
            max_score += 25
            score += 15  # Not spending is also good
        
        final_score = min(int(score / max(max_score, 1) * 100), 100)
        
        # Visual score
        if final_score >= 80:
            score_display = f"[bold green]🟢 {final_score}/100 — LUAR BIASA![/bold green]"
            score_emoji = "🏆"
        elif final_score >= 60:
            score_display = f"[bold cyan]🔵 {final_score}/100 — Bagus![/bold cyan]"
            score_emoji = "⭐"
        elif final_score >= 40:
            score_display = f"[bold yellow]🟡 {final_score}/100 — Lumayan[/bold yellow]"
            score_emoji = "💪"
        else:
            score_display = f"[bold red]🔴 {final_score}/100 — Perlu Usaha Lebih[/bold red]"
            score_emoji = "🔥"
        
        # Build report
        report = f"""
{score_emoji} [bold]Skor Produktivitas: {score_display}[/bold]

[bold cyan]📋 Task:[/bold cyan]
  ✅ Diselesaikan hari ini: {total_completed}
  ⏳ Task aktif: {total_active}

[bold magenta]🔥 Kebiasaan:[/bold magenta]
  Selesai: {habits_done}/{total_habits} ({habit_rate:.0f}%)

[bold yellow]📚 Belajar:[/bold yellow]
  Waktu belajar: {study_mins} menit ({study_mins/60:.1f} jam)

[bold green]💰 Keuangan:[/bold green]
  Pengeluaran hari ini: Rp {expense_total:,.0f}
        """
        
        console.print(Panel(report, title="🧠 Laporan Produktivitas", border_style="cyan", width=60))
        
        # Saran
        self._berikan_saran(final_score, total_active, habits_done, total_habits, study_mins, expense_total)
    
    def _berikan_saran(self, score, tasks_active, habits_done, total_habits, study_mins, expense):
        """Berikan saran berdasarkan analisa"""
        console.print("\n[bold yellow]💡 Saran untuk Kamu:[/bold yellow]\n")
        
        saran = []
        
        if tasks_active > 5:
            saran.append("📋 Task terlalu banyak! Fokus 3 yang paling penting dulu.")
        elif tasks_active == 0:
            saran.append("📋 Tidak ada task aktif. Rencanakan apa yang mau dicapai!")
        
        if total_habits > 0 and habits_done < total_habits:
            saran.append(f"🔥 Masih ada {total_habits - habits_done} kebiasaan yang belum dicheckin.")
        
        if study_mins == 0:
            saran.append("📚 Belum ada sesi belajar hari ini. Coba 25 menit Pomodoro!")
        elif study_mins < 60:
            saran.append("📚 Bagus sudah mulai belajar! Tambah 1 sesi lagi untuk hasil optimal.")
        
        jam = datetime.now().hour
        if jam < 10:
            saran.append("🌅 Pagi hari adalah golden hour! Manfaatkan untuk deep work.")
        elif jam < 14:
            saran.append("☀️ Energi masih tinggi. Selesaikan task prioritas tinggi sekarang!")
        elif jam < 18:
            saran.append("🌇 Sore hari cocok untuk review dan wrap-up pekerjaan.")
        else:
            saran.append("🌙 Malam hari — persiapan tidur penting untuk produktivitas besok.")
        
        if not saran:
            saran.append("🏆 Kamu sudah sangat produktif hari ini! Keep it up!")
        
        for s in saran:
            console.print(f"  {s}")
    
    def motivasi_harian(self):
        """Tampilkan motivasi harian"""
        motivasi_list = [
            ("💪", "Kamu tidak harus sempurna. Kamu hanya harus mulai."),
            ("🔥", "Setiap hari tanpa action adalah hari yang terbuang."),
            ("🌟", "Kesuksesan bukan tentang keberuntungan, tapi konsistensi."),
            ("🚀", "1% progress setiap hari = 37x lebih baik dalam setahun."),
            ("🎯", "Fokus pada proses, bukan hasil. Hasil akan mengikuti."),
            ("💎", "Tekanan membuat berlian. Tantangan membuatmu kuat."),
            ("🌱", "Pertumbuhan terjadi di luar zona nyaman."),
            ("⚡", "Jangan tunggu motivasi. MULAI, dan motivasi akan datang."),
            ("🏔️", "Gunung terbesar ditaklukkan selangkah demi selangkah."),
            ("🎪", "Hidupmu adalah stage-mu. Perform seperti juara."),
            ("🧠", "Otak kamu bisa dilatih. Produktivitas itu SKILL, bukan bakat."),
            ("🌊", "Be like water — adaptable but unstoppable."),
            ("📈", "Progress > Perfection. Selalu."),
            ("🦁", "Kamu lebih kuat dari yang kamu pikir."),
            ("🎸", "Rhythm is everything. Bangun ritme harianmu."),
        ]
        
        motivasi = random.choice(motivasi_list)
        
        console.print(Panel(
            f"\n[bold]{motivasi[0]}  {motivasi[1]}[/bold]\n",
            title="💫 Motivasi Hari Ini",
            border_style="yellow",
            width=60
        ))
        
        # Tambahan quote berdasarkan waktu
        jam = datetime.now().hour
        if jam < 6:
            console.print("[dim]🌙 Wow, bangun pagi sekali! Kamu sudah selangkah di depan.[/dim]")
        elif jam < 9:
            console.print("[dim]🌅 Morning warrior! Pagi yang produktif dimulai sekarang.[/dim]")
        elif jam < 12:
            console.print("[dim]☀️ Prime time! Gunakan energi pagi untuk hal penting.[/dim]")
        elif jam < 15:
            console.print("[dim]🌞 Setelah makan siang, coba istirahat 15 menit lalu lanjut.[/dim]")
        elif jam < 18:
            console.print("[dim]🌇 Masih ada waktu! Wrap up dan review hari ini.[/dim]")
        elif jam < 21:
            console.print("[dim]🌆 Malam productive! Tapi jangan lupa istirahat.[/dim]")
        else:
            console.print("[dim]🌙 Waktunya wind down. Tidur cukup = produktivitas besok naik.[/dim]")
    
    def run(self):
        """Antarmuka utama productivity coach"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print("\n[bold cyan]🧠 Pelatih Produktivitas[/bold cyan]")
            
            menu = Table(show_header=False, box=None)
            menu.add_column("Opsi", style="cyan")
            menu.add_column("Keterangan", style="green")
            
            menu_items = [
                ("1", "📊 Analisa Produktivitas Hari Ini"),
                ("2", "💫 Motivasi Harian"),
                ("0", "🔙 Kembali")
            ]
            
            for item in menu_items:
                menu.add_row(item[0], item[1])
            
            console.print(menu)
            
            choice = Prompt.ask("Pilihan", choices=["0","1","2"], default="0")
            
            if choice == "0":
                break
            elif choice == "1":
                self.analisa_hari_ini()
            elif choice == "2":
                self.motivasi_harian()
            
            if choice != "0":
                console.print("[dim]Tekan Enter untuk melanjutkan...[/dim]")
                input()
