from ..library import deps, loop, con, logging, random, File
from ..views import CountryNewView

class AILoop():
    def accept_focus(self, country: deps.Country):
        if country.doing_focus is None:
            return
        if not country.doing_focus or not country.doing_focus.is_completed:
            return
        
        focuses = country.give_available_focuses()
        if random.random() < (1 / (12 / deps.SPEED)):
            country.set_focus(random.choice(focuses))
    
    async def do_focus(self, country: deps.Country):
        if country.doing_focus is None:
            return
        if not country.doing_focus or not country.doing_focus.is_completed:
            return
        
        if country.doing_focus.req_news:
            if random.random() <= 0.5:
                text = country.doing_focus.news.replace('{self.name}', country.name)
                img = country.doing_focus.news_img
                if text is None and img is None:
                    return
                view = CountryNewView(country)
                await country.send_news(text, [File(img)], view, True)

        if not country.doing_focus.requirements_complete():
            for factory in country.doing_focus.req_factories:
                if country.factories[factory.name] < factory.quantity:
                    try:
                        country.buy_factory(factory, random.choice(range(0, factory.quantity + 1)))
                    except:
                        continue
            for factory in [item.produced_by for item in country.doing_focus.req_items if item.produced_by is not None and item.quantity > country.inventory[item.name].quantity]:
                try:
                    country.buy_factory(factory, random.choice(range(0, min(country.max_to_buy(factory) // 3, 3))))
                except:
                    continue


        
        
    @loop(hours=deps.SPEED)
    async def ai(self):
        if not deps.game_state['game_started']:
            return
        logging.info('Работает ИИ для стран...')
        
        for country in (await deps.Country.all()):
            self.accept_focus(country)
            await self.do_focus(country)

            total_buy = 0
            for factory in country.factories.values():
                if (random.random() < 0.25) and (total_buy < 8):
                    try:
                        count = min(country.max_to_buy(factory) // 1.5, 3)
                        country.buy_factory(factory, random.choice(range(0, count)))
                        total_buy += count
                    except:
                        continue
