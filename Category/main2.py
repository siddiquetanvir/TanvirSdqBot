"""
Category Bot — TanvirSdqBot
Headless version: reads English and target category names from CLI args.
Usage:
    python3 Category/main.py --encat "Mosques in Nigeria" --tgcat "Juule nder Naajeeriya"
"""
import argparse
import pywikibot


def parse_args():
    parser = argparse.ArgumentParser(description='TanvirSdqBot category mapper')
    parser.add_argument('--encat', required=True,
                        help='English Wikipedia category name (without "Category:" prefix)')
    parser.add_argument('--tgcat', required=True,
                        help='Fulani Wikipedia target category name (without "Category:" prefix)')
    return parser.parse_args()


class CategoryBot:
    def __init__(self, encat: str, tgcat: str):
        self.ff = pywikibot.Site('ff', 'wikipedia')
        self.en = pywikibot.Site('en', 'wikipedia')
        self.encat = f'Category:{encat.strip()}'
        self.tgcat = f'Category:{tgcat.strip()}'

    def auth(self):
        self.ff.login()
        print(f'✅ Logged in as {self.ff.user()}')

    def qualifies(self, page) -> bool:
        """Return True if the Fulani page has a matching English Wikipedia category."""
        if page.length() < 1500:
            return False
        en_page = None
        for link in page.langlinks():
            if link.site.lang == 'en':
                en_page = pywikibot.Page(link)
                break
        if en_page is None:
            return False
        for cat in en_page.categories():
            if cat.title() == self.encat:
                return True
        print(f'  ⏩ EnCat missing: {page.title()}')
        return False

    def add_category(self, page) -> bool:
        for cat in page.categories():
            if cat.title() == self.tgcat:
                return False   # already has it
        page.text += f'\n[[{self.tgcat}]]'
        page.save(summary=f'Bot: ɓeydunde {self.tgcat}')
        print(f'  ✅ {page.title()}')
        return True

    def run(self):
        self.auth()
        count = 0
        for page in self.ff.allpages(namespace=0):
            if self.qualifies(page) and self.add_category(page):
                count += 1
        print(f'🏁 Done — {count} page(s) categorised.')


if __name__ == '__main__':
    args = parse_args()
    bot = CategoryBot(encat=args.encat, tgcat=args.tgcat)
    bot.run()