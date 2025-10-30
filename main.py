from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time, random, sys

# === Ayarlar (isteğe bağlı değiştirebilirsin) ===
WAIT_FOR_LOGIN = 20      # QR kodla giriş için maksimum bekleme (saniye)
SELECTION_WAIT = 15      # Sohbeti açmak için kullanıcıya verilen süre (saniye)
TYPING_DELAY = 0.05      # Yazıyor modunda tuş başı bekleme (saniye)
PAUSE_BETWEEN = 2        # Yazıyor modunda döngüler arası bekleme (saniye)

def find_message_box(driver, timeout=10):
    wait = WebDriverWait(driver, timeout)
    possible_xpaths = [
        '//div[@contenteditable="true" and @data-tab and contains(@data-tab, "10")]',  # bazı sürümlerde data-tab=10
        '//div[@contenteditable="true" and @data-tab and contains(@data-tab, "1")]',   # alternatif
        '//div[@contenteditable="true" and @role="textbox"]',
        '//footer//div[@contenteditable="true"]'
    ]
    for xp in possible_xpaths:
        try:
            el = wait.until(EC.presence_of_element_located((By.XPATH, xp)))
            wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
            return el
        except Exception:
            continue
    return None

def main():
    print("Araç Seçin:")
    print("1 - Yazıyor modu (karşı tarafa yazıyor gibi gözükür)")
    print("2 - Spam modu (belirli mesajı belirli sayıda yollar)")
    mode = input("Seçiminiz (1/2): ").strip()

    if mode not in ["1", "2"]:
        print("Geçersiz seçim")
        return

    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://web.whatsapp.com/")

    print(f"QR kodla giriş bekleniyor")
    try:
        msg_box = find_message_box(driver, timeout=WAIT_FOR_LOGIN)
    except Exception:
        msg_box = None

    if not msg_box:
        print("Mesaj kutusu henüz görünmüyor. Lütfen QR ile giriş yapıp sohbeti açın.")
        print(f"{SELECTION_WAIT} saniye daha bekleniyor...")
        time.sleep(SELECTION_WAIT)
        msg_box = find_message_box(driver, timeout=10)

    if not msg_box:
        print("Mesaj kutusu bulunamadı! Lütfen sohbeti seçtiğinizden emin olun ve tekrar çalıştırın.")
        driver.quit()
        return

    print("Mesaj kutusu bulundu. (Sohbet penceresinin açtığından emin ol.)")

    if mode == "1":
        print("Yazıyor modu aktif. (Ctrl+C ile durdur)\n")
        try:
            while True:
                fake_text = ''.join(random.choice("qwertyuopğüasdfghjklşizxcvbnmöç ") for _ in range(random.randint(5, 12)))
                for char in fake_text:
                    msg_box.send_keys(char)
                    time.sleep(TYPING_DELAY)
                time.sleep(random.uniform(1.5, 3))
                for _ in range(len(fake_text)):
                    msg_box.send_keys(Keys.BACKSPACE)
                    time.sleep(TYPING_DELAY)
                time.sleep(PAUSE_BETWEEN)
        except KeyboardInterrupt:
            print("\nDurdu!")
        except Exception as e:
            print(f"Hata: {e}")
        finally:
            driver.quit()

    elif mode == "2":
        spam_text = input("Gönderilecek mesaj: ")
        try:
            spam_count = int(input("Kaç defa gönderilsin?: "))
        except ValueError:
            print("Geçersiz sayı!")
            driver.quit()
            return

        try:
            interval = float(input("Her mesaj arası kaç saniye beklesin? (örn: 0.5 veya 1.5) : ").strip())
            if interval < 0:
                raise ValueError
        except Exception:
            print("Geçersiz süre girdiniz. Varsayılan 1 saniye kullanılacak.")
            interval = 1.0

        print(f"{spam_count} mesaj gönderiliyor, her mesaj arası {interval} saniye... (Ctrl+C ile durdur)\n")
        try:
            for i in range(spam_count):
                msg_box.send_keys(spam_text)
                msg_box.send_keys(Keys.ENTER)
                print(f"[{i+1}/{spam_count}] gönderildi")
                jitter = random.uniform(-0.1, 0.1)
                wait_time = max(0, interval + jitter)
                time.sleep(wait_time)
        except KeyboardInterrupt:
            print("\nDurdu!")
        except Exception as e:
            print(f"Hata: {e}")
        finally:
            print("İşlem tamamlandı. Tarayıcı kapanıyor.")
            driver.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Beklenmedik hata:", e)
        try:
            sys.exit(1)
        except SystemExit:
            pass
