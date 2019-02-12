import boto3, io, zipfile, mimetypes

def lambda_handler(event, context):
	
	sns = boto3.resource('sns')
	topic = sns.Topic('arn:aws:sns:us-west-1:710058944513:deployPortfolioTopic')
	location = {
		"bucketName": 'portfoliobuild.codecorax.com',
		"objectKey": 'portfoliobuild.zip'
	}
	try:
		job = event.get("CodePipeline.job")
		
		if job:
			for artifact in job["data"]["inputArtifacts"]:
				if artifact["name"] == "MyAppBuild":
					location = artifact["location"]["s3Location"]
		
		print("Building portfolio from" + str(location))
		s3 = boto3.resource('s3')
		
		portfolio_bucket = s3.Bucket('portfolio.codecorax.com')
		build_bucket = s3.Bucket(location["bucketName"])
		
		portfolio_zip = io.BytesIO()
		build_bucket.download_fileobj(location["objectKey"], portfolio_zip)
		
		with zipfile.ZipFile(portfolio_zip) as myzip:
			for nm in myzip.namelist():
				obj = myzip.open(nm)
				portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
				portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
				
		print("Job Complete!")	
		topic.publish(Subject="Portfolio Deployed", Message="Portfolio deployed successfully!")
		if job:
			codepipeline = boto3.client('codepipeline')
			codepipeline.put_job_success_result(jobId=job["id"])
	except:
		topic.publish(Subject="Portfolio Deployment Failure", Message="Portfolio has failed to deploy")
		raise
	return 'Unauthorized Response Detected. Engaging Nuclear Tactical Weapons.'