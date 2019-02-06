import requests
from bs4 import BeautifulSoup
import pymongo
import configparser


def connect_database():
    '''
        connect to mongodb
        @return db object
    '''
    config = configparser.ConfigParser()        
    config.read('config.ini')
    db_conf = config["DATABASE"]

    conn_str = 'mongodb://{0}:{1}@{2}:{3}/{4}'.format(db_conf["user"],
                                                          db_conf["password"],
                                                          db_conf["host"],
                                                          db_conf["port"],
                                                          db_conf["dbname"])
    conn = pymongo.MongoClient(conn_str)
    return conn[db_conf["dbname"]]    

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
    num_pages =  int(page_text.strip().split(" ")[5].replace(".","")) #  quebra o texto e paga o num de paginas
    
    header = []
    t_info = []  
    for i in range(int(num_pages)):
        if i>1: break
        # pega os dados da tabela por pagina i
        html_page = requests.get(LINK + FILTER.format(i))
        soup   = BeautifulSoup(html_page.text, 'html.parser') 
        table  =  soup.find('table', {'id': 'salarios-magistrados'})    
        trs    =  table.findAll('tr')
        
        for line in trs:            
            if '<th>' in str(line) and len(header) == 0:
                ths = line.findAll('th')        
                for data in ths:                    
                    header.append(data.text)     
                continue
                # print result            
            tds = line.findAll('td')                        
            data_dict = {} 
            for pos in range(len(header)):
                data_dict[header[pos]] = tds[pos].text if len(tds)> pos else ''   
            t_info.append(data_dict)
          
    # GRAVA OS DADOS NO BANCO             
    try:
        db = connect_database()
        for data in t_info:
            db["info_salarios"].update_one(data,{'$set': data },upsert=True)
    except Exception as e:
        print('error inserting data: {}'.format(str(e))) 
      
if __name__ == '__main__':
    try:
        print('started script')
        run()
        print('finished script')
    except Exception as e:
        print('error processing -- {}'.format(str(e)))