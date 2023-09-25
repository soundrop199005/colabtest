# Narrative Test - Cifar 10 Classification with Small Models
This repository is created to demonstrate the work being done for Narrative Test - Cifar 10 Classification with Small Models.
Level1.ipynb file is the google colab notebook which shows the work I have done for level1 task, including the data downloading, the training process, the hyper parameter tuning and the model evaluation. Level1 task model uses MobileNetV2 basemodel slightly modified, trained from scratch. 
level1_trainmodel.py is the script you can use to train level1 model from scratch and save it to a file.
level1_testmodel.py is the script you can use to test both level1 and level2 models.
UserDoc.pdf is the documentation explaining how to run level1_trainmodel.py and level1_testmodel.py
Level2.ipynb file is the google colab notebook which shows the work I have done for level2 task, including the data downloading, the training process, the hyper parameter tuning and the model evaluation. Level2 task model uses MobileNetV2 basemodel shallow layers by removing two deep bottlenecks, trained from scratch. 
In both task1 and task2 models, mobilenetv2 preprocess is imbedded into the model itself so that we can import test data directly to the model. 
