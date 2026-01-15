import os
import sys
import django
import requests
from camoufox.sync_api import Camoufox

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangosite.settings')
django.setup()

from django.conf import settings

def run_parser():
    base_save_dir = os.path.join(settings.MEDIA_ROOT, "PrezentZP")

    if not os.path.exists(base_save_dir):
        os.makedirs(base_save_dir)
        print(f"Створено папку: {base_save_dir}")

    print(f"Починаємо завантаження в: {base_save_dir}")

    try:
        with Camoufox(headless=False) as browser:
            page = browser.new_page()
            url = "https://metinvestholding.com/ru/investor/presentations"
            print(f"Переходимо на {url}...")

            page.goto(url)
            page.wait_for_selector(".CorporatePresentations__Item", timeout=30000)

            cards = page.query_selector_all(".CorporatePresentationCard")
            print(f"Знайдено карток: {len(cards)}")

            for card in cards:
                try:
                    year_el = card.query_selector(".CorporatePresentationCard__Year")
                    if not year_el: continue
                    year = year_el.inner_text().strip()
                    links = card.query_selector_all("a.CorporatePresentationCard__Link")
                    target_link = None
                    for link in links:
                        txt = link.inner_text()
                        if "Финансовый год" in txt or "Financial year" in txt:
                            target_link = link
                            break

                    if target_link:
                        file_url = target_link.get_attribute("href")
                        if file_url.startswith("/"):
                            file_url = "https://metinvestholding.com" + file_url

                        file_name = f"Financial year_{year}.pdf"
                        full_path = os.path.join(base_save_dir, file_name)

                        if not os.path.exists(full_path):
                            print(f"Завантажую {file_name}...")
                            resp = requests.get(file_url, stream=True)
                            if resp.status_code == 200:
                                with open(full_path, 'wb') as f:
                                    for chunk in resp.iter_content(1024):
                                        f.write(chunk)
                                print(f"[OK] Збережено: {file_name}")
                            else:
                                print(f"[Помилка] Статус {resp.status_code} для {file_url}")
                        else:
                            print(f"[Пропуск] Файл вже існує: {file_name}")

                except Exception as e:
                    print(f"Помилка в картці: {e}")

    except Exception as global_e:
        print(f"Критична помилка парсера: {global_e}")


if __name__ == "__main__":
    run_parser()