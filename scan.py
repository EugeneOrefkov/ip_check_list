import subprocess
import ipaddress
import concurrent.futures
from queue import Queue

# --- НАСТРОЙКИ ---
INPUT_FILE = 'ip_cidr'
OUTPUT_FILE = 'alive.txt'
THREADS = 100  # Количество одновременных пингов. Можно поднять до 200, если сеть тянет.
TIMEOUT = "1"  # Время ожидания ответа (в секундах)
# -----------------

def ping_ip(ip):
    ip_str = str(ip)
    try:
        # -c 1: один пакет
        # -W 1: ждать ответ ровно 1 секунду
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
    print(f"[*] Запуск сканирования. Потоков: {THREADS}")
    
    try:
        # Открываем файл на дозапись (append), чтобы данные не терялись
        with open(OUTPUT_FILE, 'a') as out_file:
            # Используем ThreadPoolExecutor для параллельных задач
            with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
                
                # Читаем подсети из файла
                with open(INPUT_FILE, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line: continue
                        
                        print(f"[*] Обработка сети: {line}")
                        try:
                            network = ipaddress.ip_network(line, strict=False)
                            
                            # Запускаем пинги для всех IP в текущей подсети
                            future_to_ip = {executor.submit(ping_ip, ip): ip for ip in network}
                            
                            for future in concurrent.futures.as_completed(future_to_ip):
                                result = future.result()
                                if result:
                                    print(f"[+] {result} доступен")
                                    out_file.write(result + '\n')
                                    out_file.flush() # Мгновенная запись на диск
                        
                        except Exception as e:
                            print(f"[!] Ошибка в подсети {line}: {e}")
                            
    except FileNotFoundError:
        print(f"[-] Файл {INPUT_FILE} не найден")
    except KeyboardInterrupt:
        print("\n[!] Сканирование остановлено пользователем.")

if __name__ == "__main__":
    main()