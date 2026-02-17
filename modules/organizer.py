import os
import shutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.prompt import Prompt, Confirm

console = Console()

class FileOrganizer:
    def __init__(self):
        self.extensions = {
            "Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
            "Documents": ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx', '.csv'],
            "Videos": ['.mp4', '.mkv', '.avi', '.mov', '.wmv'],
            "Audio": ['.mp3', '.wav', '.flac', '.m4a', '.ogg'],
            "Archives": ['.zip', '.rar', '.7z', '.tar', '.gz'],
            "Programs": ['.exe', '.msi', '.apk', '.app'],
            "Code": ['.py', '.js', '.html', '.css', '.java', '.cpp', '.php']
        }
    
    def organize_files(self, directory: Path):
        """Organize files into folders by type"""
        if not directory.exists():
            console.print(f"[red]Directory not found: {directory}[/red]")
            return
        
        files = [f for f in directory.iterdir() if f.is_file() and not f.name.startswith('.')]
        
        if not files:
            console.print("[yellow]No files to organize![/yellow]")
            return
        
        moved_count = 0
        
        for file in track(files, description="Organizing files..."):
            ext = file.suffix.lower()
            
            # Find category
            category = "Others"
            for cat, exts in self.extensions.items():
                if ext in exts:
                    category = cat
                    break
            
            # Create category folder
            target_dir = directory / category
            target_dir.mkdir(exist_ok=True)
            
            # Move file
            try:
                shutil.move(str(file), str(target_dir / file.name))
                moved_count += 1
            except Exception as e:
                console.print(f"[red]Failed to move {file.name}: {e}[/red]")
        
        console.print(f"[green]✓ Organized {moved_count} files successfully![/green]")
    
    def find_duplicates(self, directory: Path):
        """Find duplicate files by content hash"""
        import hashlib
        
        duplicates = {}
        files_by_hash = {}
        
        files = [f for f in directory.rglob('*') if f.is_file()]
        
        for file in track(files, description="Scanning for duplicates..."):
            try:
                # Use file size as first check (faster)
                size = file.stat().st_size
                
                # Use MD5 hash (read in chunks)
                hasher = hashlib.md5()
                with open(file, 'rb') as f:
                    chunk = f.read(8192)
                    while chunk:
                        hasher.update(chunk)
                        chunk = f.read(8192)
                
                file_hash = f"{size}_{hasher.hexdigest()}"
                
                if file_hash in files_by_hash:
                    if file_hash not in duplicates:
                        duplicates[file_hash] = [files_by_hash[file_hash]]
                    duplicates[file_hash].append(file)
                else:
                    files_by_hash[file_hash] = file
            except:
                continue
        
        if duplicates:
            console.print(f"[yellow]Found {len(duplicates)} sets of duplicates![/yellow]")
            for hash_val, file_list in duplicates.items():
                console.print("\n[cyan]Duplicate Set:[/cyan]")
                for f in file_list:
                    console.print(f"  - {f}")
        else:
            console.print("[green]No duplicates found![/green]")
    
    def bulk_rename(self, directory: Path):
        """Bulk rename files with pattern"""
        pattern = Prompt.ask("Rename pattern (e.g., 'photo_')", default="file_")
        ext_filter = Prompt.ask("Filter extension (e.g., '.jpg' or leave empty)", default="")
        
        files = sorted([f for f in directory.iterdir() if f.is_file()])
        if ext_filter:
            files = [f for f in files if f.suffix.lower() == ext_filter.lower()]
            
        if not files:
            console.print("[yellow]No files matched filter[/yellow]")
            return
            
        if Confirm.ask(f"Rename {len(files)} files with prefix '{pattern}'?"):
            for i, file in enumerate(track(files, description="Renaming..."), 1):
                new_name = f"{pattern}{i:03d}{file.suffix}"
                file.rename(directory / new_name)
            
            console.print("[green]✓ Renamed successfully![/green]")
    
    def clean_empty_folders(self, directory: Path):
        """Remove empty directories"""
        removed = 0
        for dirpath, dirnames, filenames in os.walk(directory, topdown=False):
            if not dirnames and not filenames:
                try:
                    os.rmdir(dirpath)
                    removed += 1
                except:
                    pass
        
        console.print(f"[green]Removed {removed} empty folders[/green]")

    def disk_analyzer(self, directory: Path):
        """Analyze disk usage by folder"""
        from rich.tree import Tree
        from rich.filesize import decimal
        
        tree = Tree(f"📂 [bold]{directory.name}[/bold]")
        
        def get_size(path):
            total = 0
            try:
                for entry in os.scandir(path):
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir():
                        total += get_size(entry.path)
            except:
                pass
            return total
            
        def build_tree(path, tree_node, depth=0):
            if depth > 2:  # Limit depth
                return
            
            try:
                entries = sorted(os.scandir(path), key=lambda e: e.name)
                for entry in entries:
                    if entry.is_dir() and not entry.name.startswith('.'):
                        size = get_size(entry.path)
                        if size > 10 * 1024 * 1024:  # Only show folders > 10MB
                            node = tree_node.add(f"📁 {entry.name} ([yellow]{decimal(size)}[/yellow])")
                            build_tree(entry.path, node, depth+1)
            except:
                pass
                
        total_size = get_size(directory)
        console.print(f"[bold cyan]Total Size: {decimal(total_size)}[/bold cyan]")
        
        with console.status("[bold green]Analyzing disk usage...[/bold green]"):
            build_tree(directory, tree)
            
        console.print(tree)

    def run(self):
        """Main organizer interface"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print("\n[bold cyan]📁 File Organizer[/bold cyan]")
            
            menu = Table(show_header=False, box=None)
            menu.add_column("Option", style="cyan")
            menu.add_column("Description", style="green")
            
            menu_items = [
                ("1", "🧹 Organize Folder"),
                ("2", "👯 Find Duplicates"),
                ("3", "🏷️  Bulk Rename"),
                ("4", "🗑️  Clean Empty Folders"),
                ("5", "📊 Disk Analyzer"),
                ("0", "🔙 Kembali")
            ]
            
            for item in menu_items:
                menu.add_row(item[0], item[1])
            
            console.print(menu)
            
            choice = Prompt.ask("Pilihan", default="0")
            
            if choice == "0":
                break
            
            # Ask for directory
            path_str = Prompt.ask("Target Directory path", default=str(Path.home() / "Downloads"))
            directory = Path(path_str)
            
            if not directory.exists() or not directory.is_dir():
                console.print(f"[red]Invalid directory: {directory}[/red]")
                input("\nTekan Enter untuk melanjutkan...")
                continue
                
            if choice == "1":
                if Confirm.ask(f"Organize ALL files in {directory}?"):
                    self.organize_files(directory)
            elif choice == "2":
                self.find_duplicates(directory)
            elif choice == "3":
                self.bulk_rename(directory)
            elif choice == "4":
                self.clean_empty_folders(directory)
            elif choice == "5":
                self.disk_analyzer(directory)
            
            if choice != "0":
                input("\nTekan Enter untuk melanjutkan...")