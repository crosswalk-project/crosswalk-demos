## Introduction
crosswalk-demos is a collection of sample web apps for demonstrating and testing Crosswalk.

It is an open source project started by the [Intel Open Source Technology Center]
(http://www.01.org).

## Build web apps

### Android
Before building web apps into Android APKs, please install Android SDK and make
sure the command 'android' of Android SDK in your PATH under Linux environment.

Run it with the below command for Android:

`python ./make_webapp.py --target=android -v 2.31.27.1 -u https://download.01.org/crosswalk/releases/android-x86/beta/`


Outputs are in the folder 'out/android'.


For more information, please run:

`python make_webapp.py --help`

### Tizen
It is to be defined.

## Build 19 01.org web apps
The method for building the [19 01.org web
apps](https://01.org/html5webapps/webapps) is currently different from
the above, but efforts will be made to integrate them, as well as improve
them generally.

The script to build these apps depends on the android tools downloaded
and unpacked by the `make_webapp.py` script, above, and it assumes that
script has already been run. After that, it is a simple matter of running

`./make_01_webapps`

It will build the apps and package them into both apk and xpk files for
Android and Tizen respectively, which are placed in directories xpk/
and apk/. Building can take some time.

Note that `make_01_webapps` has a few dependencies as described in the
head of the script, notably `npm` (a commonly used tool for an html5
developers). Furthermore, the script itself, as well as some utility
scripts, is written in bash (standard on many platforms, and comes
with git on Microsoft Windows).

## Microsoft Windows support
This is currently work-in-progress.

## License
Crosswalk's code uses the BSD license, see our `LICENSE` file.
