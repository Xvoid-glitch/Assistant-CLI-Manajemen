import sqlite3
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
import json
import os

console = Console()

class NotesManager:
    def __init__(self, db):
        self.db = db
    
    def add_note(self):
        """Tambah catatan baru"""
        console.print("[bold cyan]📝 Tambah Catatan Baru[/bold cyan]")
        
        judul = Prompt.ask("[yellow]Judul catatan[/yellow]")
        
        console.print("\n[green]✏️  Isi catatan (ketik 'SELESAI' di baris baru):[/green]")
        console.print("[dim]Contoh: Ketik 'SELESAI' lalu Enter[/dim]\n")
        
        lines = []
        while True:
            line = input("> ")
            if line.strip().upper() == "SELESAI":
                break
            lines.append(line)
        
        isi = "\n".join(lines)
        
        if not isi.strip():
            console.print("[red]❌ Catatan tidak boleh kosong![/red]")
            return
        
        tags_input = Prompt.ask("[yellow]Tags (pisah dengan koma, opsional)[/yellow]", default="")
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()] if tags_input.strip() else []
        
        kategori = Prompt.ask("[yellow]Kategori (opsional)[/yellow]", default="Umum")
        
        self.db.execute_query('''
            INSERT INTO catatan (judul, isi, tags, kategori)
            VALUES (?, ?, ?, ?)
        ''', (judul, isi, json.dumps(tags), kategori))
        
        console.print(f"\n[green]✓ Catatan '[bold]{judul}[/bold]' berhasil disimpan![/green]")
    
    def edit_note(self):
        """Edit catatan yang ada"""
        rows = self.list_notes()
        if not rows:
            return
        
        try:
            note_id = int(Prompt.ask("\n[yellow]Masukkan ID catatan yang akan diedit[/yellow]"))
        except ValueError:
            console.print("[red]❌ ID harus angka![/red]")
            return
        
        note = self.db.fetch_one("SELECT * FROM catatan WHERE id = ?", (note_id,))
        
        if not note:
            console.print("[red]❌ Catatan tidak ditemukan![/red]")
            return
        
        current_tags = json.loads(note['tags']) if note['tags'] else []
        
        console.print(f"\n[bold yellow]✏️  Mengedit: {note['judul']}[/bold yellow]")
        
        new_judul = Prompt.ask("[cyan]Judul baru[/cyan]", default=note['judul'])
        
        console.print("\n[cyan]Isi catatan saat ini:[/cyan]")
        console.print(Panel(note['isi'][:200] + ("..." if len(note['isi']) > 200 else ""), 
                          border_style="dim"))
        
        edit_isi = Prompt.ask("[yellow]Ubah isi catatan?[/yellow]", choices=["y", "n"], default="n")
        
        if edit_isi.lower() == "y":
            console.print("\n[green]✏️  Isi baru (ketik 'SELESAI' di baris baru):[/green]")
            lines = []
            while True:
                line = input("> ")
                if line.strip().upper() == "SELESAI":
                    break
                lines.append(line)
            new_isi = "\n".join(lines)
            if not new_isi.strip():
                new_isi = note['isi']
        else:
            new_isi = note['isi']
        
        tags_default = ", ".join(current_tags) if current_tags else ""
        tags_input = Prompt.ask("[cyan]Tags baru (pisah dengan koma)[/cyan]", default=tags_default)
        new_tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()] if tags_input.strip() else []
        
        new_kategori = Prompt.ask("[cyan]Kategori baru[/cyan]", default=note['kategori'])
        
        self.db.execute_query('''
            UPDATE catatan 
            SET judul = ?, isi = ?, tags = ?, kategori = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_judul, new_isi, json.dumps(new_tags), new_kategori, note_id))
        
        console.print("[green]✓ Catatan berhasil diupdate![/green]")
    
    def list_notes(self, search_term=None, kategori=None):
        """Tampilkan semua catatan"""
        if search_term:
            query = """
                SELECT * FROM catatan 
                WHERE judul LIKE ? OR isi LIKE ? 
                ORDER BY updated_at DESC
            """
            params = (f"%{search_term}%", f"%{search_term}%")
        elif kategori:
            query = "SELECT * FROM catatan WHERE kategori = ? ORDER BY updated_at DESC"
            params = (kategori,)
        else:
            query = "SELECT * FROM catatan ORDER BY updated_at DESC"
            params = ()
        
        rows = self.db.fetch_all(query, params)
        
        if not rows:
            console.print("[yellow]📭 Tidak ada catatan ditemukan[/yellow]")
            return []
        
        table = Table(title="📚 Daftar Catatan", title_style="bold cyan")
        table.add_column("No", style="cyan", justify="right")
        table.add_column("ID", style="dim cyan", justify="right")
        table.add_column("Judul", style="green", width=30)
        table.add_column("Kategori", style="magenta", width=15)
        table.add_column("Tags", style="yellow", width=20)
        table.add_column("Diupdate", style="blue", width=12)
        
        for i, row in enumerate(rows, 1):
            tags = json.loads(row['tags']) if row['tags'] else []
            tags_str = ", ".join(tags[:3]) + ("..." if len(tags) > 3 else "")
            tags_str = tags_str if tags_str else "-"
            
            try:
                updated = datetime.fromisoformat(row['updated_at'])
                updated_str = updated.strftime("%d/%m %H:%M")
            except:
                updated_str = row['updated_at'][:16] if row['updated_at'] else "-"
            
            judul = row['judul'][:27] + "..." if len(row['judul']) > 27 else row['judul']
            kat = row['kategori'][:12] + "..." if len(row['kategori']) > 12 else row['kategori']
            
            table.add_row(
                str(i),
                str(row['id']),
                judul,
                kat,
                tags_str,
                updated_str
            )
        
        console.print()
        console.print(table)
        console.print(f"[dim]Total: {len(rows)} catatan (gunakan ID untuk memilih)[/dim]")
        return rows
    
    def view_note_detail(self, note_id):
        """Lihat detail catatan"""
        note = self.db.fetch_one("SELECT * FROM catatan WHERE id = ?", (note_id,))
        
        if not note:
            console.print("[red]❌ Catatan tidak ditemukan![/red]")
            return
        
        tags = json.loads(note['tags']) if note['tags'] else []
        tags_str = ", ".join(tags) if tags else "-"
        
        created = note['created_at'][:16] if note['created_at'] else "-"
        updated = note['updated_at'][:16] if note['updated_at'] else "-"
        
        content = f"""
[bold cyan]{note['judul']}[/bold cyan]

[bold yellow]📌 Informasi:[/bold yellow]
  • Kategori: {note['kategori']}
  • Tags: {tags_str}
  • Dibuat: {created}
  • Diupdate: {updated}

[bold yellow]📝 Isi Catatan:[/bold yellow]
{note['isi']}
        """
        
        console.print(Panel(
            content,
            title="📖 Detail Catatan",
            border_style="green",
            width=80
        ))
    
    def search_notes(self):
        """Cari catatan"""
        console.print("[bold cyan]🔍 Pencarian Catatan[/bold cyan]")
        search_term = Prompt.ask("[yellow]Kata kunci pencarian[/yellow]")
        
        if not search_term.strip():
            console.print("[red]❌ Kata kunci tidak boleh kosong![/red]")
            return
        
        self.list_notes(search_term=search_term)
    
    def delete_note(self):
        """Hapus catatan"""
        rows = self.list_notes()
        if not rows:
            return
        
        try:
            note_id = int(Prompt.ask("\n[yellow]Masukkan ID catatan yang akan dihapus[/yellow]"))
        except ValueError:
            console.print("[red]❌ ID harus angka![/red]")
            return
        
        note = self.db.fetch_one("SELECT judul FROM catatan WHERE id = ?", (note_id,))
        
        if not note:
            console.print("[red]❌ Catatan tidak ditemukan![/red]")
            return
        
        judul = note['judul']
        
        if Confirm.ask(f"\n[red]Yakin hapus catatan '{judul}'?[/red]", default=False):
            self.db.execute_query("DELETE FROM catatan WHERE id = ?", (note_id,))
            console.print(f"[green]✓ Catatan '{judul}' berhasil dihapus![/green]")
    
    def export_notes(self):
        """Export catatan ke JSON"""
        rows = self.db.fetch_all("SELECT * FROM catatan ORDER BY created_at DESC")
        
        if not rows:
            console.print("[yellow]📭 Tidak ada catatan untuk diexport[/yellow]")
            return
        
        clean_rows = []
        for row in rows:
            clean_row = dict(row)
            if clean_row['tags']:
                try:
                    clean_row['tags'] = json.loads(clean_row['tags'])
                except:
                    clean_row['tags'] = []
            else:
                clean_row['tags'] = []
            clean_rows.append(clean_row)
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_notes": len(clean_rows),
            "notes": clean_rows
        }
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        export_dir = os.path.join(base_dir, "exports")
        os.makedirs(export_dir, exist_ok=True)
        
        filename = os.path.join(export_dir, f"catatan_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            console.print(f"[green]✓ {len(clean_rows)} catatan berhasil diexport ke: {filename}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Gagal export: {str(e)}[/red]")
    
    def run(self):
        """Antarmuka utama catatan"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print("\n[bold cyan]════════════════════════════════════════[/bold cyan]")
            console.print("[bold cyan]📝 Manajer Catatan Pintar[/bold cyan]")
            console.print("[bold cyan]════════════════════════════════════════[/bold cyan]\n")
            
            menu = Table(show_header=False, box=None, padding=(0, 2))
            menu.add_column("Opsi", style="cyan", width=6)
            menu.add_column("Keterangan", style="green")
            
            menu_items = [
                ("1", "👀 Lihat Semua Catatan"),
                ("2", "🔍 Cari Catatan"),
                ("3", "➕ Tambah Catatan"),
                ("4", "📖 Lihat Detail"),
                ("5", "✏️ Edit Catatan"),
                ("6", "🗑️ Hapus Catatan"),
                ("7", "📂 Export Catatan"),
                ("0", "🔙 Kembali")
            ]
            
            for item in menu_items:
                menu.add_row(item[0], item[1])
            
            console.print(menu)
            
            choice = Prompt.ask("[bold cyan]Pilihan[/bold cyan]", 
                              choices=["0", "1", "2", "3", "4", "5", "6", "7"], 
                              default="0")
            
            if choice == "0":
                break
            elif choice == "1":
                self.list_notes()
            elif choice == "2":
                self.search_notes()
            elif choice == "3":
                self.add_note()
            elif choice == "4":
                self.list_notes()
                try:
                    note_id = int(Prompt.ask("\n[yellow]ID catatan untuk dilihat[/yellow]"))
                    self.view_note_detail(note_id)
                except ValueError:
                    console.print("[red]ID harus angka![/red]")
            elif choice == "5":
                self.edit_note()
            elif choice == "6":
                self.delete_note()
            elif choice == "7":
                self.export_notes()
            
            if choice != "0":
                console.print("[dim]Tekan Enter untuk melanjutkan...[/dim]")
                input()