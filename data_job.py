import os 
import sys
import time
import datetime
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import numpy as np
import tweepy
from text.search import get_twitter_cursor
from text.processing import TweetProcessor, TweetChecker
from text.sentiment import SentimentCounter, analyse_sentiment
from data_transfer.aws import AWSClient
from data_transfer.database import PSQLClient
from visualization.plotting import make_single_chart
from config import PATHS, CRYPTO_LIST, EMAIL_INFO, AWS_INFO, TWITTER_INFO, PSQL_HEROKU_CONN_STRING


# "https://stackoverflow.com/questions/6386698/using-the-logging-python-class-to-write-to-a-file"
logging.basicConfig(format="%(asctime)s - %(name)s - {%(pathname)s:%(lineno)d} - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def email_alert(error):
	from_address = EMAIL_INFO["email"]
	to_address = EMAIL_INFO["email"] 
	msg = MIMEMultipart()
	msg["From"] = from_address
	msg["To"] = to_address 
	msg["Subject"] = "CoinMoodBot: Data Update Job Failed"
	msg.attach(MIMEText(error, "plain"))
	# attachment
	with open(PATHS["update_logs"], "rb") as attachment:
		p = MIMEBase("application", "octet-stream")
		p.set_payload((attachment).read())
		encoders.encode_base64(p)
		p.add_header('Content-Disposition', "attachment; filename= %s" % PATHS["update_logs"])
	msg.attach(p) 
	session = smtplib.SMTP("smtp.gmail.com", 587)	
	session.starttls()
	session.login(from_address, EMAIL_INFO["password"]) 
	text = msg.as_string()
	# sending the mail
	session.sendmail(from_address, to_address, text)
	# terminating the session
	session.quit()


def sentiment_analysis_asset(asset, date, db_client, api_client):
    #sentiment_counter = SentimentCounter()
    #tweet_checker = TweetChecker(date=date)

    # Get last tweet id (day before yesterday)
    tweet_id_last = db_client.get_last_tweet_id(asset=asset, 
                                                date=date - datetime.timedelta(1))
    cursor = get_twitter_cursor(api=api_client,
                                asset=asset,
                                until=str(date+datetime.timedelta(1)),
                                since_id=tweet_id_last)
    for item in cursor.items():
        tweet = TweetProcessor(item)
        tweet.process_text()
        # Stop iterating if tweet is beyound start date
        if not tweet_checker.check_timestamp(ts=tweet.timestamp):
            break
        # Update max and min tweet_id
        tweet_checker.update(tweet.id)
        # Update sentiment count
        sentiment_counter.update(value=analyse_sentiment(tweet.text),
                                 is_popular=tweet.is_popular)
    # Insert results into sentiment table
    db_client.insert_sentiment(asset=asset,
                               upload_date=date,
                               min_tweet_id=id_checker.min_id,
                               max_tweet_id=id_checker.max_id,
                               counter=sentiment_counter
                               );


def sentiment_analysis_task(date):
    """
    Can be used as one-off manual task, for example when data_job failed.
    """
    # Initialize PSQL client to work with database
    psql_client = PSQLClient(conn_string=PSQL_HEROKU_CONN_STRING)

    # Initialize Twitter REST API client
    twitter_auth = tweepy.AppAuthHandler(consumer_key=TWITTER_INFO["api_key"],
                                         consumer_secret=TWITTER_INFO["api_secret"])
    twitter_api = tweepy.API(auth_handler=twitter_auth,
                             retry_count=3,
                             retry_delay=5,
                             retry_errors=set([401, 404, 500, 503]),
                             wait_on_rate_limit=True,
                             wait_on_rate_limit_notify=True)
    for asset in CRYPTO_LIST:
        sentiment_analysis_asset(asset=asset,
                                 date=date,
                                 db_client=psql_client,
                                 api_client=twitter_api
                                 );


def main():
    """
    This is wrapper-function to perform the whole cycle of everyday data update.
    """
    # Initialize PSQL client to work with database
    psql_client = PSQLClient(conn_string=PSQL_HEROKU_CONN_STRING)

    # Initialize AWS S3 client to send charts into Amazon Bucket
    aws_client = AWSClient(default_bucket=AWS_INFO["s3_bucket_name"], **AWS_INFO)

    # Initialize Twitter REST API client
    twitter_auth = tweepy.AppAuthHandler(consumer_key=TWITTER_INFO["api_key"],
                                         consumer_secret=TWITTER_INFO["api_secret"])
    twitter_api = tweepy.API(auth_handler=twitter_auth,
                             retry_count=3,
                             retry_delay=5,
                             retry_errors=set([401, 404, 500, 503]),
                             wait_on_rate_limit=True,
                             wait_on_rate_limit_notify=True)
    try:
        today_date = datetime.date.today()        
        tweets_date = today_date - datetime.timedelta(1) # Yesterday tweets
        logging.info("Starting data update job...")

        for asset in CRYPTO_LIST:
            # Search tweets and make sentiment analysis
            sentiment_analysis_asset(asset=asset,
                                     date=tweets_date,
                                     db_client=psql_client,
                                     api_client=twitter_api
                                     );
            # Read last period analytics from sentiment table
            start_date = today_date - datetime.timedelta(30)
            end_date = today_date - datetime.timedelta(1)            
            data = psql_client.select_asset_data(table_name="sentiment",
                                                 asset=asset,
                                                 start_date=start_date,
                                                 end_date=end_date)

            # Make new chart
            img_data = make_single_chart(data=data, asset=asset)
            obj_name = "_".join([asset, str(today_date)]) + ".png"
            # Send chart into bucket
            aws_client.save_object_into_bucket(obj=img_data, name=obj_name)
            # Delete old charts
            aws_client.delete_old_objects_from_bucket(pattern=asset, leave_n_last=30)
            # Get new URL of created chart
            url = aws_client.get_object_url(name=obj_name)
            # Update chart URL into chart table
            psql_client.update_asset_link(asset=asset, url=url, ts=str(np.datetime64(datetime.datetime.now())));

        logging.info("Data update job is finished")
    
    except Exception as e:
        logging.exception("Something wrong with data update job")
        email_alert(str(e))          


if __name__=="__main__":
	main()
