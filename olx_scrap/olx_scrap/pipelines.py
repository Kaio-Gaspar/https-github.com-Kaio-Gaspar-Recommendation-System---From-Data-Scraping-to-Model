import sqlite3
from itemadapter import ItemAdapter

class OlxScrapPipeline:
    
    def process_item(self, item, spider):
        # Insere os dados do item no banco de dados
        spider.conn.execute(''' 
        INSERT INTO carros (titulo, preco, marca, modelo, km, ano, tipo, pot_motor, kit_gnv, cor, combustivel, portas, cambio, direcao, municipio, url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
        ''', tuple(item.values()))  # Converte o item para uma tupla de valores
        spider.conn.commit()  # Comita a transação no banco
        return item

    def create_table(self, spider):
        # Cria a tabela carros se não existir
        spider.conn.execute('''
        CREATE TABLE IF NOT EXISTS carros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            preco TEXT,
            marca TEXT,
            modelo TEXT,
            km TEXT,
            ano TEXT,
            tipo TEXT,
            pot_motor TEXT,
            kit_gnv TEXT,
            cor TEXT,
            combustivel TEXT,
            portas TEXT,
            cambio TEXT,
            direcao TEXT,
            municipio TEXT,
            url TEXT
        );
        ''')
    
    def open_spider(self, spider):
        # Abre a conexão com o banco de dados
        spider.conn = sqlite3.connect('db.sqlite3')
        self.create_table(spider)  # Cria a tabela quando o spider inicia

    def close_spider(self, spider):
        # Fecha a conexão com o banco de dados quando o spider termina
        spider.conn.close()
