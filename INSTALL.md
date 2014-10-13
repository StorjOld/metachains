Setting up florincoind on Ubuntu
==============================

The following tutorial shows you how to compile and install florincoind on a freshly installed Ubuntu system, including the necessary dependencies. Everything is done from the Terminal. Be sure that you are logged in as the user who you want to automatically start florincoind upon system boot. This has been tested on Ubuntu 14.04.1 x86_64 on [Digital Ocean](http://digitalocean.com).

Initial Steps
-------------

First, there are some dependencies and tools that can easily be installed through apt-get:

    sudo apt-get update ; sudo apt-get install -y build-essential m4 libssl-dev libdb++-dev libboost-all-dev libminiupnpc-dev zip libgmp-dev

Then, create a directory for the files that you download and compile in the next steps:

    mkdir ~/build;

Download and Compile florincoind
------------------------------

Get the florincoind file from GitHub and extract it:

    cd ~/build
    wget https://github.com/pascalguru/florincoin/archive/master.zip
    unzip master.zip;cd florincoin-master/src ;

Then, compile and install florincoind:

    make -f makefile.unix
    sudo cp -f florincoind /usr/local/bin/

Setup florincoin
--------------

Now add a configuration file with some values to your user directory:

    mkdir -p ~/.florincoin;
    echo 'addnode=node1.metadisk.org
    addnode=node2.metadisk.org
    addnode=node3.metadisk.org
    rpcport=7313
    daemon=1
    server=1
    listen=1
    port=7312
    noirc=0
    maxconnections=30
    addnode=146.185.148.114
    addnode=192.241.171.45
    rpcallowip=127.0.0.1
    rpcuser=florincoinrpc
    rpcpassword=f1239a0069m' > ~/.florincoin/florincoin.conf

Add florincoin as a daemon
------------------------

In order to make florincoind start upon system boot and stop when the system shuts down, create an Upstart script with the following command:

    echo 'description "florincoind"
    start on filesystem
    stop on runlevel [!2345]
    oom never
    expect daemon
    respawn
    respawn limit 10 60 # 10 times in 60 seconds
    script
    user='"$USER"'
    home=/home/$user
    cmd=/usr/local/bin/florincoind
    pidfile=$home/.florincoin/florincoind.pid
    # Dont change anything below here unless you know what youre doing
    [[ -e $pidfile && ! -d "/proc/$(cat $pidfile)" ]] && rm $pidfile
    [[ -e $pidfile && "$(cat /proc/$(cat $pidfile)/cmdline)" != $cmd* ]] && rm $pidfile
    exec start-stop-daemon --start -c $user --chdir $home --pidfile $pidfile --startas $cmd -b -m
    end script' | sudo tee /etc/init/florincoind.conf > /dev/null;

Then, reload the configuration to include the script you just made:

    sudo initctl reload-configuration

If you want to manually start florincoind as a daemon, run `sudo start florincoind` and to stop it, run `sudo stop florincoind`.

