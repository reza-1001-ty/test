import requests
import socket
import base64
import time
from urllib.parse import urlparse

PROXY_URL = "http://your-proxy-ip:500"   # ← آدرس پروکسی خود را جایگزین کنید
PROXY_URL = "http://remote-fanhab.runflare.com:32249"

def fetch_requests():
    """دریافت لیست درخواست‌های ذخیره‌شده"""
    try:
        resp = requests.get(f"{PROXY_URL}/get_requests", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[!] Failed to fetch requests: {e}")
        return []

def forward_http(request_obj):
    """یک درخواست HTTP را به مقصد می‌فرستد و پاسخ خام (بایت) را برمی‌گرداند."""
    method = request_obj['method']
    path = request_obj['path']
    headers = request_obj['headers']
    body = request_obj['body']

    parsed = urlparse(path)
    host = parsed.hostname
    port = parsed.port or 80
    relative_path = parsed.path
    if parsed.query:
        relative_path += '?' + parsed.query

    request_line = f"{method} {relative_path} HTTP/1.1\r\n"
    header_lines = ""
    for key, value in headers.items():
        if key.lower() == 'host':
            continue
        header_lines += f"{key}: {value}\r\n"
    header_lines += f"Host: {host}\r\n"
    if body:
        header_lines += f"Content-Length: {len(body.encode('utf-8'))}\r\n"
    request_raw = request_line + header_lines + "\r\n" + body
    request_bytes = request_raw.encode('utf-8')

    try:
        sock = socket.create_connection((host, port), timeout=5)
        sock.send(request_bytes)
        response_data = b""
        sock.settimeout(5)
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response_data += chunk
        sock.close()
        return response_data
    except Exception as e:
        print(f"[!] Error forwarding to {host}:{port}: {e}")
        return None

def send_response(conn_id, data_bytes=None):
    """پاسخ را از طریق پروکسی به کلاینت اصلی می‌فرستد."""
    payload = {'conn_id': conn_id}
    if data_bytes is not None:
        payload['data'] = base64.b64encode(data_bytes).decode('ascii')
    else:
        payload['data'] = ''   # بستن اتصال

    try:
        resp = requests.post(f"{PROXY_URL}/send_data", json=payload, timeout=5)
        resp.raise_for_status()
        print(f"[+] Response sent for conn {conn_id}")
    except Exception as e:
        print(f"[!] Failed to send response for conn {conn_id}: {e}")

def process_batch():
    """یک دور کامل پردازش درخواست‌های معوقه"""
    requests_list = fetch_requests()
    if not requests_list:
        return

    print(f"[*] Processing {len(requests_list)} captured requests")
    for req in requests_list:
        req_type = req.get('type')
        conn_id = req['id']

        if req_type == 'HTTP':
            print(f"  -> HTTP {conn_id}: {req['path']}")
            raw_resp = forward_http(req)
            if raw_resp:
                send_response(conn_id, raw_resp)
            else:
                error_resp = b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n"
                send_response(conn_id, error_resp)
        elif req_type == 'CONNECT':
            print(f"  -> CONNECT {conn_id} (unsupported) – closing")
            send_response(conn_id, data_bytes=None)
        else:
            print(f"  -> Unknown type {req_type} – closing")
            send_response(conn_id, data_bytes=None)

def main_loop():
    print("[*] Starting relay loop (every 1 second)")
    while True:
        try:
            process_batch()
        except Exception as e:
            print(f"[!] Unhandled error in main loop: {e}")
        time.sleep(1)

if __name__ == '__main__':
    main_loop()
