# Price modeling of Ford cars sold in Iowa
This project was completed as the final project an introductory Data Science class taken at Iowa State University.

## Motivation
Cars buying and selling is an enourmous industry. When faced with a car buying decision many people will check with [Kelley Blue Book](https://www.kbb.com) to see if the car is priced fairly. Since there exist few alternitive pricing models there is not sufficient checks and balances to insure that KBB's models are fair. We wanted to produce a model that could accuretely predict prices within our dataset so that an alternitive car price model exists.

## Process
To begin this process we set an Ubuntu server box working on scraping data from [Cars.com](https://www.cars.com/). This took several days as delays between requests are were used in good practice. The scraping was a two part process. First, the internal car ids were scraped. Afterwards, the car page associated with each car id is scraped and saved. Both parts can be seen in the [Scraper.py file](https://github.com/JosephNaberhaus/ds-201-car-price-predictor/blob/master/Scraper.py). 

Once the dataset was collected, the data needed to be cleaned. The html rendering of the data cleaning jupyter notebook can be seen [here](https://josephnaberhaus.github.io/ds-201-car-price-predictor/docs/DataCleaning.html). Models were then created with the cleaned data. [GitHub page showing models and model testing](https://josephnaberhaus.github.io/ds-201-car-price-predictor/docs/PriceModel.html).

# Contributors
- [Daniel Way](https://github.com/danielway) - Model Anylisis and Accuracy Interpreation
- [Joseph Naberhaus](naberhausj.com) - Web Scraping and Model Creation
