import pywikibot
from pywikibot import pagegenerators

site = pywikibot.Site("ff", "wikipedia")
site.login()
TARGET_PAGE = "User:TanvirSdqBot/CategoryLog4"
CATEGORIES = {
    "Category:Jibinannde karniwol 20th": "20th-century births",
  #  "Category:Jibinannde karniwol 19th": "19th-century births",
    "Category:Jibinannde karniwol 17th": "17th-century births",
    "Category:Rewɓe nder leydi Naajeeriya": "Women in Nigeria"
}

def fetch_cat_pages(cat): 
    return pagegenerators.CategorizedPageGenerator(pywikibot.Category(site, cat), recurse=False)

def gen_table(cat, title):
    lines = [f"== {cat} ==", f"'''{title}'''", "", '{| class="wikitable"', "|-", "! Edit ID", "! Page Title", "! Timestamp"]
    for art in fetch_cat_pages(cat):
        art.get()
        lines += ["|-", f"| {art.latest_revision_id} || [[{art.title()}]] || {art.latest_revision.timestamp.isoformat()}"]
    return "\n".join(lines + ["|}", ""])

def main():
    page = pywikibot.Page(site, TARGET_PAGE)
    page.text = "\n".join(gen_table(cat, title) for cat, title in CATEGORIES.items())
    page.save("Bot: Updating multiple categories in tables")
    print("✅ Updated category tables.")

if __name__ == "__main__":
    main()
