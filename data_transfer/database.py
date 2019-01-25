import datetime
import numpy as np
import pandas as pd
import pandas.io.sql as psql
import psycopg2 as pg
from sqlalchemy import create_engine, text


class PSQLClient():
    def __init__(self, conn_string):
        self.engine = create_engine(conn_string)

    def insert_dataframe_into_table(self, data, table_name, **kwargs):
        data.to_sql(name=table_name, con=self.engine, **kwargs)
    
    def execute_query(self, query, **kwargs):
        """
        Insert and update operations.
        """
        psql.execute(sql=query, con=self.engine, **kwargs)

    def read_query(self, query, **kwargs):
        data = psql.read_sql(sql=query, con=self.engine, **kwargs)
        return data

    def get_last_tweet_id(self, asset, date, **kwargs):
        query = "select max_tweet_id "\
                "from sentiment where "\
                "asset='{asset}' and upload_date='{date}' "\
                "order by upload_date desc limit 1"\
                .format(asset=asset, date=date)
        return self.read_query(query)["max_tweet_id"].item()

    def insert_sentiment(self, asset, counter, **kwargs):
        query = "delete from sentiment where upload_date = :upload_date; "\
                "insert into sentiment "\
                "(upload_date, asset, positive, negative, neutral, "\
                "positive_popular, negative_popular, neutral_popular, "\
                "min_tweet_id, max_tweet_id) values"\
                "(:upload_date, :asset, :positive, :negative, :neutral, "\
                ":positive_popular, :negative_popular, :neutral_popular, "\
                ":min_tweet_id, :max_tweet_id);"
        self.engine.execute(query, 
                            upload_date=kwargs.get("upload_date"),
                            asset=asset,
                            positive=counter.counter["pos"],
                            negative=counter.counter["neg"],
                            neutral=counter.counter["neu"],
                            positive_popular=counter.counter_popular["pos"],
                            negative_popular=counter.counter_popular["neg"],
                            neutral_popular=counter.counter_popular["neu"],
                            min_tweet_id=kwargs.get("min_tweet_id"),
                            max_tweet_id=kwargs.get("max_tweet_id"),
                            );

    def select_asset_data(self, table_name, asset, **kwargs):
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        if start_date is not None and end_date is not None:
            date_filter = " and upload_date between '{start_date}' and '{end_date}' "\
                            .format(start_date=start_date, end_date=end_date)
        else:
            date_filter = ""
        
        query = "select upload_date, asset, positive, negative, neutral "\
                "from sentiment where asset='{}'".format(asset) + date_filter
        data = self.read_query(query, parse_dates=["upload_date"])
        return data

    def update_asset_link(self, **kwargs):        
        asset = kwargs.get("asset")
        url = kwargs.get("url")
        ts = kwargs.get("ts")
        query = text("update chart set upload_ts='{ts}', url= :url where asset='{asset}'; " \
                     "insert into chart (upload_ts, asset, url) "\
                     "select '{ts}', '{asset}', :url "\
                     "where not exists (select 1 from chart where asset='{asset}');"\
                     .format(asset=asset, ts=ts))
        self.engine.execute(query, url=url);

    def get_last_asset_link(self, asset):
        query = "select url from chart where asset='{asset}' "\
                "order by upload_ts desc limit 1"\
                .format(asset=asset)        
        res = self.read_query(query); 
        if res.shape[0]==0:
            return ""
        return res.url[0]

    def insert_user_feedback(self, comment, user_info, char_limit=1000):
        if len(comment)>char_limit:
            comment = "[First_{}_chars]:".format(char_limit) + comment[:char_limit]
        upload_ts = str(np.datetime64(datetime.datetime.now()))        
        query = text("insert into feedback " \
                     "(upload_ts, user_id, is_bot, first_name, last_name, "\
                     " username, language_code, comment) values "\
                     "(:upload_ts, :user_id, :is_bot, :first_name, :last_name, "\
                     " :username, :language_code, :comment );"
                     )
        self.engine.execute(query, 
                            upload_ts=upload_ts,
                            user_id=user_info.id,
                            is_bot=user_info.is_bot,
                            first_name=user_info.first_name,
                            last_name=user_info.last_name,
                            username=user_info.username,
                            language_code=user_info.language_code,
                            comment=comment
                            );
