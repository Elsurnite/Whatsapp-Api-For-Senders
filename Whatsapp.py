import customtkinter as ctk
import tkinter.messagebox as messagebox
import requests
import uuid
import time
import threading
import queue

# API endpoint ve kimlik bilgileri
send_url = "https://api.vatansms.net/api/whatsapp/v1/messages/send"
client_id = ""
client_secret = ""
reg_id = ""

# Mesaj içeriği ve telefon numaraları
phone_numbers = []
message_content = ""

# Şifre (bu örnekte basit bir şifre, daha güvenli bir yöntem tercih edilebilir)
PASSWORD = ""

# Kuyruk oluşturma
result_queue = queue.Queue()

def show_alert(title, message):
    messagebox.showinfo(title, message)  # Tkinter ile uyarı göster

def authenticate():
    password = password_entry.get()
    if password == PASSWORD:
        login_window.withdraw()  # Giriş penceresini gizle
        root.deiconify()  # Ana pencereyi göster
    else:
        show_alert("Hata", "Geçersiz şifre. Lütfen tekrar deneyin.")

def show_login_window():
    global login_window, password_entry
    login_window = ctk.CTk()
    login_window.title("Giriş Ekranı")
    login_window.geometry("300x150")  # 300x150 piksel boyutunda pencere

    # Şifre giriş etiketi ve alanı
    label = ctk.CTkLabel(login_window, text="Şifre:")
    label.pack(pady=20)
    
    # Şifre girme
    password_entry = ctk.CTkEntry(login_window, show='*')
    password_entry.pack(pady=10, padx=20, fill='x')

    # Giriş butonu
    login_button = ctk.CTkButton(login_window, text="Giriş Yap", command=authenticate)
    login_button.pack(pady=10)

    login_window.mainloop()

def get_message_content():
    global message_content

    # Mesaj içeriğini almak için büyük bir pencere oluştur
    content_window = ctk.CTkToplevel(root)
    content_window.title("Mesaj İçeriği")
    content_window.geometry("500x500")  # 500x500 piksel boyutunda pencere

    # Mesaj içeriği için büyük bir TextBox
    message_textbox = ctk.CTkTextbox(content_window, height=400, width=450)
    message_textbox.pack(padx=10, pady=10)

    def on_submit():
        global message_content
        message_content = message_textbox.get("1.0", "end").strip()
        if message_content:
            content_window.destroy()
            # Mesaj gönderimini ayrı bir iş parçacığında başlat
            threading.Thread(target=send_messages_in_group, daemon=True).start()
        else:
            show_alert("Hata", "Mesaj içeriği girilmelidir.")

    # Gönder butonu
    submit_button = ctk.CTkButton(content_window, text="Gönder", command=on_submit)
    submit_button.pack(side="left", padx=10, pady=10)

    # Ön İzle butonu işlevsiz
    preview_button = ctk.CTkButton(content_window, text="Ön İzle (Aktif Değil)")
    preview_button.pack(side="right", padx=10, pady=10)

def generate_report_id():
    return str(uuid.uuid4())

def send_message(to_phone_number):
    headers = {
        "client-id": client_id,
        "client-secret": client_secret
    }
    
    data = {
        "reg_id": reg_id,
        "to": to_phone_number,
        "message": message_content,
        "send_speed": 1,
        "report_id": generate_report_id()
    }
    
    response = requests.post(send_url, headers=headers, json=data)
    
    if response.status_code == 200:
        json_response = response.json()
        if json_response["code"] == 200:
            return True
        else:
            return False
    else:
        return False

def send_messages_in_group():
    global phone_numbers
    sent_numbers = []
    failed_numbers = []

    for phone_number in phone_numbers:
        if phone_number.strip():  # Boş numaraları kontrol et
            success = send_message(phone_number)
            if success:
                sent_numbers.append(phone_number)
            else:
                failed_numbers.append(phone_number)
            time.sleep(3)  # 3 saniye arayla gönder

    sent_message = "Başarıyla gönderilen numaralar:\n" + "\n".join(sent_numbers) if sent_numbers else "Başarıyla gönderilen numara yok."
    failed_message = "Gönderilemeyen numaralar:\n" + "\n".join(failed_numbers) if failed_numbers else "Gönderilemeyen numara yok."

    result_queue.put((sent_message, failed_message))  # Sonuçları kuyruğa ekle

def process_results():
    try:
        sent_message, failed_message = result_queue.get_nowait()
        show_alert("Bilgi", f"{sent_message}\n\n{failed_message}")
    except queue.Empty:
        root.after(100, process_results)  # Kuyruğu tekrar kontrol et

def submit_phone_numbers():
    global phone_numbers
    phone_numbers = phone_numbers_text.get("1.0", "end").strip().split("\n")
    get_message_content()

# CustomTkinter ana pencere oluştur
def create_main_window():
    global root, phone_numbers_text
    ctk.set_appearance_mode("System")  # Görünüm modu: "System" (varsayılan), "Dark" veya "Light"
    ctk.set_default_color_theme("blue")  # Tema rengi: "blue" (varsayılan), "green", "dark-blue"

    global root
    root = ctk.CTk()
    root.title("WhatsApp Mesaj Gönderme")

    # Telefon numarası etiketi ve girişi
    phone_numbers_label = ctk.CTkLabel(root, text="StudyZone International Whatsapp Bulk Mesaj")
    phone_numbers_label.pack(padx=5, pady=5)
    phone_numbers_label2 = ctk.CTkLabel(root, text="Telefon Numaraları (bir satıra bir numara):")
    phone_numbers_label2.pack(padx=10, pady=5)

    phone_numbers_text = ctk.CTkTextbox(root, height=350, width=250)
    phone_numbers_text.pack(padx=10, pady=5)

    # Gönder ve Ön İzle butonları
    send_button = ctk.CTkButton(root, text="Mesaj Gönder", command=submit_phone_numbers)
    send_button.pack(side="left", padx=10, pady=10)

    root.withdraw()  # Ana pencereyi gizle

# Ana pencereyi oluştur
create_main_window()

# Uygulamanın giriş sayfasını oluştur
show_login_window()

# Kuyruğu kontrol et
root.after(100, process_results)

# Tkinter ana döngüsü
root.mainloop()
