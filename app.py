from flask import Flask, Response, request
import ipaddress
import random
import asyncio
import time
import threading

app = Flask(__name__)

cidr_list = [
    "173.245.48.0/20",
    "103.21.244.0/22",
    "103.22.200.0/22",
    "103.31.4.0/22",
    "141.101.64.0/18",
    "108.162.192.0/18",
    "190.93.240.0/20",
    "188.114.96.0/20",
    "197.234.240.0/22",
    "198.41.128.0/17",
    "162.158.0.0/15",
    "104.16.0.0/13",
    "104.24.0.0/14",
    "172.64.0.0/13",
    "131.0.72.0/22"
]

cache = {
    "reachable_ips": [],
    "last_test_time": 0,
    "last_access_time": None
}
CACHE_EXPIRATION = 180

# 生成ip数量，这里的count是按照每个网段生成的，而不是限制的数量哦！
# 但是千万别小瞧1000这个数，总计加起来一共有大约15万的ip数量哦，而最快挑选的只有50个IP
def generate_random_ips(cidr, count=1000):
    try:
        network = ipaddress.IPv4Network(cidr, strict=False)
        hosts = list(network.hosts())
        random.shuffle(hosts)
        return [str(ip) for ip in hosts[:count]]
    except ValueError:
        return []

async def tcping(ip, port=443, timeout="300ms"):
    try:
        cmd = f"tcping {ip} {port} -T {timeout} -c 1"
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            for line in stdout.decode().splitlines():
                if "time=" in line or "Connected" in line:
                    latency = float(line.split("time=")[-1].replace("ms", "").strip())
                    return ip, latency
        return None
    except Exception:
        return None

async def update_reachable_ips():
    while True:
        tasks = []
        for cidr in cidr_list:
            ips = generate_random_ips(cidr, count=1000)
            tasks.extend(tcping(ip, port=443, timeout="300ms") for ip in ips)

        results = await asyncio.gather(*tasks)
        successful_results = [res for res in results if res]

        # 限制只保留前 50 个最快的 IP，别看很少，对于精细要求来说足够啦！
        fastest_ips = sorted(successful_results, key=lambda x: x[1])[:50]
        cache["reachable_ips"] = [ip for ip, latency in fastest_ips]
        cache["last_test_time"] = time.time()
        print(f"Reachable IPs updated. Total: {len(fastest_ips)}")

        await asyncio.sleep(CACHE_EXPIRATION)
      
# 入口设置，可以改成自己想要的入口，避免被扫描
@app.route('/cfip', methods=['GET'])
def get_reachable_ips():
    cache["last_access_time"] = time.time()
    requester_ip = request.remote_addr

    if not cache["reachable_ips"]:
        return Response("No reachable IPs found.", mimetype="text/plain")

    last_update = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cache["last_test_time"]))
    access_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cache["last_access_time"]))
    header = (
        f"# 您的IP: {requester_ip}\n"
        f"# 现在时间: {access_time}\n"
        f"# Cloudflare Best IP列表上一次更新在 {last_update}\n"
        f"# Github项目: https://github.com/zixuanya/Cloudflare_BestIP_Chooser\n\n"
    )
    return Response(header + "\n".join(cache["reachable_ips"]), mimetype="text/plain")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    threading.Thread(target=loop.run_until_complete, args=(update_reachable_ips(),), daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
