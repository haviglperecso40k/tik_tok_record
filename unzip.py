import os
import sys
import subprocess
import zipfile
import time

def run_cmd(command):
    """Chạy lệnh CMD và trả về kết quả"""
    return subprocess.run(command, shell=True, capture_output=True, text=True)

def install_tools():
    """Kiểm tra và cài đặt FFmpeg qua Chocolatey"""
    print("--- DANG KIEM TRA HE THONG ---")
    
    # 1. Kiểm tra FFmpeg đã có chưa
    check_ffmpeg = run_cmd("ffmpeg -version")
    if check_ffmpeg.returncode == 0:
        print("[OK] FFmpeg da san sang.")
        return

    print("[!] Khong tim thay FFmpeg. Dang tien hanh cai dat...")

    # 2. Kiểm tra Chocolatey đã có chưa
    check_choco = run_cmd("choco -v")
    if check_choco.returncode != 0:
        print("[*] Dang cai dat Chocolatey (trinh quan ly goi)...")
        install_choco_cmd = (
            "@"
            'powershell -NoProfile -ExecutionPolicy Bypass -Command '
            '"iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))" '
            '&& SET "PATH=%PATH%;%ALLUSERSPROFILE%\\chocolatey\\bin"'
        )
        run_cmd(install_choco_cmd)

    # 3. Cài đặt FFmpeg bằng Choco
    print("[*] Dang cai dat FFmpeg qua Choco...")
    # --yes để tự động đồng ý các điều khoản
    result = run_cmd("choco install ffmpeg --yes")
    
    if result.returncode == 0:
        print("[OK] Cai dat FFmpeg thanh cong! Vui long khoi dong lai script neu lenh ffmpeg chua nhan.")
    else:
        print(f"[LOI] Khong the cai dat: {result.stderr}")

def process_video(file_path):
    """Lách bản quyền âm thanh"""
    temp_output = file_path + "_fixed.mp4"
    print(f"  [XU LY] -> {os.path.basename(file_path)}")
    
    # Công thức lách âm thanh: Pitch + Speed
    cmd = f'ffmpeg -y -i "{file_path}" -af "asetrate=44100*1.03,aresample=44100,atempo=1.0/1.03" -vcodec copy "{temp_output}"'
    
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        os.replace(temp_output, file_path)
        print("  [OK] Da ghi de file sach.")
    except Exception as e:
        print(f"  [LOI] FFmpeg: {e}")

def main():
    # Chạy cài đặt trước
    install_tools()
    
    root_dir = os.getcwd()
    print(f"\n--- DANG THEO DOI THU MUC: {root_dir} ---")

    while True:
        for filename in os.listdir(root_dir):
            if filename.lower().endswith(".zip"):
                zip_path = os.path.join(root_dir, filename)
                extract_dir = os.path.join(root_dir, os.path.splitext(filename)[0])
                
                try:
                    print(f"\n[ZIP] Phat hien: {filename}")
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    
                    for root, dirs, files in os.walk(extract_dir):
                        for f in files:
                            if f.lower().endswith(".mp4"):
                                process_video(os.path.join(root, f))
                    
                    os.remove(zip_path)
                    print(f"[DONE] Da xu ly xong va xoa ZIP.")
                except Exception as e:
                    print(f"[LOI] {e}")
        
        time.sleep(10)

if __name__ == "__main__":
    # Kiem tra quyen Admin (can thiet de cai choco/ffmpeg)
    main()
