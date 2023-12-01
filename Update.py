import httpx, zipfile, io
import urllib.request

def get_last_release():
    reps = httpx.get("https://api.github.com/repos/nguyluky/MAOS/releases")
    data = reps.json()[0]
    tag = int(''.join(str(data['tag_name']).split('.')))
    print(tag)
    main_file = None
    for i in data['assets']:
        if "MAOS" in i["name"]:
            main_file = i["browser_download_url"]
            break
    
    return tag, main_file


def download_url(url, save_path):
    with urllib.request.urlopen(url) as dl_file:
        with open(save_path, 'wb') as out_file:
            out_file.write(dl_file.read())

def main():
    tag, url = get_last_release()
    download_url(url, "a.zip")
    

if __name__ == "__main__":
    main()