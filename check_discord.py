import discord
import os
print(f"Discord Path: {discord.__file__}")
try:
    print(f"Discord Version: {discord.__version__}")
except:
    print("Version not found")
print(f"Intents available: {hasattr(discord, 'Intents')}")
