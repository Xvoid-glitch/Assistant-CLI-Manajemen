import os
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, BarColumn, TextColumn
import json

console = Console()

class TaskManager:
    def __init__(self, db):
        self.db = db
    
    def add_task(self):
        """Tambah task baru"""
        console.print("[bold cyan]✅ Tambah Task Baru[/bold cyan]")
        
        task = Prompt.ask("Deskripsi task")
        
        priority = Prompt.ask(
            "Prioritas",
            choices=["Tinggi", "Sedang", "Rendah"],
            default="Sedang"
        )
        
        deadline = Prompt.ask(
            "Deadline (YYYY-MM-DD, atau kosong)", 
            default=""
        )
        
        if deadline:
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                console.print("[red]Format tanggal salah! Gunakan YYYY-MM-DD[/red]")
                deadline = ""
        
        kategori = Prompt.ask("Kategori (opsional)", default="Umum")
        
        self.db.execute_query('''
            INSERT INTO tasks (task, priority, status, deadline, category)
            VALUES (?, ?, 'pending', ?, ?)
        ''', (task, priority, deadline or None, kategori))
        
        console.print("[green]✓ Task berhasil ditambahkan![/green]")
    
    def list_tasks(self, filter_status=None):
        """Tampilkan daftar task"""
        if filter_status:
            query = "SELECT * FROM tasks WHERE status = ? ORDER BY deadline, priority"
            rows = self.db.fetch_all(query, (filter_status,))
        else:
            query = """SELECT * FROM tasks ORDER BY 
                CASE status WHEN 'pending' THEN 1 WHEN 'in_progress' THEN 2 WHEN 'completed' THEN 3 END,
                CASE priority WHEN 'Tinggi' THEN 1 WHEN 'Sedang' THEN 2 WHEN 'Rendah' THEN 3 END,
                deadline"""
            rows = self.db.fetch_all(query)
        
        if not rows:
            console.print("[yellow]Tidak ada task ditemukan[/yellow]")
            return []
        
        table = Table(title="📋 Daftar Task")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Task", style="green", max_width=35)
        table.add_column("Prioritas", style="magenta")
        table.add_column("Status", style="yellow")
        table.add_column("Deadline", style="blue")
        table.add_column("Kategori", style="red")
        
        today = datetime.now().date()
        
        for row in rows:
            priority_color = {
                "Tinggi": "red",
                "Sedang": "yellow",
                "Rendah": "green"
            }.get(row['priority'], "white")
            
            status_map = {
                "pending": ("⏳", "Menunggu", "yellow"),
                "in_progress": ("🔄", "Dikerjakan", "blue"),
                "completed": ("✅", "Selesai", "green")
            }
            s_icon, s_label, s_color = status_map.get(row['status'], ("❓", row['status'], "white"))
            
            deadline = row['deadline'] or "-"
            deadline_display = deadline
            if deadline != "-" and row['status'] != 'completed':
                try:
                    dl = datetime.strptime(deadline, "%Y-%m-%d").date()
                    days_left = (dl - today).days
                    if days_left < 0:
                        deadline_display = f"[red]{deadline} (terlambat!)[/red]"
                    elif days_left == 0:
                        deadline_display = f"[red]{deadline} (HARI INI!)[/red]"
                    elif days_left <= 3:
                        deadline_display = f"[yellow]{deadline} ({days_left}hr)[/yellow]"
                except:
                    pass
            
            table.add_row(
                str(row['id']),
                row['task'][:35],
                f"[{priority_color}]{row['priority']}[/{priority_color}]",
                f"[{s_color}]{s_icon} {s_label}[/{s_color}]",
                deadline_display,
                row['category'] or "-"
            )
        
        console.print(table)
        return rows
    
    def show_task_stats(self):
        """Tampilkan statistik task"""
        tasks = self.db.fetch_all("SELECT * FROM tasks")
        total = len(tasks)
        
        if total == 0:
            console.print("[yellow]Belum ada task sama sekali.[/yellow]")
            return
        
        completed = sum(1 for t in tasks if t['status'] == 'completed')
        in_progress = sum(1 for t in tasks if t['status'] == 'in_progress')
        pending = sum(1 for t in tasks if t['status'] == 'pending')
        
        overdue = 0
        today = datetime.now().date()
        for task in tasks:
            if task['deadline'] and task['status'] != 'completed':
                try:
                    deadline = datetime.strptime(task['deadline'], "%Y-%m-%d").date()
                    if deadline < today:
                        overdue += 1
                except:
                    pass
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        stats_text = f"""
[bold cyan]📊 Statistik Task:[/bold cyan]
  Total      : {total}
  ✅ Selesai  : {completed}
  🔄 Dikerjakan: {in_progress}
  ⏳ Menunggu : {pending}
  ⚠️  Terlambat: {overdue}

[bold yellow]Tingkat Penyelesaian:[/bold yellow] {completion_rate:.1f}% ({completed}/{total})
        """
        
        console.print(Panel(stats_text, border_style="cyan"))
        
        if total > 0:
            progress = Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            )
            
            with progress:
                progress.add_task(
                    "Progress Keseluruhan", 
                    total=total,
                    completed=completed
                )
    
    def update_task_status(self):
        """Update status task"""
        tasks = self.list_tasks()
        if not tasks:
            return
        
        try:
            task_id = int(Prompt.ask("Masukkan ID task untuk update status"))
        except ValueError:
            console.print("[red]ID harus angka![/red]")
            return
        
        current = self.db.fetch_one("SELECT * FROM tasks WHERE id = ?", (task_id,))
        
        if not current:
            console.print("[red]Task tidak ditemukan![/red]")
            return
        
        status_map = {
            "pending": "Menunggu",
            "in_progress": "Dikerjakan",
            "completed": "Selesai"
        }
        
        console.print(f"[yellow]Task: {current['task']} — Status: {status_map.get(current['status'], current['status'])}[/yellow]")
        
        console.print("\n[cyan]Pilih status baru:[/cyan]")
        console.print("  1. ⏳ Menunggu (pending)")
        console.print("  2. 🔄 Dikerjakan (in_progress)")
        console.print("  3. ✅ Selesai (completed)")
        
        status_choice = Prompt.ask("Pilihan", choices=["1", "2", "3"], default="1")
        new_status = {"1": "pending", "2": "in_progress", "3": "completed"}[status_choice]
        
        self.db.execute_query('''
            UPDATE tasks 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_status, task_id))
        
        console.print("[green]✓ Status task berhasil diupdate![/green]")
        
        if new_status == "completed":
            console.print("[bold green]🎉 SELAMAT! Task selesai! 🎉[/bold green]")
    
    def delete_task(self):
        """Hapus task"""
        tasks = self.list_tasks()
        if not tasks:
            return
        
        try:
            task_id = int(Prompt.ask("Masukkan ID task yang akan dihapus"))
        except ValueError:
            console.print("[red]ID harus angka![/red]")
            return
        
        if Confirm.ask(f"Yakin hapus task ID {task_id}?"):
            self.db.execute_query("DELETE FROM tasks WHERE id = ?", (task_id,))
            console.print("[green]✓ Task berhasil dihapus![/green]")
    
    def run(self):
        """Antarmuka utama task manager"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print("\n[bold cyan]✅ Manajer Task[/bold cyan]")
            
            menu = Table(show_header=False, box=None)
            menu.add_column("Opsi", style="cyan")
            menu.add_column("Keterangan", style="green")
            
            menu_items = [
                ("1", "👀 Lihat Semua Task"),
                ("2", "➕ Tambah Task"),
                ("3", "✏️ Update Status"),
                ("4", "🗑️ Hapus Task"),
                ("5", "📊 Statistik"),
                ("0", "🔙 Kembali")
            ]
            
            for item in menu_items:
                menu.add_row(item[0], item[1])
            
            console.print(menu)
            
            choice = Prompt.ask("Pilihan", 
                              choices=["0", "1", "2", "3", "4", "5"], 
                              default="0")
            
            if choice == "0":
                break
            elif choice == "1":
                self.list_tasks()
            elif choice == "2":
                self.add_task()
            elif choice == "3":
                self.update_task_status()
            elif choice == "4":
                self.delete_task()
            elif choice == "5":
                self.show_task_stats()
            
            if choice != "0":
                console.print("[dim]Tekan Enter untuk melanjutkan...[/dim]")
                input()