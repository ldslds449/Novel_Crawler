import requests
from os import path, makedirs
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from typing import List, Union

class Crawler:

  def __init__(self, url:str, saveFolder:str) -> None:
    self.url = url
    self.saveFolder = saveFolder

  def fetch(self) -> str:
    # get content of the url
    self.content = requests.get(self.url).text
    return self.content

  def get_chapter_list(self) -> List[str]:
    soup = BeautifulSoup(self.content, 'html.parser')
    # find chapter list
    self.chList = soup.find(id='chapter-list').find_all('a')
    self.chList = [f"https:{x.get('href')}" for x in self.chList]
    return self.chList

  def get_book_info(self) -> dict:
    self.book_info = {}
    soup = BeautifulSoup(self.content, 'html.parser')
    self.book_info['title'] = soup.find('span', class_='title').getText()
    self.book_info['author'] = soup.find('span', class_='author').find('a').getText()
    self.book_info['cover'] = soup.find('div', class_='thumbnail').find('img').attrs['src']

    rows = soup.find('div', class_='state').find_all('tr')
    for row in rows:
      cols = row.find_all('td')
      name = cols[0].getText().strip().replace(' ', '')
      if name == '連載狀態':
        self.book_info['state'] = cols[1].getText().strip()
      elif name == '收藏數':
        self.book_info['save'] = int(cols[1].getText().strip())
      elif name == '觀看數':
        self.book_info['view'] = int(cols[1].getText().strip())
      elif name == '更新時間':
        self.book_info['update'] = cols[1].getText().strip()
      elif name == '分類':
        self.book_info['category'] = cols[1].getText().strip()

    return self.book_info

  def crawl(self, fileName:Union[str, None]) -> Union[str, None]:
    # create folder
    if not path.exists(self.saveFolder):
      if len(self.saveFolder) > 0:
        makedirs(self.saveFolder)

    if fileName is None:
      fileName = sanitize_filename(self.book_info['title']) + '.txt'
    elif not fileName.endswith('.txt'):
      fileName = fileName + '.txt'

    # fetch contents of all chapter
    with open(path.join(self.saveFolder, fileName), 'w', encoding='utf-8') as fp:
      for ch_url in self.chList:
        res = requests.get(ch_url)
        s = BeautifulSoup(res.text, 'html.parser')
        content = s.find('div', class_ = 'content')
        fp.write(content.text)
        fp.write('\n\n\n' + '=='*30 + '\n\n\n')

        yield ch_url

    return None

