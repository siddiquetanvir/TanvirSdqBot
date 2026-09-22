import time
import pywikibot

CONFIGS = [('ff', 'jaɓɓama')]
LIMIT = 200
SUMMARY = "Bot: Jaɓɓama binndaaɗo"
SLEEP_INTERVAL = 3600

def run_once():
    for lang_code, template in CONFIGS:
        site = pywikibot.Site(lang_code, 'wikipedia')
        site.login()
        welcomed = 0
        for event in site.logevents(logtype='newusers', total=LIMIT):
            user = event.user()
            talk = pywikibot.Page(site, f'User talk:{user}')
            if talk.exists():
                continue
            talk.text = f'{{{{subst:{template}}}}}\n[[User:TanvirSdqBot|WelcomeBot]] ~~~~~'
            talk.save(summary=SUMMARY)
            print(f'  Welcomed: {user}')
            welcomed += 1
        print(f'[{lang_code}] Done — {welcomed} user(s) welcomed.')

def run_forever():
    while True:
        try:
            run_once()
        except Exception as e:
            print(f"Error during run: {e}")
        print(f"Sleeping {SLEEP_INTERVAL}s until next check...")
        time.sleep(SLEEP_INTERVAL)

if __name__ == '__main__':
    run_forever()
