#!/usr/bin/env python

# Copyright (c) 2013 Intel Corporation. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
Make webapps for both android and tizen

Sample usage from shell script:
Build all apps for both Tizen and Android
    python make_webapp.py
Build specified app
    python make_webapp.py --app=MemoryGame
Only build for Android
    python make_webapp.py --target=android
Update Web Apps and then build all of them
    python make_webapp.py -u

The build result will be under out directory.
"""
import optparse
import os
import shutil
import subprocess
import sys

import android.android_build_app


def FindApps(app_list):
  for i in os.listdir('.'):
    if os.path.isdir(i):
      check_file = os.path.join('.', i, 'manifest.json')
      check_file2 = os.path.join('.', i, 'src', 'manifest.json')
      if (os.path.exists(check_file) or
          os.path.exists(check_file2)):
        app_list.append(i)


def BuildForAndroidApp(current_real_path, app, build_result):
  return_value = android.android_build_app.BuildApp(current_real_path, app)
  if not return_value:
    build_result = build_result + app + ' :OK\n'
  else:
    build_result = build_result + app + ' :Failed, error code = ' + str(return_value) + '\n'
  return build_result


def RevertManifestFile(current_real_path, app):
  src_folder = os.path.join(current_real_path, app, 'src')
  renamed_jsonfile = os.path.join(src_folder, '_original_manifest.json_')
  target_jsonfile = os.path.join(src_folder, 'manifest.json')
  if os.path.exists(renamed_jsonfile):
    os.remove(target_jsonfile)
    shutil.move(renamed_jsonfile, target_jsonfile)


def RevertPatches(current_real_path, app):
  RevertManifestFile(current_real_path, app)
  # TODO: Need to be designed for patch files.


def CopyManifestFile(current_real_path, app):
  jsonfile = os.path.join(current_real_path, app, 'manifest.json')
  src_folder = os.path.join(current_real_path, app, 'src')
  target_jsonfile = os.path.join(src_folder, 'manifest.json')
  renamed_jsonfile = os.path.join(src_folder, '_original_manifest.json_')
  # Check whether manifest.json exists in webapp folder.
  if os.path.exists(jsonfile):
    # We need to copy manifest.json to src folder.
    # Check whether there is manifest.json under src.
    if os.path.exists(target_jsonfile):
      # Rename current manifest.json.
      shutil.move(target_jsonfile, renamed_jsonfile)
    # Copy manifest.json to src.
    shutil.copy2(jsonfile, target_jsonfile)


def ApplyPatches(current_real_path, app):
  CopyManifestFile(current_real_path, app)
  # TODO: Apply patch files with the upstream code.


def BuildApps(func, current_real_path, app_list, build_result):
  for app in app_list:
    print 'Build ' + app + ':'
    ApplyPatches(current_real_path, app)
    build_result = func(current_real_path, app, build_result)
    RevertPatches(current_real_path, app)
  return build_result


def RunDownloadScript(options, current_real_path):
  if not options.version:
    print ('Please use --version or -v argument to specify xwalk application template version\n'
          'Or you can run android/get_xwalk_app_template.py to download')
    return False
  print 'Downloading xwalk_app_template...'
  version = '--version=' + options.version
  download_script = os.path.join(current_real_path, 'android', 'get_xwalk_app_template.py')
  proc = subprocess.Popen(['python', download_script, version],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
  out, _ = proc.communicate()
  print out
  return True


def CheckAndroidBuildTool(options, current_real_path):
  xwalk_app_template_path = os.path.join(current_real_path, 'android', 'xwalk_app_template')
  if not os.path.exists(xwalk_app_template_path):
    if RunDownloadScript(options, current_real_path):
      return True
    return False
  return True


def UpdateWebApps():
  print 'Update submodules..'
  proc = subprocess.Popen(['git', 'submodule', 'foreach', 'git', 'checkout', 'master'],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
  out, _ = proc.communicate()
  print out
  proc = subprocess.Popen(['git', 'submodule', 'foreach', 'git', 'pull'],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
  out, _ = proc.communicate()
  print out


def InitWebApps():
  print 'Init submodules..'
  proc = subprocess.Popen(['git', 'submodule', 'update', '--init'],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
  out, _ = proc.communicate()
  print out


def Build_WebApps(options, current_real_path, build_result):
  app_list = []
  if options.app:
    app_list.append(options.app)
  else:
    # No app specified, loop to find all available apps.
    FindApps(app_list)

  if len(app_list) == 0:
    build_result += 'No available apps\n'
    return build_result

  # Init git submodules at the first time.
  # (git will automatically check whether need init the next time).
  InitWebApps()

  # Update git submodules if needed.
  if options.update:
    UpdateWebApps()

  # Build apps.
  if options.target == 'android':
    if CheckAndroidBuildTool(options, current_real_path):
      build_result = BuildApps(BuildForAndroidApp, current_real_path, app_list, build_result)
    else:
      build_result += 'No Build tools\n'
  elif options.target == 'tizen':
    print 'Tizen build not implemented'
  else:
    if CheckAndroidBuildTool(options, current_real_path):
      build_result = BuildApps(BuildForAndroidApp, current_real_path, app_list, build_result)
    else:
      build_result += 'No Build tools\n'
  return build_result


def main():
  build_result = '\nBuild Result:\n'
  parser = optparse.OptionParser()
  parser.add_option('--app',
      help='The app name. '
           'If no app specified, all apps will be built. '
           'Such as: --app=MemoryGame')
  parser.add_option('--target',
      help='Build target. '
           'If no target specified, all targets will be built. '
           'Such as: --target=android')
  parser.add_option('-u', '--update', action='store_true',
      dest='update', default=False,
      help='Update all the Web Apps.')
  parser.add_option('-v', '--version', action='store', dest='version',
      help='The xwalk application template version. '
           'Such as: --version=1.29.7.0')
  options, _ = parser.parse_args()
  current_real_path = os.path.abspath(os.path.dirname(sys.argv[0]))
  try:
    build_result = Build_WebApps(options, current_real_path, build_result)
  except:
    print 'Unexpected error:', sys.exc_info()[0]
  finally:
    print build_result
  return 0


if __name__ == '__main__':
  sys.exit(main())
