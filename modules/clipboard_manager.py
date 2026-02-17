import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

class ClipboardManager:
    def __init__(self, db):
        self.db = db
    
    def simpan_clipboard(self):
        """Simpan teks ke clipboard manager"""
        console.print("[bold cyan]📋 Simpan ke Clipboard[/bold cyan]")
        
        teks = Prompt.ask("[yellow]Masukkan teks untuk disimpan[/yellow]")
        
        if not teks.strip():
            console.print("[red]Teks tidak boleh kosong![/red]")
            return
        
        self.db.execute_query(
            "INSERT INTO clipboard_items (content) VALUES (?)",
            (teks,)
        )
        console.print("[green]✓ Teks berhasil disimpan ke clipboard![/green]")
        
        # Coba salin ke clipboard sistem
        try:
            import pyperclip
            pyperclip.copy(teks)
            console.print("[dim]Juga disalin ke clipboard sistem[/dim]")
        except:
            pass
    
    def lihat_clipboard(self):
        """Lihat semua item clipboard"""
        rows = self.db.fetch_all(
            "SELECT * FROM clipboard_items ORDER BY is_pinned DESC, created_at DESC LIMIT 50"
        )
        
        if not rows:
            console.print("[yellow]Clipboard kosong[/yellow]")
            return []
        
        table = Table(title="📋 Riwayat Clipboard")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("📌", style="yellow", width=3)
        table.add_column("Isi", style="green", max_width=50)
        table.add_column("Waktu", style="blue", width=16)
        
        for row in rows:
            pin = "📌" if row['is_pinned'] else ""
            content = row['content'][:47] + "..." if len(row['content']) > 47 else row['content']
            waktu = row['created_at'][:16] if row['created_at'] else "-"
            
            table.add_row(str(row['id']), pin, content, waktu)
        
        console.print(table)
        console.print(f"[dim]Total: {len(rows)} item[/dim]")
        return rows
    
    def cari_clipboard(self):
        """Cari di clipboard"""
        console.print("[bold cyan]🔍 Cari di Clipboard[/bold cyan]")
        
        kata_kunci = Prompt.ask("[yellow]Kata kunci[/yellow]")
        
        rows = self.db.fetch_all(
            "SELECT * FROM clipboard_items WHERE content LIKE ? ORDER BY is_pinned DESC, created_at DESC",
            (f"%{kata_kunci}%",)
        )
        
        if not rows:
            console.print(f"[yellow]Tidak ditemukan hasil untuk '{kata_kunci}'[/yellow]")
            return
        
        table = Table(title=f"🔍 Hasil Pencarian: '{kata_kunci}'")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("📌", style="yellow", width=3)
        table.add_column("Isi", style="green", max_width=50)
        
        for row in rows:
            pin = "📌" if row['is_pinned'] else ""
            content = row['content'][:47] + "..." if len(row['content']) > 47 else row['content']
            table.add_row(str(row['id']), pin, content)
        
        console.print(table)
        console.print(f"[dim]Ditemukan: {len(rows)} item[/dim]")
    
    def pin_item(self):
        """Pin/unpin item"""
        rows = self.lihat_clipboard()
        if not rows:
            return
        
        try:
            item_id = int(Prompt.ask("\n[yellow]ID item untuk di-pin/unpin[/yellow]"))
        except ValueError:
            console.print("[red]ID harus angka![/red]")
            return
        
        item = self.db.fetch_one("SELECT * FROM clipboard_items WHERE id = ?", (item_id,))
        if not item:
            console.print("[red]Item tidak ditemukan![/red]")
            return
        
        new_pin = 0 if item['is_pinned'] else 1
        self.db.execute_query(
            "UPDATE clipboard_items SET is_pinned = ? WHERE id = ?",
            (new_pin, item_id)
        )
        
        status = "di-pin 📌" if new_pin else "di-unpin"
        console.print(f"[green]✓ Item berhasil {status}![/green]")
    
    def salin_item(self):
        """Salin item ke clipboard sistem"""
        rows = self.lihat_clipboard()
        if not rows:
            return
        
        try:
            item_id = int(Prompt.ask("\n[yellow]ID item untuk disalin[/yellow]"))
        except ValueError:
            console.print("[red]ID harus angka![/red]")
            return
        
        item = self.db.fetch_one("SELECT * FROM clipboard_items WHERE id = ?", (item_id,))
        if not item:
            console.print("[red]Item tidak ditemukan![/red]")
            return
        
        try:
            import pyperclip
            pyperclip.copy(item['content'])
            console.print("[green]✓ Berhasil disalin ke clipboard![/green]")
        except ImportError:
            console.print(f"[yellow]Isi: {item['content']}[/yellow]")
            console.print("[dim]pyperclip tidak tersedia, salin secara manual[/dim]")
    
    def export_clipboard(self):
        """Export clipboard ke file"""
        rows = self.db.fetch_all(
            "SELECT * FROM clipboard_items ORDER BY is_pinned DESC, created_at DESC"
        )
        
        if not rows:
            console.print("[yellow]Clipboard kosong[/yellow]")
            return
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        export_dir = os.path.join(base_dir, "exports")
        os.makedirs(export_dir, exist_ok=True)
        
        filename = os.path.join(export_dir, f"clipboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"=== Clipboard Export - {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n\n")
            for row in rows:
                pin = "[PINNED] " if row['is_pinned'] else ""
                f.write(f"{pin}{row['content']}\n")
                f.write("-" * 40 + "\n")
        
        console.print(f"[green]✓ {len(rows)} item berhasil diexport ke: {filename}[/green]")
    
    def hapus_item(self):
        """Hapus item clipboard"""
        rows = self.lihat_clipboard()
        if not rows:
            return
        
        try:
            item_id = int(Prompt.ask("\n[yellow]ID item untuk dihapus[/yellow]"))
        except ValueError:
            console.print("[red]ID harus angka![/red]")
            return
        
        if Confirm.ask(f"Yakin hapus item ID {item_id}?"):
            self.db.execute_query("DELETE FROM clipboard_items WHERE id = ?", (item_id,))
            console.print("[green]✓ Item berhasil dihapus![/green]")
    
    def run(self):
        """Antarmuka utama clipboard manager"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print("\n[bold cyan]📋 Manajer Clipboard[/bold cyan]")
            
            menu = Table(show_header=False, box=None)
            menu.add_column("Opsi", style="cyan")
            menu.add_column("Keterangan", style="green")
            
            menu_items = [
                ("1", "📋 Simpan Teks Baru"),
                ("2", "👀 Lihat Semua"),
                ("3", "🔍 Cari"),
                ("4", "📌 Pin / Unpin"),
                ("5", "📄 Salin ke Clipboard"),
                ("6", "📂 Export ke File"),
                ("7", "🗑️ Hapus Item"),
                ("0", "🔙 Kembali")
            ]
            
            for item in menu_items:
                menu.add_row(item[0], item[1])
            
            console.print(menu)
            
            choice = Prompt.ask("Pilihan", choices=["0","1","2","3","4","5","6","7"], default="0")
            
            if choice == "0":
                break
            elif choice == "1":
                self.simpan_clipboard()
            elif choice == "2":
                self.lihat_clipboard()
            elif choice == "3":
                self.cari_clipboard()
            elif choice == "4":
                self.pin_item()
            elif choice == "5":
                self.salin_item()
            elif choice == "6":
                self.export_clipboard()
            elif choice == "7":
                self.hapus_item()
            
            if choice != "0":
                console.print("[dim]Tekan Enter untuk melanjutkan...[/dim]")
                input()
