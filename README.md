# jd-container-opt

How run?

Install python in your local. 

Open final -> jd_container_optimize.ipynb and run using python libraries. 

 If you want to use custom dimention then answer 'Do you want to use custom package dimensions? (yes/no): yes'
 
        -> Then it will generate report based on the excel('Optimization Problem.xlsx)
        
        -> If you answer 'no' -- You need to enter the component id, length, width and high. 
		
Attached sample out puts of both packing_report1.html and packing_report2.html. 

Deployment plans:

Next steps to follow to deploy application on production:

1. Create deployment profile in aws using terraforms.
2. Create ECS container
     2.1 Create docker image. 
3. Deploy image in the container register(ECR)
4. Spin S3 bucket to host the JD optimization report. 
5. Create public access end point to run the application and launch the report. 
    5.1 Create CDN to access application multiple region with proper caching. 
	
