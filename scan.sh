#!/bin/bash

# Устанавливаем количество параллельных процессов
THREADS=100

# Функция для конвертации CIDR в список IP и проверки
cat ip_cidr | python3 -c "
import ipaddress, sys
for line in sys.stdin:
    try:
        for ip in ipaddress.IPv4Network(line.strip(), strict=False):
            print(ip)
    except: pass
" | xargs -P $THREADS -n 1 sh -c 'ping -c 1 -W 1 $1 >/dev/null 2>&1 && echo $1' -- > alive.txt