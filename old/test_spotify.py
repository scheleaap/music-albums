'''Tests Spotify.'''

import argparse
import fnmatch
import logging
import os
import re

import spotimeta

USER_AGENT = '.url file creator on local harddisk -- contact reg-dev-spotify@wout.maaskant.info'

artist = 'Asaf Avidan & the Mojos'
title = 'The Reckoning'

metacache = {}
metadata = spotimeta.Metadata(cache=metacache, user_agent=USER_AGENT)

#search = metadata.search_track('Trip back to childhood')
search = metadata.search_artist('St-Petersburg Ska-Jazz Review')
print search["total_results"]
for k, v in search.iteritems():
	print k, v
for v in search['result']:
	for k2, v2 in v.iteritems():
		print k2, v2
