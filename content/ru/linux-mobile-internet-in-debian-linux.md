Title: Как настроить подключение к интернет через мобильный телефон в Debian
Date: 2010-11-26 20:02
Author: Admin
Category: Linux
Tags: debian, Linux, wvdial
Lang: ru

В этой статье я расскажу как использовать ваш мобильный телефон в
качестве 3G/GPRS/EDGE модема в ОС Linux.

В качестве тестового примера использовались ПК с установленной Debian
5.0 «Lenny» и мобильный телефон Nokia N96 соединённые между собой usb
кабелем.

1.  Устанавливаем соединение компьютера с телефоном.Подключаем телефон к
    компьютеру через usb кабель. В появившемся на экране телефона меню
    выбираем режим PC Suite.

    Посмотрим как на это отреагировала ОС. Для этого введём в консоль:

        :::bash
        cat /var/log/messages

    Видим следующий вывод:

        :::text
        Aug  1 08:30:43 DizballanzePC kernel: [  200.535814] usb 8-1: new high speed USB device using ehci_hcd and address 3
        Aug  1 08:30:43 DizballanzePC kernel: [  200.673679] usb 8-1: configuration #1 chosen from 1 choice
        Aug  1 08:30:43 DizballanzePC kernel: [  200.678985] usb 8-1: New USB device found, idVendor=0421, idProduct=003a
        Aug  1 08:30:43 DizballanzePC kernel: [  200.678989] usb 8-1: New USB device strings: Mfr=1, Product=2, SerialNumber=3
        Aug  1 08:30:43 DizballanzePC kernel: [  200.678991] usb 8-1: Product: Nokia N96
        Aug  1 08:30:43 DizballanzePC kernel: [  200.678993] usb 8-1: Manufacturer: Nokia
        Aug  1 08:30:43 DizballanzePC kernel: [  200.678995] usb 8-1: SerialNumber: 356406026032671
        Aug  1 08:30:43 DizballanzePC kernel: [  200.860753] cdc_acm 8-1:1.1: ttyACM0: USB ACM device

    Как вы видите новое устройство определено ОС и доступно по адресу
    `/dev/ttyACM0`.

    Теперь мы знаем что соединение успешно установлено.

2.  Настраиваем параметры модема. Для дозвона мы будем использовать
    программу wvdial. Нужно убедится что она установлена в вашей
    системе. Для этого выполните следующую команду в консоль:

        :::bash
        whereis wvdial

    Если команда сообщит вам месторасположение файлов программы, значит
    она уже установлена в вашей системе. Вот что выводит команда whereis
    на моём компьютере:

        :::text
        wvdial: /usr/bin/wvdial /etc/wvdial.conf /etc/wvdial.conf~ /usr/share/man/man1/wvdial.1.gz

    В случае если программа не установлена в вашей системе необходимо
    установить её самостоятельно. Для этого введите в консоль следующее:

        :::bash
        apt-get install wvdial

    И программа установщик выполнит все необходимые действия.

    Теперь переходим непосредственно к настройке модема.

    Для этого открываем файл `/etc/wvdial.conf` в любом текстовом
    редакторе, предварительно войдя в систему как пользователь root.

    Вам необходимо удалить следующие строки кода:

        :::text
        Modem Type = USB ModemModem = /dev/ttyACM0

    А также вам необходимо добавить следующие строки в конец файла:

        :::text
        New PPPD = yes
        Phone = *99***1#
        Username = MOVISTAR
        Password = MOVISTAR
        Init6= AT+CGDCONT=1,"IP","acces.point"

        [Dialer usb-scb]
        Modem Type = USB Modem
        Modem = /dev/ttyACM0

        [Dialer blz-scb]
        Modem = /dev/rfcomm0

    Вместо acces.point введите имя точки доступа вашего оператора
    сотовой связи.

    Все необходимые настройки выполнены, теперь можно приступать
    непосредственно к соединению.

3.  Подключение к Интернет. Для того чтобы подключится к Интернет вам
    необходимо просто соединить кабелем компьютер и телефон, а потом
    написать от пользователя root:

        :::bash
        wvdial usb-scb&﻿