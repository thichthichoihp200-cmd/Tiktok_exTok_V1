import requests
import json
import time
import os
from colorama import Fore, Style, init

# Khởi tạo colorama
init(autoreset=True)

CONFIG_FILE = "config_TikTok_ExTok_V1.json"
USER_AGENT = "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"

class ExTokBot:
    def __init__(self):
        self.base_url = "https://api.extok.net/api"
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                self.token = json.load(f).get("token")
        else:
            self.token = input(f"{Fore.CYAN}>>> Nhập Token: {Style.RESET_ALL}").strip()
            with open(CONFIG_FILE, "w") as f:
                json.dump({"token": self.token}, f)
        print(f"{Fore.GREEN}[*] Đã xác thực Token thành công!{Style.RESET_ALL}")

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}", "User-Agent": USER_AGENT, "Content-Type": "application/json"}

    def countdown(self, seconds, label):
        for i in range(seconds, 0, -1):
            print(f"\r{Fore.YELLOW}>> {label}: {i}s...{Style.RESET_ALL} ", end="", flush=True)
            time.sleep(1)
        print(f"\r{Fore.GREEN}>> {label}: Đã xong!{' '*10}{Style.RESET_ALL}")

    def get_accounts(self):
        try:
            res = requests.get(f"{self.base_url}/tiktok-account", headers=self.get_headers())
            return [a for a in res.json().get("data", []) if a.get('is_banned') == 0]
        except:
            return []

    def start(self):
        while True:
            accounts = self.get_accounts()
            if not accounts:
                print(f"{Fore.RED}[!] Không có tài khoản hoạt động!{Style.RESET_ALL}")
                break

            print(f"\n{Fore.MAGENTA}" + "="*85)
            print(f"{Fore.CYAN}{'STT':<5} | {'Nickname':<25} | {'TikTok ID':<25} | {'Số dư'}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}" + "-"*85 + Style.RESET_ALL)
            
            id_map = {}
            for idx, acc in enumerate(accounts):
                nickname = acc.get('nickname', 'N/A')
                tiktok_id = acc.get('unique_username', 'N/A')
                id_map[str(tiktok_id)] = acc
                # Màu sắc xen kẽ hoặc làm nổi bật số dư
                print(f"{idx:<5} | {str(nickname):<25} | {Fore.WHITE}{str(tiktok_id):<25} | {Fore.YELLOW}{acc.get('balance', 0)}{Style.RESET_ALL}")
            
            try:
                choice = input(f"\n{Fore.GREEN}>>> Nhập STT hoặc TikTok ID (hoặc 'exit'): {Style.RESET_ALL}")
                if choice.lower() == 'exit': break
                
                if choice.isdigit() and int(choice) < len(accounts):
                    selected_acc = accounts[int(choice)]
                elif choice in id_map:
                    selected_acc = id_map[choice]
                else:
                    print(f"{Fore.RED}[!] Không tìm thấy tài khoản!{Style.RESET_ALL}")
                    continue
                
                max_jobs = int(input(f"{Fore.CYAN}>>> Số job làm: {Style.RESET_ALL}"))
                max_fails = int(input(f"{Fore.CYAN}>>> Giới hạn lỗi: {Style.RESET_ALL}"))
                time_wait = int(input(f"{Fore.CYAN}>>> Delay (giây): {Style.RESET_ALL}"))
            except:
                continue

            u_id = selected_acc['unique_id']
            jobs_done, fails = 0, 0
            
            while jobs_done < max_jobs:
                res = requests.get(f"{self.base_url}/tiktok-jobs", headers=self.get_headers(), params={"unique_id": u_id, "type": "follow"})
                jobs = res.json().get("data", [])
                
                if not jobs:
                    print(f"{Fore.YELLOW}[!] Hết job, quay về danh sách...{Style.RESET_ALL}")
                    break

                for job in jobs:
                    if jobs_done >= max_jobs: break
                    
                    print(f"\n{Fore.BLUE}=== Đang xử lý: @{job.get('tiktok_username', 'N/A')} ==={Style.RESET_ALL}")
                    os.system(f"termux-open '{job.get('link')}'")
                    self.countdown(time_wait, "Chờ hoàn thành")
                    
                    complete_res = requests.post(f"{self.base_url}/tiktok-jobs/complete", 
                                  json={"job_id": job['id'], "unique_id": u_id, "success": True}, headers=self.get_headers())
                    
                    if complete_res.status_code == 200:
                        jobs_done += 1
                        fails = 0
                        print(f"{Fore.GREEN}[+] Success: {jobs_done}/{max_jobs}{Style.RESET_ALL}")
                    else:
                        fails += 1
                        print(f"{Fore.RED}[!] Fail: {fails}/{max_fails}{Style.RESET_ALL}")
                        if fails >= max_fails:
                            print(f"{Fore.RED}[!] Đã đạt giới hạn lỗi!{Style.RESET_ALL}")
                            jobs_done = max_jobs
            
            print(f"{Fore.GREEN}=== Hoàn tất tài khoản này ==={Style.RESET_ALL}")

if __name__ == "__main__":
    bot = ExTokBot()
    bot.start()
