import os
import requests
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()


# WMO Weather Code mapping ke deskripsi Indonesia
WMO_CODES = {
    0: ("☀️", "Cerah", "Langit bersih, tidak ada awan"),
    1: ("🌤️", "Sebagian Cerah", "Sebagian besar cerah"),
    2: ("⛅", "Berawan Sebagian", "Awan menutupi sebagian langit"),
    3: ("☁️", "Berawan", "Langit tertutup awan tebal"),
    45: ("🌫️", "Berkabut", "Kabut tipis menyelimuti area"),
    48: ("🌫️", "Berkabut Tebal", "Kabut tebal dengan embun beku"),
    51: ("🌦️", "Gerimis Ringan", "Hujan gerimis ringan"),
    53: ("🌦️", "Gerimis Sedang", "Hujan gerimis sedang"),
    55: ("🌧️", "Gerimis Lebat", "Hujan gerimis lebat"),
    56: ("🌧️❄️", "Gerimis Beku Ringan", "Gerimis beku ringan"),
    57: ("🌧️❄️", "Gerimis Beku Lebat", "Gerimis beku lebat"),
    61: ("🌧️", "Hujan Ringan", "Hujan ringan"),
    63: ("🌧️", "Hujan Sedang", "Hujan sedang"),
    65: ("🌧️🌧️", "Hujan Lebat", "Hujan lebat, hati-hati banjir!"),
    66: ("🧊🌧️", "Hujan Beku Ringan", "Hujan beku ringan"),
    67: ("🧊🌧️", "Hujan Beku Lebat", "Hujan beku lebat"),
    71: ("🌨️", "Salju Ringan", "Salju ringan turun"),
    73: ("🌨️", "Salju Sedang", "Salju sedang turun"),
    75: ("❄️", "Salju Lebat", "Salju lebat turun"),
    77: ("❄️", "Butiran Salju", "Butiran salju jatuh"),
    80: ("🌦️", "Hujan Singkat Ringan", "Hujan singkat ringan"),
    81: ("🌧️", "Hujan Singkat Sedang", "Hujan singkat sedang"),
    82: ("⛈️", "Hujan Singkat Lebat", "Hujan singkat sangat lebat"),
    85: ("🌨️", "Hujan Salju Ringan", "Hujan salju ringan"),
    86: ("🌨️❄️", "Hujan Salju Lebat", "Hujan salju lebat"),
    95: ("⛈️", "Badai Petir", "Badai petir, tetap di dalam rumah!"),
    96: ("⛈️🧊", "Badai Petir + Hujan Es Ringan", "Badai petir dengan hujan es ringan"),
    99: ("⛈️🧊", "Badai Petir + Hujan Es Lebat", "Badai petir dengan hujan es lebat!"),
}


def get_wind_direction(degrees):
    """Konversi derajat angin ke arah mata angin"""
    directions = [
        "Utara", "Timur Laut", "Timur", "Tenggara",
        "Selatan", "Barat Daya", "Barat", "Barat Laut"
    ]
    idx = round(degrees / 45) % 8
    return directions[idx]


def get_wind_description(speed_kmh):
    """Deskripsi kecepatan angin (skala Beaufort sederhana)"""
    if speed_kmh < 2:
        return "Tenang (tidak terasa)"
    elif speed_kmh < 12:
        return "Sepoi-sepoi"
    elif speed_kmh < 20:
        return "Angin ringan"
    elif speed_kmh < 29:
        return "Angin sedang"
    elif speed_kmh < 39:
        return "Angin agak kencang"
    elif speed_kmh < 50:
        return "Angin kencang"
    elif speed_kmh < 62:
        return "Angin sangat kencang"
    else:
        return "⚠️ Angin badai!"


def get_uv_description(uv_index):
    """Deskripsi UV Index"""
    if uv_index <= 2:
        return ("🟢", "Rendah - Aman beraktivitas luar")
    elif uv_index <= 5:
        return ("🟡", "Sedang - Gunakan sunscreen")
    elif uv_index <= 7:
        return ("🟠", "Tinggi - Hindari matahari langsung")
    elif uv_index <= 10:
        return ("🔴", "Sangat Tinggi - Bahaya!")
    else:
        return ("🟣", "Ekstrem - Jangan keluar rumah!")


def rain_advice(precipitation_mm, rain_prob):
    """Saran berdasarkan curah hujan"""
    tips = []
    if rain_prob >= 70:
        tips.append("☂️ BAWA PAYUNG! Kemungkinan hujan sangat tinggi!")
    elif rain_prob >= 40:
        tips.append("🌂 Disarankan bawa payung jaga-jaga")
    elif rain_prob >= 20:
        tips.append("🤔 Kemungkinan kecil hujan, tapi sedia payung")
    else:
        tips.append("😎 Kemungkinan hujan kecil, aman tanpa payung")

    if precipitation_mm > 10:
        tips.append("⚠️ Curah hujan tinggi, waspada genangan!")
    elif precipitation_mm > 5:
        tips.append("🌧️ Curah hujan sedang, jalanan mungkin basah")
    elif precipitation_mm > 0:
        tips.append("💧 Curah hujan ringan")

    return tips


class WeatherInfo:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.cached_location = None

    def geocode_city(self, city_name):
        """Cari koordinat kota berdasarkan nama"""
        try:
            params = {
                "name": city_name,
                "count": 5,
                "language": "id",
                "format": "json"
            }
            resp = requests.get(self.geocode_url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if "results" not in data or len(data["results"]) == 0:
                console.print(f"[red]Kota '{city_name}' tidak ditemukan![/red]")
                return None

            results = data["results"]

            if len(results) == 1:
                loc = results[0]
                return {
                    "name": loc.get("name", city_name),
                    "country": loc.get("country", ""),
                    "admin1": loc.get("admin1", ""),
                    "lat": loc["latitude"],
                    "lon": loc["longitude"],
                    "timezone": loc.get("timezone", "Asia/Jakarta"),
                }

            # Kalau ada banyak hasil, user pilih
            console.print("\n[yellow]Ditemukan beberapa lokasi:[/yellow]")
            table = Table(show_header=True)
            table.add_column("No", style="cyan")
            table.add_column("Kota", style="green")
            table.add_column("Wilayah", style="yellow")
            table.add_column("Negara", style="magenta")

            for i, loc in enumerate(results, 1):
                table.add_row(
                    str(i),
                    loc.get("name", "-"),
                    loc.get("admin1", "-"),
                    loc.get("country", "-"),
                )
            console.print(table)

            choice = Prompt.ask(
                "Pilih nomor lokasi",
                choices=[str(i) for i in range(1, len(results) + 1)],
                default="1",
            )
            loc = results[int(choice) - 1]
            return {
                "name": loc.get("name", city_name),
                "country": loc.get("country", ""),
                "admin1": loc.get("admin1", ""),
                "lat": loc["latitude"],
                "lon": loc["longitude"],
                "timezone": loc.get("timezone", "Asia/Jakarta"),
            }
        except requests.RequestException as e:
            console.print(f"[red]Error geocoding: {e}[/red]")
            return None

    def fetch_weather(self, lat, lon, timezone="Asia/Jakarta"):
        """Ambil data cuaca dari Open-Meteo API"""
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "timezone": timezone,
                "current": ",".join([
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "precipitation",
                    "rain",
                    "weather_code",
                    "cloud_cover",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "wind_gusts_10m",
                    "surface_pressure",
                    "is_day",
                ]),
                "hourly": ",".join([
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "precipitation_probability",
                    "precipitation",
                    "rain",
                    "weather_code",
                    "cloud_cover",
                    "visibility",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "wind_gusts_10m",
                    "uv_index",
                    "is_day",
                ]),
                "forecast_days": 2,
            }

            resp = requests.get(self.base_url, params=params, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            console.print(f"[red]Gagal mengambil data cuaca: {e}[/red]")
            return None

    def display_current_weather(self, data, location):
        """Tampilkan cuaca saat ini"""
        current = data["current"]
        wmo = current["weather_code"]
        icon, label, desc = WMO_CODES.get(wmo, ("❓", "Tidak Diketahui", ""))

        is_day = current.get("is_day", 1)
        time_icon = "🌞" if is_day else "🌙"

        wind_dir = get_wind_direction(current["wind_direction_10m"])
        wind_desc = get_wind_description(current["wind_speed_10m"])

        loc_label = location["name"]
        if location.get("admin1"):
            loc_label += f", {location['admin1']}"
        if location.get("country"):
            loc_label += f" ({location['country']})"

        info = (
            f"{time_icon} [bold cyan]Cuaca Saat Ini - {loc_label}[/bold cyan]\n"
            f"[yellow]Waktu:[/yellow] {current['time']}\n\n"
            f"  {icon}  [bold]{label}[/bold] — {desc}\n\n"
            f"  🌡️  Suhu          : [bold]{current['temperature_2m']}°C[/bold]\n"
            f"  🤒 Terasa Seperti : {current['apparent_temperature']}°C\n"
            f"  💧 Kelembapan     : {current['relative_humidity_2m']}%\n"
            f"  ☁️  Tutupan Awan  : {current['cloud_cover']}%\n"
            f"  🌬️  Angin         : {current['wind_speed_10m']} km/h ({wind_desc})\n"
            f"  🧭 Arah Angin     : {wind_dir} ({current['wind_direction_10m']}°)\n"
            f"  💨 Hembusan Maks  : {current['wind_gusts_10m']} km/h\n"
            f"  🌧️  Curah Hujan   : {current['precipitation']} mm\n"
            f"  🌧️  Hujan         : {current['rain']} mm\n"
            f"  🔽 Tekanan Udara  : {current['surface_pressure']} hPa\n"
        )

        # Saran hujan berdasarkan data saat ini
        # Cek probabilitas dari hourly data (jam paling dekat)
        hourly = data.get("hourly", {})
        rain_prob = 0
        if "precipitation_probability" in hourly:
            times = hourly.get("time", [])
            now_str = current["time"]
            for i, t in enumerate(times):
                if t >= now_str:
                    rain_prob = hourly["precipitation_probability"][i]
                    break

        tips = rain_advice(current["precipitation"], rain_prob)
        info += f"\n  🎯 Prob. Hujan    : {rain_prob}%\n"
        info += "\n[bold green]💡 Saran:[/bold green]\n"
        for tip in tips:
            info += f"  {tip}\n"

        console.print(Panel(info, border_style="blue", title="⛅ Cuaca Sekarang"))

    def display_hourly_forecast(self, data, location, hours_ahead):
        """Tampilkan prakiraan cuaca per jam"""
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])

        if not times:
            console.print("[red]Data prakiraan tidak tersedia![/red]")
            return

        now = datetime.now()
        # Cari index jam paling dekat dengan sekarang
        start_idx = 0
        for i, t in enumerate(times):
            dt = datetime.fromisoformat(t)
            if dt >= now:
                start_idx = i
                break

        end_idx = min(start_idx + hours_ahead, len(times))

        loc_label = location["name"]
        if location.get("admin1"):
            loc_label += f", {location['admin1']}"

        table = Table(
            title=f"📊 Prakiraan {hours_ahead} Jam Kedepan — {loc_label}",
            show_lines=True,
        )
        table.add_column("Waktu", style="cyan", min_width=12)
        table.add_column("Cuaca", style="green", min_width=20)
        table.add_column("Suhu", style="yellow", min_width=8)
        table.add_column("Hujan %", style="red", min_width=8)
        table.add_column("Curah Hujan", style="blue", min_width=10)
        table.add_column("Angin", style="magenta", min_width=14)
        table.add_column("Awan", style="white", min_width=6)

        has_rain_risk = False
        max_rain_prob = 0

        for i in range(start_idx, end_idx):
            time_str = times[i]
            dt = datetime.fromisoformat(time_str)
            time_display = dt.strftime("%H:%M")

            wmo = hourly["weather_code"][i]
            icon, label, _ = WMO_CODES.get(wmo, ("❓", "?", ""))

            temp = hourly["temperature_2m"][i]
            rain_prob = hourly["precipitation_probability"][i]
            precip = hourly["precipitation"][i]
            wind = hourly["wind_speed_10m"][i]
            wind_dir_deg = hourly["wind_direction_10m"][i]
            wind_dir = get_wind_direction(wind_dir_deg)
            cloud = hourly["cloud_cover"][i]

            if rain_prob >= 40:
                has_rain_risk = True
            if rain_prob > max_rain_prob:
                max_rain_prob = rain_prob

            # Color code rain probability
            if rain_prob >= 70:
                prob_str = f"[bold red]{rain_prob}%[/bold red]"
            elif rain_prob >= 40:
                prob_str = f"[yellow]{rain_prob}%[/yellow]"
            else:
                prob_str = f"[green]{rain_prob}%[/green]"

            table.add_row(
                time_display,
                f"{icon} {label}",
                f"{temp}°C",
                prob_str,
                f"{precip} mm",
                f"{wind} km/h {wind_dir}",
                f"{cloud}%",
            )

        console.print(table)

        # UV Index untuk jam siang
        if "uv_index" in hourly:
            uv_values = [hourly["uv_index"][i] for i in range(start_idx, end_idx)]
            max_uv = max(uv_values) if uv_values else 0
            if max_uv > 0:
                uv_icon, uv_desc = get_uv_description(max_uv)
                console.print(f"\n  {uv_icon} UV Index Maks: {max_uv} — {uv_desc}")

        # Visibility
        if "visibility" in hourly:
            vis_values = [hourly["visibility"][i] for i in range(start_idx, end_idx)]
            min_vis = min(vis_values) if vis_values else 99999
            vis_km = min_vis / 1000
            if vis_km < 1:
                console.print(f"\n  ⚠️ Jarak Pandang Minimum: {vis_km:.1f} km — SANGAT RENDAH!")
            elif vis_km < 5:
                console.print(f"\n  🌫️ Jarak Pandang Minimum: {vis_km:.1f} km — Rendah")
            else:
                console.print(f"\n  👁️ Jarak Pandang Minimum: {vis_km:.1f} km — Baik")

        # Overall advice
        console.print()
        tips = rain_advice(
            max(hourly["precipitation"][i] for i in range(start_idx, end_idx)),
            max_rain_prob
        )
        console.print("[bold green]💡 Saran:[/bold green]")
        for tip in tips:
            console.print(f"  {tip}")

    def run(self):
        """Antarmuka utama fitur cuaca"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print("\n[bold cyan]⛅ Info Cuaca[/bold cyan]")

            menu = Table(show_header=False, box=None)
            menu.add_column("Option", style="cyan")
            menu.add_column("Description", style="green")

            menu_items = [
                ("1", "🌤️  Cuaca Saat Ini"),
                ("2", "⏱️  Prakiraan 1 Jam Kedepan"),
                ("3", "🕐 Prakiraan 5 Jam Kedepan"),
                ("4", "📊 Prakiraan Custom (pilih jam)"),
                ("0", "🔙 Kembali"),
            ]

            for item in menu_items:
                menu.add_row(item[0], item[1])

            console.print(menu)

            choice = Prompt.ask(
                "Pilihan", choices=["0", "1", "2", "3", "4"], default="0"
            )

            if choice == "0":
                break

            # Tanya lokasi
            if self.cached_location:
                loc_name = self.cached_location["name"]
                if self.cached_location.get("admin1"):
                    loc_name += f", {self.cached_location['admin1']}"
                use_cached = Confirm.ask(
                    f"Gunakan lokasi terakhir ({loc_name})?", default=True
                )
                if not use_cached:
                    self.cached_location = None

            if not self.cached_location:
                city = Prompt.ask(
                    "Masukkan nama kota",
                    default="Jakarta",
                )
                location = self.geocode_city(city)
                if not location:
                    continue
                self.cached_location = location
            else:
                location = self.cached_location

            # Ambil data cuaca
            with console.status("[bold green]Mengambil data cuaca...[/bold green]"):
                weather_data = self.fetch_weather(
                    location["lat"],
                    location["lon"],
                    location.get("timezone", "Asia/Jakarta"),
                )

            if not weather_data:
                continue

            if choice == "1":
                self.display_current_weather(weather_data, location)
            elif choice == "2":
                self.display_current_weather(weather_data, location)
                console.print()
                self.display_hourly_forecast(weather_data, location, 1)
            elif choice == "3":
                self.display_current_weather(weather_data, location)
                console.print()
                self.display_hourly_forecast(weather_data, location, 5)
            elif choice == "4":
                hours = Prompt.ask("Berapa jam kedepan? (1-24)", default="3")
                try:
                    h = min(max(int(hours), 1), 24)
                except ValueError:
                    h = 3
                self.display_current_weather(weather_data, location)
                console.print()
                self.display_hourly_forecast(weather_data, location, h)
            
            input("\nTekan Enter untuk melanjutkan...")
