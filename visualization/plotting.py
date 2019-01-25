import os
import io
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns
from config import PATHS


def make_single_chart(data, asset):
    """
	Makes chart for particular crypto asset and saves it in byte format.
    """

    # initialize output
    img_data = io.BytesIO();

    # filtering data
    rcParams["font.family"] = "monospace"
    data = data.set_index("upload_date").sort_index()
    n_days = data.shape[0]
    time = data.index.values
    last_row = data.iloc[-1,:]
    last_date = last_row.name.date()
    last_values = dict(last_row.drop("asset"))
    
    fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(8,8), gridspec_kw=dict(height_ratios=[2,3]));
    
    # plotting lines
    line_kwargs = {"marker": "s",
                   "markersize": 3
                   }
    ax[0].plot(time, data["positive"], color="navy", label="positive", **line_kwargs);
    ax[0].plot(time, data["negative"], color="red", label="negative", **line_kwargs);
    ax[0].plot(time, data["neutral"], color="dimgray", label="neutral", **line_kwargs);
    ax[0].set_xticks(data.index.values, minor=True);
    ax[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    ax[0].grid(color="gray", linestyle="--", linewidth=.5, which="both");
    ax[0].legend(loc="upper left", fontsize=8);
    ax[0].set_title("last {n_days}-day period".format(n_days), pad=10);
    ax[0].set_ylabel("count");
    ax[0].set_ylim(bottom=0);
    sns.despine(left=False, bottom=False, ax=ax[0])
    
    # plotting pie-chart    
    pie_labels = ["positive", "negative", "neutral"]
    pie_sizes = [100 * last_values[x] / sum(last_values.values()) for x in pie_labels]
    pie_legend = [x + " ({:,})".format(last_values.get(x)) for x in pie_labels]
    pie_kwargs = {"explode": 		[.03, .03, .03],                  
                  "colors": 		["navy", "red", "gray"],              
                  "labels": 		["{:.1%}".format(x/100) for x in pie_sizes],
                  "shadow": 		False,
                  "startangle": 	90,
                  "counterclock": 	False,
                  "wedgeprops": 	dict(width=.4, edgecolor="white")}
    patches, texts = ax[1].pie(x=pie_sizes, **pie_kwargs);
    ax[1].legend(patches, pie_legend, loc="upper left", fontsize=8)
    ax[1].axis("equal");
    ax[1].set_title("last day ({})".format(last_date), pad=10);

    # general formatting
    suptitle = r"Sentiment of comments on $\bf{}$".format(asset)
    fig_suptitle = fig.suptitle(suptitle, fontsize=14);
    fig.subplots_adjust(hspace=.35, top=.9, bottom=.05)    

    # writing chart as bytes
    fig.savefig(img_data, format="png");
    img_data.seek(0);
    return img_data
