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
Specify build tool version
    python make_webapp.py -v 2.31.27.0

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
  if os.path.exists(os.path.join(current_real_path, app, 'manifest.json')):
    os.remove(target_jsonfile)
  if os.path.exists(renamed_jsonfile):
    shutil.move(renamed_jsonfile, target_jsonfile)


def RevertPatchFiles(current_real_path, app):
  # Check whether it's a git submodule.
  git_file = os.path.join(current_real_path, app, 'src', '.git')
  if not os.path.exists(git_file):
    # It's not a git submodule, no patch files applied.
    return
  # cd to submodule dir.
  previous_cwd = os.getcwd()
  os.chdir(os.path.join(current_real_path, app, 'src'))
  # Checkout to master branch.
  proc = subprocess.Popen(['git', 'checkout', 'master'],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
  out, _ = proc.communicate()
  print out
  # Revert cd.
  os.chdir(previous_cwd)


def RevertPatches(current_real_path, app):
  RevertManifestFile(current_real_path, app)
  RevertPatchFiles(current_real_path, app)


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


def FindPatchFiles(current_real_path, app, patch_list):
  app_path = os.path.join(current_real_path, app)
  # Patch files will be sorted after below scenario.
  # Because patches should be orderly patched one by one.
  for i in sorted(os.listdir(app_path)):
    if os.path.isfile(os.path.join(app_path, i)):
      extension = os.path.splitext(i)[1][1:].lower()
      if extension == 'patch':
        patch_list.append(i)


def ApplyPatchFiles(current_real_path, app):
  # Check whether it's a git submodule.
  git_file = os.path.join(current_real_path, app, 'src', '.git')
  if not os.path.exists(git_file):
    # It's not a git submodule, no patch files needed.
    return

  patch_list = []
  FindPatchFiles(current_real_path, app, patch_list)

  if len(patch_list) == 0:
    return

  # cd to submodule dir.
  previous_cwd = os.getcwd()
  os.chdir(os.path.join(current_real_path, app, 'src'))
  # Checkout to master branch.
  proc = subprocess.Popen(['git', 'checkout', 'master'],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
  out, _ = proc.communicate()
  print out

  # Delete previous auto_patch branch.
  proc = subprocess.Popen(['git', 'branch', '-D', 'auto_patch'],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
  out, _ = proc.communicate()
  print out

  # Create auto_patch branch.
  proc = subprocess.Popen(['git', 'checkout', '-b', 'auto_patch', 'origin/master'],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
  out, _ = proc.communicate()
  print out

  # Apply all the patches.
  for patch in patch_list:
    patch_path = os.path.join(current_real_path, app, patch)
    proc = subprocess.Popen(['git', 'am', patch_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    out, _ = proc.communicate()
    print out

  # Revert cd.
  os.chdir(previous_cwd)


def ApplyPatches(current_real_path, app):
  ApplyPatchFiles(current_real_path, app)
  CopyManifestFile(current_real_path, app)


def BuildApps(func, current_real_path, app_list, build_result):
  for app in app_list:
    print 'Build ' + app + ':'
    ApplyPatches(current_real_path, app)
    build_result = func(current_real_path, app, build_result)
    RevertPatches(current_real_path, app)
  return build_result


def RunGetBuildToolScript(options, current_real_path):
  xwalk_app_template_path = os.path.join(current_real_path, 'android', 'xwalk_app_template')
  # Remove build tool, we need to get new one.
  if os.path.exists(xwalk_app_template_path):
    shutil.rmtree(xwalk_app_template_path)
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
  # Check whether download xwalk_app_template succeed.
  if not os.path.exists(xwalk_app_template_path):
    return False;
  return True


def CheckAndroidBuildTool(options, current_real_path):
  xwalk_app_template_path = os.path.join(current_real_path, 'android', 'xwalk_app_template')

  # If the version of build tool is specified.
  # We need to switch to the specified version.
  if options.version:
    return RunGetBuildToolScript(options, current_real_path)

  # No build tool version specified.
  # Use previous build tool.
  if os.path.exists(xwalk_app_template_path):
    return True
  else:
    # No build tool found, download one.
    return RunGetBuildToolScript(options, current_real_path)


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
           'Such as: --version=2.31.27.0')
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
