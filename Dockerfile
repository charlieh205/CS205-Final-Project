FROM ubuntu:18.04

WORKDIR /root/
RUN apt-get update && apt-get install -y wget git build-essential cmake lsb-release software-properties-common vim tmux papi-tools
RUN add-apt-repository ppa:ubuntu-toolchain-r/test 
RUN wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null && \
            apt-add-repository "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main" && \
            apt-get update && \
            apt-get install -y cmake gcc-11 g++-11 && \
            apt-get clean all

RUN update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 10

RUN git clone https://github.com/kz04px/libchess/ /opt/libchess && \
            cd /opt/libchess && \
            git checkout 32719b80a48f7f575414274106042b100f5abc21 && \
            mkdir build && \
            cd build && \
            cmake .. && \
            make && \
            cd ..

ADD Makefile /root/Makefile
ADD main.cpp /root/main.cpp
RUN make
