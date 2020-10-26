import argparse
import os
import sys
import requests
from requests.auth import HTTPBasicAuth
from os import environ
from sodapy import Socrata

parser = argparse.ArgumentParser(description='Process data from parking violations.')
parser.add_argument('--page_size', type=int, help='how many rows to get per page - starts at page 1, not 0', required=True)
parser.add_argument('--num_pages', type=int, help='how many pages to get in total')
parser.add_argument('--start_date', nargs='?', type=str, default='07/01/2019', help='enter start date range. cannot be before May 2016. format: mm/dd/yyyy')
parser.add_argument('--end_date', nargs='?', type=str, default='08/01/2019', help='enter end date range. must enter if entered start date. must be after start date. format: mm/dd/yyyy')
args = parser.parse_args(sys.argv[1:])
#print(args.start_date)
#print(args.end_date)
nump = args.num_pages

DATASET_ID = os.environ["DATASET_ID"]
APP_TOKEN = os.environ["APP_TOKEN"]
ES_HOST = os.environ["ES_HOST"]
ES_USERNAME = os.environ["ES_USERNAME"]
ES_PASSWORD = os.environ["ES_PASSWORD"]

###test connection to Socrata 
#client = Socrata("data.cityofnewyork.us", APP_TOKEN,)
#rows = client.get(DATASET_ID, limit=1)
#print(rows)

###test connection to ES
#resp = requests.get(ES_HOST, auth=HTTPBasicAuth(ES_USERNAME, ES_PASSWORD))
#print(resp.json())

if __name__ == '__main__':

#create ES index

	try:
		resp = requests.put(
			# this is the URL to create parking "index"
			f"{ES_HOST}/parking",
			auth=HTTPBasicAuth(ES_USERNAME, ES_PASSWORD),
			# these are the "columns" of this database/table
			json={
				"settings": {
					"number_of_shards": 1,
					"number_of_replicas": 1
				},
				"mappings": {
					"properties": {
						"plate": { "type": "text" },
						"state": { "type": "text" },
						"license_type": { "type": "text" },
						"summons_number": { "type": "text" , "fields": { "raw": {"type": "keyword"}}},
						"issue_date": { "type": "date" , "format": "yyyy-MM-dd HH:mm" },
						"violation": { "type": "text" },
						"fine_amount": { "type": "float" },
						"penalty_amount": { "type": "float" },
						"interest_amount": { "type": "float" },
						"reduction_amount": { "type": "float" },
						"payment_amount": { "type": "float" },
						"amount_due": { "type": "float" },
						"precinct": { "type": "integer" },
						"county": { "type": "text" },
						"issuing_agency": { "type": "text" },
						"violation_status": { "type": "text" },
					}
				}
			}
		)
		resp.raise_for_status()
		print(resp.json())
	except Exception as e:
		print(f"Error!: {e}, Index already exists! Skipping")

    ##get data from Socrata and create doc in ES

	client = Socrata(
		"data.cityofnewyork.us",
		APP_TOKEN,
		timeout = 60,
	)

	p = 'issue_date > "{start}" AND issue_date < "{end}"'.format(start=args.start_date, end=args.end_date)
	print("Dataset filters: " + p)
	#rows = client.get(DATASET_ID, limit=args.page_size, where=p)
	#r = client.get(DATASET_ID, select='COUNT(*)', where=p )
	#print(r)
	
	def violations(rows):
		r = []
		for row in rows:
			t = row["violation_time"]
			#remove unwanted attribute
			df = row
			df.pop("summons_image")
			df.pop("violation_time")
			df.pop("judgment_entry_date", None)

			try:
				# convert 
				row["precinct"] = int(row["precinct"])
				row["fine_amount"] = float(row["fine_amount"])
				row["interest_amount"] = float(row["interest_amount"])
				row["reduction_amount"] = float(row["reduction_amount"])
				row["amount_due"] = float(row["amount_due"])
				row["penalty_amount"] = float(row["penalty_amount"])
				row["payment_amount"] = float(row["payment_amount"])
				##can only run once per row
				#convert PM to military time
				if t[-1] == 'p' or t[-1] == 'P' :
					h = int(t[0:2]) + 12
					h = str(h)
					if h == '24':
						h = '00'
					#print(h)
				#elif t[-1] == 'P':
					#h = int(t[0:2]) + 12
					#h = str(h)
					#print(h)
				else:
					h = t[0:2]
				t = h + ':' + t[3:5] 
				#convert to ES date format yyyy-MM-dd HH:mm
				s = row["issue_date"]
				row["issue_date"] = s[6:] + '-' + s[0:2] + '-' + s[3:5] + ' ' + t
			except Exception as e:
				print(f"Error!: {e}, skipping row: {row}")
				continue

			try:
				# upload to elasticsearch by creating a doc
				resp = requests.post(
					# this is the URL to create a new parking document
					f"{ES_HOST}/parking/_doc/",
					json=row,
					auth=HTTPBasicAuth(ES_USERNAME, ES_PASSWORD),
				)
				resp.raise_for_status()
			except Exception as e:
				print(f"Failed to insert in ES: {e}, skipping row: {row}")
				continue
			r.append(resp.json())
		return [print(i) for i in r]
	
	#violations(rows)

	i=1
	while i <= nump:
		print(f"page {i}")
		resp = client.get(DATASET_ID, limit=args.page_size, offset=i*args.page_size, where=p)
		violations(resp)
		#print(resp)
		i += 1
