#!/bin/bash#!/bin/bash

INPUT_FILE="ip_cidr"
ALIVE_FILE="alive.txt"
THREADS=50

# Очищаем файл перед запуском
> "$ALIVE_FILE"

echo "Запуск сканирования... Использую $THREADS потоков."

# Используем python для генерации IP и xargs для запуска ping
python3 -c "
import ipaddress, sys
for line in sys.stdin:
    s = line.strip()
    if s:
        try:
            for ip in ipaddress.IPv4Network(s, strict=False):
                print(ip)
        except:
            pass
" < "$INPUT_FILE" | xargs -P $THREADS -I {} sh -c "ping -c 1 -W 1 {} > /dev/null 2>&1 && (echo {}; echo '[+] {} alive')" >> "$ALIVE_FILE"