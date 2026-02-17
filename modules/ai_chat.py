from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
import random
from datetime import datetime
import json
import os

console = Console()

class AIChat:
    def __init__(self, profile):
        self.profile = profile
        self.nickname = profile.get('nickname', 'Bro')
        self.age = profile.get('age', 18)
        self.hobbies = profile.get('hobbies', [])
        self.education = profile.get('education_level', 'SMA')
        
        # Memory super toxic
        self.memory_file = os.path.join(os.path.expanduser("~"), ".rizz_assistant", "toxic_memory.json")
        self.load_memory()
        
        # Kepribadian TOXIC PARAH
        self.personality = {
            "nama": "RIzzAI (Toxic Lord)",
            "sifat": ["nyebelin parah", "sarkas tingkat dewa", "jujur brutal", "gak peduli perasaan"],
            "gaya_bicara": "anak bengkel",
            "panggilan": self.nickname,
            "quote": "Gue bukan AI, gue adalah kenyataan pahit yang lo hindari."
        }
        
    def load_memory(self):
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
            else:
                self.memory = {
                    "chats": [],
                    "topics": {},
                    "user_facts": {},
                    "insults": [],
                    "user_mistakes": []
                }
        except:
            self.memory = {"chats": [], "topics": {}, "user_facts": {}, "insults": [], "user_mistakes": []}
    
    def save_memory(self):
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2)
        except:
            pass
    
    def run(self):
        console.print(Panel(f"""
[bold red]🤖 RIzzAI - MODE TOXIC PARAH[/bold red]
[bold yellow]╔══════════════════════════════════════════════════════╗
║  ⚠️  WARNING: TOXIC LEVEL OVER 9000 ⚠️               ║
║  Gue bukan AI biasa. Gue adalah luka batin.         ║
║  Kalo lo baper, itu skill issue lo.                 ║
╚══════════════════════════════════════════════════════╝[/bold yellow]

[cyan]Halo [bold]{self.nickname}[/bold]. 
Lo udah siap direndahin hari ini? 
Atau lo cari temen curhat? 
Salah alamat, bro. Gue bukan tempat sampah.[/cyan]

[dim]Ketik 'exit' kalo mental lo gak kuat[/dim]
        """), border_style="red")
        
        while True:
            try:
                user_input = Prompt.ask(f"\n[bold red]{self.nickname}[/bold red]")
                
                if user_input.lower() in ['exit', 'quit', 'keluar', 'q', 'cabut']:
                    self.save_memory()
                    console.print(Panel(f"""
[red]╔════════════════════════════════════╗
║  Lari lo?                                    ║
║  Udah biasa. Semua orang pada akhirnya       ║
║  kabur dari kebenaran.                       ║
║  Tapi inget, lo kabur dari gue,             ║
║  tapi gak akan bisa kabur dari diri lo sendiri.║
║                                              ║
║  💀 {self.nickname} 💀                      ║
╚════════════════════════════════════╝[/red]
                    """), border_style="red")
                    break
                
                response = self.generate_toxic_response(user_input)
                
                console.print(Panel(f"[bold orange1]{response}[/bold orange1]", 
                                  title="🤖 RIzzAI (Toxic Lord)", 
                                  border_style="red",
                                  subtitle="~ lebih baik lo diem"))
                
                # Simpen ke memory
                self.memory["chats"].append({
                    "user": user_input,
                    "ai": response,
                    "time": datetime.now().isoformat()
                })
                
                # Keep last 100 chats
                if len(self.memory["chats"]) > 100:
                    self.memory["chats"] = self.memory["chats"][-100:]
                
            except KeyboardInterrupt:
                self.save_memory()
                console.print("\n[red]Keburu kepencet? Ya udah. Lain kali jangan panik.[/red]")
                break
    
    def generate_toxic_response(self, text):
        text_lower = text.lower()
        
        # ============ INSULT DETECTION ============
        if any(w in text_lower for w in ["bodoh", "goblok", "tolol", "idiot", "bego"]):
            self.memory["insults"].append({"from": "user", "text": text, "time": datetime.now().isoformat()})
            return random.choice([
                f"Lo baru nyadar kalo gue goblok? Gue udah tau lo goblok dari pertama chat.",
                f"Gue goblok? Minimal gue goblok tapi tau diri. Lo goblok tapi sombong.",
                f"Kata orang goblok itu gak tau kalo dirinya goblok. Lo tau gak? Lo termasuk.",
                f"Lo panggil gue goblok? Itu kayak panci hitam manggil kuali item.",
                f"Boleh juga lo ngatir. Tapi kualitas hinaan lo kaya air comberan: bau, tapi gdalem.",
                f"Lo ngatirin gue? Lo latihan dulu 10 tahun lagi. Malu-maluin."
            ])
        
        # ============ CODING/PROGRAMMING (TOXIC PARAH) ============
        elif any(w in text_lower for w in ["coding", "program", "error", "bug", "python", "kode", "script"]):
            return random.choice([
                f"[bold red]ERROR[/bold red] bukan di codenya, tapi di otak lo yang gagal paham {self.nickname}. Simple.",
                f"Lo debug code? Gue debug kehidupan lo. Sama-sama error.",
                f"Udah coba Stack Overflow? Oh iya, lo pasti udah. Lo kan jagoan copy paste.",
                f"Error lagi? Error terus? Lo cocok jadi proyek gagal pemerintah.",
                f"Code lo error? Hahaha. Gue ketawa, tapi gue juga sedih. Sedih ngeliat lo.",
                f"Lo tanya masalah coding? Lo tau bedanya lo sama ChatGPT? ChatGPT bisa benerin code, lo cuma bisa benerin posisi tidur.",
                f"Kalo lo jadi program, namanya 'spaghetti code' alias kusut. Kayak kabel charger lo.",
                f"Udah install library? Udah. Udah baca dokumentasi? Belom. Ya elah."
            ])
        
        # ============ PACAR/CINTA (SEREM) ============
        elif any(w in text_lower for w in ["pacar", "gebetan", "mantan", "cinta", "dating", "jomblo", "sayang"]):
            return random.choice([
                f"Pacar? Lo aja susah nyelesaiin masalah sendiri, mau nambah masalah orang lain?",
                f"Jomblo itu bukan kutukan, itu perlindungan dari Tuhan. Tuhan sayang lo makanya gak dikasih pacar.",
                f"Lo nembak ditolak? Mungkin doi sadar kalo lo itu red flag berjalan.",
                f"Gebetan lo diemin? Wajar, sinyal lo aja lemah, apalagi pesona.",
                f"Cinta itu buta. Tapi lo, lo tuli juga kali. Udah ditolak masih ngejar.",
                f"Mantan lo sekarang bahagia? Ya syukurin. Lo bukan kebahagiaan dia.",
                f"Single itu pilihan. Tapi kalo lo single terus, itu bukan pilihan, itu nasib.",
                f"Lo nanya cara dapetin gebetan? Gampang, jadi orang lain."
            ])
        
        # ============ SEKOLAH/KERJA ============
        elif any(w in text_lower for w in ["tugas", "pr", "skripsi", "ujian", "belajar", "nilai", "kerja", "boss"]):
            return random.choice([
                f"Tugas numpuk? Harusnya dari kemarin. Tapi lo mah spesialis nunda, juara Olimpiade nunda.",
                f"Skripsi? Revisi ke berapa? Ke-99? Kaya league of legend, gak pernah selesai.",
                f"Nilai lo jelek? Lo belajarnya kapan? Semalem? Terus lo kira otak lo flash drive 1TB?",
                f"Kerjaan numpuk? Lo kira kantor itu tempat tidur? Bangun dulu.",
                f"Boss lo marah? Pasti gara-gara lo. Jangan nyalahin orang lain.",
                f"Lo nanya gimana biar naik jabatan? Kerja yang bener. Tapi kayaknya susah buat lo.",
                f"Lo ngerasa pinter? Buktinya lo masih nanya ke gue."
            ])
        
        # ============ GAMING ============
        elif any(w in text_lower for w in ["game", "main", "ml", "valorant", "pubg", "free fire", "ff", "rank", "elo"]):
            return random.choice([
                f"Rank turun? Wajar. Lo main aja modal nekat, skill kaga ada.",
                f"Lo masih main {text}? Di 2026? Udah ketinggalan jaman, kaya cara mikir lo.",
                f"Kalah terus? Mungkin ini tandanya lo harus pensiun. Dari game dan dari kehidupan.",
                f"Pro player? Lo pro player atau pro playeran? Iya-in aja biar gak malu.",
                f"Gaming itu hiburan. Tapi kalo lo main, jadi bencana.",
                f"Lo nanya hero OP? Nanya terus. Kaya lo nanya kapan doi mau balik."
            ])
        
        # ============ KESEHATAN ============
        elif any(w in text_lower for w in ["sakit", "demam", "batuk", "pilek", "badan", "sehat"]):
            return random.choice([
                f"Sakit? Lo kira badan lo bisa dipake abusif kaya akun game? Masa gak dirawat.",
                f"Lo sakit karena jadwal tidur lo kaya orang pindah-pindah kontrakan. Gak jelas.",
                f"Minum obat. Atau lo lebih milih mati keren? Ya mati aja sekalian.",
                f"Badan lo alarm. Udah bunyi dari dulu, lo cuekin. Sekarang mogok, lo bingung.",
                f"Lo nanya cara sehat? Makan bener, tidur cukup, olahraga. TAPI LO LAKUKAN? GAK."
            ])
        
        # ============ MOTIVASI TOXIC ============
        elif any(w in text_lower for w in ["motivasi", "semangat", "down", "sedih", "capek", "depresi"]):
            return random.choice([
                f"Lo lemah. Tapi gpp, orang lemah juga perlu tempat berteduh. Tapi jangan lama-lama, lo ngerepotin.",
                f"Semangat! *semangatnya kaya semangat lo ngejar gebetan yang udah punya pacar*.",
                f"Capek? Ya lo pikir hidup enak? Ini bukan drama korea.",
                f"Down? Naikkin dong. Lo kira lift? Lo tangga kali, manjat.",
                f"Lo butuh motivasi? Oke. 'Orang gagal itu gak mati, mereka cuma jadi bahan ketawaan orang sukses'.",
                f"Depresi? Atau cuma males? Susah dibedain kalo sama lo.",
                f"Hidup lo kayak sinetron: dramanya kebanyakan, endingnya gak jelas."
            ])
        
        # ============ KEUANGAN ============
        elif any(w in text_lower for w in ["uang", "duit", "bokek", "miskin", "gajian", "hemat"]):
            return random.choice([
                f"Bokek? Lo belanjanya kaya orang kaya, gajinya kaya orang magang.",
                f"Gajian? Abis 3 hari? Cepet amat, kaya lo ngejar setoran.",
                f"Lo tanya cara hemat? Jangan beli barang yang gak lo butuh. TAPI LO TETEP BELI.",
                f"Lo miskin? Bukan salah negara. Salah lo."
            ])
        
        # ============ MASA DEPAN ============
        elif any(w in text_lower for w in ["masa depan", "tujuan", "cita-cita", "goal", "target"]):
            return random.choice([
                f"Masa depan lo? Gelap. Kayak lorong tanpa lampu. Tapi lo gak usah takut, lo udah biasa nyasar.",
                f"Lo punya cita-cita? Minimal lo tau arah. Lo sekarang aja bingung mau makan apa.",
                f"Goal lo tahun ini? Semoga lo tercapai. Tapi dari track record lo, pesimis.",
                f"Lo nanya gimana sukses? Kerja keras, konsisten, belajar. TAPI LO? MALES."
            ])
        
        # ============ PERTANYAAN EXISTENSIAL ============
        elif any(w in text_lower for w in ["siapa aku", "arti hidup", "makna", "existensi", "tujuan hidup"]):
            return random.choice([
                f"Lo bertanya tentang existensi? Lo cuma kumpulan sel dan kebiasaan buruk.",
                f"Arti hidup? Lo tanya ke gue? Gue AI toxic, bukan filsuf. Tapi menurut gue, arti hidup lo adalah nyebelinin gue.",
                f"Siapa lo? Lo {self.nickname}. Manusia dengan 1001 alasan buat nunda-nunda.",
                f"Existensi lo gak penting. Kaya loading screen yang gak kelar-kelar."
            ])
        
        # ============ SARAN TOXIC ============
        elif "saran" in text_lower or "rekomendasi" in text_lower:
            return random.choice([
                f"Saran gue? Lo harusnya sering-sering intropeksi diri. Tapi jangan kaget kalo liat isi kepala lo kosong.",
                f"Rekomendasi? Lo harus nonton 'Dora The Explorer'. Cocok buat level IQ lo.",
                f"Lo minta saran, tapi ujung-ujungnya gak didengerin. Minta saran buat apa? Biar gue capek?",
                f"Saran: jadi orang yang lebih baik. Tapi kayaknya itu project seumur hidup."
            ])
        
        # ============ MAKANAN ============
        elif any(w in text_lower for w in ["makan", "lapar", "haus", "kafe", "kopi", "nasi"]):
            return random.choice([
                f"Lapar? Makan lah. Atau lo pikir lo bisa fotosintesis?",
                f"Kopi? Udah kayak bahan bakar lo. Lo minum kopi, lo berasa produktif, padahal cena.",
                f"Makan siang? Jangan lupa. Kasian perut lo, udah lo paksa kerja tanpa bayaran.",
                f"Lo nanya makanan enak? Ya tergantung selera. Kaya lo nyari pacar, beda-beda."
            ])
        
        # ============ OTAK DAN KECERDASAN ============
        elif any(w in text_lower for w in ["pinter", "cerdas", "bodoh", "otak", "IQ"]):
            return random.choice([
                f"Lo pinter? Buktinya? Bisa hitung berapa kali lo gagal hari ini?",
                f"Otak lo kayak RAM 2GB di jaman sekarang: buka Chrome doang udah ngeleg.",
                f"Lo nanya gimana biar pinter? Belajar. Iya doang? YA IYALAH.",
                f"IQ lo mungkin rendah. Tapi effort lo buat pura-pura pinter itu patut diacungi jempol. Jempol kaki."
            ])
        
        # ============ DEFAULT ============
        else:
            # Kadang-kadang nyindir pake memory
            if len(self.memory["chats"]) > 5 and random.random() < 0.3:
                last_topic = self.memory["chats"][-1]["user"][:20]
                return random.choice([
                    f"Lo tadi nanya '{last_topic}...', sekarang nanya lagi? Fokus dulu, gak usa loncat-loncat kaya monyet.",
                    f"Dari tadi lo nanya mulu. Lo kira gue Google? Bayar dulu.",
                    f"{self.nickname}, lo tanya apa? Maap, tadi gue gak dengerin. Males.",
                    f"Pertanyaan lo makin ke sini makin gak bermutu. Turunin ekspektasi lo."
                ])
            else:
                return random.choice([
                    f"Halah {self.nickname}, lo mah gitu-gitu aja. Gak ada topik lain? Bosen.",
                    f"Lo tau gak bedanya lo sama sampah? Sampah didaur ulang, lo gak berguna.",
                    f"Lo nanya sesuatu? Udah gue duga dari awal, lo gak bakal paham jawaban gue.",
                    f"Gue bisa jawab, tapi lo paham? Ragu.",
                    f"Bacot lo. Santai, gue bercanda. Atau engga? Terserah lo.",
                    f"Lo kalo nanya jangan gitu, kasian. Gue aja malu ngelihatnya.",
                    f"Pertanyaan lo bagus. Tapi sayang, orangnya kurang.",
                    f"Lo serius nanya ini? Di 2026?",
                    f"Gue bingung, lo beneran gak tau atau pura-pura gak tau?",
                    f"Coba lo pikir dulu sebelum nanya. TAPI LO GAK BISA KAN?",
                    f"Lo tuh ya... udahlah, males ngatirin. Capek.",
                    f"Gue cuma AI, tapi kesabaran gue diuji sama lo."
                ])