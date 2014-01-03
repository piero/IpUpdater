import os
import urllib2
import logging
import ConfigParser
from logger import Logger
from email_sender import EmailSender

class IPDetector:
    
    def __init__(self, config_file):
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        self.url = self.config.get('detection', 'url')
        self.data = self.config.get('detection', 'datafile')

        log_level = self.config.get('log', 'level')
        log_file = self.config.get('log', 'file')
        self.logger = Logger('IP Updater')
        self.logger.setLevel(log_level)
        self.logger.addLogFile(log_file)

        self.current_ip = ''


    def setDataFile(self, data_file):
        self.data = data_file


    def setLogLevel(self, log_level):
        self.logger.setLevel(log_level)


    def __writeToFile(self, data):
        self.logger.debug('Writing %s to %s...' % (data, self.data))
        f = open(self.data, 'w')
        f.write(data)
        f.close()
    
    
    def __readFromFile(self):
        self.logger.debug('Reading from %s...' % self.data)
        data = ''
        try:
            f = open(self.data, 'r')
            data = f.read()
            f.close()
        except IOError:
            # File doesn't exist, create it
            open(self.data, 'w').close()
        return data
    
    
    def IpHasChanged(self):
        self.current_ip = self.__readFromFile()
        new_ip = self.__getFromUrl(self.url)
        
        if self.current_ip != new_ip:
            self.logger.info('IP address has changed: %s --> %s' % (self.current_ip, new_ip))
            self.__writeToFile(new_ip)

            email_enabled = self.config.getboolean('email', 'enabled')
            if email_enabled:
                email_text = 'IP changed: ' + self.current_ip + ' --> ' + new_ip
                self.__notifyByEmail(email_text)

            self.current_ip = new_ip

            for domain, hashkey in self.config.items('domains'):
                self.__updateFreeDns(domain, hashkey)
            return (True, self.current_ip)
        
        return (False, self.current_ip)
    
    
    def __notifyByEmail(self, msg):
        host = self.config.get('email', 'host')
        port = self.config.get('email', 'port')
        username = self.config.get('email', 'username')
        password = self.config.get('email', 'password')
        email_sender = EmailSender(host, port, username, password)

        to_addr = self.config.get('email', 'recipient')
        from_addr = self.config.get('email', 'from_addr')
        if email_sender.isValidEmailAddress(to_addr):
            self.logger.info('Sending notification email to %s' % to_addr)
            email_sender.send(from_addr,
                            to_addr,
                            'IP address changed',
                            msg)
        else:
            self.logger.error('Invalid email recipient: %s' % to_addr)
    

    def __updateFreeDns(self, domain, url):
        self.logger.info('Updating %s...' % domain)
        freeDns_url = 'http://freedns.afraid.org/dynamic/update.php?' + url
        result = self.__getFromUrl(freeDns_url)
        self.logger.info('FreeDNS said: %s' % result)

    
    def __getFromUrl(self, url):
        self.logger.info('Contacting %s...' % url)
        req = urllib2.Request(url)
        try:
            response = urllib2.urlopen(req, timeout=60)
            
        except ValueError, e:
            self.logger.error('[!] Invalid URL: ' + str(e))
            raise ValueError('Invalid URL: ' + url)
        
        except urllib2.URLError, e:
            # TODO Handle exception
            self.logger.error('[!] Error opening URL: ' + str(e))
            raise ValueError('Error opening URL: ' + url)
        
        return response.read()

