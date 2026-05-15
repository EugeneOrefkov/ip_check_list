import subprocess
import ipaddress
import random
import concurrent.futures
import time

# --- НАСТРОЙКИ (как в твоем скрипте) ---
INPUT_FILE = 'ip_cidr'
OUTPUT_FILE = 'alive_subnets.txt'
NUM_IPS_TO_TEST = 5  # Сколько случайных IP проверять в одной подсети
TIMEOUT = 2          # Таймаут пинга
THREADS = 20         # Количество потоков
# ---------------------------------------

def check_ping(ip, timeout):
    # Пинг 2 пакета, как в твоем исходнике
    cmd = ['ping', '-c', '2', '-W', str(timeout), str(ip)]
    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0
    except:
        return False

def get_ips_to_test(cidr_str, num_ips):
    try:
        network = ipaddress.IPv4Network(cidr_str.strip(), strict=False)
        total_ips = network.num_addresses
        
        if total_ips <= num_ips:
            return list(network)
        
        # Выбираем случайные IP, чтобы не сканировать всю сеть /14
        indices = random.sample(range(total_ips), num_ips)
        return [network[i] for i in indices]
    except:
        return []

def evaluate_subnet(cidr_str):
    ips = get_ips_to_test(cidr_str, NUM_IPS_TO_TEST)
    if not ips:
        return cidr_str, False

    # Если хотя бы один IP из выборки ответил — подсеть жива
    for ip in ips:
        if check_ping(ip, TIMEOUT):
            return cidr_str, True
    return cidr_str, False

def main():
    tasks = []
    try:
        with open(INPUT_FILE, 'r') as f:
            tasks = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"Файл {INPUT_FILE} не найден!")
        return

    print(f"[*] Начинаю проверку {len(tasks)} подсетей...")
    print(f"[*] Режим: {NUM_IPS_TO_TEST} случайных IP на каждую сеть.")

    start_time = time.time()
    alive_count = 0

    with open(OUTPUT_FILE, 'w') as out_file:
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
            future_to_subnet = {executor.submit(evaluate_subnet, cidr): cidr for cidr in tasks}
            
            for i, future in enumerate(concurrent.futures.as_completed(future_to_subnet)):
                subnet, is_reachable = future.result()
                
                status = "\033[1;32m[+]\033[0m" if is_reachable else "\033[1;31m[-]\033[0m"
                print(f"{status} {subnet:<18} проверено {i+1}/{len(tasks)}")
                
                if is_reachable:
                    out_file.write(subnet + '\n')
                    out_file.flush()
                    alive_count += 1

    end_time = time.time()
    print(f"\n[*] Готово! Доступно подсетей: {alive_count}")
    print(f"[*] Результаты сохранены в: {OUTPUT_FILE}")
    print(f"[*] Время выполнения: {int(end_time - start_time)} сек.")

if __name__ == "__main__":
    main()