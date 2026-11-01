# YazarPress

YazarPress, WordPress sitelerinde yazı ve sayfa yayınlamak için Python ile
yazılmış bir masaüstü uygulamasıdır. Arayüz GTK 3 kullanır; klavye gezinmesi ve
ekran okuyucularla çalışacak şekilde etiketlenmiştir.

## Gereksinimler

- Python 3
- GTK 3 ve PyGObject Python bağlamaları
- REST API'si etkin bir WordPress sitesi
- Yayınlama yetkisi olan bir hesap için WordPress uygulama parolası

Raspberry Pi OS üzerinde GTK 3 Python bağlamalarını şu komutla yükleyin:

```sh
sudo apt install python3-gi gir1.2-gtk-3.0
```

Uygulamayı depo dizininden başlatın:

```sh
python3 yazarpress.py
```

Site adresini, WordPress kullanıcı adını ve uygulama parolasını girin; ardından
yazı veya sayfa yayınlamayı seçin. Başlık ve içerik doğrudan yayınlanır.
Kimlik bilgileri yalnızca istek sırasında kullanılır ve kaydedilmez. Ağ
üzerinden bağlanırken HTTPS kullanın. Form alanları etiketlidir; alanlar arasında
Sekme tuşuyla gezebilir, düğmelere kısayol olarak Alt ve etiket harfini
kullanabilir, ekran okuyucu desteğinden yararlanabilirsiniz.

WordPress istemcisi testlerini çalıştırın:

```sh
python3 -m unittest discover -s tests
```
