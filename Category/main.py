import mwclient

class AtCategoryBot:
    def __init__(self):
        self.ff = mwclient.Site('ff.wikipedia.org', scheme='https')
        self.en = mwclient.Site('en.wikipedia.org', scheme='https')
        self.bot, self.pwd = "TanvirSdqBot", input('Pass: ')
        self.ecat = f"Category:{input('EnCat: ').strip()}"  # Added .strip()
        self.tcat = f"Category:{input('TgCat: ').strip()}"  # Added .strip()
        
    def auth(self):
        try: self.ff.login(self.bot, self.pwd); print(f"✅ {self.bot}")
        except Exception as e: print(f"❌ {e}"); exit()

    def check(self, p):
        if p.length < 1500: return False
        if not (en := next((ll for ll in p.langlinks() if ll[0] == 'en'), None)): return False
        if self.ecat in [c.name for c in self.en.pages[en[1]].categories()]: return True
        print(f"❌EnCat missing:{p.name}")
        return False

    def add(self, p):
        if self.tcat not in [c.name for c in p.categories()]:
            p.save(f"{p.text()}\n[[{self.tcat}]]", summary=f"ɓeydunde {self.tcat}")
            print(f"✅ {p.name}"); return True
        print(f"⏩ {p.name}"); return False

    def run(self):
        self.auth()
        count = sum(self.add(p) for p in self.ff.allpages(namespace=0) if self.check(p))
        print(f"🏁 {count}")

if __name__ == "__main__": AtCategoryBot().run()
