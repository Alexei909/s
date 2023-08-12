import csv
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from datetime import datetime


COUNT = 1 
result_data = []
async def get_data(session, url):
    global COUNT

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }

    category = None
    count = 1
    while True:
        async with session.get(url=url+f'?page={count}', headers=headers) as response:
            response_text = await response.text()

            soup = BeautifulSoup(response_text, 'lxml')

            if category is None:
                category = soup.find('h1', class_='catheading').text.strip()

            product_cards = soup.find_all('div', class_='product-layout product-grid grid-view col-sm-6 col-md-4 col-lg-4 col-xxl-5')

            for product_card in product_cards:
                product_caption = product_card.find('div', class_='product-thumb__caption')

                # product_url = product_caption.find('a', class_='product-thumb__name').get('href')
                product_name = product_caption.find('a', class_='product-thumb__name').text.strip()
                code = product_caption.find('div', class_='product-thumb__model', attrs={"data-text": 'Код товара:'}).text.strip()
                article = product_caption.find('div', class_='product-thumb__model', attrs={"data-text": 'Артикул:'}).text.strip()
                brand = product_caption.find('div', class_='product-thumb__model', attrs={"data-text": 'Бренд:'}).text.strip()
                price = product_caption.find('div', class_='product-thumb__price price').text.strip()

                result_data.append(
                       {
                            "ID": COUNT,
                            "product_name": product_name,
                            # "product_url": product_url,
                            "code": code,
                            "article": article,
                            "brand": brand,
                            "price": price
                        }
                )

                COUNT += 1

        if soup.find('a', string='>'):
            count += 1
            await asyncio.sleep(0.0001)
        else:
            break


async def get_gather():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }

    url = 'https://santoros.ru/'

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        soup = BeautifulSoup(await response.text(), 'lxml')
        chapters = soup.find_all('a', class_='menu__level-1-a')

        tasks = []
        for chapter in chapters:
            task = asyncio.create_task(get_data(session, chapter.get('href')))
            tasks.append(task)

        await asyncio.gather(*tasks)


 
def main():
    asyncio.run(get_gather())

    cur_date = datetime.now().strftime('%d-%m-%Y')

    with open(f'data_{cur_date}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                "ID",
                "Название товара",
                # "URL товара",
                "Код товара",
                "Артикул",
                "Бренд",
                "Цена",
            )
        )
            
    for product in result_data:
        with open(f'data_{cur_date}.csv', 'a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)

            writer.writerow(
                (
                    product['ID'],
                    product['product_name'],
                    # product['product_url'],
                    product['code'],
                    product['article'],
                    product['brand'],
                    product['price'],
                )
            )


if __name__ == '__main__':
    main()