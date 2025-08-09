import os
import requests
from urllib.parse import urljoin
import subprocess

def download_and_merge(m3u8_url, base_url, output_file):
    # m3u8 ফাইল ডাউনলোড
    print(f"📥 Downloading playlist from: {m3u8_url}")
    r = requests.get(m3u8_url)
    r.raise_for_status()
    lines = r.text.splitlines()

    # segments ফোল্ডার তৈরি
    os.makedirs("segments", exist_ok=True)

    # সব ts লিংক বের করা
    ts_links = [urljoin(base_url, line) for line in lines if line and not line.startswith("#")]
    print(f"✅ Found {len(ts_links)} segments")

    # ts লিংক লিস্ট ফাইলে লেখা (ffmpeg concat এর জন্য)
    with open("file_list.txt", "w") as f:
        for i, ts_url in enumerate(ts_links):
            ts_path = f"segments/part_{i:04d}.ts"
            if not os.path.exists(ts_path):
                print(f"[{i+1}/{len(ts_links)}] Downloading {ts_url}")
                ts_data = requests.get(ts_url, stream=True)
                with open(ts_path, "wb") as seg:
                    for chunk in ts_data.iter_content(chunk_size=1024*1024):
                        seg.write(chunk)
            f.write(f"file '{ts_path}'\n")

    # ffmpeg দিয়ে merge করা
    print("\n🔄 Merging all segments into MP4...")
    subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", "file_list.txt", "-c", "copy", output_file])

    print(f"\n🎉 Done! Saved as {output_file}")

if __name__ == "__main__":
    m3u8_url = input("Enter M3U8 file URL: ").strip()
    base_url = input("Enter Base URL (where .ts files are hosted): ").strip()
    output_file = input("Enter output MP4 file name: ").strip() or "output.mp4"
    download_and_merge(m3u8_url, base_url, output_file)
