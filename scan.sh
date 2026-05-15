#!/bin/bash

# Настройки
INPUT_FILE="ip_cidr"
ALIVE_FILE="alive.txt"
DEAD_FILE="dead.txt"
THREADS=50  # Оптимально для Termux, чтобы не получить Signal 9

# Очистка файлов перед работой
> "$ALIVE_FILE"
> "$DEAD_FILE"

echo "Запуск сканирования... Потоков: $THREADS"

# Python-скрипт генерирует IP по одному и передает в xargs
# Это экономит память, так как весь список не грузится в RAM
python3 -c "
import ipaddress, sys
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        for ip in ipaddress.IPv4Network(line, strict=False):
            print(ip)
    except:
        pass
" < "$INPUT_FILE" | xargs -P $THREADS -I {} sh -c "
    if ping -c 1 -W 1 {} > /dev/null 2>&1; then
        echo {} >> $ALIVE_FILE
        echo '[+] {} доступен'
    else
        # Опционально: записывать недоступные
        # echo {} >> $DEAD_FILE
        fi
"