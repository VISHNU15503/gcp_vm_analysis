#!/bin/bash

# Install Git
sudo apt install git -y

# Install Pip to install Python packages
sudo apt install python3-pip -y

# Install Python packages
pip3 install numpy
pip3 install pandas
pip3 install joblib
pip3 install scikit-learn
pip3 install flask

# Clone the repository
git clone https://github.com/VISHNU15503/iris_classification.git
cd iris_classification
python3 predict.py
# Predict the class of Iris flower
#python3 predict.py 5.1 3.5 1.4 0.2

