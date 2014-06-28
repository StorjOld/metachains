Setting up datacoind on Ubuntu
==============================

The following tutorial shows you how to compile and install datacoind on a freshly installed Ubuntu system, including the necessary dependencies. Everything is done from the Terminal. Be sure that you are logged in as the user who you want to automatically start datacoind upon system boot. This has been tested on Ubuntu 12.04.4 x32 on [Digital Ocean](http://digitalocean.com).

Initial Steps
-------------

First, there are some dependencies and tools that can easily be installed through apt-get:

    sudo apt-get update ; sudo apt-get install -y build-essential m4 libssl-dev libdb++-dev libboost-all-dev libminiupnpc-dev zip libgmp-dev

Then, create a directory for the files that you download and compile in the next steps:

    mkdir ~/build;

Download and Compile datacoind
------------------------------

Get the datacoind file from GitHub and extract it:

    cd ~/build
    wget https://github.com/foo1inge/datacoin-hp/archive/master.zip ;
    unzip master.zip;cd datacoin-hp-master/src ;

The makefile needs some editing before it can be used for compiling:

    cp makefile.unix makefile.my;
    sed -i -e 's/$(OPENSSL_INCLUDE_PATH))/$(OPENSSL_INCLUDE_PATH) \/usr\/local\/include)/' makefile.my;
    sed -i -e 's/$(OPENSSL_LIB_PATH))/$(OPENSSL_LIB_PATH) \/usr\/local\/lib)/' makefile.my ;
    sed -i -e 's/$(LDHARDENING) $(LDFLAGS)/$(LDHARDENING) -Wl,-rpath,\/usr\/local\/lib $(LDFLAGS)/' makefile.my;

Then, compile and install datacoind:

    make -f makefile.my
    sudo cp -f datacoind /usr/local/bin/

Setup datacoin
--------------

Now add a configuration file with some values to your user directory:

    mkdir -p ~/.datacoin;
    echo 'addnode=node1.storj.io
    addnode=node2.storj.io
    addnode=76.126.98.2:4777
    addnode=95.85.19.138:4777
    addnode=92.222.24.57:4777
    addnode=89.122.9.160:4777
    addnode=87.106.56.19:4777
    addnode=222.223.153.175:41430
    addnode=66.85.122.10:60452
    addnode=174.0.123.157:4777
    addnode=86.138.230.200:52832
    server=1
    rpcallowip=127.0.0.1
    rpcuser=primecoinrpc
    rpcpassword=f1239a0069m
    sievesize=1000000' > ~/.datacoin/datacoin.conf

Add datacoin as a daemon
------------------------

In order to make datacoind start upon system boot and stop when the system shuts down, create an Upstart script with the following command:

    echo 'description "datacoind"
    start on filesystem
    stop on runlevel [!2345]
    oom never
    expect daemon
    respawn
    respawn limit 10 60 # 10 times in 60 seconds
    script
    user='"$USER"'
    home=/home/$user
    cmd=/usr/local/bin/datacoind
    pidfile=$home/.datacoin/datacoind.pid
    # Dont change anything below here unless you know what youre doing
    [[ -e $pidfile && ! -d "/proc/$(cat $pidfile)" ]] && rm $pidfile
    [[ -e $pidfile && "$(cat /proc/$(cat $pidfile)/cmdline)" != $cmd* ]] && rm $pidfile
    exec start-stop-daemon --start -c $user --chdir $home --pidfile $pidfile --startas $cmd -b -m
    end script' | sudo tee /etc/init/datacoind.conf > /dev/null;

Then, reload the configuration to include the script you just made:

    sudo initctl reload-configuration

If you want to manually start datacoind as a daemon, run `sudo start datacoind` and to stop it, run `sudo stop datacoind`.

