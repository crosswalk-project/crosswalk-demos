#!/usr/bin/env python

# Copyright (c) 2013 Intel Corporation. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
Buid web app with xwalk_app_template with argument --manifest=manifest.json.
And the build result will be copied to ../out/android.
"""

import optparse
import os
import shutil
import subprocess
import sys

def MoveApkToOut(apk_path, base_dir, app_name):
  destination = os.path.join(base_dir, 'out', 'android')
  apk_destination = os.path.join(destination, app_name + '.apk')

  if not os.path.exists(destination):
    os.makedirs(destination)

  # Remove previous Build result.
  if os.path.exists(apk_destination):
    os.remove(apk_destination)

  if not os.path.exists(apk_path):
    print "Build failed"
    return 3

  # Move the apk in xwalk_app_template to out.
  shutil.move(apk_path, apk_destination)
  return 0


def BuildApp(base_dir, app_name):
  xwalk_app_template_path = os.path.join(base_dir, 'android', 'xwalk_app_template')
  make_apk_script = os.path.join(xwalk_app_template_path, 'make_apk.py')

  # Check xwalk_app_template.
  if not os.path.exists(make_apk_script):
    print 'Please install xwalk_app_template'
    return 1

  # Check manifest.json file.
  jsonfile = os.path.join(base_dir, app_name, 'src', 'manifest.json')
  if not os.path.exists(jsonfile):
    print 'No manifest.json found at ' + jsonfile
    return 2

  manifest = "--manifest=" + jsonfile
  previous_cwd = os.getcwd()
  os.chdir(xwalk_app_template_path)
  proc = subprocess.Popen(['python', make_apk_script, manifest],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  out, _ = proc.communicate()
  print out
  os.chdir(previous_cwd)

  # Move result to out.
  apk_path = os.path.join(xwalk_app_template_path, app_name)
  return MoveApkToOut(apk_path + '.apk', base_dir, app_name)
