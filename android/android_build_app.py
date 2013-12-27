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

  # Move the apk in xwalk_app_template to out.
  shutil.move(apk_path, apk_destination)
  return 0


def BuildApp(base_dir, app_name):
  xwalk_app_template_path = os.path.join(base_dir, 'android', 'xwalk_app_template')
  make_apk_script = os.path.join(xwalk_app_template_path, 'make_apk.py')

  # Check xwalk_app_template.
  if not os.path.exists(make_apk_script):
    print ('Please install xwalk_app_template')
    return 1

  # Check manifest.json file.
  jsonfile = os.path.join(base_dir, app_name, 'src', 'manifest.json')
  if not os.path.exists(jsonfile):
    print ('No manifest.json found at ' + jsonfile)
    return 2

  manifest = "--manifest=" + jsonfile

  # Enable embedded mode by default.
  build_mode = "--mode=embedded"
  previous_cwd = os.getcwd()
  os.chdir(xwalk_app_template_path)
  proc = subprocess.Popen(['python', make_apk_script, manifest, build_mode],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  out, _ = proc.communicate()
  print (out)
  os.chdir(previous_cwd)

  # Move result to out.
  # From v3.32.51.0, the apk name is different, there is a tail after app name.
  # We need to check all.
  apk_path = os.path.join(xwalk_app_template_path, app_name)
  apk_path_arm = apk_path + '_arm'
  apk_path_x86 = apk_path + '_x86'

  if os.path.exists(apk_path + '.apk'):
    return MoveApkToOut(apk_path + '.apk', base_dir, app_name)
  elif os.path.exists(apk_path_x86 + '.apk'):
    return MoveApkToOut(apk_path_x86 + '.apk', base_dir, app_name + '_x86')
  elif os.path.exists(apk_path_arm + '.apk'):
    return MoveApkToOut(apk_path_arm + '.apk', base_dir, app_name + '_arm')
  else:
    print ('[Error]: Can\'t find the web application APK, Failed to build.')
    return 3

