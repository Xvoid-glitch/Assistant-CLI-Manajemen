import os
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

console = Console()

class LifeDashboard:
    def __init__(self, db):
        self.db = db
    
    def tampilkan(self):
        """Tampilkan life dashboard dalam satu layar"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        bulan = now.strftime("%Y-%m")
        
        console.print(f"\n[bold cyan]{'═' * 60}[/bold cyan]")
        console.print(f"[bold cyan]   🧠 DASHBOARD KEHIDUPAN — {now.strftime('%A, %d %B %Y')}[/bold cyan]")
        console.print(f"[bold cyan]{'═' * 60}[/bold cyan]\n")
        
        # === 1. TOP 3 TASK ===
        top_tasks = self.db.fetch_all('''
            SELECT * FROM tasks 
            WHERE status != 'completed' 
            ORDER BY CASE priority 
                WHEN 'Tinggi' THEN 1 WHEN 'High' THEN 1
                WHEN 'Sedang' THEN 2 WHEN 'Medium' THEN 2
                WHEN 'Rendah' THEN 3 WHEN 'Low' THEN 3
            END, deadline
            LIMIT 3
        ''')
        
        task_text = "[bold yellow]📌 3 Task Terpenting:[/bold yellow]\n"
        if top_tasks:
            for i, t in enumerate(top_tasks, 1):
                deadline_str = f" (⏰ {t['deadline']})" if t['deadline'] else ""
                priority_icon = {"Tinggi": "🔴", "High": "🔴", "Sedang": "🟡", "Medium": "🟡", "Rendah": "🟢", "Low": "🟢"}.get(t['priority'], "⚪")
                task_text += f"   {i}. {priority_icon} {t['task'][:40]}{deadline_str}\n"
        else:
            task_text += "   [dim]Tidak ada task aktif[/dim]\n"
        
        console.print(Panel(task_text, border_style="yellow", width=60))
        
        # === 2. SISA WAKTU PRODUKTIF ===
        jam_sekarang = now.hour
        if jam_sekarang < 6:
            sisa_jam = 22 - jam_sekarang  # Productive until 22:00
            waktu_msg = f"⏳ Sisa Waktu Produktif: [bold green]{sisa_jam} jam[/bold green] (mulai dari jam 6)"
        elif jam_sekarang < 22:
            sisa_jam = 22 - jam_sekarang
            if sisa_jam > 6:
                waktu_msg = f"⏳ Sisa Waktu Produktif: [bold green]{sisa_jam} jam[/bold green]"
            elif sisa_jam > 3:
                waktu_msg = f"⏳ Sisa Waktu Produktif: [bold yellow]{sisa_jam} jam[/bold yellow]"
            else:
                waktu_msg = f"⏳ Sisa Waktu Produktif: [bold red]{sisa_jam} jam[/bold red] — manfaatkan!"
        else:
            waktu_msg = "🌙 Waktunya istirahat! Produktivitas terbaik saat cukup tidur."
        
        console.print(f"  {waktu_msg}\n")
        
        # === 3. BUDGET BULAN INI ===
        budget = self.db.fetch_one(
            "SELECT * FROM budget WHERE bulan = ? ORDER BY id DESC LIMIT 1",
            (bulan,)
        )
        total_expense = self.db.fetch_one(
            "SELECT COALESCE(SUM(jumlah), 0) as total FROM expenses WHERE strftime('%Y-%m', tanggal) = ?",
            (bulan,)
        )
        
        expense_total = total_expense['total'] if total_expense else 0
        
        if budget:
            sisa_budget = budget['budget_bulanan'] - expense_total
            persen_terpakai = (expense_total / budget['budget_bulanan'] * 100) if budget['budget_bulanan'] > 0 else 0
            
            if sisa_budget > 0:
                budget_msg = f"  💰 Budget: Rp {budget['budget_bulanan']:,.0f} | Terpakai: Rp {expense_total:,.0f} | [green]Sisa: Rp {sisa_budget:,.0f}[/green]"
            else:
                budget_msg = f"  💰 Budget: Rp {budget['budget_bulanan']:,.0f} | [red]TERLAMPAUI Rp {abs(sisa_budget):,.0f}![/red]"
            
            bar_len = min(int(persen_terpakai / 5), 20)
            bar_color = "green" if persen_terpakai < 70 else ("yellow" if persen_terpakai < 90 else "red")
            bar = f"[{bar_color}]{'█' * bar_len}{'░' * (20 - bar_len)}[/{bar_color}] {persen_terpakai:.0f}%"
            budget_msg += f"\n  {bar}"
        else:
            budget_msg = f"  💰 Total Pengeluaran Bulan Ini: Rp {expense_total:,.0f}\n  [dim]Belum ada budget — atur di Pencatat Pengeluaran[/dim]"
        
        console.print(budget_msg + "\n")
        
        # === 4. HABIT STREAK ===
        habits = self.db.fetch_all("SELECT * FROM habits ORDER BY id LIMIT 5")
        
        if habits:
            habit_text = "[bold magenta]🔥 Streak Kebiasaan:[/bold magenta]\n"
            for h in habits:
                streak = self._hitung_streak(h['id'])
                fire = "🔥" * min(streak // 3 + (1 if streak > 0 else 0), 5)
                habit_text += f"   {h['emoji']} {h['nama']}: {streak} hari {fire}\n"
            console.print(Panel(habit_text, border_style="magenta", width=60))
        
        # === 5. TARGET MASA DEPAN ===
        goals = self.db.fetch_all(
            "SELECT * FROM future_goals ORDER BY deadline LIMIT 2"
        )
        
        if goals:
            goal_text = "[bold blue]🎯 Target Utama:[/bold blue]\n"
            for g in goals:
                try:
                    deadline = datetime.strptime(g['deadline'], "%Y-%m-%d").date()
                    days_left = (deadline - now.date()).days
                    bar_len = min(int(g['progress'] / 5), 20)
                    bar = f"[cyan]{'█' * bar_len}{'░' * (20 - bar_len)}[/cyan] {g['progress']}%"
                    goal_text += f"   • {g['target'][:35]} ({days_left} hari lagi)\n     {bar}\n"
                except:
                    goal_text += f"   • {g['target'][:35]}\n"
            console.print(Panel(goal_text, border_style="blue", width=60))
        
        console.print(f"\n[dim]Jam sekarang: {now.strftime('%H:%M:%S')} — Semangat! 💪[/dim]")
    
    def _hitung_streak(self, habit_id):
        """Hitung streak kebiasaan"""
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
    
    def run(self):
        """Tampilkan dashboard"""
        self.tampilkan()
        console.print("\n[dim]Tekan Enter untuk kembali...[/dim]")
        input()
