
"""
    Discord Sunucu Kopyalayıcı
    Project by Xllor0001
    
    Hesaplar arası geçiş veya sunucu yedekleme için tasarlanmış 
    profesyonel düzeyde bir Discord sunucu kopyalama aracı.
"""

import discord
import asyncio
import os
import sys
from colorama import Fore, Style, init
from discord.ext import commands

# Colorama'yı başlat
init(autoreset=True)

class XllorCloner(commands.Bot):
    def __init__(self, token, source_id, target_id):
        super().__init__(command_prefix=".", self_bot=True)
        self.token = token
        self.source_id = source_id
        self.target_id = target_id
        self.role_map = {}

    def log(self, durum, mesaj):
        """CLI görünürlüğü için özel loglama"""
        renkler = {
            "BİLGİ": Fore.CYAN,
            "BAŞARI": Fore.GREEN,
            "UYARI": Fore.YELLOW,
            "HATA": Fore.RED
        }
        renk = renkler.get(durum, Fore.WHITE)
        print(f"{Style.BRIGHT}[{renk}{durum}{Style.RESET_ALL}] {mesaj}")

    async def on_ready(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.display_banner()
        self.log("BİLGİ", f"Giriş yapıldı: {Fore.MAGENTA}{self.user}")
        
        source = self.get_guild(self.source_id)
        target = self.get_guild(self.target_id)

        if not source or not target:
            self.log("HATA", "Sunucular bulunamadı. ID'lerin doğru olduğundan ve her iki sunucuda da olduğunuzdan emin olun.")
            await self.close()
            return

        self.log("BİLGİ", f"Senkronize ediliyor: {Fore.YELLOW}{source.name}{Fore.WHITE} -> {Fore.GREEN}{target.name}")
        await self.start_cloning(source, target)
        self.log("BAŞARI", "Kopyalama tamamlandı. Çıkış yapılıyor...")
        await self.close()

    def display_banner(self):
        banner = f"""
{Fore.CYAN}{Style.BRIGHT}    ██╗  ██╗██╗     ██╗      ██████╗ ██████╗  ██████╗  ██████╗  ██╗
    ╚██╗██╔╝██║     ██║     ██╔═══██╗██╔══██╗██╔═████╗██╔═████╗███║
     ╚███╔╝ ██║     ██║     ██║   ██║██████╔╝██║██╔██║██║██╔██║╚██║
     ██╔██╗ ██║     ██║     ██║   ██║██╔══██╗██████╔╝██████╔╝ ██║
    ██╔╝ ██╗███████╗███████╗╚██████╔╝██║  ██║╚██████╔╝╚██████╔╝ ██║
    ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚═════╝  ╚═╝
    {Fore.WHITE}------------------ {Fore.RED}Project by Xllor0001{Fore.WHITE} ------------------
        """
        print(banner)

    async def clear_target(self, target):
        self.log("BİLGİ", "Hedef sunucu verileri temizleniyor...")
        # Kanalları temizle
        for ch in target.channels:
            try:
                await ch.delete()
                await asyncio.sleep(0.3)
            except: pass
        
        # Rolleri temizle (everyone ve yönetilen roller hariç)
        for role in target.roles:
            if not role.is_default() and not role.managed:
                try:
                    await role.delete()
                    await asyncio.sleep(0.3)
                except: pass

    async def clone_roles(self, source, target):
        self.log("BİLGİ", "Roller kopyalanıyor...")
        for role in reversed(source.roles):
            if not role.is_default() and not role.managed:
                try:
                    new_role = await target.create_role(
                        name=role.name,
                        permissions=role.permissions,
                        color=role.color,
                        hoist=role.hoist,
                        mentionable=role.mentionable
                    )
                    self.role_map[role.id] = new_role
                    await asyncio.sleep(0.4)
                except Exception as e:
                    self.log("UYARI", f"Rol kopyalanamadı: {role.name} | {e}")

    async def clone_channels(self, source, target):
        self.log("BİLGİ", "Kanal yapısı oluşturuluyor...")
        
        # Kategorileri ve içindeki kanalları kopyala
        for category in source.categories:
            try:
                new_cat = await target.create_category(name=category.name)
                await asyncio.sleep(0.4)
                
                for ch in category.channels:
                    overwrites = {self.role_map[r.id]: v for r, v in ch.overwrites.items() if r.id in self.role_map}
                    
                    if isinstance(ch, discord.TextChannel):
                        await target.create_text_channel(name=ch.name, category=new_cat, overwrites=overwrites, topic=ch.topic, nsfw=ch.nsfw)
                    elif isinstance(ch, discord.VoiceChannel):
                        await target.create_voice_channel(name=ch.name, category=new_cat, overwrites=overwrites, bitrate=ch.bitrate, user_limit=ch.user_limit)
                    await asyncio.sleep(0.4)
            except Exception as e:
                self.log("HATA", f"Kategori hatası: {category.name} | {e}")

        # Kategorisiz kanallar
        for ch in source.channels:
            if ch.category is None:
                try:
                    overwrites = {self.role_map[r.id]: v for r, v in ch.overwrites.items() if r.id in self.role_map}
                    if isinstance(ch, discord.TextChannel):
                        await target.create_text_channel(name=ch.name, overwrites=overwrites)
                    elif isinstance(ch, discord.VoiceChannel):
                        await target.create_voice_channel(name=ch.name, overwrites=overwrites)
                    await asyncio.sleep(0.4)
                except: pass

    async def clone_emojis(self, source, target):
        self.log("BİLGİ", "Emojiler kopyalanıyor...")
        for emoji in source.emojis:
            try:
                img = await emoji.read()
                await target.create_custom_emoji(name=emoji.name, image=img)
                await asyncio.sleep(0.5)
            except: pass

    async def start_cloning(self, source, target):
        await self.clear_target(target)
        await self.clone_roles(source, target)
        await self.clone_channels(source, target)
        await self.clone_emojis(source, target)

def main():
    # Kullanıcı Ayarları
    TOKEN = "MTQ2ODk0MTA5ODk2ODY4MjU4OQ.Gw9kbE.8YVfoFdWuAKbUVpzOFvwPpgIqzi5FQE03cRtIA"
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.RED}{Style.BRIGHT}XLLOR KOPYALAMA ARACI{Style.RESET_ALL}")
    print("-" * 25)
    
    try:
        src_id = int(input(f"{Fore.CYAN}Kaynak Sunucu ID: {Style.RESET_ALL}"))
        dst_id = int(input(f"{Fore.CYAN}Hedef Sunucu ID: {Style.RESET_ALL}"))
    except ValueError:
        print(f"{Fore.RED}Geçersiz giriş. Lütfen sadece sayısal ID girin.")
        return

    cloner = XllorCloner(TOKEN, src_id, dst_id)
    try:
        cloner.run(TOKEN)
    except Exception as e:
        print(f"{Fore.RED}Çalışma Hatası: {e}")

if __name__ == "__main__":
    main()