import pywikibot, time

configs = [('ff', 'jaɓɓama')]
limit, sleep_time, summary = 100, 86400, "Welcome!"

while True:
    for code, tmpl in configs:
        site = pywikibot.Site(code, 'wikipedia')
        site.login()
        for change in site.logevents(logtype="newusers", total=limit):
            user = change.user()
            tp = pywikibot.Page(site, f"User talk:{user}")
            if tp.exists():
                continue
            tp.text = f"{{{{subst:{tmpl}}}}}\n[[User:TanvirSdqBot|WelcomeBot]] ~~~~~"
            tp.save(summary=summary)
            print(f"Welcomed {user} on {code}")
    print(f"Sleeping for {sleep_time} seconds...")
    time.sleep(sleep_time)
