import hashlib
import os
import random
import socket
import sys
import time

import byteconversion

class ClientException(Exception):
  pass

class Client(object):
  def __init__(self):
    self.connection_id = int('41727101980', 16)
    self.current_transaction_id = random.getrandbits(31)
    self.peer_id = os.urandom(20)
    self.key = random.getrandbits(31)

    def retry(function_to_repeat):
      def repeated(*args, **kwargs):
        for _ in range(10):
          try:
            response = send_function(*args, **kwargs)
            print 'Sent'
            return response
          except socket.error as e:
            print "Error\n"
            print e
      return repeated

    @retry
    def send_packet(self, sock, host, port, packet):
      sock.send(packet, (host, port))
      response = sock.recv(1024)
      return response

    def make_connection_packet(self):
      action = 0
      connection_packet = byteconversion.pack_binary_string('>qii', self.connection_id, action,
                                                            self.current_transaction_id)
      return connection_packet

    def check_packet(self, action_sent, response):
      action_recieved = byteconversion.unpack_binary_string('>i', response[:4])[0]
      if(action_recieved != action_sent):
        raise ClientException("Action Error")

      current_transaction_id_recieved = byteconversion.unpack_binary_string('>i', response[4:8])[0]
      if(self.current_transaction_id != current_transaction_id_recieved):
        raise ClientException("Transaction id does not match")
      else:
        if action_recieved == 0:
          print 'Connect packet recieved -- Reseting connection id'
          self.connection_id = byteconversion.unpack_binary_string('>q', response[8:])[0]
        elif action_recieved == 1:
          print 'Announce packet recieved'
        else:
          raise 'Action packet not recieved'



    def make_announce_packet(self, total_file_length, bencoded_info_hash):
      action = 1
      self.current_transaction_id = random.getrandbits(31)
      bytes_downloaded = 0
      bytes_left = total_file_length - bytes_downloaded
      bytes_uploaded = 0
      event = 0
      ip = 0
      num_want = -1
      info_hash = hashlib.sha1(bencoded_info_hash).digest()
      preamble = byteconversion.pack_binary_string('>qii',
                                                    self.connection_id,
                                                    action,
                                                    self.current_transaction_id)
      download_info = byteconversion.pack_binary_string('>qqqiiiih',
                                                         bytes_downloaded,
                                                         bytes_left,
                                                         bytes_uploaded,
                                                         event,
                                                         ip,
                                                         self.key,
                                                         num_want,
                                                         6881)
      return preamble + info_hash + self.peer_id + download_info

    def get_list_of_peers(self, response):
      num_bytes = len(response)
      if num_bytes < 20:
        raise ClientException("Error in getting peers")
      else:
        interval, leechers, peers = byteconversion.unpack_binary_string('iii', response[8:20])
        peers_list = []
        for i in range(peers):
          start_index = (20 + 6 * i)
          end_index = start_index + 6
          ip, port = byteconversion.unpack_binary_string('>IH', response[start_index : end_index])
          ip = socket.inet_ntoa(struct.pack('I', ip))
          print (ip, port)
          peer_list.append((ip, port))
        return peers_list

    def build_peer(self, (ip, port), num_pieces, info_hash, torrent_download):
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.setblocking(0)
      return peer_connection.PeerConnection(ip, port, sock, num_pieces, info_hash, torrent_download)

    def open_connection_with_timeout(timeout, type = 'udp'):
      if type == 'tcp':
        type = socket.SOCK_STREAM
      else:
        type = sock.SOCK_DGRAM
      try:
        sock = socket.socket(socket.AF_INET, type)
        sock.settimeout(timeout)
        return sock
      except:
        print 'Could not create socket'
        sys.exit()



























