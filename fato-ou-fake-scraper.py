import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
import re
import os

class FatoOuFakeScraper:
    """
    Classe para extrair notícias da seção Fato ou Fake do G1
    e criar um dataset estruturado de checagens de notícias falsas.
    """
    
    def __init__(self, num_pages=5):
        """
        Inicializa o scraper.
        
        Parâmetros:
        num_pages (int): Número de páginas a serem extraídas (padrão: 5)
        """
        self.base_url = "https://g1.globo.com/fato-ou-fake/"
        self.num_pages = num_pages
        self.dataset = []
    
    def extrair_pagina(self, url):
        """
        Extrai conteúdo de uma página.
        
        Parâmetros:
        url (str): URL da página a ser extraída
        
        Retorna:
        BeautifulSoup: Objeto contendo o HTML parseado
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar a página {url}: {e}")
            return None
    
    def extrair_noticias_da_pagina(self, soup):
        """
        Extrai as notícias de uma página parseada.
        
        Parâmetros:
        soup (BeautifulSoup): Objeto contendo o HTML parseado
        
        Retorna:
        list: Lista de dicionários com as informações das notícias
        """
        noticias = []
        
        # Localizando os elementos da página que contêm as notícias
        # Nota: Os seletores CSS podem precisar de ajustes conforme a estrutura atual do site
        artigos = soup.select('.feed-post-body')
        
        for artigo in artigos:
            try:
                # Obtendo os elementos da notícia
                titulo_element = artigo.select_one('.feed-post-link')
                if not titulo_element:
                    continue
                
                titulo = titulo_element.get_text().strip()
                link = titulo_element['href']
                
                # Verificar se é uma checagem Fato ou Fake
                if not self._eh_checagem_fato_ou_fake(titulo, link):
                    continue
                
                # Extrair data da publicação
                data_element = artigo.select_one('.feed-post-datetime')
                data = data_element.get_text().strip() if data_element else "Data não encontrada"
                
                # Extrair resumo/subtítulo
                resumo_element = artigo.select_one('.feed-post-body-resumo')
                resumo = resumo_element.get_text().strip() if resumo_element else ""
                
                # Extrair imagem (se disponível)
                img_element = artigo.select_one('.feed-post-figure img')
                imagem_url = img_element['src'] if img_element and 'src' in img_element.attrs else ""
                
                # Determinar se é FATO ou FAKE com base no título ou resumo
                classificacao = self._classificar_checagem(titulo, resumo)
                
                # Extrair conteúdo detalhado da página da notícia
                detalhes = self._extrair_detalhes_noticia(link)
                
                noticia = {
                    'titulo': titulo,
                    'link': link,
                    'data_publicacao': data,
                    'resumo': resumo,
                    'classificacao': classificacao,
                    'imagem_url': imagem_url,
                    'conteudo': detalhes.get('conteudo', ''),
                    'tags': detalhes.get('tags', []),
                    'autor': detalhes.get('autor', ''),
                    'data_extracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                noticias.append(noticia)
                
            except Exception as e:
                print(f"Erro ao processar artigo: {e}")
                continue
        
        return noticias
    
    def _eh_checagem_fato_ou_fake(self, titulo, link):
        """
        Verifica se a notícia é uma checagem Fato ou Fake.
        
        Parâmetros:
        titulo (str): Título da notícia
        link (str): Link da notícia
        
        Retorna:
        bool: True se for uma checagem, False caso contrário
        """
        # Verificar pelo link se contém 'fato-ou-fake'
        if 'fato-ou-fake' in link.lower():
            return True
        
        # Verificar por palavras-chave no título
        keywords = ['fato', 'fake', 'falso', 'verdade', 'é falso que', 'é verdade que', 'checamos']
        for keyword in keywords:
            if keyword.lower() in titulo.lower():
                return True
        
        return False
    
    def _classificar_checagem(self, titulo, resumo):
        """
        Determina se o conteúdo foi classificado como FATO ou FAKE.
        
        Parâmetros:
        titulo (str): Título da notícia
        resumo (str): Resumo da notícia (não utilizado na classificação)
        
        Retorna:
        str: 'FATO', 'FAKE' ou 'INDETERMINADO'
        """
        # Considerar apenas o título para a classificação
        texto_titulo = titulo.lower()
        
        # Padrões comuns usados pelo G1 para indicar FAKE no título
        padroes_fake = [
            'é fake',
            'é falso', 
            'não é verdade', 
            'não é verdadeiro',
            'falso que', 
            'fake news',
            'boato', 
            'mentira', 
            'enganoso', 
            'não é real', 
            'não aconteceu',
            'não procede',
            'não existe',
            'não é fato'
        ]
        
        # Padrões comuns usados pelo G1 para indicar FATO no título
        padroes_fato = [
            'é fato', 
            'é verdade', 
            'verdadeiro', 
            'aconteceu', 
            'é real',
            'confirmado', 
            'verificado', 
            'comprovado',
            'procede',
            'é verdadeiro'
        ]
        
        # Verificar se é FAKE
        for padrao in padroes_fake:
            if padrao in texto_titulo:
                return 'FAKE'
        
        # Verificar se é FATO
        for padrao in padroes_fato:
            if padrao in texto_titulo:
                return 'FATO'
        
        # Verificar se é FAKE com base em apenas "fake" isolado
        if re.search(r'\bfake\b', texto_titulo, re.IGNORECASE):
            return 'FAKE'
            
        # Verificar se é FATO com base em apenas "fato" isolado
        if re.search(r'\bfato\b', texto_titulo, re.IGNORECASE):
            return 'FATO'
        
        # Se não foi possível determinar com certeza
        return 'INDETERMINADO'
    
    def _extrair_detalhes_noticia(self, url):
        """
        Extrai detalhes adicionais da página específica da notícia.
        
        Parâmetros:
        url (str): URL da notícia
        
        Retorna:
        dict: Dicionário com os detalhes da notícia
        """
        detalhes = {
            'conteudo': '',
            'tags': [],
            'autor': ''
        }
        
        soup = self.extrair_pagina(url)
        if not soup:
            return detalhes
        
        try:
            # Extrair conteúdo principal
            conteudo_elements = soup.select('.content-text__container p')
            conteudo = ' '.join([p.get_text().strip() for p in conteudo_elements])
            detalhes['conteudo'] = conteudo
            
            # Extrair tags (se disponíveis)
            tags_elements = soup.select('.entities__list-item')
            detalhes['tags'] = [tag.get_text().strip() for tag in tags_elements]
            
            # Extrair autor
            autor_element = soup.select_one('.content-publication-data__from')
            if autor_element:
                detalhes['autor'] = autor_element.get_text().strip()
            
        except Exception as e:
            print(f"Erro ao extrair detalhes da notícia {url}: {e}")
        
        return detalhes
    
    def percorrer_paginas(self):
        """
        Percorre múltiplas páginas para extrair notícias.
        
        Retorna:
        list: Lista de todas as notícias extraídas
        """
        todas_noticias = []
        
        print(f"[SCRAPER] Iniciando extração em {self.num_pages} páginas...")
        
        # Primeira página (principal)
        soup_primeira_pagina = self.extrair_pagina(self.base_url)
        if soup_primeira_pagina:
            noticias_pagina = self.extrair_noticias_da_pagina(soup_primeira_pagina)
            todas_noticias.extend(noticias_pagina)
            print(f"[SCRAPER] Página 1: {len(noticias_pagina)} notícias extraídas")
        
        # Percorrer páginas adicionais (se houver paginação)
        for i in range(2, self.num_pages + 1):
            # O formato de URL para páginas adicionais pode variar
            # Aqui estamos supondo um formato comum, mas pode ser necessário ajustar
            next_page_url = f"{self.base_url}?page={i}"
            
            soup_pagina = self.extrair_pagina(next_page_url)
            if soup_pagina:
                noticias_pagina = self.extrair_noticias_da_pagina(soup_pagina)
                todas_noticias.extend(noticias_pagina)
                print(f"[SCRAPER] Página {i}: {len(noticias_pagina)} notícias extraídas")
            else:
                print(f"[SCRAPER] Falha ao acessar página {i}")
                break
        
        return todas_noticias
    
    def executar_extracao(self):
        """
        Executa o processo completo de extração e processamento.
        
        Retorna:
        DataFrame: DataFrame pandas com todas as notícias extraídas
        """
        print(f"[SCRAPER] Extração iniciada")
        
        # Extrair notícias de todas as páginas
        self.dataset = self.percorrer_paginas()
        print(f"[SCRAPER] Concluído. Total: {len(self.dataset)} notícias extraídas")
        
        # Converter para DataFrame
        df = pd.DataFrame(self.dataset)
        
        return df
    
    def salvar_dataset(self, df, formato='csv'):
        """
        Salva o dataset no formato especificado.
        
        Parâmetros:
        df (DataFrame): DataFrame com os dados
        formato (str): Formato de saída ('csv' ou 'json')
        
        Retorna:
        str: Caminho do arquivo salvo
        """
        # Criar pasta 'datasets' se não existir
        if not os.path.exists('datasets'):
            os.makedirs('datasets')
        
        # Gerar nome do arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if formato.lower() == 'csv':
            filepath = f'datasets/fato_ou_fake_{timestamp}.csv'
            df.to_csv(filepath, index=False, encoding='utf-8')
        elif formato.lower() == 'json':
            filepath = f'datasets/fato_ou_fake_{timestamp}.json'
            df.to_json(filepath, orient='records', force_ascii=False, indent=4)
        else:
            raise ValueError(f"Formato '{formato}' não suportado. Use 'csv' ou 'json'.")
        
        print(f"[SCRAPER] Dataset salvo em: {filepath}")
        return filepath


# Exemplo de uso
if __name__ == "__main__":
    # Criar instância do scraper com 10 páginas
    scraper = FatoOuFakeScraper(num_pages=10)
    
    # Executar extração
    df_noticias = scraper.executar_extracao()
    
    # Exibir estatísticas básicas
    total_noticias = len(df_noticias)
    total_fake = len(df_noticias[df_noticias['classificacao'] == 'FAKE'])
    total_fato = len(df_noticias[df_noticias['classificacao'] == 'FATO'])
    total_indeterminado = len(df_noticias[df_noticias['classificacao'] == 'INDETERMINADO'])
    
    print(f"\nEstatísticas do Dataset:")
    print(f"Total de notícias: {total_noticias}")
    print(f"Classificadas como FAKE: {total_fake} ({total_fake/total_noticias*100:.1f}%)")
    print(f"Classificadas como FATO: {total_fato} ({total_fato/total_noticias*100:.1f}%)")
    print(f"Classificação indeterminada: {total_indeterminado} ({total_indeterminado/total_noticias*100:.1f}%)")
    
    # Salvar em CSV e JSON
    scraper.salvar_dataset(df_noticias, formato='csv')
    scraper.salvar_dataset(df_noticias, formato='json')