import requests
from bs4 import BeautifulSoup
import csv

def run():       
    
    LINK     = 'https://brasil.io/dataset/salarios-magistrados'
    FILTER   = '?cargo=DESEMBARGADOR&page={0}' 
    
    html_page = requests.get(LINK + FILTER.format(1))
    # BUSCAR NUMERO DE PAGINAS EXISTENTES
    soup   =  BeautifulSoup(html_page.text, 'html.parser') 
    ul     =  soup.find('ul', {'class': 'pagination right'})
    li     =  ul.findAll('li')
    li     =  li[0]
    page_text = li.text # pega o conteudo do elemtno li
    num_pages =  page_text.strip().split(" ")[5] #  quebra o texto e paga o num de paginas
    
    header = []
    t_info = []
    
    for i in range(int(num_pages)):
        
        # pega os dados da tabela por pagina i
        html_page = requests.get(LINK + FILTER.format(i))
        soup   = BeautifulSoup(html_page.text, 'html.parser') 
        table  =  soup.find('table', {'id': 'salarios-magistrados'})    
        trs    =  table.findAll('tr')
        
        for line in trs:            
            if '<th>' in str(line) and len(header) == 0:
                ths = line.findAll('th')        
                for data in ths:                    
                    header.append(data.text.encode("utf-8"))     
                continue
                # print result            
            tds = line.findAll('td') 
                       
            data_dict = {} 
            for pos in range(len(header)):
                data_dict[header[pos]] = tds[pos].text.encode("utf-8") if len(tds)> pos else ''   
            t_info.append(data_dict)
          
    # GRAVA OS DADOS EM ARQUIVO CSV
    with open('salarios.csv', 'w') as csvfile:      
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        for data in t_info:
            writer.writerow(data)
      
run() 
