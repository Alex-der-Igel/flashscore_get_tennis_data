from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

#from lxml import html

from bs4 import BeautifulSoup

import re
import datetime, time

import pandas as pd


#create dataframes for tables
players = pd.DataFrame(columns=['id_player', 'name_player', 'dob', 'sex'])

ranks = pd.DataFrame(columns=['id_player', 'year', 'rank'])
match_stats = pd.DataFrame(columns=['id_match', 'set_num', 'game_home', 'game_away', 'set_duration'])

matches = pd.DataFrame(columns=['id_match', 'tournament', 'date', 'id_player_home', 'id_player_away', 'odd_home', 'odd_away'])




url = "https://www.flashscore.com/tennis/rankings/atp/"

options = Options()
options.add_argument("--headless")
options.add_argument('--ignore-ssl-errors')

blank_dob = datetime.date(2000, 1, 1)
blank_dob = int(time.mktime(blank_dob.timetuple()))

# create a new Firefox session
profile = webdriver.FirefoxProfile()
profile.set_preference('permissions.default.image', 2)
profile.set_preference("browser.cache.disk.enable", False)
profile.set_preference("browser.cache.memory.enable", False)
profile.set_preference("browser.cache.offline.enable", False)
profile.set_preference("network.http.use-cache", False) 


caps = DesiredCapabilities().FIREFOX
#caps["pageLoadStrategy"] = "normal"  #  complete
caps["pageLoadStrategy"] = "eager"  #  interactive не ждать загрузки всякой рекламы
#caps["pageLoadStrategy"] = "none"

driver = webdriver.Firefox(firefox_options = options, firefox_profile=profile, capabilities = caps)
driver.implicitly_wait(40)
driver.get(url)

info_players = BeautifulSoup(driver.page_source, "html.parser").find_all('tr', {'class': re.compile('^rank-row')})

print(len(info_players))

player_links = []
match_links = []
game_home = []
game_away = []
dur = []

for inf in info_players:
    player_links.append(inf.find('a').get('href'))
    
i = 0
m = 0
'''
for lin in player_links[605: 615]:
    print(i)
    
    while True:
        try:
            driver.get('https://www.flashscore.com' + lin)
        except:
            continue
        break
    
    src = driver.page_source
    soup = BeautifulSoup(src, "html.parser")
    
    #смотрим есть ли вообще сведения по игроку
    table = soup.find('table', {'class': 'base-table match-record-table'})
    
    if table is not None:
        i += 1
    else:
        continue        
    
    
    name = soup.find('div', {'class': 'team-name'}).text
    
    dob = soup.find('div', {'class': 'player-birthdate'})
    
    #проверяем, что дата рождения заполнена
    if dob is not None:
        dob = dob.find('script').text
        dob = int(dob[dob.find('getAge') + 7: dob.find(';') - 2])
    else:
        dob = blank_dob
        
    #добавляем в конец dataframe полученную запись
    players.loc[len(players)] =  [lin, name, dob, 1]
    
    entrs = table.find('tbody')
    entrs = entrs.find_all('tr')
    
    for rec in entrs:
        year = int(rec.find('td', {'class': 'season'}).text)
        rank = rec.find('td', {'class': 'rank'}).text
        if rank.find('.') > 0:
            rank = int(rank[0: rank.find('.')])
        else:
            rank = 2000
            
        ranks.loc[len(ranks)] =  [lin, year, rank]
  
players.to_csv('players.csv', sep = ';')
ranks.to_csv('ranks.csv', sep = ';')
'''     

for lin in player_links[0:10]:
    i += 1
    print('Current player: ', i, ' ', lin)
    
    while True:
        try:
            driver.get('https://www.flashscore.com' + lin + '/results/')
        except:
            continue
        break
        
    #нажимаем кномку load more для дозагрузки матчей
    
    WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.ID, "preload")))
   
    for cnt in range(0, 4):
        driver.execute_script("loadMoreGames('_s');")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.ID, "preload")))
        
    
   
    soup = BeautifulSoup(driver.page_source, "html.parser")
      
    table = soup.find('div', {'id': 'fs-results_s'}).find_all('tr', {'id': re.compile('^g_2')})
      
    print(len(table))
    
    for tab in table:
        
        m_l = tab.get('id')[4:]
        
        while True:
            try:
                driver.get('https://www.flashscore.com/match/' + m_l + '/#match-summary/')
            except:
                continue
            break
        
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "tab-match-summary")))
        
        soup = BeautifulSoup(driver.page_source, "html.parser")   
        
        if soup.find('div', {'class': 'info-status mstat'}).text == 'Walkover':
            continue
        
        m_t = soup.find('div', {'class': 'info-time mstat-date'}).text
         
        summ = soup.find('div', {'id':'summary-content'})
        sum_home = summ.find('tr', {'class': 'odd'})
        
        for scor in sum_home.find_all('td', {'class': re.compile('^score')}):
            if scor.get('class') == ['score']:
                if scor.find('strong') is not None:
                    set_home = int(scor.find('strong').text)
                    
            elif scor.find('span') is not None:
                game_home.append(int(scor.find('span').text))
                
                
        sum_away = summ.find('tr', {'class': 'even'})
        
        for scor in sum_away.find_all('td', {'class': re.compile('^score')}):
            if scor.get('class') == ['score']:
                if scor.find('strong') is not None:
                    set_away = int(scor.find('strong').text)
                    
            elif scor.find('span') is not None:
                game_away.append(int(scor.find('span').text))
               
        
        if soup.find('tfoot', {'class':'match-time'}) is not None:
            for tm in soup.find('tfoot', {'class':'match-time'}).find_all('td', {'class': 'score'}):
                if len(tm.text) > 0:
                    dur.append(int(tm.text[0: 1]) * 60 + int(tm.text[2: 4]))
        
        
        for s in range(0, len(game_home)):
            if len(dur) > 0:
                match_stats.loc[len(match_stats)] =  [m_l, s, game_home[s], game_away[s], dur[s + 1]]
            else:
                match_stats.loc[len(match_stats)] =  [m_l, s, game_home[s], game_away[s], None]
            
        game_home = []
        game_away = []
        dur = []
        
        tour = soup.find('th', {'class': 'header'}).find('a').text
           
        pl_home = soup.find('div', {'class': 'team-text tname-home'}).find('a').get('onclick')
        pl_home = pl_home[pl_home.find('/'): pl_home.find(')') - 1]
            
        pl_away = soup.find('div', {'class': 'team-text tname-away'}).find('a').get('onclick')
        pl_away = pl_away[pl_away.find('/'): pl_away.find(')') - 1]
        
               
        if soup.find('span', {'class': 'odds value'}) is not None:
            odd_home = soup.find('td', {'class': re.compile('^kx o_1')}).find('span', {'class': 'odds-wrap'}).text
            odd_away = soup.find('td', {'class': re.compile('^kx o_2')}).find('span', {'class': 'odds-wrap'}).text
            
        matches.loc[len(matches)] =  [m_l, tour, m_t, pl_home, pl_away, odd_home, odd_away]
        
        m += 1
        print('Total matches: ', m ,' ' , m_l)
       

match_stats.to_csv('match_stats.csv', sep = ';')
matches.to_csv('matches.csv', sep = ';')

driver.close()

    
    

