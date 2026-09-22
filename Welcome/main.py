"""
Welcome Bot — TanvirSdqBot
Runs once per execution. Schedule via Toolforge cron (every 6 hours).
Welcomes new users on Fulani Wikipedia who have no talk page yet.
"""
import pywikibot

CONFIGS = [
    ('ff', 'jaɓɓama'),   # Fulani Wikipedia, welcome template name
]
LIMIT  = 200   # how many recent new-user log events to scan per run
SUMMARY = "Bot: Jaɓɓama binndaaɗo"

def run():
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
        print(f'[{lang_code}] Done — {welcomed} user(s) welcomed this run.')

if __name__ == '__main__':
    run()
