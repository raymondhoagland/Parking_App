import mechanize
from BeautifulSoup import BeautifulSoup
from time import sleep
br = mechanize.Browser()
br.set_handle_robots(False)
br.set_handle_refresh(False)
br.addheaders = [('User-agent', 'Firefox')]

def access_sweeps():
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

				#handle special per number case
				streetname = new_blocks[0]
				schedule[streetname] = []
				if(streetname in new_blocks[1:]):
					special_handle()

				#handle general situation
				else:
					for i in range(1, len(new_blocks)):
						schedule[streetname].append(new_blocks[i])

			#catch bad entries		
			except IndexError:

				#return to selection page
				br.back()
				br.select_form(nr=0)
				continue

			def special_handle():

				#possible cleaning days
				weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
				
				#name of the street
				streetname = new_blocks[0]

				#2nd-order dictionary
				schedule[streetname] = {}

				#locate the schedule
				td = soup.find('td', width='605', valign = 'top')
				pars = td.findAll('p')
				
				for piece in pars:

					#find the correct paragraphs
					if('Addresses' in str(piece)):
					
						#split and find the days 
						pices = str(piece).replace(' -', '-').split()
						days = []

						#add all days for this 
						idx = 1
						for i in range(1, len(pices)):

							#if it is a weekday, add it in
							pices[i] = str(pices[i]).replace(',', '')
							if(pices[i] in weekdays):
								days.append(pices[i])
							
							#otherwise get the street number index and break
							else:
								idx = i+1
								break

						#get street numbers
						street_num = pices[idx]

						#set up the 2nd-order dict
						schedule[streetname][street_num] = days

			#return to selection page
			sleep(1)
			br.back()
			br.select_form(nr=0)

		#open output file
		output = open('database_test.txt', 'wb')
		
		#go through all streetnames
		for streetname in schedule.keys():
			output.write(streetname+' ')
			#print streetname

			#if 2nd order dict, handle it
			if(type(schedule[streetname]) is dict):
				for key in schedule[streetname].iterkeys():
					output.write(key+' ')
					for val in schedule[streetname][key]:
						output.write(val+' ')
					#output.write('\n')
					#print key, schedule[streetname][key]

			#output all possible days
			else:
				for day in schedule[streetname]:
					output.write(' ' + day)
					#print day

			#write the newline
			output.write('\n')
		output.close()

access_sweeps()