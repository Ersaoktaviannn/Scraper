from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException, StaleElementReferenceException

import time
import csv
import os
import getpass
import pyautogui
import shutil

def setup_driver():
    """Setup WebDriver dengan konfigurasi yang tepat"""
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Tetapkan preferensi download
    prefs = {
        "download.default_directory": os.path.abspath("./downloads"),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    
    # Uncomment baris berikut jika ingin melihat browser
    # options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver

def login(driver, username, password):
    """Login ke portal Telkom"""
    print("🔐 Mencoba login ke portal Telkom...")
    
    try:
        # Buka halaman login
        driver.get("https://newgobeyond.mytens.co.id/login")
        time.sleep(3)  # Tunggu halaman dimuat
        
        # Periksa apakah halaman login sudah terbuka
        if "login" not in driver.current_url.lower():
            print("⚠️ Tidak diarahkan ke halaman login")
            return False
        
        # Tangkap screenshot halaman login
        driver.save_screenshot("login_page.png")
        print("📷 Screenshot halaman login disimpan")
        
        # Cari dan isi field username/email
        try:
            username_field = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'], input[type='email'], input[name='username'], input[name='email']"))
            ) 
            username_field.clear()
            username_field.send_keys(username)
            print("✅ Mengisi username")
        except Exception as e:
            print(f"❌ Error saat mengisi username: {str(e)}")
            return False
        
        # Cari dan isi field password
        try:
            password_field = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']"))
            ) 
            password_field.clear()
            password_field.send_keys(password)
            print("✅ Mengisi password")
        except Exception as e:
            print(f"❌ Error saat mengisi password: {str(e)}")
            return False
        
        # Cari dan klik checkbox Syarat dan Ketentuan & Kebijakan Privasi
        try:
            checkbox_selectors = [
                "//input[@type='checkbox']",
                "//label[contains(text(), 'Syarat dan Ketentuan') or contains(text(), 'Kebijakan Privasi')]//preceding::input[@type='checkbox'][1]",
                "//label[contains(., 'Syarat dan Ketentuan') or contains(., 'Kebijakan Privasi')]//input[@type='checkbox']",
                "//div[contains(@class, 'checkbox') or contains(@class, 'form-check')]//input",
                "//span[contains(text(), 'Saya menyetujui')]/preceding::input[@type='checkbox'][1]",
                "//span[contains(text(), 'Saya menyetujui')]/parent::*/preceding::input[@type='checkbox'][1]"
            ]
            
            checkbox_found = False
            for selector in checkbox_selectors:
                checkboxes = driver.find_elements(By.XPATH, selector)
                if checkboxes:
                    for checkbox in checkboxes:
                        try:
                            if not checkbox.is_selected():
                                checkbox.click()
                                checkbox_found = True
                                print("✅ Klik checkbox Syarat dan Ketentuan & Kebijakan Privasi")
                                break
                        except:
                            try:
                                driver.execute_script("arguments[0].click();", checkbox)
                                checkbox_found = True
                                print("✅ Klik checkbox dengan JavaScript")
                                break
                            except:
                                continue
                if checkbox_found:
                    break
            
            if not checkbox_found:
                label_selectors = [
                    "//label[contains(text(), 'Syarat dan Ketentuan') or contains(text(), 'Kebijakan Privasi')]",
                    "//span[contains(text(), 'Saya menyetujui')]",
                    "//div[contains(text(), 'Saya menyetujui')]",
                    "//p[contains(text(), 'Saya menyetujui')]"
                ]
                
                for selector in label_selectors:
                    labels = driver.find_elements(By.XPATH, selector)
                    if labels:
                        for label in labels:
                            try:
                                label.click()
                                checkbox_found = True
                                print("✅ Klik label Syarat dan Ketentuan & Kebijakan Privasi")
                                break
                            except:
                                try:
                                    driver.execute_script("arguments[0].click();", label)
                                    checkbox_found = True
                                    print("✅ Klik label dengan JavaScript")
                                    break
                                except:
                                    continue
                    if checkbox_found:
                        break
            
            if not checkbox_found:
                print("⚠️ Tidak dapat menemukan atau klik checkbox Syarat dan Ketentuan")
        except Exception as e:
            print(f"⚠️ Error saat mencoba klik checkbox: {str(e)}")
        
        # Klik tombol login
        time.sleep(10) 
        login_buttons = driver.find_elements(By.XPATH, 
            "//button[contains(text(), 'Login') or contains(text(), 'Sign in') or contains(text(), 'Masuk')]")
        
        if not login_buttons:
            login_buttons = driver.find_elements(By.CSS_SELECTOR, 
                "button[type='submit'], input[type='submit']")
        
        if login_buttons:
            login_buttons[0].click()
            print("✅ Klik tombol login")
        else:
            print("❌ Tidak dapat menemukan tombol login")
            return False
        
        # Tunggu proses login selesai
        time.sleep(10) 
        
        # Periksa apakah login berhasil
        if "login" in driver.current_url.lower():
            print("❌ Login gagal - masih di halaman login")
            driver.save_screenshot("login_failed.png")
            return False
        
        print("✅ Login berhasil")
        driver.save_screenshot("after_login.png")
        return True
        
    except Exception as e:
        print(f"❌ Error saat login: {str(e)}")
        driver.save_screenshot("login_error.png")
        return False

def navigate_to_dashboard(driver):
    print("🔄 Navigasi ke halaman dashboard Rising Star...")
    
    try:
        driver.get("https://newgobeyond.mytens.co.id/dashboard-rising-star?tab=bintang-1")
        time.sleep(5)
        driver.save_screenshot("dashboard_page.png")
        
        if "dashboard-rising-star" in driver.current_url.lower():
            print("✅ Berhasil navigasi ke halaman dashboard")
            return True
        else:
            print("❌ Gagal navigasi ke halaman dashboard")
            return False
            
    except Exception as e:
        print(f"❌ Error saat navigasi: {str(e)}")
        return False

def scroll_and_download(driver, current_tab="", time_sleep01=5, time_sleep02=10):
    print(f"🔄 Melakukan load list tabel...")
    
    # Ambil nomor bintang dari tab saat ini
    star_number = ""
    if current_tab:
        # Ekstrak angka bintang dari teks tab (misalnya "Bintang 1" -> "1")
        try:
            star_number = ''.join(filter(str.isdigit, current_tab))
            print(f"⭐ Tab saat ini: {current_tab}, Nomor Bintang: {star_number}")
        except Exception as e:
            print(f"⚠️ Tidak dapat mengekstrak nomor bintang: {str(e)}")
            star_number = ""

    # Switch ke iframe section
    try:
        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe"))
        )
        driver.switch_to.frame(iframe)
    except Exception as e:
        print(f"❌ Error saat mencari iframe: {str(e)}")
        return 0

    # Add action 
    actions = ActionChains(driver)
    successful_download_count = 0
    download_dir = os.path.abspath("./downloads")

    try:
        # Temukan semua tabel
        link_items = [
            (link, link.text.strip())
            for link in driver.find_elements(By.XPATH, "//div[@class='header-title']//a")
            if link.text.strip()
        ]
        print(f"🔍 Ditemukan {len(link_items)} tabel")
        print(f"✅ List tabel telah ditemukan")
        print(f"🔄 Melakukan scrolling ke masing-masing tabel...")

        # Loop untuk scroll ke masing-masing parent div dari <a>
        for link, table_name in link_items:
            try:
                # Naik ke parent div terdekat (bisa diatur lebih tinggi jika perlu)
                container_div = link.find_element(By.XPATH, "./ancestor::div[9]")

                # Scroll ke container div
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", container_div)
    
                print(f"✅ Scrolled ke tabel: {table_name}")
                time.sleep(time_sleep01)

                # Membuat nama file yang bersih dan format sesuai permintaan
                clean_table_name = table_name.replace(" ", "_").replace("/", "_").replace("\\", "_").replace(":", "_")
                custom_filename = f"B{star_number}_{clean_table_name}.csv"
                target_file_path = os.path.join(download_dir, custom_filename)
                
                # Mencari dan klik kebab menu (ant-dropdown-trigger)
                trigger = container_div.find_element(By.CLASS_NAME, "ant-dropdown-trigger")
                actions.move_to_element(trigger).click().perform()
                print(f"☰ Klik kebab menu: {table_name}")
                time.sleep(time_sleep01)
                
                try:
                    # Mengambil semua menu ant-dropdown-menu, pilih yang paling akhir (yang baru)
                    download_menus = WebDriverWait(driver, time_sleep02).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ant-dropdown-menu"))
                    )

                    latest_download = download_menus[-1]

                    # Mencari item "Download" di dalam menu terbaru
                    download_item = latest_download.find_element(By.XPATH, ".//li[contains(., 'Download')]")

                    # Hover ke item "Download"
                    actions.move_to_element(download_item).perform()
                    print("✅ Hover ke Download berhasil")

                    time.sleep(time_sleep02)

                    # Ambil semua menu lagi, cari yang terbaru (submenu muncul belakangan)
                    menus = driver.find_elements(By.CSS_SELECTOR, ".ant-dropdown-menu")
                    latest_submenu = menus[-1]

                    # Klik export
                    export_item = latest_submenu.find_element(By.XPATH, ".//li[contains(., 'Export to .CSV')]")
    
                    driver.execute_script("arguments[0].click();", export_item)
                    print("📥 Klik Export berhasil")
                    
                    # Tunggu hingga file terdownload
                    time.sleep(10)
                    
                    # Cari file yang baru didownload (paling baru berdasarkan waktu pembuatan)
                    try:
                        # Cari file CSV yang baru saja diunduh (biasanya dimulai dengan tanggal)
                        all_files = [f for f in os.listdir(download_dir) if f.endswith('.csv')]
                        if all_files:
                            newest_file = max([os.path.join(download_dir, f) for f in all_files], key=os.path.getctime)
                            
                            # Rename file ke nama yang diinginkan (overwrite jika sudah ada)
                            if os.path.exists(target_file_path):
                                os.remove(target_file_path)
                                print(f"🔄 Overwrite file yang sudah ada: {custom_filename}")
                            
                            shutil.move(newest_file, target_file_path)
                            print(f"✅ File berhasil diunduh dan disimpan sebagai: {custom_filename}")
                            successful_download_count += 1
                        else:
                            print("⚠️ Tidak ada file CSV ditemukan di direktori download")
                    except Exception as e:
                        print(f"❌ Gagal mengganti nama file: {str(e)}")
                    
                except Exception as e:
                    print(f"❌ Proses ekstraksi data gagal: {str(e)}")
                
            except Exception as e:
                print(f"⚠️ Gagal scroll ke tabel: {table_name} | Error: {e}")
        
        # Switch back to default content
        driver.switch_to.default_content()
        return successful_download_count

    except Exception as e:
        print(f"⚠️ Error pada proses scroll dan download: {str(e)}")
        # Switch back to default content
        driver.switch_to.default_content()
        return 0

def navigate_to_other_tab(driver):
    """Navigasi ke semua tab Bintang dan download data dari masing-masing tab"""
    print("🔄 Mencari dan menavigasi ke semua tab Bintang...")
    total_downloads = 0
    
    try:
        # Tunggu hingga halaman dimuat sepenuhnya
        time.sleep(10)
        
        # Cari semua tab button yang berisi teks "Bintang"
        tab_buttons = driver.find_elements(By.XPATH, "//button[div[contains(text(), 'Bintang')]]")
        
        print(f"🔍 Ditemukan {len(tab_buttons)} tab Bintang")
        
        # Loop melalui semua tab Bintang
        for i, btn in enumerate(tab_buttons):
            try:
                # Ambil teks tab
                tab_text = btn.text.strip()
                print(f"🌟 Clicking tab: {tab_text}")
                
                # Scroll ke element tab untuk memastikan terlihat
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(2)
                
                # Tangkap screenshot sebelum klik
                driver.save_screenshot(f"before_click_tab_{i+1}.png")
                
                # Klik tab
                driver.execute_script("arguments[0].click();", btn)
                
                # Tunggu konten dimuat
                print(f"⏳ Menunggu konten tab {tab_text} dimuat (10 detik)...")
                time.sleep(10)
                
                # Tangkap screenshot setelah klik
                driver.save_screenshot(f"after_click_tab_{i+1}.png")
                
                # Jalankan fungsi scroll dan download untuk tab ini
                print(f"🔄 Memulai proses download untuk tab {tab_text}...")
                downloads = scroll_and_download(driver, tab_text)
                total_downloads += downloads
                
                print(f"✅ Selesai memproses tab {tab_text}. Berhasil download {downloads} file.")
                
            except Exception as e:
                print(f"❌ Gagal mengklik tab ke-{i+1}: {str(e)}")
        
        return total_downloads
        
    except Exception as e:
        print(f"❌ Error saat navigasi ke tab Bintang: {str(e)}")
        driver.save_screenshot("tab_navigation_error.png")
        return 0

def main():
    """Improved main function with direct flow from login to extraction without reloading dashboard"""
    driver = None
    
    try:
        driver = setup_driver()
        username = "isi_dengan_username_anda"  # Ganti dengan username Anda
        password = "isi_dengan_password_anda"  # Ganti dengan password Anda
        
        # Persiapkan direktori download
        download_dir = os.path.abspath("./downloads")
        os.makedirs(download_dir, exist_ok=True)
        
        # 1. Login
        if not login(driver, username, password):
            print("❌ Login gagal pada percobaan awal")
            return
        
        # 2. Navigasi ke dashboard hanya sekali
        if not navigate_to_dashboard(driver):
            print("❌ Gagal navigasi ke dashboard")
            return
        
        print("⏳ Menunggu halaman dashboard dimuat sepenuhnya (10 detik)...")
        time.sleep(10)
        
        # 3. Navigasi ke semua tab Bintang dan download data
        print("🔄 Memulai proses navigasi tab dan ekstraksi data...")
        total_downloads = navigate_to_other_tab(driver)
        
        # Dapatkan semua file CSV dengan format B{x}_*
        csv_files = [f for f in os.listdir(download_dir) if f.endswith('.csv') and f[0] == 'B' and f[1].isdigit()]
        
        print("\n===== HASIL PENGAMBILAN DATA =====")
        print(f"📊 Total file CSV: {len(csv_files)}")
        print(f"📊 Total CSV yang baru saja terdownload: {total_downloads}")
        
        # Tampilkan daftar file yang telah diunduh
        print("\n📋 Daftar file CSV yang diunduh:")
        for i, file in enumerate(csv_files):
            print(f"  {i+1}. {file}")
        
    except Exception as e:
        print(f"❌ Error dalam fungsi main: {str(e)}")
        if driver:
            driver.save_screenshot("main_error.png")
    finally:
        if driver:
            print("🔚 Menutup browser")
            driver.quit()

if __name__ == "__main__":
    main()
