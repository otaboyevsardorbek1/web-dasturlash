#!/usr/bin/env python3
"""
GitHub Repo RAW URL Generator
Berilgan GitHub repo URL uchun barcha fayllarning RAW URL'larini topadi va saqlaydi
"""

import requests
import json
import re
import os
import sys
from urllib.parse import urlparse
from typing import List, Dict, Optional
from datetime import datetime

class GitHubRawURLGenerator:
    """
    GitHub repodagi barcha fayllarning RAW URL'larini olish
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "GitHub-Raw-URL-Generator/2.0",
            "Accept": "application/vnd.github.v3+json"
        })
        # GitHub API rate limitni tekshirish uchun
        self.api_calls = 0
    
    def get_default_branch(self, owner: str, repo: str) -> str:
        """
        Reponing default branchini aniqlash
        """
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            response = self.session.get(api_url, timeout=10)
            self.api_calls += 1
            if response.status_code == 200:
                data = response.json()
                return data.get("default_branch", "main")
            elif response.status_code == 403:
                print("⚠️  API rate limit chegarasiga yetdingiz. 'main' branch ishlatiladi.")
        except Exception as e:
            print(f"⚠️  Branchni aniqlashda xatolik: {e}")
        return "main"
    
    def extract_owner_repo(self, github_url: str) -> tuple: # type: ignore
        """
        GitHub URL-dan owner va repo nomini ajratadi
        """
        # .git ni olib tashlash
        github_url = github_url.replace('.git', '').rstrip('/')
        
        # URL parse qilish
        parsed = urlparse(github_url)
        path_parts = parsed.path.strip("/").split("/")
        
        if len(path_parts) < 2:
            raise ValueError(f"❌ Noto'g'ri GitHub URL: {github_url}")
        
        owner, repo = path_parts[0], path_parts[1]
        
        return owner, repo
    
    def get_all_files_from_repo(self, owner: str, repo: str, branch: str) -> List[Dict]:
        """
        Repodagi barcha fayllarni GitHub API orqali olish
        """
        all_files = []
        page = 1
        per_page = 100  # GitHub API maksimal
        
        print(f"📂 Fayllar ro'yxati olinmoqda...")
        
        while True:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}"
            params = {
                "recursive": 1,
                "page": page,
                "per_page": per_page
            }
            
            try:
                response = self.session.get(api_url, params=params, timeout=30)
                self.api_calls += 1
                
                if response.status_code == 200:
                    data = response.json()
                    tree = data.get("tree", [])
                    
                    if not tree:
                        break
                    
                    # Faqat fayllarni olish (blob)
                    for item in tree:
                        if item["type"] == "blob":
                            all_files.append({
                                "path": item["path"],
                                "sha": item.get("sha", ""),
                                "size": item.get("size", 0),
                                "url": item.get("url", "")
                            })
                    
                    # Pagination tekshirish
                    if len(tree) < per_page:
                        break
                    
                    page += 1
                    
                elif response.status_code == 404:
                    # Agar branch topilmasa, master ni tekshirish
                    if branch == "main":
                        print(f"⚠️  '{branch}' branch topilmadi, 'master' tekshirilmoqda...")
                        return self.get_all_files_from_repo(owner, repo, "master")
                    else:
                        raise Exception(f"Repo yoki branch topilmadi: {owner}/{repo} {branch}")
                elif response.status_code == 403:
                    print("⚠️  API rate limit chegarasiga yetdingiz. Keyinroq qayta urinib ko'ring.")
                    break
                else:
                    print(f"⚠️  API xatosi: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"⚠️  Xatolik: {e}")
                break
        
        print(f"✅ {len(all_files)} ta fayl topildi")
        return all_files
    
    def generate_raw_urls(self, owner: str, repo: str, branch: str, files: List[Dict]) -> List[str]:
        """
        Fayllar ro'yxatidan RAW URL'lar yaratish
        """
        raw_urls = []
        
        for file_info in files:
            file_path = file_info["path"]
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
            raw_urls.append(raw_url)
        
        return raw_urls
    
    def process_repo(self, github_url: str) -> Dict:
        """
        Reponi to'liq qayta ishlash
        """
        print(f"\n{'='*60}")
        print(f"🔍 GitHub Repo tahlil qilinmoqda...")
        print(f"{'='*60}")
        
        # 1. Owner va repo nomini ajratish
        owner, repo = self.extract_owner_repo(github_url)
        print(f"📌 Owner: {owner}")
        print(f"📌 Repo: {repo}")
        
        # 2. Default branchni aniqlash
        branch = self.get_default_branch(owner, repo)
        print(f"📌 Branch: {branch}")
        
        # 3. Repodagi barcha fayllarni olish
        files = self.get_all_files_from_repo(owner, repo, branch)
        
        if not files:
            raise Exception("Hech qanday fayl topilmadi!")
        
        # 4. RAW URL'lar yaratish
        raw_urls = self.generate_raw_urls(owner, repo, branch, files)
        
        # 5. Natijalarni tayyorlash
        results = {
            "metadata": {
                "repo_url": github_url,
                "owner": owner,
                "repo": repo,
                "branch": branch,
                "total_files": len(files),
                "total_raw_urls": len(raw_urls),
                "generated_at": datetime.now().isoformat(),
                "api_calls": self.api_calls
            },
            "files": [],
            "raw_urls": raw_urls
        }
        
        # Fayl tafsilotlarini qo'shish
        for i, file_info in enumerate(files):
            results["files"].append({
                "path": file_info["path"],
                "filename": file_info["path"].split('/')[-1],
                "size": file_info["size"],
                "size_kb": round(file_info["size"] / 1024, 2) if file_info["size"] else 0,
                "raw_url": raw_urls[i],
                "github_url": f"https://github.com/{owner}/{repo}/blob/{branch}/{file_info['path']}"
            })
        
        return results
    
    def save_results(self, results: Dict, output_dir: str = ".") -> tuple:
        """
        Natijalarni fayllarga saqlash
        """
        owner = results["metadata"]["owner"]
        repo = results["metadata"]["repo"]
        
        # Fayl nomlarini yaratish
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{owner}_{repo}_{timestamp}"
        
        # 1. JSON fayl (to'liq ma'lumot)
        json_file = os.path.join(output_dir, f"{base_filename}_full.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        # 2. TEXT fayl (faqat RAW URL'lar)
        txt_file = os.path.join(output_dir, f"{base_filename}_raw_urls.txt")
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(f"# GitHub RAW URLs\n")
            f.write(f"# Repo: {results['metadata']['repo_url']}\n")
            f.write(f"# Branch: {results['metadata']['branch']}\n")
            f.write(f"# Total files: {results['metadata']['total_files']}\n")
            f.write(f"# Generated: {results['metadata']['generated_at']}\n")
            f.write("=" * 60 + "\n\n")
            
            for url in results["raw_urls"]:
                f.write(url + "\n")
        
        # 3. CSV fayl (fayl nomi va URL)
        csv_file = os.path.join(output_dir, f"{base_filename}_details.csv")
        with open(csv_file, "w", encoding="utf-8") as f:
            f.write("File Path,Filename,Size (KB),RAW URL\n")
            for file_info in results["files"]:
                f.write(f'"{file_info["path"]}",{file_info["filename"]},{file_info["size_kb"]},{file_info["raw_url"]}\n')
        
        return json_file, txt_file, csv_file
    
    def print_summary(self, results: Dict):
        """
        Natijalarni chiroyli qilib ko'rsatish
        """
        print(f"\n{'='*60}")
        print(f"✅ HISOBOT")
        print(f"{'='*60}")
        print(f"📊 Jami fayllar: {results['metadata']['total_files']}")
        print(f"🔗 Jami RAW URL: {results['metadata']['total_raw_urls']}")
        print(f"📁 Kengaytmalar bo'yicha:")
        
        # Kengaytmalar bo'yicha guruhlash
        extensions = {}
        for file_info in results["files"]:
            filename = file_info["filename"]
            ext = filename.split('.')[-1] if '.' in filename else "no-ext"
            extensions[ext] = extensions.get(ext, 0) + 1
        
        for ext, count in sorted(extensions.items())[:10]:
            print(f"   .{ext}: {count} ta")
        
        print(f"\n📋 Birinchi 10 ta RAW URL:")
        for i, url in enumerate(results["raw_urls"][:10], 1):
            print(f"{i:2}. {url}")
        
        if len(results["raw_urls"]) > 10:
            print(f"... va yana {len(results['raw_urls']) - 10} ta")


def main():
    """
    Asosiy dastur
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🚀 GitHub RAW URL Generator v2.0                        ║
║     GitHub repo URL → RAW formatdagi URL'lar                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # GitHub repo URL so'rash
    default_url = "https://github.com/otaboyevsardorbek1/web-dasturlash"
    print(f"Masalan: {default_url}")
    github_url = input("\n🔗 GitHub repo URL kiriting: ").strip()
    
    if not github_url:
        github_url = default_url
        print(f"📌 Default URL ishlatiladi: {github_url}")
    
    try:
        # Generator yaratish
        generator = GitHubRawURLGenerator()
        
        # Reponi qayta ishlash
        results = generator.process_repo(github_url)
        
        # Natijalarni ko'rsatish
        generator.print_summary(results)
        
        # Natijalarni saqlash
        print(f"\n💾 Natijalar saqlanmoqda...")
        json_file, txt_file, csv_file = generator.save_results(results)
        
        print(f"\n✅ Fayllar saqlandi:")
        print(f"   📄 JSON (to'liq): {json_file}")
        print(f"   📄 TEXT (URL'lar): {txt_file}")
        print(f"   📄 CSV (tafsilotlar): {csv_file}")
        
        print(f"\n✨ Bajarildi! Jami {results['metadata']['total_files']} ta fayl uchun RAW URL yaratildi.")
        
    except Exception as e:
        print(f"\n❌ Xato yuz berdi: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())