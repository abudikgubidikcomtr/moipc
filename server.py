import socket
from threading import Thread

clients = {}
addresses = {}

# Küfür filtresi listesi
kotu_sozcukler = ["amk", "mal", "amq", "aq", "sik", "skm", "sikim", "sikeyim", "sikeim", "orospu", "oç", "orspu", "orusbu", "orsbu", "hassiktir", "hassktr", "hasktr", "hasktir"]

HOST = "0.0.0.0"
PORT = 23456
BUFFERSIZE = 1024
ADDR = (HOST, PORT)
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER.bind(ADDR)

def gelen_mesaj():
    """Gelen bağlantıları kabul eden ana döngü"""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s bağlandı." % client_address)
        # Bağlanan kişiye ilk karşılama mesajını gönderiyoruz
        client.send(bytes("AbudikGubidik Sohbet Uygulamasına Hoş Geldiniz!\nLütfen isminizi giriniz:", "utf8"))
        addresses[client] = client_address
        Thread(target=baglan_client, args=(client,)).start()

def baglan_client(client):
    """Her bir istemci (client) için çalışan fonksiyon"""
    isim = ""
    try:
        # 1. İsim alma ve küfür kontrolü
        isim_verisi = client.recv(BUFFERSIZE).decode("utf8").strip()
        
        if isim_verisi.lower() in kotu_sozcukler:
            client.send(bytes("UYARI: Uygunsuz isim! Bağlantınız kesiliyor.", "utf8"))
            client.close()
            return

        if not isim_verisi:
            client.close()
            return

        isim = isim_verisi
        clients[client] = isim

        # --- EKSİK KISIMLAR: Hoş geldin ve Katıldı Mesajları ---
        client.send(bytes(f"Merhaba {isim}! Çıkmak için '{{cikis}}' yazabilirsin.", "utf8"))
        yayin(bytes(f"{isim} sohbete katıldı!", "utf8"))
        # -----------------------------------------------------

        while True:
            msg_bytes = client.recv(BUFFERSIZE)
            if not msg_bytes:
                break
            
            msg_str = msg_bytes.decode("utf8")
            
            # Küfür kontrolü
            kufur_var_mi = any(kelime in msg_str.lower() for kelime in kotu_sozcukler)
            
            if kufur_var_mi:
                client.send(bytes("Sistem: Küfürlü mesaj gönderemezsin!", "utf8"))
                continue 
            
            if msg_str == "{cikis}":
                client.send(bytes("{cikis}", "utf8")) # İstemciye çıkış onayı
                break
            
            # Mesajı yayınla
            yayin(msg_bytes, prefix=isim + ": ")

    except (ConnectionResetError, BrokenPipeError, OSError):
        print(f"Bağlantı hatası: {isim if isim else 'Bilinmeyen kullanıcı'} aniden ayrıldı.")
    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {e}")
    finally:
        # Temizlik aşaması
        if client in clients:
            ayrilan_isim = clients[client]
            del clients[client]
            print(f"{ayrilan_isim} sistemden temizlendi.")
            try:
                yayin(bytes(f"{ayrilan_isim} kanaldan ayrıldı.", "utf8"))
            except:
                pass
        client.close()

def yayin(msg, prefix=""):
    """Mesajı tüm istemcilere gönderir"""
    for sock in list(clients.keys()):
        try:
            sock.send(bytes(prefix, "utf8") + msg)
        except:
            # Hatalı soketleri burada silmek yerine, kendi döngülerinde kapanmalarını beklemek daha güvenlidir
            pass

if __name__ == "__main__":
    SERVER.listen(10)
    print(f"Sunucu {PORT} portunda başlatıldı. Bağlantı bekleniyor...")
    ACCEPT_THREAD = Thread(target=gelen_mesaj)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
