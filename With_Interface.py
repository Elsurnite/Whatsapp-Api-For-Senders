import customtkinter as ctk
import requests
import uuid
import time
import threading
from tkinter import messagebox

# Airtable API bilgileri
base_id = ''
table_id = ''
view_name = ''
personal_access_token = ''
base_table_api_url = f'https://api.airtable.com/v0/{base_id}/{table_id}'
headers = {
    'Authorization': f'Bearer {personal_access_token}',
}

def send_data_to_airtable(sent_numbers):
    global selected_advisor, message_content

    # Airtable verisi hazırlama
    data = {
        "fields": {
            "Name": selected_advisor,
            "Notes": "\n".join(sent_numbers),
            "Message": message_content
        }
    }

    # API isteği gönderme
    response = requests.post(base_table_api_url, headers=headers, json=data)

    if response.status_code == 401:
        show_alert("Hata", f"Airtable'a veri gönderilemedi. Hata kodu: {response.status_code}, Mesaj: {response.text}")

# API endpoint ve kimlik bilgileri
send_url = "https://api.vatansms.net/api/whatsapp/v1/messages/send"
client_id = ""
client_secret = ""
reg_id = ""

# Danışman bilgilerini ve dahili numaraları saklayan sözlük
advisors_info = {
    'Elsurnite': '1',
    'ELS': '2',

    }

# Mesaj içeriği ve telefon numaraları
phone_numbers = []
message_content = ""
selected_advisor = ""

# Danışman listesi
advisors = list(advisors_info.keys())

def show_alert(title, message):
    messagebox.showinfo(title, message)

def show_preview_window():
    global message_content

    # Önizleme penceresi oluştur
    preview_window = ctk.CTkToplevel(root)
    preview_window.title("Mesaj Önizleme ve Düzenleme")
    preview_window.geometry("500x500")

    # Mesaj içeriği için TextBox
    preview_textbox = ctk.CTkTextbox(preview_window, height=400, width=450)
    preview_textbox.insert("1.0", message_content)  # Önceden belirlenmiş mesaj içeriğini ekle
    preview_textbox.pack(padx=10, pady=10)

    def on_send():
        global message_content
        message_content = preview_textbox.get("1.0", "end").strip()
        if message_content:
            preview_window.destroy()
            # Mesaj gönderimini başlat
            threading.Thread(target=send_messages_in_group, daemon=True).start()
        else:
            show_alert("Hata", "Mesaj içeriği girilmelidir.")

    # Gönder butonu
    send_button = ctk.CTkButton(preview_window, text="Gönder", command=on_send)
    send_button.pack(side="left", padx=10, pady=10)

    # İptal butonu
    cancel_button = ctk.CTkButton(preview_window, text="İptal", command=preview_window.destroy)
    cancel_button.pack(side="right", padx=10, pady=10)

def select_advisor_window():
    global selected_advisor

    # Danışman seçimi için yeni bir pencere oluştur
    advisor_window = ctk.CTkToplevel(root)
    advisor_window.title("Danışman Seçiniz")
    advisor_window.geometry("300x200")  

    # Danışman seçimi için etiket ve dropdown menü
    advisor_label = ctk.CTkLabel(advisor_window, text="Lütfen danışmanınızı seçiniz:")
    advisor_label.pack(padx=10, pady=10)

    advisor_window.lift()
    advisor_window.focus_force()
    advisor_window.grab_set()

    selected_advisor_var = ctk.StringVar(value=advisors[0])  # Varsayılan değer

    advisor_dropdown = ctk.CTkOptionMenu(advisor_window, values=advisors, variable=selected_advisor_var)
    advisor_dropdown.pack(padx=10, pady=10)

    def on_submit_advisor():
        global selected_advisor
        selected_advisor = selected_advisor_var.get()
        advisor_window.destroy()

        # Mesaj türü seçimi penceresini aç
        select_message_type_window()

    # Seçimi onayla butonu
    confirm_button = ctk.CTkButton(advisor_window, text="Seçimi Onayla", command=on_submit_advisor)
    confirm_button.pack(padx=10, pady=10)

def select_message_type_window():
    # Mesaj türü seçimi için yeni bir pencere oluştur
    type_window = ctk.CTkToplevel(root)
    type_window.title("Mesaj Türünü Seçiniz")
    type_window.geometry("300x200")  

    # Mesaj türü için etiket ve butonlar
    type_label = ctk.CTkLabel(type_window, text="Lütfen mesaj türünü seçiniz:")
    type_label.pack(padx=10, pady=10)

    def select_wat():
        create_message_content("WAT")
        type_window.destroy()
        show_preview_window()

    def select_ups():
        create_message_content("UPS")
        type_window.destroy()
        show_preview_window()

    def select_lang():
        create_message_content("LANG")
        type_window.destroy()
        show_preview_window()

    wat_button = ctk.CTkButton(type_window, text="WAT", command=select_wat)
    wat_button.pack(padx=10, pady=5)

    ups_button = ctk.CTkButton(type_window, text="UPS", command=select_ups)
    ups_button.pack(padx=10, pady=5)

    lang_button = ctk.CTkButton(type_window, text="LANG", command=select_lang)
    lang_button.pack(padx=10, pady=5)

def create_message_content(message_type):
    global message_content

    # Danışman bilgilerini al
    advisor_internal_number = advisors_info.get(selected_advisor, "Bilinmiyor")

    # Mesaj içeriğini oluştur
    if message_type == "WAT":
        message_content = (
            f"Merhaba, Ben {selected_advisor} XXX Yurtdışı Eğitim'den. "
            f"Work and Travel programı hakkında bilgi talebinizle ilgili aradım ama ulaşamadım. "
            f"Gün içinde tekrar arayacağım. Siz de bana hafta içi XXXXXX saatleri arasında "
            f"XXXXXXXXXXX numaralı telefondan, {advisor_internal_number} dahili üzerinden ulaşabilirsiniz. "
            f"Size yardımcı olmaktan mutluluk duyar, iyi günler dilerim!"
        )
    elif message_type == "UPS":
        message_content = (
            f"Merhaba, Ben {selected_advisor} XXXX Yurtdışı Eğitim'den. "
            f"Yurtdışı Üniversite Eğitimi hakkında bilgi talebinizle ilgili aradım ama ulaşamadım. "
            f"Gün içinde tekrar arayacağım. Siz de bana hafta içi XXXXXXXX saatleri arasında "
            f"XXXXXXXX numaralı telefondan, {advisor_internal_number} dahili üzerinden ulaşabilirsiniz. "
            f"Size yardımcı olmaktan mutluluk duyar, iyi günler dilerim!"
        )
    elif message_type == "LANG":
        message_content = (
            f"Merhaba, Ben {selected_advisor} XXXXXXX Yurtdışı Eğitim'den. "
            f"Yurtdışı Dil Okulları hakkında bilgi talebinizle ilgili aradım ama ulaşamadım. "
            f"Gün içinde tekrar arayacağım. Siz de bana hafta içi XXXXXXXX saatleri arasında "
            f"XXXXXXXX numaralı telefondan, {advisor_internal_number} dahili üzerinden ulaşabilirsiniz. "
            f"Size yardımcı olmaktan mutluluk duyar, iyi günler dilerim!"
        )

def generate_report_id():
    return str(uuid.uuid4())

def send_message(to_phone_number):
    if not to_phone_number:
        return False

    headers = {
        "client-id": client_id,
        "client-secret": client_secret
    }
    
    data = {
        "reg_id": reg_id,
        "to": to_phone_number,
        "message": message_content,
        "send_speed": 4,
        "report_id": generate_report_id()
    }
    
    try:
        response = requests.post(send_url, headers=headers, json=data)
        response.raise_for_status()  # Raise HTTPError for bad responses
        
        json_response = response.json()
        if json_response["code"] == 200:
            return True
        else:
            show_alert("Hata", f"Mesaj gönderilemedi: {json_response.get('message', 'Bilinmeyen hata')}")
            return False
    except requests.RequestException as e:
        show_alert("Hata", f"Mesaj gönderilemedi. Hata: {e}")
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

    show_alert("Bilgi", f"{sent_message}\n\n{failed_message}")
    send_data_to_airtable(sent_numbers)

def submit_phone_numbers():
    global phone_numbers
    phone_numbers = phone_numbers_text.get("1.0", "end").strip().split("\n")
    select_advisor_window()

# CustomTkinter ana pencere oluştur
ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue") 

root = ctk.CTk()
root.title("WhatsApp Mesaj Gönderme")

# Telefon numarası etiketi ve girişi
phone_numbers_label = ctk.CTkLabel(root, text="Whatsapp Bulk Mesaj")
phone_numbers_label.pack(padx=5, pady=5)
phone_numbers_label2 = ctk.CTkLabel(root, text="Telefon Numaraları (bir satıra bir numara):")
phone_numbers_label2.pack(padx=10, pady=5)

phone_numbers_text = ctk.CTkTextbox(root, height=350, width=250)
phone_numbers_text.pack(padx=10, pady=5)

# Gönder ve Ön İzle butonları
send_button = ctk.CTkButton(root, text="Mesaj Gönder", command=submit_phone_numbers)
send_button.pack(side="left", padx=10, pady=10)

# İşlevsiz Ön İzle butonu
preview_button = ctk.CTkButton(root, text="Ön İzle (İşlevsiz)")
preview_button.pack(side="right", padx=10, pady=10)

# Tkinter ana döngüsü
root.mainloop()
