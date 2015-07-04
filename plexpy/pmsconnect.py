# This file is part of PlexPy.
#
#  PlexPy is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  PlexPy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PlexPy.  If not, see <http://www.gnu.org/licenses/>.

from plexpy import logger, helpers, plexwatch

from xml.dom import minidom
from httplib import HTTPSConnection
from httplib import HTTPConnection

import plexpy


class PmsConnect(object):
    """
    Retrieve data from Plex Server
    """

    def __init__(self):
        self.host = plexpy.CONFIG.PMS_IP
        self.port = str(plexpy.CONFIG.PMS_PORT)
        self.token = plexpy.CONFIG.PMS_TOKEN
        self.protocol = 'HTTP'

    """
    Return base url of Plex Server.

    Output: string
    """
    def get_base_url(self):
        if self.host != '' and self.port != '':
            base_url = self.protocol + self.host + ':' + self.port
            return base_url
        else:
            return False

    """
    Handle the HTTP requests.

    Output: object
    """
    def make_request(self, uri=None, proto='HTTP', request_type='GET', output_format='xml'):

        valid_request_types = ['GET', 'POST', 'PUT', 'DELETE']

        if request_type.upper() not in valid_request_types:
            logger.debug(u"HTTP request made but unsupported request type given.")
            return None

        if uri:
            if proto.upper() == 'HTTPS':
                handler = HTTPSConnection(self.host, self.port, timeout=10)
            else:
                handler = HTTPConnection(self.host, self.port, timeout=10)

            if uri.find('?') > 0:
                token_string = '&X-Plex-Token=' + self.token
            else:
                token_string = '?X-Plex-Token=' + self.token

            try:
                handler.request(request_type, uri + token_string)
                response = handler.getresponse()
                request_status = response.status
                request_content = response.read()
            except IOError, e:
                logger.warn(u"Failed to access uri endpoint %s with error %s" % (uri, e))
                return None

            if request_status == 200:
                if output_format == 'dict':
                    output = helpers.convert_xml_to_dict(request_content)
                elif output_format == 'json':
                    output = helpers.convert_xml_to_json(request_content)
                elif output_format == 'xml':
                    output = self.parse_xml(request_content)
                else:
                    output = request_content

                return output
            else:
                logger.warn(u"Failed to access uri endpoint %s. Status code %r" % (uri, request_status))
                return []
        else:
            logger.debug(u"HTTP request made but no enpoint given.")
            return None

    def parse_xml(self, unparsed=None):
        if unparsed:
            try:
                xml_parse = minidom.parseString(unparsed)
                return xml_parse
            except Exception, e:
                logger.warn("Error parsing XML for Plex recently added: %s" % e)
                return []
            except:
                logger.warn("Error parsing XML for Plex recently added.")
                return []
        else:
            logger.warn("XML parse request made but no data received.")
            return []

    """
    Return current sessions.

    Optional parameters:    output_format { dict, json }

    Output: array
    """
    def get_sessions(self, output_format=''):
        uri = '/status/sessions'
        request = self.make_request(uri=uri,
                                    proto=self.protocol,
                                    request_type='GET',
                                    output_format=output_format)

        return request

    """
    Return metadata for request item.

    Parameters required:    rating_key { Plex ratingKey }
    Optional parameters:    output_format { dict, json }

    Output: array
    """
    def get_metadata(self, rating_key='', output_format=''):
        uri = '/library/metadata/' + rating_key
        request = self.make_request(uri=uri,
                                    proto=self.protocol,
                                    request_type='GET',
                                    output_format=output_format)

        return request

    """
    Return list of recently added items.

    Parameters required:    count { number of results to return }
    Optional parameters:    output_format { dict, json }

    Output: array
    """
    def get_recently_added(self, count='0', output_format=''):
        uri = '/library/recentlyAdded?X-Plex-Container-Start=0&X-Plex-Container-Size=' + count
        request = self.make_request(uri=uri,
                                    proto=self.protocol,
                                    request_type='GET',
                                    output_format=output_format)

        return request

    """
    Return list of episodes in requested season.

    Parameters required:    rating_key { ratingKey of parent }
    Optional parameters:    output_format { dict, json }

    Output: array
    """
    def get_episode_list(self, rating_key='', output_format=''):
        uri = '/library/metadata/' + rating_key + '/children'
        request = self.make_request(uri=uri,
                                    proto=self.protocol,
                                    request_type='GET',
                                    output_format=output_format)

        return request

    """
    Return list of local servers.

    Optional parameters:    output_format { dict, json }

    Output: array
    """
    def get_server_list(self, output_format=''):
        uri = '/servers'
        request = self.make_request(uri=uri,
                                    proto=self.protocol,
                                    request_type='GET',
                                    output_format=output_format)

        return request

    """
    Return the local servers preferences.

    Optional parameters:    output_format { dict, json }

    Output: array
    """
    def get_server_prefs(self, output_format=''):
        uri = '/:/prefs'
        request = self.make_request(uri=uri,
                                    proto=self.protocol,
                                    request_type='GET',
                                    output_format=output_format)

        return request

    """
    Return the local server identity.

    Optional parameters:    output_format { dict, json }

    Output: array
    """
    def get_local_server_identity(self, output_format=''):
        uri = '/identity'
        request = self.make_request(uri=uri,
                                    proto=self.protocol,
                                    request_type='GET',
                                    output_format=output_format)

        return request

    """
    Return sync item details.

    Parameters required:    sync_id { unique sync id for item }
    Optional parameters:    output_format { dict, json }

    Output: array
    """
    def get_sync_item(self, sync_id=None, output_format=''):
        uri = '/sync/items/' + sync_id
        request = self.make_request(uri=uri,
                                    proto=self.protocol,
                                    request_type='GET',
                                    output_format=output_format)

        return request

    """
    Return sync transcode queue.

    Optional parameters:    output_format { dict, json }

    Output: array
    """
    def get_sync_transcode_queue(self, output_format=''):
        uri = '/sync/transcodeQueue'
        request = self.make_request(uri=uri,
                                    proto=self.protocol,
                                    request_type='GET',
                                    output_format=output_format)

        return request

    """
    Return processed and validated list of recently added items.

    Parameters required:    count { number of results to return }

    Output: array
    """
    def get_recently_added_details(self, count='0'):
        recent = self.get_recently_added(count, output_format='xml')
        recents_list = []

        xml_head = recent.getElementsByTagName('MediaContainer')
        if not xml_head:
            logger.warn("Error parsing XML for Plex recently added.")
            return None

        for a in xml_head:
            if a.getAttribute('size'):
                if a.getAttribute('size') == '0':
                    output = {'recently_added': None}
                    return output

            if a.getElementsByTagName('Directory'):
                recents_main = a.getElementsByTagName('Directory')
                for item in recents_main:
                    recent_type = self.get_xml_attr(item, 'type')

                    if recent_type == 'season':
                        recent_items = {'type': recent_type,
                                        'ratingKey': self.get_xml_attr(item, 'ratingKey'),
                                        'title': self.get_xml_attr(item, 'title'),
                                        'thumb': self.get_xml_attr(item, 'thumb'),
                                        'addedAt': self.get_xml_attr(item, 'addedAt')
                                        }
                        recents_list.append(recent_items)
                    else:
                        recent_items = {}
                        recents_list.append(recent_items)
            if a.getElementsByTagName('Video'):
                recents_main = a.getElementsByTagName('Video')
                for item in recents_main:
                    recent_type = self.get_xml_attr(item, 'type')

                    if recent_type == 'movie':
                        recent_items = {'type': recent_type,
                                        'ratingKey': self.get_xml_attr(item, 'ratingKey'),
                                        'title': self.get_xml_attr(item, 'title'),
                                        'year': self.get_xml_attr(item, 'year'),
                                        'thumb': self.get_xml_attr(item, 'thumb'),
                                        'addedAt': self.get_xml_attr(item, 'addedAt')
                                        }
                        recents_list.append(recent_items)
                    else:
                        recent_items = {}
                        recents_list.append(recent_items)

        output = {'recently_added': sorted(recents_list, key=lambda k: k['addedAt'], reverse=True)}
        return output

    """
    Return processed and validated metadata list for requested item.

    Parameters required:    rating_key { Plex ratingKey }

    Output: array
    """
    def get_metadata_details(self, rating_key=''):
        metadata = self.get_metadata(rating_key, output_format='xml')
        metadata_list = []

        xml_head = metadata.getElementsByTagName('MediaContainer')
        if not xml_head:
            logger.warn("Error parsing XML for Plex metadata.")
            return None

        for a in xml_head:
            if a.getAttribute('size'):
                if a.getAttribute('size') != '1':
                    metadata_list = {'metadata': None}
                    return metadata_list

            if a.getElementsByTagName('Directory'):
                metadata_main = a.getElementsByTagName('Directory')[0]
                metadata_type = self.get_xml_attr(metadata_main, 'type')
            elif a.getElementsByTagName('Video'):
                metadata_main = a.getElementsByTagName('Video')[0]
                metadata_type = self.get_xml_attr(metadata_main, 'type')
            else:
                logger.debug(u"Metadata failed")

        genres = []
        actors = []
        writers = []
        directors = []

        if metadata_main.getElementsByTagName('Genre'):
            for genre in metadata_main.getElementsByTagName('Genre'):
                genres.append(self.get_xml_attr(genre, 'tag'))

        if metadata_main.getElementsByTagName('Role'):
            for actor in metadata_main.getElementsByTagName('Role'):
                actors.append(self.get_xml_attr(actor, 'tag'))

        if metadata_main.getElementsByTagName('Writer'):
            for writer in metadata_main.getElementsByTagName('Writer'):
                writers.append(self.get_xml_attr(writer, 'tag'))

        if metadata_main.getElementsByTagName('Director'):
            for director in metadata_main.getElementsByTagName('Director'):
                directors.append(self.get_xml_attr(director, 'tag'))

        if metadata_type == 'show':
            metadata = {'type': metadata_type,
                        'rating_key': self.get_xml_attr(metadata_main, 'ratingKey'),
                        'grandparent_title': self.get_xml_attr(metadata_main, 'grandparentTitle'),
                        'parent_index': self.get_xml_attr(metadata_main, 'parentIndex'),
                        'parent_title': self.get_xml_attr(metadata_main, 'parentTitle'),
                        'index': self.get_xml_attr(metadata_main, 'index'),
                        'studio': self.get_xml_attr(metadata_main, 'studio'),
                        'title': self.get_xml_attr(metadata_main, 'title'),
                        'content_rating': self.get_xml_attr(metadata_main, 'contentRating'),
                        'summary': self.get_xml_attr(metadata_main, 'summary'),
                        'rating': self.get_xml_attr(metadata_main, 'rating'),
                        'duration': helpers.convert_milliseconds_to_minutes(self.get_xml_attr(metadata_main, 'duration')),
                        'year': self.get_xml_attr(metadata_main, 'year'),
                        'thumb': self.get_xml_attr(metadata_main, 'thumb'),
                        'parent_thumb': self.get_xml_attr(metadata_main, 'parentThumb'),
                        'art': self.get_xml_attr(metadata_main, 'art'),
                        'originally_available_at': self.get_xml_attr(metadata_main, 'originallyAvailableAt'),
                        'writers': writers,
                        'directors': directors,
                        'genres': genres,
                        'actors': actors
                        }
            metadata_list = {'metadata': metadata}
        elif metadata_type == 'episode':
            metadata = {'type': metadata_type,
                        'rating_key': self.get_xml_attr(metadata_main, 'ratingKey'),
                        'grandparent_title': self.get_xml_attr(metadata_main, 'grandparentTitle'),
                        'parent_index': self.get_xml_attr(metadata_main, 'parentIndex'),
                        'parent_title': self.get_xml_attr(metadata_main, 'parentTitle'),
                        'index': self.get_xml_attr(metadata_main, 'index'),
                        'studio': self.get_xml_attr(metadata_main, 'studio'),
                        'title': self.get_xml_attr(metadata_main, 'title'),
                        'content_rating': self.get_xml_attr(metadata_main, 'contentRating'),
                        'summary': self.get_xml_attr(metadata_main, 'summary'),
                        'rating': self.get_xml_attr(metadata_main, 'rating'),
                        'duration': helpers.convert_milliseconds_to_minutes(self.get_xml_attr(metadata_main, 'duration')),
                        'year': self.get_xml_attr(metadata_main, 'year'),
                        'thumb': self.get_xml_attr(metadata_main, 'thumb'),
                        'parent_thumb': self.get_xml_attr(metadata_main, 'parentThumb'),
                        'art': self.get_xml_attr(metadata_main, 'art'),
                        'originally_available_at': self.get_xml_attr(metadata_main, 'originallyAvailableAt'),
                        'writers': writers,
                        'directors': directors,
                        'genres': genres,
                        'actors': actors
                        }
            metadata_list = {'metadata': metadata}
        elif metadata_type == 'movie':
            metadata = {'type': metadata_type,
                        'rating_key': self.get_xml_attr(metadata_main, 'ratingKey'),
                        'grandparent_title': self.get_xml_attr(metadata_main, 'grandparentTitle'),
                        'parent_index': self.get_xml_attr(metadata_main, 'parentIndex'),
                        'parent_title': self.get_xml_attr(metadata_main, 'parentTitle'),
                        'index': self.get_xml_attr(metadata_main, 'index'),
                        'studio': self.get_xml_attr(metadata_main, 'studio'),
                        'title': self.get_xml_attr(metadata_main, 'title'),
                        'content_rating': self.get_xml_attr(metadata_main, 'contentRating'),
                        'summary': self.get_xml_attr(metadata_main, 'summary'),
                        'rating': self.get_xml_attr(metadata_main, 'rating'),
                        'duration': helpers.convert_milliseconds_to_minutes(self.get_xml_attr(metadata_main, 'duration')),
                        'year': self.get_xml_attr(metadata_main, 'year'),
                        'thumb': self.get_xml_attr(metadata_main, 'thumb'),
                        'parent_thumb': self.get_xml_attr(metadata_main, 'parentThumb'),
                        'art': self.get_xml_attr(metadata_main, 'art'),
                        'originally_available_at': self.get_xml_attr(metadata_main, 'originallyAvailableAt'),
                        'genres': genres,
                        'actors': actors,
                        'writers': writers,
                        'directors': directors
                        }
            metadata_list = {'metadata': metadata}
        elif metadata_type == 'season':
            parent_rating_key = self.get_xml_attr(metadata_main, 'parentRatingKey')
            show_details = self.get_metadata_details(parent_rating_key)
            metadata = {'type': metadata_type,
                        'rating_key': self.get_xml_attr(metadata_main, 'ratingKey'),
                        'grandparent_title': self.get_xml_attr(metadata_main, 'grandparentTitle'),
                        'parent_index': self.get_xml_attr(metadata_main, 'parentIndex'),
                        'parent_title': self.get_xml_attr(metadata_main, 'parentTitle'),
                        'index': self.get_xml_attr(metadata_main, 'index'),
                        'studio': self.get_xml_attr(metadata_main, 'studio'),
                        'title': self.get_xml_attr(metadata_main, 'title'),
                        'content_rating': self.get_xml_attr(metadata_main, 'contentRating'),
                        'summary': show_details['metadata']['summary'],
                        'rating': self.get_xml_attr(metadata_main, 'rating'),
                        'duration': show_details['metadata']['duration'],
                        'year': self.get_xml_attr(metadata_main, 'year'),
                        'thumb': self.get_xml_attr(metadata_main, 'thumb'),
                        'parent_thumb': self.get_xml_attr(metadata_main, 'parentThumb'),
                        'art': self.get_xml_attr(metadata_main, 'art'),
                        'originally_available_at': self.get_xml_attr(metadata_main, 'originallyAvailableAt'),
                        'genres': genres,
                        'actors': actors,
                        'writers': writers,
                        'directors': directors
                        }
            metadata_list = {'metadata': metadata}
        else:
            return None

        return metadata_list

    """
    Validate xml keys to make sure they exist and return their attribute value, return blank value is none found
    """
    @staticmethod
    def get_xml_attr(xml_key, attribute, return_bool=False, default_return=''):
        if xml_key.getAttribute(attribute):
            if return_bool:
                return True
            else:
                return xml_key.getAttribute(attribute)
        else:
            if return_bool:
                return False
            else:
                return default_return

    """
    Return processed and validated session list.

    Output: array
    """
    def get_current_activity(self):
        session_data = self.get_sessions(output_format='xml')
        session_list = []

        xml_head = session_data.getElementsByTagName('MediaContainer')
        if not xml_head:
            logger.warn("Error parsing XML for Plex session data.")
            return None

        for a in xml_head:
            if a.getAttribute('size'):
                if a.getAttribute('size') == '0':
                    session_list = {'stream_count': '0',
                                    'sessions': []
                                    }
                    return session_list

            if a.getElementsByTagName('Track'):
                session_data = a.getElementsByTagName('Track')
                session_type = 'track'
                for session in session_data:
                    session_output = self.get_session_each(session_type, session)
                    session_list.append(session_output)
            if a.getElementsByTagName('Video'):
                session_data = a.getElementsByTagName('Video')
                session_type = 'video'
                for session in session_data:
                    session_output = self.get_session_each(session_type, session)
                    session_list.append(session_output)

        output = {'stream_count': self.get_xml_attr(xml_head[0], 'size'),
                  'sessions': session_list
                  }

        return output

    """
    Return selected data from current sessions.
    This function processes and validates session data

    Parameters required:    stream_type { track or video }
                            session { the session dictionary }
    Output: dict
    """
    def get_session_each(self, stream_type='', session=None):
        session_output = None
        plex_watch = plexwatch.PlexWatch()
        if stream_type == 'track':
            if session.getElementsByTagName('TranscodeSession'):
                transcode_session = session.getElementsByTagName('TranscodeSession')[0]
                audio_decision = self.get_xml_attr(transcode_session, 'audioDecision')
                audio_channels = self.get_xml_attr(transcode_session, 'audioChannels')
                audio_codec = self.get_xml_attr(transcode_session, 'audioCodec')
                duration = self.get_xml_attr(transcode_session, 'duration')
                progress = self.get_xml_attr(session, 'viewOffset')
            else:
                media_info = session.getElementsByTagName('Media')[0]
                audio_decision = 'direct play'
                audio_channels = self.get_xml_attr(media_info, 'audioChannels')
                audio_codec = self.get_xml_attr(media_info, 'audioCodec')
                duration = self.get_xml_attr(media_info, 'duration')
                progress = self.get_xml_attr(session, 'viewOffset')

            session_output = {'session_key': self.get_xml_attr(session, 'sessionKey'),
                              'art': self.get_xml_attr(session, 'art'),
                              'parent_thumb': self.get_xml_attr(session, 'parentThumb'),
                              'thumb': self.get_xml_attr(session, 'thumb'),
                              'user': self.get_xml_attr(session.getElementsByTagName('User')[0], 'title'),
                              'friendly_name': plex_watch.get_user_friendly_name(
                                  self.get_xml_attr(session.getElementsByTagName('User')[0], 'title')),
                              'player': self.get_xml_attr(session.getElementsByTagName('Player')[0], 'platform'),
                              'state': self.get_xml_attr(session.getElementsByTagName('Player')[0], 'state'),
                              'grandparent_title': self.get_xml_attr(session, 'grandparentTitle'),
                              'parent_title': self.get_xml_attr(session, 'parentTitle'),
                              'title': self.get_xml_attr(session, 'title'),
                              'rating_key': self.get_xml_attr(session, 'ratingKey'),
                              'audio_decision': audio_decision,
                              'audio_channels': audio_channels,
                              'audio_codec': audio_codec,
                              'video_decision': '',
                              'video_codec': '',
                              'height': '',
                              'width': '',
                              'duration': duration,
                              'progress': progress,
                              'progress_percent': str(helpers.get_percent(progress, duration)),
                              'type': 'track',
                              'indexes': 0
                              }
        elif stream_type == 'video':
            if session.getElementsByTagName('TranscodeSession'):
                transcode_session = session.getElementsByTagName('TranscodeSession')[0]
                audio_decision = self.get_xml_attr(transcode_session, 'audioDecision')
                audio_channels = self.get_xml_attr(transcode_session, 'audioChannels')
                audio_codec = self.get_xml_attr(transcode_session, 'audioCodec')
                video_decision = self.get_xml_attr(transcode_session, 'videoDecision')
                video_codec = self.get_xml_attr(transcode_session, 'videoCodec')
                width = self.get_xml_attr(transcode_session, 'width')
                height = self.get_xml_attr(transcode_session, 'height')
                duration = self.get_xml_attr(session, 'duration')
                progress = self.get_xml_attr(session, 'viewOffset')
            else:
                media_info = session.getElementsByTagName('Media')[0]
                audio_decision = 'direct play'
                audio_channels = self.get_xml_attr(media_info, 'audioChannels')
                audio_codec = self.get_xml_attr(media_info, 'audioCodec')
                video_decision = 'direct play'
                video_codec = self.get_xml_attr(media_info, 'videoCodec')
                width = self.get_xml_attr(media_info, 'width')
                height = self.get_xml_attr(media_info, 'height')
                duration = self.get_xml_attr(media_info, 'duration')
                progress = self.get_xml_attr(session, 'viewOffset')

            media_info = session.getElementsByTagName('Media')[0]
            if media_info.getElementsByTagName('Part'):
                indexes = self.get_xml_attr(media_info.getElementsByTagName('Part')[0], 'indexes')
                part_id = self.get_xml_attr(media_info.getElementsByTagName('Part')[0], 'id')
                if indexes == 'sd':
                    bif_thumb = '/library/parts/' + part_id + '/indexes/sd/' + progress
                else:
                    bif_thumb = ''
            else:
                indexes = ''
                bif_thumb = ''

            if plexpy.CONFIG.PMS_USE_BIF and indexes == 'sd':
                thumb = bif_thumb
                use_indexes = 1
            else:
                thumb = self.get_xml_attr(session, 'thumb')
                use_indexes = 0

            if self.get_xml_attr(session, 'type') == 'episode':
                session_output = {'session_key': self.get_xml_attr(session, 'sessionKey'),
                                  'art': self.get_xml_attr(session, 'art'),
                                  'parent_thumb': self.get_xml_attr(session, 'parentThumb'),
                                  'thumb': thumb,
                                  'user': self.get_xml_attr(session.getElementsByTagName('User')[0], 'title'),
                                  'friendly_name': plex_watch.get_user_friendly_name(
                                      self.get_xml_attr(session.getElementsByTagName('User')[0], 'title')),
                                  'player': self.get_xml_attr(session.getElementsByTagName('Player')[0], 'platform'),
                                  'state': self.get_xml_attr(session.getElementsByTagName('Player')[0], 'state'),
                                  'grandparent_title': self.get_xml_attr(session, 'grandparentTitle'),
                                  'parent_title': self.get_xml_attr(session, 'parentTitle'),
                                  'title': self.get_xml_attr(session, 'title'),
                                  'rating_key': self.get_xml_attr(session, 'ratingKey'),
                                  'audio_decision': audio_decision,
                                  'audio_channels': audio_channels,
                                  'audio_codec': audio_codec,
                                  'video_decision': video_decision,
                                  'video_codec': video_codec,
                                  'height': height,
                                  'width': width,
                                  'duration': duration,
                                  'progress': progress,
                                  'progress_percent': str(helpers.get_percent(progress, duration)),
                                  'type': self.get_xml_attr(session, 'type'),
                                  'indexes': use_indexes
                                  }
            elif self.get_xml_attr(session, 'type') == 'movie':
                session_output = {'session_key': self.get_xml_attr(session, 'sessionKey'),
                                  'art': self.get_xml_attr(session, 'art'),
                                  'thumb': thumb,
                                  'parent_thumb': self.get_xml_attr(session, 'parentThumb'),
                                  'user': self.get_xml_attr(session.getElementsByTagName('User')[0], 'title'),
                                  'friendly_name': plex_watch.get_user_friendly_name(
                                      self.get_xml_attr(session.getElementsByTagName('User')[0], 'title')),
                                  'player': self.get_xml_attr(session.getElementsByTagName('Player')[0], 'platform'),
                                  'state': self.get_xml_attr(session.getElementsByTagName('Player')[0], 'state'),
                                  'grandparent_title': self.get_xml_attr(session, 'grandparentTitle'),
                                  'parent_title': self.get_xml_attr(session, 'parentTitle'),
                                  'title': self.get_xml_attr(session, 'title'),
                                  'rating_key': self.get_xml_attr(session, 'ratingKey'),
                                  'audio_decision': audio_decision,
                                  'audio_channels': audio_channels,
                                  'audio_codec': audio_codec,
                                  'video_decision': video_decision,
                                  'video_codec': video_codec,
                                  'height': height,
                                  'width': width,
                                  'duration': duration,
                                  'progress': progress,
                                  'progress_percent': str(helpers.get_percent(progress, duration)),
                                  'type': self.get_xml_attr(session, 'type'),
                                  'indexes': use_indexes
                                  }
            elif self.get_xml_attr(session, 'type') == 'clip':
                session_output = {'session_key': self.get_xml_attr(session, 'sessionKey'),
                                  'art': self.get_xml_attr(session, 'art'),
                                  'thumb': thumb,
                                  'parent_thumb': self.get_xml_attr(session, 'parentThumb'),
                                  'user': self.get_xml_attr(session.getElementsByTagName('User')[0], 'title'),
                                  'friendly_name': plex_watch.get_user_friendly_name(
                                      self.get_xml_attr(session.getElementsByTagName('User')[0], 'title')),
                                  'player': self.get_xml_attr(session.getElementsByTagName('Player')[0], 'platform'),
                                  'state': self.get_xml_attr(session.getElementsByTagName('Player')[0], 'state'),
                                  'grandparent_title': self.get_xml_attr(session, 'grandparentTitle'),
                                  'parent_title': self.get_xml_attr(session, 'parentTitle'),
                                  'title': self.get_xml_attr(session, 'title'),
                                  'rating_key': self.get_xml_attr(session, 'ratingKey'),
                                  'audio_decision': audio_decision,
                                  'audio_channels': audio_channels,
                                  'audio_codec': audio_codec,
                                  'video_decision': video_decision,
                                  'video_codec': video_codec,
                                  'height': height,
                                  'width': width,
                                  'duration': duration,
                                  'progress': progress,
                                  'progress_percent': str(helpers.get_percent(progress, duration)),
                                  'type': self.get_xml_attr(session, 'type'),
                                  'indexes': 0
                                  }
        else:
            logger.warn(u"No known stream types found in session list.")

        return session_output

    """
    Return processed and validated episode list.

    Output: array
    """
    def get_season_children(self, rating_key=''):
        episode_data = self.get_episode_list(rating_key, output_format='xml')
        episode_list = []

        xml_head = episode_data.getElementsByTagName('MediaContainer')
        if not xml_head:
            logger.warn("Error parsing XML for Plex session data.")
            return None

        for a in xml_head:
            if a.getAttribute('size'):
                if a.getAttribute('size') == '0':
                    logger.debug(u"No episode data.")
                    episode_list = {'episode_count': '0',
                                    'episode_list': []
                                    }
                    return episode_list

            if a.getElementsByTagName('Video'):
                result_data = a.getElementsByTagName('Video')
                for result in result_data:
                    episode_output = {'rating_key': self.get_xml_attr(result, 'ratingKey'),
                                      'index': self.get_xml_attr(result, 'index'),
                                      'title': self.get_xml_attr(result, 'title'),
                                      'thumb': self.get_xml_attr(result, 'thumb')
                                      }
                    episode_list.append(episode_output)

        output = {'episode_count': self.get_xml_attr(xml_head[0], 'size'),
                  'title': self.get_xml_attr(xml_head[0], 'title2'),
                  'episode_list': episode_list
                  }

        return output

    """
    Return the list of local servers.

    Output: array
    """
    def get_servers_info(self):
        recent = self.get_server_list(output_format='xml')

        xml_head = recent.getElementsByTagName('Server')
        if not xml_head:
            logger.warn("Error parsing XML for Plex server prefs.")
            return None

        server_info = []
        for a in xml_head:
            output = {"name": self.get_xml_attr(a, 'name'),
                      "machine_identifier": self.get_xml_attr(a, 'machineIdentifier'),
                      "host": self.get_xml_attr(a, 'host'),
                      "port": self.get_xml_attr(a, 'port'),
                      "version": self.get_xml_attr(a, 'version')
                      }

            server_info.append(output)

        return server_info

    """
    Return the local machine identity.

    Output: dict
    """
    def get_server_identity(self):
        identity = self.get_local_server_identity(output_format='xml')

        xml_head = identity.getElementsByTagName('MediaContainer')
        if not xml_head:
            logger.warn("Error parsing XML for Plex server identity.")
            return None

        server_identity = {}
        for a in xml_head:
            server_identity = {"machine_identifier": self.get_xml_attr(a, 'machineIdentifier'),
                               "version": self.get_xml_attr(a, 'version')
                               }

        return server_identity

    """
    Return image data as array.
    Array contains the image content type and image binary

    Parameters required:    img { Plex image location }
    Optional parameters:    width { the image width }
                            height { the image height }
    Output: array
    """
    def get_image(self, img, width='0', height='0'):
        if img != '':
            try:
                http_handler = HTTPConnection(self.host, self.port, timeout=10)
                if width != '0' and height != '0':
                    image_path = '/photo/:/transcode?url=http://127.0.0.1:32400' + img + '&width=' + width + '&height=' + height
                else:
                    image_path = '/photo/:/transcode?url=http://127.0.0.1:32400' + img

                http_handler.request("GET", image_path + '&X-Plex-Token=' + self.token)
                response = http_handler.getresponse()
                request_status = response.status
                request_content = response.read()
                request_content_type = response.getheader('content-type')
            except IOError, e:
                logger.warn(u"Failed to retrieve image. %s" % e)
                return None

        if request_status == 200:
            return [request_content_type, request_content]
        else:
            logger.warn(u"Failed to retrieve image. Status code %r" % request_status)
            return None

        return None
