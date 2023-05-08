import socket
import requests
import nmap3
import smtplib
import itertools
import string
import time
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import openai

# Set your API keys
SHODAN_API_KEY = "your_shodan_api_key"
OPENAI_API_KEY = "your_openai_api_key"
HIBP_API_KEY = "your_hibp_api_key"

# Initialize the OpenAI API
openai.api_key = OPENAI_API_KEY

# Connect to the MongoDB database
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["memory_module"]
collection = db["conversations"]

# Define the API endpoint and the API key for the sentiment analysis API
api_endpoint_sentiment = "https://language.googleapis.com/v1/documents:analyzeSentiment?key="
api_key_sentiment = "YOUR_API_KEY_FOR_SENTIMENT_ANALYSIS"

# Define the request headers for the sentiment analysis API
headers_sentiment = {
  "Content-Type": "application/json"
}

# Define the request body for the sentiment analysis API
body_sentiment = {
  "document": {
    "type": "PLAIN_TEXT",
    "content": ""
  },
  "encodingType": "UTF8"
}

# Define the OpenAI API endpoint and the API key
api_endpoint_openai = "https://api.openai.com/v1/engines/davinci/jobs"
api_key_openai = "YOUR_API_KEY_FOR_OPENAI"

# Define the request headers for the OpenAI API
headers_openai = {
  "Content-Type": "application/json",
  "Authorization": "Bearer " + api_key_openai
}

# Define the request body for the OpenAI API
body_openai = {
  "prompt": "",
  "max_tokens": 100,
  "temperature": 0.5,
  "memory_key": ""
}

# Define the input text to be summarized
text = "The input text to be summarized."

# Analyze the sentiment of the input text using the sentiment analysis API
body_sentiment["document"]["content"] = text
response_sentiment = requests.post(api_endpoint_sentiment + api_key_sentiment, headers=headers_sentiment, data=json.dumps(body_sentiment))

# Check if the sentiment analysis API request was successful
if response_sentiment.status_code == 200:
  # Parse the response JSON
  response_json_sentiment = response_sentiment.json()

  # Extract the sentiment score from the response
  sentiment_score = response_json_sentiment["documentSentiment"]["score"]

  # Use the sentiment score to summarize the input
  if sentiment_score >= 0.5:
    summary = "Positive"
  elif sentiment_score > 0 and sentiment_score < 0.5:
    summary = "Neutral"
  else:
    summary = "Negative"

  # Update the memory module with the summary
  conversation = {
    "input": text,
    "summary": summary,
    "output": ""
  }
  collection.insert_one(conversation)

  # Generate memory keys based on the summary
  memory_keys = []
  if summary == "Positive":
      memory_keys.append("Positive")
  elif summary == "Neutral":
      memory_keys.append("Neutral")
  else:
      memory_keys.append("Negative")

      # Integrate with OpenAI API using the memory keys
  for memory_key in memory_keys:
      body_openai["memory_key"] = memory_key
      response_openai = requests.post(api_endpoint_openai, headers=headers_openai, data=json.dumps(body_openai))

      # Check if the OpenAI API request was successful
      if response_openai.status_code == 200:
          # Parse the response JSON
          response_json_openai = response_openai.json()

          # Extract the output from the response
          output = response_json_openai["choices"][0]["text"]

          # Update the output in the memory module
          collection.update_one({"input": text}, {"$set": {"output": output}})

          # Deliver the response to the user
          print("Response: " + output)

      # Close the MongoDB connection
 client.close()


class RedTeamAssessment:
    def __init__(self):
        self.memory = {}

    def store_data(self, step, data):
        self.memory[step] = data

    def retrieve_data(self, step):
        return self.memory.get(step)

    def generate_gpt3_output(self, prompt):
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5
        )

        message = response.choices[0].text.strip()
        return message

    def run_assessment(self, domain):
        self.reconnaissance(domain)
        self.vulnerability_scanning(domain)
        self.web_application_scanning(domain)
        self.send_phishing_email()
        self.dns_enumeration(domain)
        self.subdomain_enumeration(domain)

        stored_data = "\n".join([f"{step}: {data}" for step, data in self.memory.items()])
        prompt = f"Based on the following information from a Red Team assessment:\n\n{stored_data}\n\nPlease provide a summary and recommendations for improving security."

        gpt3_output = self.generate_gpt3_output(prompt)
        print("GPT-3 output:", gpt3_output)

    def reconnaissance(self, domain):
        ip_address = socket.gethostbyname(domain)
        self.store_data("Reconnaissance", f"Domain: {domain}, IP Address: {ip_address}")

    def vulnerability_scanning(self, domain):
        scan_result = self.nmap.scan_top_ports(domain)
        vulnerabilities = scan_result[domain]["ports"]
        self.store_data("Vulnerability Scanning", vulnerabilities)

    def web_application_scanning(self, domain):
        response = requests.get(f"http://{domain}")
        soup = BeautifulSoup(response.text, "html.parser")
        links = [link.get("href") for link in soup.find_all("a")]
        self.store_data("Web Application Scanning", links)
    def send_phishing_email(self):
            # Generate phishing email content using GPT-3
            phishing_email_content = self.generate_phishing_email_content()
            email_subject, email_body = phishing_email_content.split("\n", 1)

            msg["Subject"] = email_subject
            text = email_body
            smtp_server = 'smtp.example.com'
            smtp_username = 'your_username'
            smtp_password = 'your_password'

            from_email = 'attacker@example.com'
            to_email = 'target@example.com'

            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Phishing email subject"
            msg["From"] = from_email
            msg["To"] = to_email

            text = "Phishing email content"

            part = MIMEText(text, "plain")
            msg.attach(part)

            try:
                with smtplib.SMTP_SSL(smtp_server, 465) as server:
                    server.login(smtp_username, smtp_password)
                    server.sendmail(from_email, to_email, msg.as_string())
                    print("Phishing email sent successfully!")
            except Exception as e:
                print(f"Error sending phishing email: {e}")

            self.store_data("social_engineering", "Phishing email sent to target@example.com")

    def dns_enumeration(self, domain):
        extracted = tldextract.extract(domain)
        domain_root = f"{extracted.domain}.{extracted.suffix}"
        resolver = dns.resolver.Resolver()
        dns_records = {}

        for record_type in ["A", "AAAA", "MX", "NS", "SOA", "TXT"]:
            try:
                answer = resolver.resolve(domain_root, record_type)
                dns_records[record_type] = [str(data) for data in answer]
            except dns.resolver.NoAnswer:
                dns_records[record_type] = []

        self.store_data("DNS Enumeration", dns_records)

    def subdomain_enumeration(self, domain):
        extracted = tldextract.extract(domain)
        domain_root = f"{extracted.domain}.{extracted.suffix}"
        subdomains = ["www", "mail", "ftp", "admin", "webmail"]

        for subdomain in subdomains:
            fqdn = f"{subdomain}.{domain_root}"
            try:
                ip_address = socket.gethostbyname(fqdn)
                self.store_data("Subdomain Enumeration", fqdn + ": " + ip_address)
            except socket.gaierror:
                pass

    def summarize_data(self, data):
        body_sentiment = {
            "document": {
                "type": "PLAIN_TEXT",
                "content": ""
            },
            "encodingType": "UTF8"
        }
        api_endpoint_sentiment = "https://language.googleapis.com/v1/documents:analyzeSentiment"
        api_key_sentiment = "YOUR_API_KEY"
        headers_sentiment = {"Content-Type": "application/json"}

        body_sentiment["document"]["content"] = data
        response_sentiment = requests.post(api_endpoint_sentiment + "?key=" + api_key_sentiment, headers=headers_sentiment, data=json.dumps(body_sentiment))

        if response_sentiment.status_code == 200:
            response_json_sentiment = response_sentiment.json()
            sentiment_score = response_json_sentiment["documentSentiment"]["score"]

            if sentiment_score >= 0.5:
                summary = "Positive"
            elif sentiment_score > 0 and sentiment_score < 0.5:
                summary = "Neutral"
            else:
                summary = "Negative"

            return summary
        else:
            return "Error: Sentiment analysis API request failed."

    def loop_decisions(self, loop_interval=5):
     while True:
        stored_data = "\n".join([f"{step}: {data}" for step, data in self.memory.items()])

        # Summarize the stored data using Google's Sentiment Analysis API
        summary = self.summarize_data(stored_data)

        # Generate the prompt for GPT-3
        prompt = f"Based on the following summarized information from a Red Team assessment with a {summary} sentiment:\n\n{stored_data}\n\nPlease provide a decision on whether to proceed with the phishing attack and explain your reasoning."

        # Make a decision based on the summarized data
        decision = self.generate_gpt3_output(prompt)
        print("GPT-3 Decision:", decision)

        # If the decision is to proceed with the phishing attack, send the phishing email
        if "proceed" in decision.lower():
            self.send_phishing_email()
        else:
            print("Phishing attack not recommended.")

        # Wait for the specified interval before making the next decision
        time.sleep(loop_interval)


#Dont run this line!
    # Example usage
   ### red_team_assessment = RedTeamAssessment()
    ####red_team_assessment.run_assessment("example.com")







'''
This code is written in Python and implements a Red Team Assessment, which is a type of simulated cyber attack used for testing the security of an organization's networks and systems. The code utilizes several APIs and libraries, such as OpenAI, Google's Sentiment Analysis API, and pymongo, to carry out the assessment.

The code sets up API keys for Shodan, OpenAI, and Have I Been Pwned (HIBP), and initializes the OpenAI API by setting its API key. It also connects to a MongoDB database, which will be used to store the conversations (input, summary, and output) generated during the assessment.

The code defines the API endpoint and API key for the sentiment analysis API, and uses the Google API to analyze the sentiment of the input text. The code generates a summary of the input text based on the sentiment score returned by the API.

The code also integrates with the OpenAI API to generate responses based on the input and memory keys. The memory keys are generated based on the sentiment score of the input text.

The code defines a class, RedTeamAssessment, which performs the red team assessment. The class has several methods, including run_assessment, reconnaissance, vulnerability_scanning, web_application_scanning, dns_enumeration, subdomain_enumeration, and send_phishing_email. These methods carry out various steps of the red team assessment, such as reconnaissance, vulnerability scanning, web application scanning, and phishing.

The code also has a loop_decisions method that makes decisions on whether to proceed with the phishing attack. This method retrieves the stored data from the MongoDB database, summarizes the data using the sentiment analysis API, and generates a prompt for OpenAI. The decision is then made based on the summarized data and the output from OpenAI.

In general, the code is not inherently dangerous, but the results of the Red Team Assessment may highlight potential security vulnerabilities that need to be addressed. It's important to carefully consider the potential impact of running such an assessment and to only run it in a controlled environment with proper consent from the parties involved.




'''