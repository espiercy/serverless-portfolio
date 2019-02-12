import boto3, io, zipfile, mimetypes

def lambda_handler(event, context):
	
	sns = boto3.resource('sns')
	topic = sns.Topic('arn:aws:sns:us-west-1:710058944513:deployPortfolioTopic')
	try:
		s3 = boto3.resource('s3')
		portfolio_bucket = s3.Bucket('portfolio.codecorax.com')
		
		build_bucket = s3.Bucket('portfoliobuild.codecorax.com')
		
		portfolio_zip = io.BytesIO()
		build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)
		
		with zipfile.ZipFile(portfolio_zip) as myzip:
			for nm in myzip.namelist():
				obj = myzip.open(nm)
				portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
				portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
				
		print("Job Complete!")	
		topic.publish(Subject="Portfolio Deployed", Message="Portfolio deployed successfully!")
	except:
		topic.publish(Subject="Portfolio Deployment Failure", Message="Portfolio has failed to deploy")
		raise
	return 'Unauthorized Response Detected. Engaging Nuclear Tactical Weapons.'