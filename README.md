# parking_violations
*NYC Open Data - Open Parking and Camera Violations Dataset Analysis*

## Instructions
* Place unzipped Project01 folder in a folder you can access
* Navigate to that folder in the terminal and open it using `cd`
* To build the Docker image, enter in terminal `docker build -t parking:1.0 .`
* To run the Docker image, enter the below command after following these steps:
  * replace ES Host, ES Username and ES Password with the values of the ElasticSearch instance you will be using 
  * enter your Socrata App Token you registered for
  * this program takes 4 arguments, page_size is required. replace x with the number of rows you'd like. Counting starts at Page 1, not 0.
  * optional: replace y with the number of pages you'd like (if page size is 1,000, then num_pages of 2 will upload 2,000 rows to ES)
  *Recommended to be no more than 5*
  * optional: --start_date=<date> --end_date=<date>
If desired, you can request data from a specific time range. The dates must be entered in the format mm/dd/yyyy.
If a start date is entered, please enter the end date as well, which should be after the start date.
Please note that adding date filters will result in a longer run time.
  
```
docker run \
  -v ${PWD}:/app \
  --network="host" \
  -e DATASET_ID="nc67-uf89" \
  -e APP_TOKEN="SOCRATA APP TOKEN" \
  -e ES_HOST="ES URL" \
  -e ES_USERNAME="YOUR ES MASTER USERNAME" \
  -e ES_PASSWORD="YOUR ES MASTER PASSWORD" \
  parking:1.0 --page_size=x --num_pages=y --start_date=<date> --end_date=<date>
```

## Design Considerations
* For the ElasticSearch index mapping:
  * index *opcv* is created
  * text fields were labeled as keyword in order to be searchable in Kibana for visualizations.
  * date format was specified as *"yyyy-MM-dd HH:mm"*, as per documentation. 
  This information is found in 2 fields in the raw data, which needed to be combined and reformatted to match the above format.
  The raw data included an A or P (AM/PM) with the time. I used this to convert the times into military time so it would correspond with the format.
* From the raw data, I removed the *'judgment_entry_date'*, as it only appeared occasionally, and *'summons_image'* which is a link.
While the information contained in the summons image is useful for further analysis, more processing would be needed to obtain the information from the image.
* For the function, I added date filters so that a dataset for a specific range could be obtained, in order to perform meaningful analysis. 
However this resulted in the call taking longer to run, and each subsequent run takes even longer. This could be improved
by considering the data structure and time complexity for the search when redesigning the code. Prior to adding threading, this function worked as expected, but after I added the threading for some reason the data returned is offset by a year. I was unable to debug this.
* Added threading functionality so that each request doesn't wait on the current one to finish before starting. The number of threads is based on num_pages which is why num_pages is recommended to be a maximum of 5.
* Initially there was an if statement to check that the total rows requested didn't exceed the number of filtered rows available but I removed it because when page_size was large (100,000) it took too long to run. In addition, that check had to be performed before loading any data.

## Data Analysis

![Image][1]

[1]:https://github.com/zafirah-b/parking_violations/blob/main/kibana%20dashboard%20-%20count%20by%20agency1.PNG

![Image][1]

[1]https://github.com/zafirah-b/parking_violations/blob/main/kibana%20dashboard%20-%20Heat%20map%20violations1.PNG


![Image][1]

[1]https://github.com/zafirah-b/parking_violations/blob/main/kibana%20dashboard%20-%20violations%20by%20time.PNG

![Image][1]

[1]https://github.com/zafirah-b/parking_violations/blob/main/kibana%20dashboard%20-%20violation%20status1.PNG

* need Kibana Dashboard attachment in folder
