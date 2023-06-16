from bs4 import BeautifulSoup
import time
import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

dr = webdriver.Chrome()
base_url = "https://www.upwork.com/search/profiles/"
url = base_url + "?page={0}&q=english%20teacher"

def get_or_none(object):
    if object is None:
        return float('nan')
    return object.text.strip()

# Maks range(1, 501), ketentuan upwork
failed_to_load_ids = []
df = pd.DataFrame(columns=['profile', 'name', 'description', 'skills', 'earned', 'success_rate', 'salary', 'work_total', 'total_hours', 'avg_rate'])
for pageNum in range(1, 500):
    print(pageNum)
    url_page = url.format(pageNum)
    counter = 0

    page = ''
    while page == '':
        try:
            page = dr.get(url_page) 
            counter = 0
            break
        except:
            print("Counter: {}".format(counter))
            if counter == 10:
                print("Dah kelewat")
                break
            time.sleep(5)
            counter = counter + 1
            continue
        
    soup = BeautifulSoup(dr.page_source, 'lxml')

    worker_cards = soup.find_all('div', 'up-card-section up-card-hover')

    for worker_card in worker_cards:
        id = worker_card['data-test-key'].replace('null', '')
        name = get_or_none(worker_card.find('div', 'identity-name'))
        description = get_or_none(worker_card.find('div', 'up-line-clamp-v2 clamped'))
        skill_objects = worker_card.find_all('div', 'up-skill-badge')
        skills = []
        for skill_object in skill_objects:
            skills.append(skill_object.text.strip())
        skills = json.dumps(skills)
        earned = get_or_none(worker_card.find('div', 'profile-stats mb-10').contents[0].find('strong').contents[0])
        success_rate = get_or_none(worker_card.find('span', 'up-job-success-text'))
        salary = get_or_none(worker_card.find('div', 'profile-stats mb-10').contents[0].find('strong'))
        detail = dr.get(base_url+'?profile='+id)
        work_total = None
        total_hours = None
        avg_rate = None
        try:
            WebDriverWait(dr, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'stat-amount')))
            detail_soup = BeautifulSoup(dr.page_source, 'lxml')
            stats = detail_soup.find_all('div', 'stat-amount')
            work_total = get_or_none(stats[0].contents[0])
            total_hours = get_or_none(stats[1].contents[0])
            rate_objects = detail_soup.find_all('div', 'mt-20 mg-lg-0')
            rate = []
            total_rate = 0
            n_rate = 0
            for rate_object in rate_objects:
                rate_value = get_or_none(rate_object.find('strong'))
                if type(rate_value) == str:
                    total_rate += float(rate_value)
                    n_rate += 1
                rate.append(rate_value)
            if n_rate != 0:
                avg_rate = total_rate / n_rate
        except:
            failed_to_load_ids.append(id)
            print("Gagal load")
        data = [id, name, description, skills, earned, success_rate, salary, work_total, total_hours, avg_rate]
        df.loc[len(df)] = data

df.to_csv('upwork_english_teacher.csv', index=False)
df.to_excel('upwork_english_teacher.xlsx', index=False)


