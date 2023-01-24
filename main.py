import openai, os, requests, smtplib

class GPT3:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key
        
    def generate_text(self, prompt, max_tokens=1024, n=1, temperature=0.5):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=max_tokens,
            n=n,
            temperature=temperature
        )
        return response.choices[0].text

class Canvas:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_courses(self, enrollment_state='active', per_page=150):
        response = requests.get(
            "https://canvas.instructure.com/api/v1/courses",
            params={'per_page': per_page, 'enrollment_state': enrollment_state},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()
    
    def get_assignments(self, course_id):
        response = requests.get(
            f"https://uk.instructure.com/api/v1/courses/{course_id}/assignments",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()

class Email:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def send_email(self, to_email, subject, body):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.username, self.password)
        message = f'Subject: {subject}\n\n{body}'
        server.sendmail(self.username, to_email, message)
        server.quit()

# Set up the API keys
canvas_api_key = os.environ['canvasKey']
openai.api_key = os.environ['openAIKey']
email_username = os.environ['gEmail']
email_password = os.environ['gPass']

# Initialize the classes
canvas = Canvas(canvas_api_key)
gpt3 = GPT3(openai.api_key)
email = Email(email_username, email_password)

# Get the current classes
courses = canvas.get_courses()

# Filter the classes that have "Spring 2023" in their name
spring_courses = [course for course in courses if "Spring 2023" in course["name"]]

# Get the assignments for each class
assignment_dict = {}
for course in spring_courses:
    course_id = course["id"]
    assignments = canvas.get_assignments(course_id)
    for assignment in assignments:
        assignment_dict[f"{course['name']}: {assignment['name']}"] = assignment['description']

# Send the assignments to GPT-3 and generate text
for key, value in assignment_dict.items():
    prompt = (f"Use HTML to help parse the following assignment. Provide an in depth completion using markdown to organize your thoughts. Don't repeat my prompt in your response: {key} - {value}")
    gpt3_response = gpt3.generate_text(prompt)
    with open(f"{key}.md", "w") as file:
        file.write(gpt3_response)

    # Send the response to the email
    email.send_email(email_username, 'GPT-3 Response', gpt3_response)
