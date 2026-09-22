import pywikibot

CONFIGS = [('ff', 'jaɓɓama')]
LIMIT = 200
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
        print(f'[{lang_code}] Done — {welcomed} user(s) welcomed.')

if __name__ == '__main__':
    run()
