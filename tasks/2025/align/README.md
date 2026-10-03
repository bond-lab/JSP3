# Describe and document your code here
https://colab.research.google.com/drive/14EWXk92l_ec1UWjaHGB3BtOojpdt1uyr?usp=sharing

import os

def zpracovat_knihy(soubor_cz, soubor_en, soubor_vystup):
    # Kontrola, zda soubory existují
    if not os.path.exists(soubor_cz) or not os.path.exists(soubor_en):
        print("CHYBA: Nemohu najít vstupní soubory!")
        print(f"Ujistěte se, že ve složce máte soubory: '{soubor_cz}' a '{soubor_en}'")
        return

    print("Načítám soubory...")

    try:
        # Otevření souborů s kódováním utf-8 (důležité pro češtinu)
        with open(soubor_cz, 'r', encoding='utf-8') as f_cz, \
             open(soubor_en, 'r', encoding='utf-8') as f_en:
            
            # Načtení řádků a odstranění prázdných znaků kolem
            lines_cz = [line.strip() for line in f_cz if line.strip()]
            lines_en = [line.strip() for line in f_en if line.strip()]

        # Kontrola délky
        if len(lines_cz) != len(lines_en):
            print(f"\nPOZOR: Počet řádků nesedí!")
            print(f"CZ soubor má {len(lines_cz)} řádků.")
            print(f"EN soubor má {len(lines_en)} řádků.")
            print("Zpracování proběhne jen do konce kratšího souboru.\n")

        # Otevření výstupního souboru pro zápis
        with open(soubor_vystup, 'w', encoding='utf-8') as f_out:
            
            # Smyčka přes oba texty
            for i, (cz, en) in enumerate(zip(lines_cz, lines_en), start=1):
                # Sestavení bloku textu
                blok = (
                    f"[{i}]\n"
                    f"CZ: {cz}\n"
                    f"EN: {en}\n"
                    f"{'-' * 40}\n"
                )
                
                # 1. Výpis na obrazovku (konzole)
                print(blok, end='') 
                
                # 2. Zápis do souboru
                f_out.write(blok)

        print(f"\nHotovo! Výsledek byl uložen do souboru: '{soubor_vystup}'")

    except Exception as e:
        print(f"Došlo k neočekávané chybě: {e}")

# --- NASTAVENÍ SOUBORŮ ---
vstup_cesky = "kniha_cz.txt"
vstup_anglicky = "kniha_en.txt"
vystup = "vysledek.txt"

# --- SPUŠTĚNÍ ---
if _name_ == "_main_":
    zpracovat_knihy(vstup_cesky, vstup_anglicky, vystup)
