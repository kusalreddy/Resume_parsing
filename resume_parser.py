import re
import json
from transformers import BertTokenizer, BertForTokenClassification, pipeline

def combine_subwords(tokens):
    """
    Combine subword tokens into full words by removing '##' and joining tokens.
    """
    words = []
    current_word = ""
    for token in tokens:
        if token.startswith('##'):
            # Append token without '##'
            current_word += token[2:]
        else:
            if current_word:
                # Add the current word to the list
                words.append(current_word)
                current_word = ""
            # Add the new token
            current_word = token
    
    if current_word:
        words.append(current_word)
    
    return words

def parse_resume(resume_data):
    # Load pre-trained BERT model and tokenizer for NER
    model_name = 'dbmdz/bert-large-cased-finetuned-conll03-english'
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForTokenClassification.from_pretrained(model_name)
    nlp = pipeline("ner", model=model, tokenizer=tokenizer)

    # Extract entities
    entities = nlp(resume_data)

    # Initialize parsed information
    parsed_info = {
        "Full Name": "",
        "Email ID": "",
        "GitHub Portfolio": "",
        "LinkedIn ID": "",
        "Employment Details": [],
        "Technical Skills": [],
        "Soft Skills": []
    }

    # Regex patterns
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    name_pattern = re.compile(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b')
    github_pattern = re.compile(r'github\.com\/[\w\-]+')
    linkedin_pattern = re.compile(r'linkedin\.com\/in\/[\w\-]+')

    # Extract email
    email_match = email_pattern.search(resume_data)
    if email_match:
        parsed_info["Email ID"] = email_match.group()

    # Extract names using regex as fallback
    names = name_pattern.findall(resume_data)
    if names:
        parsed_info["Full Name"] = ' '.join(names[:2])  # Assuming the full name is the first two capitalized words

    # Extract URLs
    github_match = github_pattern.search(resume_data)
    linkedin_match = linkedin_pattern.search(resume_data)
    
    if github_match:
        parsed_info["GitHub Portfolio"] = github_match.group()
    if linkedin_match:
        parsed_info["LinkedIn ID"] = linkedin_match.group()

    # Aggregating entity values
    employment_details = []
    technical_skills = []
    for entity in entities:
        word = entity['word']
        if entity['entity'] == 'I-ORG':
            employment_details.append(word)
        elif entity['entity'] == 'I-MISC':
            technical_skills.append(word)

    # Clean and combine tokens
    parsed_info["Employment Details"] = combine_subwords(employment_details)
    parsed_info["Technical Skills"] = combine_subwords(technical_skills)
    
    # Convert parsed information to JSON format
    json_output = json.dumps(parsed_info, indent=4)
    
    # Display results (optional)
    print(json_output)

    return json_output


# Example usage-single-shot response
resume_data = """
Kusal Degapudi
Hyderabad Telangana
Objective: Highly Automation Manual Selenium Automation Proven Seeking
Education: Bachelor Technology Electronics Communication School Technology Hyderabad Telangana June
Professional Experience: Software Engineer Value Momentum Software Pvt Hyderabad Telangana June Present
Conducted Experience Designed Test Cases Test User Stories Azure Execution Test Test Plans Reported Worked Performed Integration Maintained Selenium Java Cucumber Developed Collaborated Conducted Postman Performed Participated Collaborated Developed Actively
Technical Skills: Test Automation Tools Selenium Cucumber Testing Proficient Test Automation Had Selenium Testing Tools Experience Postman Bug Tracking Tools Experience Azure Version Control Systems Familiarity Git Agile Methodology Knowledge Agile Agile
Declaration: Date Signature Place
"""

# Run the function
parse_resume(resume_data)
