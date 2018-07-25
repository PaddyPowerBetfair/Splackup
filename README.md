splackup.py
=
A simple backup for Splunk. This program connects to a Splunk instance, using an admin enabled account, and transfers knowledge elements from the instance, storing them as XML files on your local system.

This program was written to allow us to commit changes made on our Splunk cloud instance into git (on a nightly basis), allowing a certain amount of source control.

To run the program, edit it providing details on how to connect to your splunk instance (search for the # CHANGE HERE comments in the code), then run with no parameters, e.g.:

>$ python ./splackup.py

This has been tested on _Python 2.7_ using _requests_, _xml_, _os_, _urllib2_ and _re_ libraries.

The code will produce a _services_ and _servicesNS_ directory in the current directory storing the elements. The elements will be named _object-0.xml_. At the moment the program only saves elements that return a single result, however it can be simply made to save list elements as well. If you modify 
> if searchSize==1:

to save lists (for example _if searchSize>0_), note that the file will be object-_page_.xml. where page size is defined by _pageSize_, so you may now see several object files on larger lists.

As we wish to send the data into git, we currently remove 2 elements:

>_\<updated\>_ ..._\</updated>_

and

>_\<s:key name="next_scheduled_time">_ ... _\</s:key>_

As these elements will vary even if the element has not been changed. If you don't need or want this, search for the lines containing _start=re.sub_ and comment them out.

The _init.sh_ and _update.sh_ scripts are provided as examples of how you can use this program to backup to a git repo. You'll need to modify _init.sh_ to contain the details of your repository, and also provide the git_dsa file needed to connect to your repository.

## How can I contribute?
Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## What licence is this released under?
This is released under a modified version of the BSD licence.
Please see [LICENCE.md](https://github.com/PaddyPowerBetfair/standards/blob/master/LICENCE.md).