import pywikibot

sites = ['ff']
user_name = "TanvirSdqBot"

for code in sites:
    site = pywikibot.Site(code, "wikipedia")
    site.login()
    user = pywikibot.User(site, user_name)
    talk = sum(1 for _ in user.contributions(namespaces=[3], total=None))
    main = sum(1 for _ in user.contributions(namespaces=[0], total=None))
    template_text = f"{{{{#switch: {{{{{{1}}}}}}|1={talk}|2={main}}}}}"
    page = pywikibot.Page(site, f"User:{user_name}/CountTalkpage")
    page.text = template_text
    page.save("Bot: Updating counts")
    print(f"Updated counts for {code}")
