import socket
from threading import Thread

clients = {}
addresses = {}

kotu_sozcukler=["amk", "mal"]



HOST = "0.0.0.0"
PORT = 23456
BUFFERSIZE = 1024
ADDR = (HOST, PORT)
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Sunucunun portu hızlıca geri almasını sağlar
SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER.bind(ADDR)

def gelen_mesaj():
    """Gelen mesajların kontrolünü sağlayan fonksiyon"""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s baglandı." %client_address)
        client.send(bytes("AbudikGubidik Sohbet Uygulaması!", "utf8"))
        addresses[client] = client_address
        Thread(target=baglan_client, args=(client,)).start()

def baglan_client(client):
    """Client bağlantısını yöneten güvenli fonksiyon"""
    isim = ""
    try:
        # 1. İsim alma ve küfür kontrolü
        isim_verisi = client.recv(BUFFERSIZE).decode("utf8").strip()
        
        # 'in' operatörü ile listenin içinde var mı diye bakıyoruz
        if isim_verisi.lower() in kotu_sozcukler:
            client.send(bytes("Uygunsuz isim!", "utf8"))
            client.close()
            return

        if not isim_verisi:
            client.close()
            return

        isim = isim_verisi
        # ... (hoşgeldin ve katıldı mesajları) ...
        clients[client] = isim

        while True:
            msg_bytes = client.recv(BUFFERSIZE)
            if not msg_bytes: break
            
            msg_str = msg_bytes.decode("utf8") # Karşılaştırma için string'e çevir
            
            # Mesajın içinde küfür geçiyor mu kontrolü
            kufur_var_mi = False
            for kelime in kotu_sozcukler:
                if kelime in msg_str.lower():
                    kufur_var_mi = True
                    break
            
            if kufur_var_mi:
                client.send(bytes("Sistem: Küfürlü mesaj gönderemezsin!", "utf8"))
                continue # Mesajı yayınlamadan döngünün başına dön
            
            if msg_str == "{cikis}":
                break
            
            yayin(msg_bytes, isim + ": ")
    # ... (finally ve except kısımları aynı kalabilir) ...
    except (ConnectionResetError, BrokenPipeError, OSError):
        print(f"Baglanti hatasi: {isim if isim else 'Bilinmeyen kullanici'} aniden ayrildi.")
    except Exception as e:
        print(f"Beklenmedik bir hata olustu: {e}")
    finally:
        # 3. Temizlik aşaması (Hata olsa da olmasa da çalışır)
        if client in clients:
            ayrilan_isim = clients[client]
            del clients[client]
            print(f"{ayrilan_isim} sistemden temizlendi.")
            # Diğerlerine ayrılma bilgisini gönder
            try:
                yayin(bytes(f"{ayrilan_isim} kanaldan cikis yapti.", "utf8"))
            except:
                pass
        
        client.close()

def yayin(msg, kisi=""):
    """Mesajı tüm istemcilere gönderir, kopanları listeden siler."""
    silinecekler = []
    # clients sözlüğünün kopyası üzerinde dönüyoruz ki döngü sırasında silme hatası almayalım
    for yayim in list(clients.keys()):
        try:
            yayim.send(bytes(kisi, "utf8") + msg)
        except (BrokenPipeError, ConnectionResetError, OSError):
            silinecekler.append(yayim)

    for kopuk_istemci in silinecekler:
        if kopuk_istemci in clients:
            isim = clients[kopuk_istemci]
            print(f"Bağlantı koptu, temizleniyor: {isim}")
            del clients[kopuk_istemci]
if __name__ == "__main__":
    SERVER.listen(10) # En fazla 10 bağlantıya izin verir!
    print("Baglanti bekleniyor...")
    ACCEPT_THREAD = Thread(target=gelen_mesaj)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
