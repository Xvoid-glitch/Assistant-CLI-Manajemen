import os
import subprocess
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import sys

class VideoConverter:
    def __init__(self):
        self.console = Console()
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        
    def check_dependencies(self):
        """Check if ffmpeg is installed"""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def install_ffmpeg(self):
        """Guide user to install ffmpeg"""
        self.console.print("[yellow]FFmpeg tidak ditemukan![/yellow]")
        self.console.print("[cyan]Install FFmpeg dengan perintah berikut:[/cyan]")
        
        if sys.platform == "linux":
            self.console.print("[green]sudo apt update && sudo apt install ffmpeg[/green]")
        elif sys.platform == "darwin":  # macOS
            self.console.print("[green]brew install ffmpeg[/green]")
        elif sys.platform == "win32":  # Windows
            self.console.print("[green]Download dari: https://ffmpeg.org/download.html[/green]")
            self.console.print("[green]Atau gunakan Chocolatey: choco install ffmpeg[/green]")
        
        self.console.print("[yellow]Install FFmpeg terlebih dahulu, lalu jalankan ulang![/yellow]")
        return False
    
    def convert_video_to_mp3(self, input_path: Path, output_path: Path):
        """Convert video file to MP3"""
        try:
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-q:a', '0',  # Best quality
                '-map', 'a',
                str(output_path),
                '-y'  # Overwrite output file if exists
            ]
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task("Converting...", total=None)
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True
                )
                
                progress.update(task, completed=100)
            
            if result.returncode == 0:
                # Get file size
                output_size = output_path.stat().st_size / (1024 * 1024)  # MB
                self.console.print(f"[green]✓ Converted successfully! ({output_size:.2f} MB)[/green]")
                return True
            else:
                self.console.print(f"[red]Conversion failed: {result.stderr}[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]Error during conversion: {str(e)}[/red]")
            return False
    
    def get_video_info(self, filepath: Path):
        """Get video file information using ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration,size',
                '-show_entries', 'stream=codec_type,codec_name',
                '-of', 'json',
                str(filepath)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            return None
        except:
            return None
    
    def run(self):
        """Main converter interface"""
        self.console.print("[bold cyan]🎵 Video to MP3 Converter[/bold cyan]")
        
        # Check dependencies
        if not self.check_dependencies():
            self.install_ffmpeg()
            return
        
        # Get input file
        from rich.prompt import Prompt
        
        input_file = Prompt.ask(
            "[cyan]Path ke video file[/cyan]",
            default=str(Path.home() / "Downloads")
        )
        
        input_path = Path(input_file)
        
        if not input_path.exists():
            self.console.print(f"[red]File tidak ditemukan: {input_path}[/red]")
            return
        
        if input_path.suffix.lower() not in self.supported_formats:
            self.console.print(f"[red]Format tidak didukung. Format yang didukung: {', '.join(self.supported_formats)}[/red]")
            return
        
        # Get output path
        default_output = input_path.with_suffix('.mp3')
        output_file = Prompt.ask(
            "[cyan]Output MP3 file path[/cyan]",
            default=str(default_output)
        )
        
        output_path = Path(output_file)
        
        # Show file info
        info = self.get_video_info(input_path)
        if info:
            duration = float(info['format']['duration'])
            self.console.print(f"[yellow]Duration: {duration/60:.1f} minutes[/yellow]")
        
        if Confirm.ask(f"Convert {input_path.name} ke MP3?"):
            success = self.convert_video_to_mp3(input_path, output_path)
            if success:
                self.console.print(f"[green]File saved: {output_path}[/green]")
        else:
            self.console.print("[yellow]Conversion cancelled[/yellow]")