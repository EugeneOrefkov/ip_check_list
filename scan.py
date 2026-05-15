import subprocess
import ipaddress
import sys

def ping_ip(ip):
    # -c 1 (1 пакет), -W 1 (ждать ответ 1 сек)
    try:
        res = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
        return res.returncode == 0
    except:
        return False

def main():
    input_file = 'ip_cidr'
    output_file = 'alive.txt'
    
    print(f"Чтение сетей из {input_file}...")
    
    try:
        with open(input_file, 'r') as f, open(output_file, 'a') as out:
            for line in f:
                line = line.strip()
                if not line: continue
                
                print(f"Обработка подсети: {line}")
                try:
                    network = ipaddress.ip_network(line, strict=False)
                    for ip in network:
                        if ping_ip(ip):
                            print(f"[+] {ip} доступен")
                            out.write(str(ip) + '\n')
                            out.flush() # Сохраняем сразу
                except Exception as e:
                    print(f"Ошибка в строке {line}: {e}")
    except FileNotFoundError:
        print(f"Файл {input_file} не найден!")

if __name__ == "__main__":
    main()