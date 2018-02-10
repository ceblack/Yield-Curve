import sys
import os
import json
import requests
import re
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import xml.etree.ElementTree as ET
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class Curve:
    def __init__(self):
        self.rawData = None
        self.data = []
        self.dates = []
        self.getData()

    def getData(self):
        response = requests.get("http://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData")
        xmlString = re.sub(' xmlns="[^"]+"', '', response.text, count=2)

        it = ET.iterparse(StringIO(xmlString))
        for _, el in it:
            if '}' in el.tag:
                el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
        self.rawData = it.root

        self.processData()

    def fillVals(self, values):
        # PLACEHOLDER MAKE BETTER
        for i in range(0, len(values)):
            if(values[i] == None):
                values[i] = 0.
        return(values)

    def processData(self):
        titles =    ["DATE", "1 MO", "3 MO", "6 MO", "1 YR", "2 YR", "3 YR",
                    "5 YR", "7 YR", "10 YR", "20 YR", "30 YR"]
        #self.data.append(titles)
        for entry in self.rawData.findall("entry"):
            contents = entry.findall("content")
            curveOrder =    ["BC_1MONTH", "BC_3MONTH", "BC_6MONTH", "BC_1YEAR", "BC_2YEAR",
                            "BC_3YEAR", "BC_5YEAR", "BC_7YEAR", "BC_10YEAR", "BC_20YEAR",
                            "BC_30YEAR"]
            curveIndex = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            for contentItem in contents:
                curveDict = {}
                for prop in contentItem:
                    yieldVals = []
                    date = datetime.strptime(prop.find("NEW_DATE").text, "%Y-%m-%dT%H:%M:%S")
                    date = datetime.strftime(date, "%Y-%m-%d")
                    self.dates.append(date)
                    for key in curveOrder:
                        val = prop.find(key).text
                        if(val != None):
                            val = float(val)
                        yieldVals.append(val)

                    yieldVals = self.fillVals(yieldVals)
                    self.data.append([curveIndex,yieldVals])

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

curve = Curve()
data = curve.data
dates = curve.dates


def animate(i):
    global data

    if(i > 10):
        ax1.clear()
        for k in range(0, 10):
            x = data[i - k][0]
            y = data[i - k][1]
            ax1.plot(x,y,marker='o')
            plt.xlabel(dates[i])

    else:
        x = data[i][0]
        y = data[i][1]

        ax1.clear()
        ax1.plot(x,y,marker='o')
        plt.xlabel(dates[i])

ani = animation.FuncAnimation(fig,animate,interval=1)

#Writer = animation.writers['ffmpeg']
#writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
#ani.save('im.mp4', writer=writer)

plt.show()

if __name__ == "__main__":
    animate()
