import requests; 
import re; 
from bs4 import BeautifulSoup; 
from time import sleep; 
import itertools; 
import json; 
from copy import deepcopy; 

class scrapper : 
	def __init__(self) : 
		upper_a = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
		num = [' ','0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

		self.searchKeys = [];  
		all = []
		all = upper_a + num

		for r in range(3, 4):
			for s in itertools.product(all, repeat=r):
				 self.searchKeys.append(''.join(s))
		self.outputFolder = "jsonOutput"; 
	
	def TabToDicLst(self,tabSoup): 
		trs = tabSoup.findAll('tr'); 
		headerLst = [re.sub('[^0-9a-zA-Z]',"",th.getText()) for th in trs[0].findAll('th')]; 
		retLst = []; 
		for tr in trs : 
			temp = {}; 
			for idx,td in enumerate(tr.findAll('td')) : 
				temp[headerLst[idx]] = td.getText().replace("\n","").replace("\n","").strip(); 
				anchors = td.findAll("a"); 
				if len(anchors) : 
					temp[headerLst[idx]]+= ","+anchors[0]["href"]
			retLst.append(temp); 
		return retLst; 

	def DataExtractor(self,page) : 
		if type(page) != type(BeautifulSoup()): 
			page = BeautifulSoup(page); 
		tab = page.findAll(id="PartyListView_GridViewParties")[0]; 
		rsl = self.TabToDicLst(tab); 
		return rsl; 
	def getData(self,searchKey) :
		dataLst = []; 
		prams = None; 
		baseUrl = "https://abr.business.gov.au/SearchByName.aspx?SearchText=%s" %searchKey; 
		s = requests.Session(); 
		res = s.get(baseUrl,verify=False,data=prams); 
		i = 1; 
		while True : 
			data = self.DataExtractor(res.text)
			dataLst.append(deepcopy(data)); 
			with open("res.html","w") as f : 
				f.write(res.text); 
			soup = BeautifulSoup(res.text); 
			__EVENTTARGET = soup.findAll(id="ButtonNext");
			if len(__EVENTTARGET)==0 :
				pDiv = soup.findAll(class_="container-content"); 
				if len(pDiv)>0: 
					p = pDiv[0].findAll("p"); 
					if len(p)>0 :
						dataLst.append(p[0].getText())
				break; 
			__EVENTTARGET = __EVENTTARGET[0]["name"];
			prams = {
				"__EVENTTARGET" : __EVENTTARGET,
				"__EVENTARGUMENT" : "",
				"__VIEWSTATE" : soup.findAll(id="__VIEWSTATE")[0]["value"],
				"__VIEWSTATEGENERATOR" :  soup.findAll(id="__VIEWSTATEGENERATOR")[0]["value"],
				"__EVENTVALIDATION" :  soup.findAll(id="__EVENTVALIDATION")[0]["value"],	
			}
			sleep(5); 
			for i in range(5):
				try :
					res = s.post(baseUrl,verify=False,data=prams)
					break; 
				except : 		
					print("Exception Happend count %s!" %i)
					sleep(10); 
					pass; 
		with open("%s/%s.json" %(self.outputFolder,searchKey),'w') as f:
			json.dump(dataLst,f,indent=4); 
		print("%s page count %s" %(searchKey,len(dataLst)))
		return dataLst; 

if __name__ == "__main__" : 
	obj = scrapper();
	outLst = []; 
	for key in obj.searchKeys: 
		obj.getData(key); 
	