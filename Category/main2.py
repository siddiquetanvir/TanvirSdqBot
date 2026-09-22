import argparse
import pywikibot


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--encat', required=True)
    parser.add_argument('--tgcat', required=True)
    return parser.parse_args()


class CategoryBot:
    def __init__(self, encat, tgcat):
        self.ff = pywikibot.Site('ff', 'wikipedia')
        self.en = pywikibot.Site('en', 'wikipedia')
        self.encat = f'Category:{encat.strip()}'
        self.tgcat = f'Category:{tgcat.strip()}'

    def qualifies(self, page):
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
        return False

    def add_category(self, page):
        for cat in page.categories():
            if cat.title() == self.tgcat:
                return False
        page.text += f'\n[[{self.tgcat}]]'
        page.save(summary=f'Bot: ɓeydunde {self.tgcat}')
        print(f'  ✅ {page.title()}')
        return True

    def run(self):
        self.ff.login()
        print(f'✅ Logged in as {self.ff.user()}')
        count = 0
        for page in self.ff.allpages(namespace=0):
            if self.qualifies(page) and self.add_category(page):
                count += 1
        print(f'🏁 Done — {count} page(s) categorised.')


if __name__ == '__main__':
    args = parse_args()
    CategoryBot(encat=args.encat, tgcat=args.tgcat).run()