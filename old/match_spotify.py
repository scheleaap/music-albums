'''Looks for songs on the harddisk in Spotify.'''

import argparse
import fnmatch
import logging
import os
import pprint
import re
import time

import spotimeta

USER_AGENT = '.url shortcut creator on local harddisk -- contact reg-dev-spotify@wout.maaskant.info'

RE_ALBUM_DIR_NAME = re.compile(r'^(?P<artist>[^_-][^-]+) - (?P<year>\d+) - (?P<album>.+)$', re.IGNORECASE)

def listdir_with_fnmatch(path, pattern):
	'''Lists all files in a directory whose file names match a shell-style pattern.
	
	This is the same as os.listdir() combined with fnmatch.filter().
	'''
	return fnmatch.filter(os.listdir(path), pattern)

def listdir_with_re(path, re_obj):
	'''Lists all files in a directory whose file names match a regular expression pattern.
	
	This is the same as os.listdir() combined with fnmatch.filter().
	'''
	return [dir_name for dir_name in os.listdir(path) if re_obj.match(dir_name)]

def list_directories(path):
	'''Returns a list of all directories in a directory.'''
	return [dir_name for dir_name in os.listdir(path) if os.path.isdir(os.path.join(path, dir_name))]

def parse_directory_name(dir_name):
	'''Parses a directory name and returns a (artist, year, album) tuple or None.'''
	if dir_name.startswith('! '):
		dir_name = dir_name[2:]
	elif dir_name.startswith('@'):
		dir_name = dir_name[1:]
	elif dir_name.startswith('_'):
		return None
	
	match = RE_ALBUM_DIR_NAME.match(dir_name)
	if match:
		return (match.group('artist'), match.group('year'), match.group('album'))
	else:
		return None

def process_directory(source_root_path, target_root_path, base_path_rel, metadata):
	for dir_name in list_directories(os.path.join(source_root_path, base_path_rel)):
		dir_path = os.path.join(source_root_path, base_path_rel, dir_name)
		dir_path_rel = os.path.join(base_path_rel, dir_name)
		logging.info('Processing {0}'.format(dir_path_rel))
		
		# Get the directory's creation time etc.
		dir_times = os.stat(dir_path)
		
		# Recurse.
		process_directory(source_root_path, target_root_path, dir_path_rel, metadata)
		
		parsed_name = parse_directory_name(dir_name)
		if parsed_name is not None:
			#continue
			artist, year, album = parsed_name
			logging.info('Found {0} - {1} - {2}'.format(*parsed_name))
			del parsed_name
			#if not album.startswith('Greatest Hits'):
			#	continue
			#if not album.startswith('Cold Water Music'):
			#	continue
			
			# Artist aliases.
			if artist == 'Aphex Twin (Polygon Window)':
				search_artist = 'Polygon Window'
			else:
				search_artist = artist
			
			search_year = year
			
			# Album aliases.
			if album == 'Selected Ambient Works, Volume II':
				search_album = 'Selected Ambient Works Volume II'
			else:
				search_album = album
			
			spotify_id = get_spotify_id(search_artist, search_year, search_album)
			if spotify_id is not None:
				file_path = create_shortcut(os.path.join(target_root_path, base_path_rel), artist, year, album, spotify_id)
			else:
				file_path = create_album_placeholder(os.path.join(target_root_path, base_path_rel), artist, year, album)
			time.sleep(0.5)
		else:
			file_path = create_dir_placeholder(os.path.join(target_root_path, base_path_rel), dir_name)
		
		set_times(file_path, dir_times)
			

def get_spotify_id(search_artist, search_year, search_album):
	try:
		logging.debug('Searching for album \'{0}\''.format(search_album))
		result = metadata.search_album(search_album)
		if result['total_results'] > result['items_per_page']:
			logging.warn('\'{0}\': {1} query results (only {2} processed)'.format(search_album, result['total_results'], result['items_per_page']))
		else:
			logging.debug('\'{0}\': {1} query results'.format(search_album, result['total_results']))		
		
		#pprint.PrettyPrinter(indent=4).pprint(result)
		matching_albums = []
		
		# Filter by artist
		for album in result['result']:
			if album['artist']['name'].lower() == search_artist.lower():
				if album['name'].lower() == search_album.lower():
					matching_albums.append(album)
					#logging.debug('\'{0}\': matched {1} - {2}'.format(search_artist, album['artist']['name'], album['name']))
		
		# TODO: Filter by available territories if >1 matching albums

		# Sort by popularity
		if len(matching_albums) >= 1:
			if len(matching_albums) == 1:
				href = matching_albums[0]['href']
			else:
				href = sorted(matching_albums, key=lambda album: album['popularity'])[0]['href']
			logging.debug('\'{0}\': {1} matching albums, result: {2}'.format(search_album, len(matching_albums), href))
			return href
		elif len(matching_albums) == 0:
			logging.debug('\'{0}\': No matching albums'.format(search_album))

	except spotimeta.SpotimetaError as e:
		logging.debug('Caught {0}'.format(e.__class__.__name__))

def create_shortcut(dir_path, artist, year, album, spotify_id):
	checked_makedirs(dir_path)
	file_path = os.path.join(dir_path, '{0} - {1} - {2}.url'.format(artist, year, album))
	with open(file_path, 'w') as f:
		f.write('[InternetShortcut]\n')
		f.write('URL={0}\n'.format(spotify_id))
	return file_path
	
def create_album_placeholder(dir_path, artist, year, album):
	checked_makedirs(dir_path)
	file_path = os.path.join(dir_path, '{0} - {1} - {2}.txt'.format(artist, year, album))
	with open(file_path, 'w') as f:
		f.write('spotify:search:artist:"{0}" album:"{1}"\n'.format(artist, album))
	return file_path
	
def create_dir_placeholder(parent_path, dir_name):
	checked_makedirs(parent_path)
	file_path = os.path.join(parent_path, '_notparsed.{0}.txt'.format(dir_name))
	with open(file_path, 'w'):
		pass
	return file_path

def checked_makedirs(path):
	try:
		os.makedirs(path)
	except Exception:
		pass

def set_times(path, times):
	os.utime(path, (times.st_atime, times.st_mtime))

if __name__ == '__main__':
	# Parse command-line options.
	args = argparse.ArgumentParser(
			description=__doc__,
			formatter_class=argparse.RawDescriptionHelpFormatter
			)
	args.add_argument('source', help='The directory to process.')
	args.add_argument('target', help='The target directory.')
	args = args.parse_args()
	
	# Initialize logging.
	logging.basicConfig(
			level=logging.DEBUG,
			format='%(levelname)s %(message)s',
			)

	metacache = {}
	metadata = spotimeta.Metadata(cache=metacache, user_agent=USER_AGENT)
	
	process_directory(args.source, args.target, '', metadata)
	
