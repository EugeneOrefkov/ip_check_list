import subprocess
import ipaddress
import concurrent.futures
import time

# --- НАСТРОЙКИ ---
INPUT_FILE = 'ip_cidr'
OUTPUT_FILE = 'alive.txt'
THREADS = 100     # Сколько пингов идет одновременно
MAX_QUEUE = 500   # Сколько задач держать в очереди (чтобы не вылетал Signal 9)
TIMEOUT = "1"     # Секунда на ожидание ответа
# -----------------

def ping_ip(ip):
    ip_str = str(ip)
    try:
        # Прямой вызов системного пинга
        result = subprocess.run(
            ['ping', '-c', '1', '-W', TIMEOUT, ip_str],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            return ip_str
    except:
        pass
    return None

def main():
    print(f"[*] Старт. Потоков: {THREADS}, Лимит очереди: {MAX_QUEUE}")
    
    try:
        with open(OUTPUT_FILE, 'a') as out_file, open(INPUT_FILE, 'r') as f:
            # Создаем пул потоков
            with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    
                    print(f"[*] Обработка сети: {line}")
                    try:
                        network = ipaddress.ip_network(line, strict=False)
                        futures = set()
                        
                        for ip in network:
                            # Добавляем задачу в пул
                            futures.add(executor.submit(ping_ip, ip))
                            
                            # ГЛАВНОЕ: Если задач стало слишком много, ждем их завершения
                            # Это не дает памяти переполниться
                            if len(futures) >= MAX_QUEUE:
                                done, futures = concurrent.futures.wait(
                                    futures, return_when=concurrent.futures.FIRST_COMPLETED
                                )
                                for future in done:
                                    res = future.result()
                                    if res:
                                        print(f"[+] {res} жив")
                                        out_file.write(res + '\n')
                                        out_file.flush()

                        # Дочищаем оставшиеся задачи в подсети
                        for future in concurrent.futures.as_completed(futures):
                            res = future.result()
                            if res:
                                out_file.write(str(res) + '\n')
                                out_file.flush()
                                
                    except Exception as e:
                        print(f"[!] Ошибка в {line}: {e}")
                        
    except KeyboardInterrupt:
        print("\n[!] Остановлено.")

if __name__ == "__main__":
    main()