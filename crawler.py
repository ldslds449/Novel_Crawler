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

  def get_bookName(self) -> str:
    soup = BeautifulSoup(self.content, 'html.parser')
    # find the name of the novel
    self.name = soup.find('span', class_='title').getText()
    return self.name

  def get_chapter_list(self) -> List[str]:
    soup = BeautifulSoup(self.content, 'html.parser')
    # find chapter list
    self.chList = soup.find(id='chapter-list').find_all('a')
    self.chList = [f"https:{x.get('href')}" for x in self.chList]
    return self.chList

  def get_book_info(self):
    pass

  def crawl(self) -> Union[str, None]:
    # create folder
    if not path.exists(self.saveFolder):
      if len(self.saveFolder) > 0:
        makedirs(self.saveFolder)

    fileName = sanitize_filename(self.name) + '.txt'

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

