#!/usr/bin/env python

# Copyright (c) 2013 Intel Corporation. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
Downloads the crosswalk package based on the specific url address,
package prefix, version and extracts it to the destination directory.
Then extracts the xwalk application template package to the specific
destination directory.

Sample usage from shell script:
python get_xwalk_app_template.py --version=1.29.7.0
"""
import optparse
import os
import shutil
import sys
import tarfile
import urllib2
import zipfile

from urllib2 import urlopen


class GetXWalkAppTemplate(object):
  """ Retrieves the xwalk application template build version and provides
  the interfaces of downloading crosswalk package, extracting this package to
  the destination path and extracting the xwalk application template package.

  Args:
    url: The url address of the crosswalk package.
    package_prefix: The crosswalk package prefix.
    version: The version number of crosswalk package name.
    file_name: The file name of the xwalk application template package.
    dest_dir: The destination directory.
  """
  def __init__(self, url, package_prefix, version, file_name, dest_dir):
    self.url = url
    self.package_prefix = package_prefix
    self.version = version
    self.file_name = file_name
    self.dest_dir = dest_dir

  def DownloadCrosswalkPackage(self):
    """Downloads the crosswalk package to the destination path based on the
    package url address, package prefix and package version number.
    """
    package_name = self.package_prefix + self.version + '.zip'
    file_path = os.path.join(self.dest_dir, package_name)
    # We have previously downloaded, skip download.
    if os.path.isfile(file_path):
      return True
    package_url = self.url+ '/' + self.package_prefix + self.version + '.zip'
    try:
      input_file = urllib2.urlopen(package_url)
    except urllib2.HTTPError, e:
      print ('[Error]: Failed to open ' + package_url + ' with error HTTP %s.' % e.code)
      return False
    except urllib2.URLError, e:
      print ('[Error]: Failed to download, ', e.reason)
      return False
    try:
      contents = input_file.read()
      input_file.close()
      output_file = open(file_path, 'wb')
      output_file.write(contents)
      output_file.close()
    except:
      print ("[Error]: The file downloaded is broken.")
      return False
    return True


  def __extract_crosswalk_package(self):
    """ Extracts the specific crosswalk package file to the destination
    directory. It is an internally used function.
    """
    package_name = self.package_prefix + self.version + '.zip'
    zip_file_name = os.path.join(self.dest_dir, package_name)
    file_dir = os.path.join(self.dest_dir, self.package_prefix + self.version)
    if os.path.exists(file_dir):
      shutil.rmtree(file_dir)
    try:
      crosswalk_zip = zipfile.ZipFile(zip_file_name, 'r')
      for afile in crosswalk_zip.namelist():
        crosswalk_zip.extract(afile, self.dest_dir)
      crosswalk_zip.close()
    except zipfile.BadZipfile:
      print ('[Error]: There is something wrong with ' + zip_file_name)
      return False
    except zipfile.LargeZipFile:
      print ('[Error]: The file %s is too large' % zip_file_name)
      return False
    return True


  def ExtractAppTemplate(self):
    """ Extracts the specific xwalk app template to the destination directory.
    """
    if not self.__extract_crosswalk_package():
      return
    file_dir = os.path.join(self.dest_dir, self.file_name.split('.tar.gz')[0])
    if os.path.exists(file_dir):
      shutil.rmtree(file_dir)
    file_path = os.path.join(self.dest_dir, self.package_prefix +
                             self.version, self.file_name)
    try:
      tar = tarfile.open(file_path, 'r:gz')
      tar.extractall(self.dest_dir)
      tar.close()
    except:
      print ('[Error]: Failed to extract ' + file_path)

def main():
  parser = optparse.OptionParser()
  info = ('The destination directory name. Such as: '
          '--dest-dir=/')
  parser.add_option('-d', '--dest-dir', action='store', dest='dest_dir',
                    default='android', help=info)
  info = ('The xwalk application template version. Such as: '
          '--version=1.29.7.0')
  parser.add_option('-v', '--version', action='store', dest='version',
                    help=info)
  info = ('The xwalk application template basic url address. Such as: '
          '--url=https://download.01.org/crosswalk/releases/android-x86/canary')
  default_url = 'https://download.01.org/crosswalk/releases/android-x86/canary'
  parser.add_option('-u', '--url', action='store', dest='url',
                    default=default_url, help=info)
  info = ('not to download package')
  parser.add_option('-n', '--no-downloading', action='store_true',
                    dest='no_downloading', help=info)
  opts, _ = parser.parse_args()
  if not opts.version:
    parser.error('Version number is required! please use "--version" option.')
    return 1
  if not os.path.exists(opts.dest_dir):
    os.mkdir(opts.dest_dir)
  dest_dir = opts.dest_dir
  url = opts.url
  version = opts.version
  crosswalk_package_prefix = 'crosswalk-'
  file_name = 'xwalk_app_template.tar.gz'
  if opts.no_downloading:
    if not os.path.exists(os.path.join(dest_dir, crosswalk_package_prefix +
                          version + '.zip')):
      print (crosswalk_package_prefix + version + '.zip' +
             ' does not exist in %s' % dest_dir)
      return 2
    else:
      app_template_handler = GetXWalkAppTemplate(url, crosswalk_package_prefix,
                                                 version, file_name, dest_dir)
  else:
    app_template_handler = GetXWalkAppTemplate(url, crosswalk_package_prefix,
                                               version, file_name, dest_dir)
    if not app_template_handler.DownloadCrosswalkPackage():
      return 3
  app_template_handler.ExtractAppTemplate()
  return 0


if __name__ == '__main__':
  sys.exit(main())
