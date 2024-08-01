import requests

# API endpoint ve kimlik bilgileri
url = "https://api.vatansms.net/api/whatsapp/v1/login/phone"
client_id = ""
client_secret = ""

# Telefon numarası (örnek: +90xxxxxxxxxx)
phone_number = "+902129527243"

# İstek başlıkları
headers = {
    "client-id": client_id,
    "client-secret": client_secret
}

# İstek gövdesi
data = {
    "phone": phone_number
}

# POST isteği gönder
response = requests.post(url, headers=headers, json=data)

# Yanıtı kontrol et
if response.status_code == 200:
    json_response = response.json()
    print("API Yanıtı:", json_response)
    if json_response["code"] == 200 and "data" in json_response:
        verification_code = json_response["data"]["code"]
        reg_id = json_response["data"]["regId"]
        print(f"Doğrulama Kodu: {verification_code}")
        print(f"regId: {reg_id}")
        print("WhatsApp uygulamasında gelen kodu girin.")
    else:
        print("Giriş işlemi başarısız. Açıklama:", json_response.get("description", "Açıklama bulunamadı."))
else:
    print(f"HTTP Hatası: {response.status_code}. Açıklama: {response.text}")
