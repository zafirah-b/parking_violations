# parking_violations
*NYC Open Data - Open Parking and Camera Violations Dataset Analysis*

Link: https://github.com/zafirah-b/parking_violations/blob/main/README.md

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

# Violations Count by Agency and Fine amounts
![Image][1]

[1]:https://github.com/zafirah-b/parking_violations/blob/main/kibana%20dashboard%20-%20count%20by%20agency1.PNG

* This bar chart shows that the most violations are given out by the Traffic agency, followed by Department of Transportation (DOT) and Police Department. Upon inspection of the data, police department appears to be the same as Traffic agency as it reports precincts; whereas the DOT always reports precinct as 0. This could be addressed with data cleaning.
* All violations by the DOT have a fine amount of $50, whereas the fine amount for Traffic violations vary depending on the violation. Some of the Traffic violations are more costly, at a fine of $115. The $115 fines correspond to the most ticketed items - *no standing* and *no parking*.

# Violations Dashboard (by agency and precinct)
![Chart 2](https://github.com/zafirah-b/parking_violations/blob/main/kibana%20dashboard%20-%20Heat%20map%20violations1.PNG)

* On this heat map dashboard, we see that the most violations issued by the Traffic agency are in Manhattan (NY) for *no standing-day/time limits*. 
* The most violations issued by precinct 19 are for *double parking*, precinct 14 for *failing to display muni meter receipt*, and by precinct 18 for *no standing-day/time limits*. The precincts shown are the precincts with the most violations.

# Violations Issued by DOT
![Chart 5](https://github.com/zafirah-b/parking_violations/blob/main/kibana%20dashboard%20-%20Heat%20map%20violations%20DOT.PNG)
* From this heat map, we see that the most violations issued by the DOT are for *school zone speed*, with second most for *failure to stop at red light*. This makes sense because a red traffic light is clearly visible and normally in a spot a driver would expect, rather than a school zone speed restriction where the signs may unexpected and overlooked. Also, failure to stop at a red light is more imminently dangerous to the driver than a school zone speed restriction.

# Violations over a 24-hr period
![Chart 3](https://github.com/zafirah-b/parking_violations/blob/main/kibana%20dashboard%20-%20violations%20by%20time.PNG)

* These plots show violations count over a 24-hr period. Gaps in the curve may be due to data rows that were not yet loaded for the specific timeframe.
* The *School Zone* violation plot appears to have a more consistent count over time with less drastic peaks as that of *No Standing* violation plot. This makes sense because the *School Zone* violations are issued by the DOT and detected/reported via camera so there is constant monitoring of those locations.
* In contrast, the *No standing* violations are issued by Traffic agency by officers on foot. This plot has many peaks. This makes sense because the locations are spot checked by officers during their walking route so violations are not constantly picked up. Once an officer passes a location during their shift, any violations that occur after may be underreported.

# Violations Status by Type
![Chart 4](https://github.com/zafirah-b/parking_violations/blob/main/kibana%20dashboard%20-%20violation%20status1.PNG)

* It appears that the most contested violations are *no standing* and *double parking*. This makes sense because as discussed previously, these are issued by officers and  there isn't photo evidence like there is for DOT camera-detected violations, which are not contested much.

