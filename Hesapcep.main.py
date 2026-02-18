import flet as ft
import pandas as pd
import os
import json
import datetime
import re

# --- AYARLAR VE VERİTABANI ---
class FinansalEkosistem:
    def __init__(self):
        self.db_name = "hesapcep_v23.csv"
        self._baslat()

    def _baslat(self):
        # Veritabanı yoksa oluştur
        if not os.path.exists(self.db_name):
            cols = ['ID', 'Tarih', 'Musteri', 'Islem', 'Miktar', 'Bakiye', 'Ref']
            pd.DataFrame(columns=cols).to_csv(self.db_name, index=False, encoding='utf-8-sig')

# --- ANA UYGULAMA ---
def main(page: ft.Page):
    eko = FinansalEkosistem()
    
    # Sayfa Ayarları
    page.title = "HesapCep V23"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # Bileşenler
    bakiye_metni = ft.Text("0.00 TL", size=40, weight="bold", color="green")
    islem_listesi = ft.ListView(expand=True, spacing=10, height=400)
    
    bilgi_mesaji = ft.SnackBar(ft.Text("İşlem Tamam!"))

    # Verileri Güncelleme Fonksiyonu
    def verileri_yukle():
        if os.path.exists(eko.db_name):
            df = pd.read_csv(eko.db_name, encoding='utf-8-sig')
            if not df.empty:
                # Toplam Bakiye
                son_durum = df.groupby('Musteri')['Bakiye'].last()
                toplam = son_durum.sum()
                bakiye_metni.value = f"{toplam:,.2f} TL"
                
                # Listeyi Temizle ve Doldur
                islem_listesi.controls.clear()
                for _, satir in df.iloc[::-1].iterrows():
                    kart = ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.PERSON, color="cyan"),
                            ft.Column([
                                ft.Text(str(satir['Musteri']), weight="bold"),
                                ft.Text(str(satir['Tarih']), size=12, color="grey")
                            ], expand=True),
                            ft.Text(f"{satir['Miktar']} TL", weight="bold", color="green" if satir['Islem'] == "Alındı" else "red")
                        ]),
                        padding=15,
                        bgcolor="#1f1f1f",
                        border_radius=10
                    )
                    islem_listesi.controls.append(kart)
                page.update()

    # Yeni İşlem Ekleme Fonksiyonu
    def islem_ekle(e):
        komut = giris_kutusu.value.lower()
        try:
            # Metinden sayıyı bul
            miktar_bul = re.search(r"(\d+)", komut)
            if miktar_bul:
                miktar = float(miktar_bul.group(1))
                isim = komut.split(str(int(miktar)))[0].strip().title()
                tip = "Verildi" if "verdim" in komut else "Alındı"
                
                # Veritabanını oku ve güncelle
                df = pd.read_csv(eko.db_name, encoding='utf-8-sig')
                
                # Eski bakiyeyi bul
                eski_bakiye = 0
                if not df.empty and isim in df['Musteri'].values:
                    kisi_verisi = df[df['Musteri'] == isim]
                    if not kisi_verisi.empty:
                        eski_bakiye = kisi_verisi.iloc[-1]['Bakiye']
                
                yeni_bakiye = eski_bakiye + miktar if tip == "Verildi" else eski_bakiye - miktar
                
                yeni_satir = {
                    'ID': len(df) + 1,
                    'Tarih': datetime.datetime.now().strftime("%d.%m.%Y"),
                    'Musteri': isim,
                    'Islem': tip,
                    'Miktar': miktar,
                    'Bakiye': yeni_bakiye,
                    'Ref': "MOBIL"
                }
                
                df = pd.concat([df, pd.DataFrame([yeni_satir])], ignore_index=True)
                df.to_csv(eko.db_name, index=False, encoding='utf-8-sig')
                
                # Ekranı temizle
                giris_kutusu.value = ""
                page.show_snack_bar(bilgi_mesaji)
                verileri_yukle()
        except Exception as hata:
            print(f"Hata: {hata}")

    # Giriş Kutusu
    giris_kutusu = ft.TextField(
        hint_text="Örnek: Ahmet 500 verdim", 
        expand=True, 
        on_submit=islem_ekle,
        border_color="cyan"
    )

    # Admin Giriş Ekranı
    def giris_yap(e):
        if k_adi.value == "kaesuca" and sifre.value == "abalkan9":
            page.clean()
            page.add(
                ft.Column([
                    ft.Text("HESAPCEP PORTFÖY", size=20, weight="bold", color="grey"),
                    bakiye_metni,
                    ft.Divider(),
                    ft.Row([giris_kutusu, ft.IconButton(ft.icons.SEND, on_click=islem_ekle, icon_color="cyan")]),
                    ft.Text("Son İşlemler", size=16, weight="bold"),
                    islem_listesi
                ])
            )
            verileri_yukle()
        else:
            k_adi.error_text = "Hatalı Giriş"
            page.update()

    k_adi = ft.TextField(label="Kullanıcı Adı")
    sifre = ft.TextField(label="Şifre", password=True)
    
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.LOCK, size=80, color="green"),
                ft.Text("GÜVENLİ GİRİŞ", size=24, weight="bold"),
                k_adi,
                sifre,
                ft.ElevatedButton("Sistemi Aç", on_click=giris_yap, bgcolor="green", color="white")
            ], horizontal_alignment="center", spacing=20),
            alignment=ft.alignment.center,
            expand=True
        )
    )

if __name__ == "__main__":
    import flet as ft
    ft.app(target=main)
