# John Deere Container Optimization Project
Context:
John Deere’s Mattoon IL business unit is transitioning to a new warehouse management system.​ John Deere has tasked the JD Container Team to determine the Standard Quantity for SKUs in six storage containers.​

Standard Quantity = the maximum number of boxes of a specific SKU that can fit into each of the six storage containers without overlap and within their size constraints.​

Establishing the Standard Quantity for each of the 6 containers will ensure:​
1) consistent packing standards across units ​
2) maximized storage density ​
3) enhanced labor efficiency​
  
## The end goal for this project:
To create an excel document which lists out every one of John Deere's SKU's , along with the maxiumum number of SKU's that can fit into the 6 different containers that we can pack the SKUs in. 

## How the JD Optimization Team went above and beyond:
1) Firstly, we delivered on the excel document ask. We have created an excel document which lists out all SKU's , along with the standard quantities for each of the 6 containers.
2) On top of just providing an excel document with the standard quantities, we provided the John Deere team with code , which will output charts of how the SKU'S should be stacked/positioned within each of the 6 containers - This code takes in input from the user (what SKU they want to analyze) and then outputs a PDF document with the stacking patten (In chart form), standard quantity, and % utilization for each of the 6 containers - We then go ahead and provide a reccomendation on what container to use for a particular SKU, based on the % utilization metric.
3) Finally, we created a web app, which essentially provides all the outputs listed in bullet point number 2 , but this now utilizes a better end user interface.
 
## What logic are we using to come up with these optimized stacking patterns for the John Deere Team?
We are using a Python library called Py3dbp​. This library:
1) Handles 3D packing: Designed for complex three-dimensional packing challenges.​
2) Flexible for various shapes: Can manage a wide variety of shapes, adaptable to different use cases.​

## Where can I find the various components of this project?
We have created 2 branches in this GitHub Repository - One branch which houses the web application code, and another branch which houses the "MVP" code. Here are the locations of the following items:
Found on Main Branch (This is the branch which deals with delivering on the MVP solution):
1) Code which populates the CSV which lists the standard quantities for all of our packages = https://github.com/vrayas/jd-container-opt/blob/main/final/jd_container_optimize_final.ipynb
2) Code which generates charts for stacking patterns, standard quantites, % of volumne utilzed etc... = https://github.com/vrayas/jd-container-opt/blob/main/final/jd_container_optimize.ipynb

Found on Web App Branch:
1) Code which populates the web app: https://github.com/vrayas/jd-container-opt/blob/WebApp/BinPacking/App.py
2) Web app URL: https://binpacking-h85ysor5ginzwbc5awp8ld.streamlit.app/

## How can I run the Non Web App version of the project (The code found on the main branch)?

1) Install python on your local machine. 
2) Open final -> jd_container_optimize.ipynb and run using python libraries. 
3) If you want to use custom dimensions, then answer 'Do you want to use custom package dimensions? (yes/no): yes'. If you answer no, you will need to enter a SKU found in the raw excel file that we received from John Deere : "Optimization Problem.xlsx"
	
