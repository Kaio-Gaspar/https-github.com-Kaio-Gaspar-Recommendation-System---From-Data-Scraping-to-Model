import scrapy
import re
import cloudscraper
import pandas as pd

class CarsSpider(scrapy.Spider):
    name = "cars"
    start_urls = ["https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios"]
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'RANDOMIZE_DOWNLOAD_DELAY': False,
        'CONCURRENT_REQUESTS': 256,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
        'AUTOTHROTTLE_DEBUG': True,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scraper = cloudscraper.create_scraper(browser={'browser': 'firefox', 'platform': 'windows', 'desktop': True})
        self.carros_data = []

    def start_requests(self):
        for url in self.start_urls:
            self.logger.info(f"Usando cloudscraper para acessar: {url}")
            response = self.scraper.get(url)
            if response.status_code == 200:
                scrapy_response = scrapy.http.TextResponse(
                    url=response.url,
                    body=response.text,
                    encoding="utf-8"
                )
                yield from self.parse(scrapy_response, 1)  # Começa na página 1
            else:
                self.logger.error(f"Erro ao acessar {url}: {response.status_code}")

    def parse(self, response, current_page):
        link_carros = response.xpath('/html/body/div[1]/div/main/div[2]/div/main/div[7]/section/div/div/div/a/@href').extract()
        preco_carros = response.xpath('/html/body/div[1]/div/main/div[2]/div/main/div[7]/section/div[2]/div[1]/div[2]/h3/text()').extract()

        for link, preco in zip(link_carros, preco_carros):
            self.logger.info(f"Usando cloudscraper para acessar detalhes: {link}")
            response = self.scraper.get(link)
            if response.status_code == 200:
                scrapy_response = scrapy.http.TextResponse(
                    url=response.url,
                    body=response.text,
                    encoding="utf-8"
                )
                yield from self.parse_detail(scrapy_response, response.url)
            else:
                self.logger.error(f"Erro ao acessar {link}: {response.status_code}")

        # Navega para a próxima página até o limite de 100
        next_page = current_page + 1
        if next_page <= 100:
            next_page_url = f"https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?o={next_page}"
            self.logger.info(f"Usando cloudscraper para acessar a página {next_page}: {next_page_url}")
            response = self.scraper.get(next_page_url)
            if response.status_code == 200:
                scrapy_response = scrapy.http.TextResponse(
                    url=response.url,
                    body=response.text,
                    encoding="utf-8"
                )
                yield from self.parse(scrapy_response, next_page)
            else:
                self.logger.error(f"Erro ao acessar {next_page_url}: {response.status_code}")

    def parse_detail(self, response, url):
        titulo = response.xpath('//title/text()').extract_first()
        marca = response.xpath('//span[contains(text(), "Marca")]/following-sibling::a/text()').extract_first()
        modelo = response.xpath('//span[contains(text(), "Modelo")]/following-sibling::a/text()').extract_first()
        km = response.xpath('//span[contains(text(), "Quilometragem")]/following-sibling::span/text()').extract_first()
        ano = response.xpath('//span[contains(text(), "Ano")]/following-sibling::a/text()').extract_first()
        tipo = response.xpath('//span[contains(text(), "Tipo")]/following-sibling::span/text()').extract_first()
        pot_motor = response.xpath('//span[contains(text(), "Potência do motor")]/following-sibling::span/text()').extract_first()
        kit_gnv = response.xpath('//span[contains(text(), "Possui Kit GNV")]/following-sibling::span/text()').extract_first()
        cor = response.xpath('//span[contains(text(), "Cor")]/following-sibling::span/text()').extract_first()
        combustivel = response.xpath('//span[contains(text(), "Combustível")]/following-sibling::a/text()').extract_first()
        portas = response.xpath('//span[contains(text(), "Portas")]/following-sibling::span/text()').extract_first()
        cambio = response.xpath('//span[contains(text(), "Câmbio")]/following-sibling::span/text()').extract_first()
        direcao = response.xpath('//span[contains(text(), "Tipo de direção")]/following-sibling::span/text()').extract_first()
        municipio = response.xpath('//span[contains(text(), "Município")]/following-sibling::span/text()').extract_first()
        if not municipio:
            municipio = response.xpath('//span/text()').re_first(r'([A-Za-zÀ-ÿ]+(?: [A-Za-zÀ-ÿ]+)*),\s\w{2},\s\d{8}')
        preco = response.xpath('/html/body/div[1]/div/div[3]/div[2]/div/div[2]/div[1]/div[20]/div/div/div/div[1]/div[1]/h2/text()').extract_first()
        if not preco:
            preco = response.xpath('//span[contains(text(), "R$")]/text()').extract_first()



        carro_data = {
            'titulo': titulo,
            'preco': preco,
            'marca': marca,
            'modelo': modelo,
            'km': km,
            'ano': ano,
            'tipo': tipo,
            'pot_motor': pot_motor,
            'kit_gnv': kit_gnv,
            'cor': cor,
            'combustivel': combustivel,
            'portas': portas,
            'cambio': cambio,
            'direcao': direcao,
            'municipio': municipio,
            'url': url
        }

        self.carros_data.append(carro_data)
        self.logger.info(f"Detalhes do carro: {carro_data}")
        df = pd.DataFrame(self.carros_data)
        df.to_csv("carros.csv", index=False)
        yield carro_data