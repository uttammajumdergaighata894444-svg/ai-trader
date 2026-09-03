name: Build APK

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y \
            build-essential \
            git \
            python3-pip \
            libffi-dev \
            libssl-dev \
            zlib1g-dev \
            openjdk-17-jdk \
            autoconf \
            libtool \
            pkg-config \
            libncurses5-dev \
            libncursesw5-dev \
            unzip \
            zip \
            libltdl-dev \
            wget \
            curl

    - name: Install Buildozer and Cython
      run: |
        pip install --upgrade pip
        pip install --user cython==0.29.36
        pip install --user buildozer

    - name: Run Buildozer
      run: |
        export PATH=$PATH:~/.local/bin
        # Force buildozer to accept licenses and build using correct parameters
        yes | buildozer -v android debug

    - name: Upload APK Artifact
      uses: actions/upload-artifact@v4
      with:
        name: package
        path: bin/*.apk
        
