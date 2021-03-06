# coding=utf-8

"""
The MIT License

Copyright (c) 2013 Mustafa İlhan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from model import Trend, Error
from globals import Globals
import logging
import math
import time
import traceback
import twitter

class Cron(webapp.RequestHandler):
    """ makes twitter api call, inserts trends to db """

    def get(self):
        logging.info("Cron starting...")
        
        try:
            # authenticate to twitter
            client = twitter.Api(consumer_key=Globals.CONSUMER_KEY,
                                 consumer_secret=Globals.CONSUMER_SECRET,
                                 access_token_key=Globals.CLIENT_TOKEN,
                                 access_token_secret=Globals.CLIENT_SECRET,
                                 cache=None)
            
            q_futures = []
            for region in Globals.REGIONS:
                # make request
                response = client.GetTrendsWoeid(id=region)
                # get current timestamp in seconds
                timestamp = int(math.floor(time.time()))
                # put trends to db
                entityList = []
                for trend in response:
                    entityList.append(Trend(name=trend.name, woeid=region, timestamp=timestamp, time=10))
                q_futures.extend(ndb.put_multi_async(entityList))
            
            # wait all async put operations to finish.
            ndb.Future.wait_all(q_futures)
        except Exception, e:
            traceback.print_exc()
            Error(msg=str(e), timestamp=int(math.floor(time.time()))).put()
        
        logging.info("Cron finished.")

application = webapp.WSGIApplication([('/cron', Cron)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
