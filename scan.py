import asyncio
import ipaddress

# --- НАСТРОЙКИ ---
INPUT_FILE = 'ip_cidr'
OUTPUT_FILE = 'alive.txt'
CONCURRENT_LIMIT = 50  # Количество одновременных проверок (начни с 50)
TIMEOUT = 1.0           # Таймаут в секундах
# -----------------

async def check_ip(ip, semaphore):
    """Проверяет IP с использованием системной команды ping, но асинхронно"""
    async with semaphore:
        ip_str = str(ip)
        # Асинхронный запуск процесса
        proc = await asyncio.create_subprocess_exec(
            'ping', '-c', '1', '-W', str(int(TIMEOUT)), ip_str,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc.wait()
        if proc.returncode == 0:
            return ip_str
    return None

async def main():
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
    
    try:
        with open(INPUT_FILE, 'r') as f, open(OUTPUT_FILE, 'a') as out_file:
            for line in f:
                line = line.strip()
                if not line: continue
                
                print(f"[*] Сканирую подсеть: {line}")
                try:
                    network = ipaddress.ip_network(line, strict=False)
                    tasks = []
                    
                    # Создаем задачи для всех IP в подсети
                    for ip in network:
                        tasks.append(check_ip(ip, semaphore))
                    
                    # Запускаем задачи и обрабатываем по мере готовности
                    for result in asyncio.as_completed(tasks):
                        ip_found = await result
                        if ip_found:
                            print(f"[+] {ip_found} доступен")
                            out_file.write(ip_found + '\n')
                            out_file.flush()
                            
                except Exception as e:
                    print(f"[!] Ошибка в {line}: {e}")
                    
    except FileNotFoundError:
        print(f"[-] Файл {INPUT_FILE} не найден")
    except KeyboardInterrupt:
        print("\n[!] Остановлено.")

if __name__ == "__main__":
    asyncio.run(main())