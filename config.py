TOKEN = ""

PSQL_HEROKU_CONN_STRING = ""
#PSQL_HEROKU_CONN_STRING = ""

CHATBASE_API_KEY = ""

REQUEST_PARAMS = {"connect_timeout":    30,
                  "read_timeout":       30,
                  #"proxy_url":          "https://german3d:Zaebali1@us-wa.proxymesh.com:31280",                  
                  #"urllib3_proxy_kwargs": dict(headers="test:iDscwvTL")
                  }

TWITTER_INFO = {"api_key":      "",
                "api_secret":   ""
                }

PATHS = {"data_csv":        "./data/sentiment.csv",
         "charts":          "./charts/",
         "feedback_csv":    "./data/feedback.csv",
         "bot_logs":        "./logs/bot_logs.txt",
         "update_logs":     "./logs/update_logs.txt"
         }

HEROKU_INFO = {"app_url":   "",
               "app_name":  ""
               }

AWS_INFO = {"access_key_id":        "",
            "secret_access_key":    "",
            "s3_bucket_name":       ""
            }

EMAIL_INFO = {"email":         "",
              "password":      ""
              }

MAIN_LIST = ["📋 Crypto List",
             "🏗 Future Improvements",
             "❓ What I Can Do",
             "💸 Make a Donation",
             "✏ Leave Feedback"
             ]

CRYPTO_INFO = {"Bitcoin":           ("bitcoin", "btc"),
               "Ethereum":          ("ethereum", "eth"),
               "Ripple":            ("xrp",),
               "Bitcoin Cash":      ("bitcoin cash", "bitcoincash", "bch", "bcash"),
               "EOS":               ("#eos", "$eos"),
               "Litecoin":          ("litecoin", "ltc"),
               "Stellar":           ("xlm",),
               "Cardano":           ("cardano", "ada"),
               "TRON":              ("tron", "trx"),
               "IOTA":              ("iota", "miota"),
               "NEO":               ("#neo", "$neo"),
               "Dash":              ("#dash", "$dash"),
               "Monero":            ("monero", "xmr"),
               "Tether":            ("tether", "#usdt", "$usdt"),
               "NEM":               ("nem", "xem"),
               "VeChain":           ("vechain", "ven"),
               "Ethereum Classic":  ("ethereum classic", "ethereumclassic", "$etc", "#etc"),
               "Other":             ("ico", "kucoin", "htmlcoin", "purk", "rekt", "neochain", "gld"),
               }

CRYPTO_LIST = ["Bitcoin",
               "Ethereum",
               "Ripple",
               "Bitcoin Cash",
               "Litecoin"
               ]

TEXTS = {"start": "Please, choose your option below:",
         
         "list": "Please, choose your asset:",
         
         "no_info": """         
Oops, I can't find information about this asset.. 🙄
Please, try again later.
         """,
         
         "feedback": "To leave your feedback, please type '/fb' and your text after space",
         
         "feedback_ok": "Thanks! I will review your feedback later 👍",
         
         "donate": """
You can make a donation to support my future plans (blockchain addresses + QR codes):

🔗 Bitcoin: https://blockchain.info/address/1Jkr3ggY7wXRHdBcTbhK9EFgWznQgrvkch

🔗 Bitcoin Cash: https://blockdozer.com/address/qrwah4xz5r3u35qw7kthelf2ehj3d6a67y48n6x36x

🔗 Etherium: https://etherscan.io/address/0x2C1CA917F864Ddd11A2608F0F8f625a544c4D754

🔗 Etherium Classic: http://gastracker.io/addr/0x3dd09371d1fc714acbd9593734a67cc4107268da

🔗 Litecoin: https://live.blockcypher.com/ltc/address/Ld1nMUoL93wfJTLggSk93FyCGeKBd9XsWd/

🔗 Dash: https://insight.dashevo.org/insight/address/XfuEA372hfu91Lec9tj3R97CTwb7Wi6koh         

🔗 Zcash: https://explorer.zcha.in/accounts/t1gdgEDMueXPtFY7VbmE8oCiQpkL1MX6X92/

         """,
         
         "plans": """
My future plans:

🔨 Add other sources of comments: Quora, Facebook etc.;

🔨 Show last comments of top influencers;

🔨 Provide personal delivery of analytics (ex. hourly alerts on target assets);

🔨 Predict prices using all available open-source information and state-of-the-art ML/DL algorithms;
         """,
         
         "about": """
I am weaponed with superior machine learning algorithm which allows me to:

1️⃣ Make everyday search of relevant public comments in Twitter;

2️⃣ Recognize sentiment polarity of comments (negative/neutral/positive);

3️⃣ Deliver simple and useful charts;
         """ 
}
