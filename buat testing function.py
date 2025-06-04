from client import RestClient

# Credential for API
Login_email = "gani@team.superfk.co"
Login_password = "f881f3d369097a8a"

# Initialize client
client = RestClient(Login_email, Login_password)

# using this method you can get a list of categories
# GET /v3/keywords_data/google_trends/categories
response = client.get("/v3/keywords_data/google_trends/categories")
# you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
if response["status_code"] == 20000:
    print(response)
    # do something with result
else:
    print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))