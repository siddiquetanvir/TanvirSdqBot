import pywikibot


class AtCategoryBot:

    def __init__(self):
        self.ff = pywikibot.Site('ff', 'wikipedia')
        self.en = pywikibot.Site('en', 'wikipedia')

        self.bot = "TanvirSdqBot"
        self.pwd = input("Pass: ")

        self.ecat = f"Category:{input('EnCat: ').strip()}"
        self.tcat = f"Category:{input('TgCat: ').strip()}"

    def auth(self):
        try:
            self.ff.login(user=self.bot)
            print(f"✅ {self.bot}")
        except Exception as e:
            print(f"❌ {e}")
            exit()

    def check(self, page):

        if page.length() < 1500:
            return False

        english_page = None

        for link in page.langlinks():
            if link.site.lang == "en":
                english_page = pywikibot.Page(link)
                break

        if english_page is None:
            return False

        for category in english_page.categories():
            if category.title() == self.ecat:
                return True

        print(f"❌ EnCat missing: {page.title()}")
        return False

    def add(self, page):

        for category in page.categories():
            if category.title() == self.tcat:
                print(f"➡️ {page.title()}")
                return False

        page.text += f"\n[[{self.tcat}]]"
        page.save(summary=f"ɓeydunde {self.tcat}")

        print(f"✅ {page.title()}")
        return True

    def run(self):

        self.auth()

        count = 0

        for page in self.ff.allpages(namespace=0):

            if self.check(page):
                if self.add(page):
                    count += 1

        print(f"🏁 {count}")


if __name__ == "__main__":
    AtCategoryBot().run()