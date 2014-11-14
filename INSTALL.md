Setting up florincoind on Ubuntu
==============================

The following tutorial shows you how to compile and install florincoind on a freshly installed Ubuntu system, including the necessary dependencies. Everything is done from the Terminal. Be sure that you are logged in as the user who you want to automatically start florincoind upon system boot. This has been tested on Ubuntu 14.04.1 x86_64 on [Digital Ocean](http://digitalocean.com).

Initial Steps
-------------

First, there are some dependencies and tools that can easily be installed through apt-get:

    sudo apt-get update ; sudo apt-get install -y build-essential m4 libssl-dev libdb++-dev libboost-all-dev libminiupnpc-dev zip libgmp-dev

Pre-complied florincoind
--------------------------------
In the Storj fork of [Florincoin](https://github.com/Storj/florincoin), there are release binaries [here](https://github.com/Storj/florincoin/releases), that you may download those instead of compiling from scatch. 

    wget https://github.com/Storj/florincoin/releases/download/0.6.5.15/florincoind-ubuntu1404x64
    mv florincoind-ubuntu1404x64 florincoind
    sudo cp -f florincoind /usr/local/bin/
    
Skip the steps for to "Download and Compile florincoind", and procede to "Setup florincoin."

Download and Compile florincoind
--------------------------------
Create a directory for the files that you download and compile in the next steps:

    mkdir ~/build;

Get the florincoind file from GitHub and extract it:

    cd ~/build
    wget https://github.com/pascalguru/florincoin/archive/master.zip
    unzip master.zip;cd florincoin-master/src ;

Then, compile and install florincoind:

    make -f makefile.unix
    sudo cp -f florincoind /usr/local/bin/

If you are using a virtual machine with 1 GB or less the build may fail due to insufficient RAM. You can use [this guide](https://www.digitalocean.com/community/tutorials/how-to-add-swap-on-ubuntu-12-04) to add some swap.

Setup florincoin
----------------

Now add a configuration file with some values to your user directory. You should change `rpcuser` and `rpcpassword` values to your own for security reasons. 

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
    rpcuser=user
    rpcpassword=pass' > ~/.florincoin/florincoin.conf

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

Finding florincoin sync status
------------------------
You can run florincoind independently:

    florincoind -daemon
    florincoind getinfo

This will give you the current block as part of the status. See the [Florincoin block explorer](http://florincoin.info/explorer/) to see the latest block. 

    root@florincoin:~/build/florincoin-master/src# florincoind getinfo
    {
        "version" : 60515,
        "protocolversion" : 60001,
        "walletversion" : 60000,
        "balance" : 0.00000000,
        "blocks" : 251144,
        "connections" : 4,
        "proxy" : "",
        "difficulty" : 0.37392803,
        "testnet" : false,
        "keypoololdest" : 1415921429,
        "keypoolsize" : 101,
        "paytxfee" : 0.00000000,
        "mininput" : 0.00010000,
        "errors" : ""
    }
