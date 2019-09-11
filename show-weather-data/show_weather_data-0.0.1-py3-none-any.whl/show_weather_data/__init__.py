import webbrowser
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from datetime import datetime


class gather_input():
	'''
		code to list menu for user Input
	'''
	def __init__(self):
		print("***Weather Forecast Application***")
		print("==================================")
		while True:
			option = int(input("\nSelect an Option\n 1. List Cities 2. Enter City Name 3.Quit :- "))
			if option == 1:
				print("Choose a City : ")
				try:
					city = int(input("1. Mumbai  2. Delhi  3. Bengaluru  4.Chennai\n"\
						  "5. Kolkata 6. Ahmedabad 7. Hyderabad 8. Pune\n"\
						  "9. Surat  10. Jaipur 11. Lucknow 12.Chandigarh :- "
						))
					if city > 12 or city < 1:
						print("invalid choice!!")
						continue
					time = input("\n Enter Time (Format:- Yes/No) :- ")
					forecast = input("\n Enter Forecast \n options 1) 10 days 2) Default=Daily ")
					show_weather_data(city, time, forecast)	
					
				except ValueError:
					print("Sorry, Invalid Input.")
			elif option == 2:
				city_name = input("Enter City Name:- ")
				input("\n Enter Time :- ")
				input("\n Enter Forecast :- ")
				filter_by_city(city_name)
			else:
				break


def show_weather_data(city, time, forecast):
	city_lis =[]
	more_data_text = []
	more_data_value = []
	url = "https://weather.com/en-IN/"
	page_src = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	webpage = urlopen(page_src).read()
	soup = BeautifulSoup(webpage, 'html.parser')
	data = soup.findAll('div', attrs={"class":"styles__citiesContainer__31KL6"})
	for div in data:
	    links = div.findAll('a')
	    for a in links:
	        city_lis.append(a['href'])
	if city == 1:
		nxt_link = city_lis[0]
	elif city == 2:
		nxt_link = city_lis[1]
	elif city == 3:
		nxt_link = city_lis[2]
	elif city == 4:
		nxt_link = city_lis[3]
	elif city == 5:
		nxt_link = city_lis[4]
	elif city == 6:
		nxt_link = city_lis[5]
	elif city == 7:
		nxt_link = city_lis[6]
	elif city == 8:
		nxt_link = city_lis[7]
	elif city == 9:
		nxt_link = city_lis[8]
	elif city == 10:
		nxt_link = city_lis[9]
	elif city == 11:
		nxt_link = city_lis[10]
	elif city == 12:
		nxt_link = city_lis[11]
	# uncomment below line to open web page
	#new_page = webbrowser.open('https://weather.com'+nxt_link)
	new_page_url = 'https://weather.com'+nxt_link
	new_html_src = Request(new_page_url, headers={'User-Agent': 'Mozilla/5.0'})
	new_web_page = urlopen(new_html_src).read()
	soup_new = BeautifulSoup(new_web_page, 'html.parser')
	if bool(time):
		if time == 'No':
			pass
		else:
			filter_with_time(new_page_url)
	if bool(forecast):
		if forecast == '3':
			pass
		else:
			filter_with_forecast(new_page_url, forecast)
	for weather_data in soup_new.findAll('div',attrs={"class":"today_nowcard-temp"}):
		 temprature = weather_data.find('span', class_='').text
		 weather_description = soup_new.find('div', attrs={"class":"today_nowcard-phrase"}).text
		 wind_speed = soup_new.find('div', attrs={"class":"today_nowcard-sidecar component panel"})
		 for th in wind_speed.find_all('tr'):
		 	for th_data in th.findAll('th'):
		 		more_data_text.append(th_data.text)
		 for td_data in wind_speed.find_all('td'):
	 		for span_data in td_data.findAll('span', class_=''):
	 			if span_data.span:
	 				pass
	 			more_data_value.append(span_data.text)
		 print("temperature :- ", temprature, "\n"
		 	   "Weather Description :- ", weather_description
		 	)
		 unique_list = list(dict.fromkeys(more_data_value))
		 res = {}
		 for key in more_data_text:
		 	for value in unique_list:
		 		res[key] = value
		 		unique_list.remove(value)
		 		break  
	for k, v in res.items():
		print(k, " :- ",  v)


def filter_with_forecast(link, forecast):
	tenday_link = link.replace('today','tenday')
	page = requests.get(tenday_link)
	soup=BeautifulSoup(page.content,"html.parser")
	all=soup.find("div",{"class":"locations-title ten-day-page-title"}).find("h1").text
	table=soup.find_all("table",{"class":"twc-table"})
	l = []
	for items in table:
	    for i in range(len(items.find_all("tr"))-1):
	        d = {}  
	        d["day"]=items.find_all("span",{"class":"date-time"})[i].text
	        d["date"]=items.find_all("span",{"class":"day-detail"})[i].text
	        d["desc"]=items.find_all("td",{"class":"description"})[i].text 
	        d["temp"]=items.find_all("td",{"class":"temp"})[i].text 
	        d["precip"]=items.find_all("td",{"class":"precip"})[i].text
	        d["wind"]=items.find_all("td",{"class":"wind"})[i].text  
	        d["humidity"]=items.find_all("td",{"class":"humidity"})[i].text 
	        l.append(d)
	item = l[0]
	print("sample output!...")
	for key, value in item.items():
		print(key, " :- ",  value)
	print("Full data is saved as a csv file named output.csv")
	df = pd.DataFrame(l)
	try:
		df.to_csv("output.csv")
	except Exception as E:
		print(str(E))

def filter_with_time(link):
	hr_link = link.replace('today','hourbyhour')
	hr_data_src = Request(hr_link, headers={'User-Agent': 'Mozilla/5.0'})
	hr_web_page = urlopen(hr_data_src).read()
	soup_new = BeautifulSoup(hr_web_page, 'html.parser')
	
def filter_by_city(city_name):
	search = requests.get("https://weather.com/en-IN/weather/today/l/"+city_name)
	if search.status_code != 200:
		print("Searced City Not Found")

obj = gather_input() 