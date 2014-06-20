import mechanize
from BeautifulSoup import BeautifulSoup
from time import sleep
import json

br = mechanize.Browser()
br.set_handle_robots(False)
br.set_handle_refresh(False)
br.addheaders = [('User-agent', 'Firefox')]

def access_sweeps():

	def special_handle(found_extra):

		#possible cleaning days
		weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
		
		#name of the street
		streetname = new_blocks[0]

		#2nd-order dictionary
		schedule[streetname] = {}
		if(found_extra == 0):
			schedule[streetname]['All'] = []
			for i in range(1, len(new_blocks)):
				schedule[streetname]['All'].append(new_blocks[i])
		else:
		
			#locate the schedule
			td = soup.find('td', width='605', valign = 'top')
			pars = td.findAll('p')
			
			for piece in pars:

				#find the correct paragraphs
				if('Addresses' in str(piece)):
				
					#split and find the days 
					pices = str(piece).replace(' -', '-').replace('- ', '-').split()
					days = []

					#add all days for this 
					idx = 1
					for i in range(1, len(pices)):

						#if it is a weekday, add it in
						pices[i] = str(pices[i]).replace(',', '')
						if(pices[i].replace('-odd','').replace('-even', '') in weekdays):
							days.append(pices[i])
						
						#otherwise get the street number index and break
						else:
							idx = i+1
							break

					#get street numbers
					street_num = pices[idx]

					#set up the 2nd-order dict
					schedule[streetname][street_num] = days
		print schedule[streetname]

	#construct the url
	url = 'http://archive.cityofpaloalto.org/forms/streetsweeping/streetsweeping.lasso'

	#hash table and counter
	schedule = {}
	num = 0

	#open the page, select the form and find the control
	resp = br.open(url)
	search_val = 'st_id'
	br.select_form(nr=0)
	control = br.form.find_control(search_val)
	
	#make sure it exists and then begin
	if(control != None):
		#loop through all selections	
		for item in control.items:

			#skip the first one
			if(num == 0):
				num += 1
				continue
	
			#num += 1
			#if(num > 10):
			#	break

			#select the item and submit the page
			br[search_val] = [str(item),]
			response = br.submit().read()
			
			#find all bold words (street name and schedule)
			soup = BeautifulSoup(response)
			blocks = soup.findAll('strong')

			#remove extra parts
			new_blocks = []
			for block in blocks:
				new_blocks.append(str(block).replace('<strong>', '').replace('</strong>', '').replace('.', ''))

			#get streetname and days swept and add to hash
			try:
				found_extra = 0

				#handle special per number case
				streetname = new_blocks[0]
				schedule[streetname] = []
				streetname_no_suffix = streetname.split()
				streetname_no_suffix = ' '.join(streetname_no_suffix[0:len(streetname_no_suffix)-1])
				for i in range(1, len(new_blocks)):
					if(streetname_no_suffix in new_blocks[i]):
				#if(streetname_no_suffix in new_blocks[1:]):
						found_extra = 1
				special_handle(found_extra)

			#catch bad entries		
			except IndexError:

				#return to selection page
				br.back()
				br.select_form(nr=0)
				continue

			#return to selection page
			sleep(1)
			br.back()
			br.select_form(nr=0)

		#go through all streetnames
		with open('Info_JSON.json', "w") as f:
			json.dump([{'Street': s, 'AddressNumbers': k, 'Days': v} for s, k in schedule.iteritems() for k, v in schedule[s].iteritems()], f)

access_sweeps()