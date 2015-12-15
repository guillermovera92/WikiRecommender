# WikiRecommender
### Asra Nizami, Guillermo Vera and Sam Horlbeck Olsen

## Before using:
- Clone this repository
- Download [this](https://drive.google.com/a/macalester.edu/file/d/0BztV2ktprAPMcmhTMkJzMzBhU0E/view?usp=sharing) zip file and extract it in the same directory where you cloned the repository. Make sure the extracted directory is called 'classified' and it contains several JSON files.
- Alternatively, you can download the entire project (including the JSON files from the above step) from [here](https://drive.google.com/a/macalester.edu/file/d/0BztV2ktprAPMSXVkLUdhZG9oSXc/view?usp=sharing). Extract it and you're ready to use the recommender

## What you can do:
- Run `python recommender.py` and follow the instructions to get recommendations.
- Run `python scraper.py "[starting term]" [max num links]` to test the scraper with any starting query and a maximum number of links. This will also print a small information block for each page.
- Run `python classifier.py` to train and test a classifier and print the accuracy and precision of the test (This is the only way of getting that information)

## Important limitations:
For some reason the [wikiapi](https://github.com/richardasaurus/wiki-api) that we used became unreliable halfway through the project. It still words but sometimes it gets stuck trying to get a page. We realized this mostly happens after a long period of not using the program and it usually resolves after stopping and starting the program again a few times. If that does not resolve the issue, leave the program running for a few minutes and then try again. We can't explain why this works (or even if) but it *seems* to work for us.
