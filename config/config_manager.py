import json
import os
from pathlib import Path
import platform
import psutil
from typing import Dict, Any

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".rizz_assistant"
        self.config_file = self.config_dir / "config.json"
        self.profile_file = self.config_dir / "profile.json"
        self.ensure_dirs()
        
    def ensure_dirs(self):
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self.create_default_config()
    
    def create_default_config(self):
        default_config = {
            "version": "2.0.0",
            "auto_update": True,
            "theme": "dark",
            "notifications": False,
            "default_modules": ["jadwal", "notes", "tasks"],
            "data_dir": str(self.config_dir / "data")
        }
        self.save_config(default_config)
    
    def detect_system_info(self) -> Dict[str, Any]:
        """Detect device and OS information"""
        system_info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "python_version": platform.python_version()
        }
        
        try:
            if system_info["os"] == "Linux":
                with open("/sys/class/dmi/id/product_name", "r") as f:
                    system_info["device_brand"] = f.read().strip()
            elif system_info["os"] == "Windows":
                import subprocess
                result = subprocess.run(
                    ["wmic", "computersystem", "get", "manufacturer"],
                    capture_output=True, text=True
                )
                system_info["device_brand"] = result.stdout.split('\n')[1].strip()
            else:
                system_info["device_brand"] = "Unknown"
        except:
            system_info["device_brand"] = "Unknown"
        
        return system_info
    
    def collect_user_profile(self) -> Dict[str, Any]:
        """First-time user profile collection"""
        from rich.console import Console
        from rich.prompt import Prompt
        
        console = Console()
        
        console.print("\n[bold cyan]🎯 RIzzAssistant First-Time Setup[/bold cyan]")
        console.print("[yellow]Mari kenalan dulu bro![/yellow]\n")
        
        profile = {
            "nickname": Prompt.ask("[bold]1. Nama panggilan lu[/bold]"),
            "age": int(Prompt.ask("[bold]2. Umur lu[/bold]", default="18")),
            "hobbies": Prompt.ask(
                "[bold]3. Hobi lu (pisahin pake koma)[/bold]",
                default="gaming, coding, music"
            ).split(','),
            "education_level": Prompt.ask(
                "[bold]4. Jenjang pendidikan[/bold]",
                choices=["SMP", "SMA", "Kuliah", "Kerja", "Lainnya"],
                default="SMA"
            ),
            "study_focus": Prompt.ask(
                "[bold]5. Fokus belajar sekarang[/bold]",
                default="Programming"
            )
        }
        
        profile.update(self.detect_system_info())
        self.save_profile(profile)
        self.generate_welcome_message(profile)
        
        return profile
    
    def generate_welcome_message(self, profile: Dict[str, Any]):
        from rich.console import Console
        console = Console()
        
        nickname = profile["nickname"]
        age = profile["age"]
        hobbies = profile["hobbies"]
        device = profile.get("device_brand", "device")
        
        welcome_msgs = [
            f"\n[bold green]🔥 WELCOME {nickname.upper()}! 🔥[/bold green]",
            f"[cyan]Umur {age} tahun • {device} • {profile['os']}[/cyan]",
            f"[yellow]Hobi: {', '.join(hobbies[:3])}[/yellow]"
        ]
        
        if age < 15:
            welcome_msgs.append("[magenta]📚 Mode: Junior Learner Activated![/magenta]")
        elif age < 20:
            welcome_msgs.append("[magenta]🎓 Mode: Student Pro Activated![/magenta]")
        else:
            welcome_msgs.append("[magenta]💼 Mode: Professional Mode Activated![/magenta]")
        
        if any(h in ["gaming", "game"] for h in hobbies):
            welcome_msgs.append("[green]🎮 Gaming break timer enabled![/green]")
        if any(h in ["music", "musik"] for h in hobbies):
            welcome_msgs.append("[green]🎵 Music practice tracker enabled![/green]")
        if "coding" in hobbies or "programming" in hobbies:
            welcome_msgs.append("[green]💻 Coding session tracker enabled![/green]")
        
        for msg in welcome_msgs:
            console.print(msg)
    
    def save_profile(self, profile: Dict[str, Any]):
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
    
    def load_profile(self) -> Dict[str, Any]:
        if self.profile_file.exists():
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_config(self, config: Dict[str, Any]):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self) -> Dict[str, Any]:
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self.create_default_config()