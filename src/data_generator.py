import json
import random
from datetime import datetime, timedelta
from faker import Faker
from typing import List, Dict, Any

fake = Faker()

class HRDataGenerator:
    """Generate synthetic HR and organizational documents"""
    
    def __init__(self):
        self.departments = [
            "Human Resources", "Engineering", "Marketing", "Sales", 
            "Finance", "Operations", "Legal", "Customer Support",
            "Product Management", "Data Science", "IT", "Quality Assurance"
        ]
        
        self.document_types = [
            "employee_handbook", "job_description", "policy_document",
            "training_material", "performance_review", "company_announcement",
            "benefits_guide", "code_of_conduct", "safety_guidelines",
            "onboarding_checklist"
        ]
        
        self.job_titles = [
            "Software Engineer", "Data Scientist", "Product Manager",
            "Marketing Specialist", "Sales Representative", "HR Generalist",
            "Financial Analyst", "Operations Manager", "UX Designer",
            "DevOps Engineer", "Business Analyst", "Customer Success Manager"
        ]
    
    def generate_employee_handbook_section(self) -> str:
        """Generate a section of an employee handbook"""
        sections = [
            self._generate_welcome_section(),
            self._generate_company_culture_section(),
            self._generate_benefits_section(),
            self._generate_policies_section(),
            self._generate_workplace_guidelines()
        ]
        return random.choice(sections)
    
    def _generate_welcome_section(self) -> str:
        company_name = fake.company()
        return f"""
        Welcome to {company_name}
        
        Dear Team Member,
        
        Welcome to {company_name}! We are thrilled to have you join our dynamic team. 
        This handbook serves as your guide to understanding our company culture, policies, 
        and procedures. Our mission is to {fake.catch_phrase().lower()}, and we believe 
        that every team member plays a crucial role in achieving this goal.
        
        At {company_name}, we value innovation, collaboration, and continuous learning. 
        We are committed to creating an inclusive environment where everyone can thrive 
        and contribute their unique perspectives and skills.
        
        Your journey with us begins now, and we look forward to supporting your 
        professional growth and success.
        
        Best regards,
        The {company_name} Leadership Team
        """
    
    def _generate_company_culture_section(self) -> str:
        return f"""
        Company Culture and Values
        
        Our Core Values:
        
        1. Innovation: We embrace creativity and encourage new ideas that drive progress.
        2. Integrity: We conduct business with honesty, transparency, and ethical standards.
        3. Collaboration: We work together as one team, supporting each other's success.
        4. Excellence: We strive for the highest quality in everything we do.
        5. Respect: We treat everyone with dignity and value diverse perspectives.
        
        Work Environment:
        We foster a collaborative and inclusive work environment where every voice is heard.
        Our open-door policy encourages communication at all levels, and we believe in
        work-life balance to ensure our team members can perform at their best.
        
        Professional Development:
        We invest in our people through continuous learning opportunities, mentorship
        programs, and career advancement paths. We encourage attendance at conferences,
        workshops, and training sessions relevant to your role.
        """
    
    def _generate_benefits_section(self) -> str:
        return f"""
        Employee Benefits Package
        
        Health and Wellness:
        - Comprehensive health insurance (medical, dental, vision)
        - Mental health support and counseling services
        - Wellness programs and gym membership reimbursement
        - Annual health screenings and preventive care
        
        Time Off and Flexibility:
        - {random.randint(15, 25)} days of paid vacation annually
        - {random.randint(8, 12)} paid holidays per year
        - Flexible work arrangements and remote work options
        - Parental leave for new parents
        - Personal and sick leave as needed
        
        Financial Benefits:
        - Competitive salary with annual reviews
        - Performance-based bonuses
        - 401(k) retirement plan with company matching
        - Stock options for eligible employees
        - Professional development budget of ${random.randint(1000, 3000)} annually
        
        Additional Perks:
        - Free snacks and beverages in the office
        - Team building events and company outings
        - Employee recognition programs
        - Referral bonuses for successful hires
        """
    
    def _generate_policies_section(self) -> str:
        return f"""
        Company Policies
        
        Attendance and Punctuality:
        Regular attendance and punctuality are essential for maintaining productivity
        and team collaboration. Core business hours are 9:00 AM to 5:00 PM, with
        flexibility for different work arrangements as approved by management.
        
        Communication Guidelines:
        - Use professional language in all business communications
        - Respond to emails within 24 hours during business days
        - Keep meetings focused and productive
        - Respect confidential information and maintain discretion
        
        Technology and Equipment:
        - Company equipment must be used responsibly and primarily for business purposes
        - Follow IT security protocols and report any security incidents immediately
        - Personal use of company technology should be minimal and appropriate
        - All software installations must be approved by the IT department
        
        Performance Standards:
        - Meet or exceed established performance goals and objectives
        - Participate actively in team meetings and collaborative projects
        - Maintain professional development through continuous learning
        - Provide constructive feedback and support to colleagues
        """
    
    def _generate_workplace_guidelines(self) -> str:
        return f"""
        Workplace Guidelines and Conduct
        
        Professional Behavior:
        All employees are expected to maintain the highest standards of professional
        conduct. This includes treating colleagues, clients, and partners with respect,
        maintaining confidentiality, and representing the company positively.
        
        Diversity and Inclusion:
        We are committed to creating a workplace free from discrimination and harassment.
        We celebrate diversity and believe that different perspectives make us stronger.
        Any form of discrimination based on race, gender, age, religion, sexual orientation,
        or any other protected characteristic will not be tolerated.
        
        Safety and Security:
        - Follow all safety protocols and report any hazards immediately
        - Maintain a clean and organized workspace
        - Secure confidential documents and information
        - Report any security concerns to management
        
        Social Media and External Communications:
        When representing the company or discussing work-related matters on social media
        or in public forums, employees should maintain professionalism and avoid sharing
        confidential information. Personal opinions should be clearly distinguished from
        company positions.
        """
    
    def generate_job_description(self) -> str:
        """Generate a job description"""
        title = random.choice(self.job_titles)
        department = random.choice(self.departments)
        company = fake.company()
        
        return f"""
        Job Description: {title}
        Department: {department}
        Company: {company}
        
        Position Overview:
        We are seeking a talented {title} to join our {department} team. This role offers
        an exciting opportunity to contribute to innovative projects and work with a
        collaborative team of professionals.
        
        Key Responsibilities:
        - {fake.sentence()}
        - {fake.sentence()}
        - {fake.sentence()}
        - {fake.sentence()}
        - Collaborate with cross-functional teams to deliver high-quality results
        - Participate in team meetings and contribute to strategic planning
        - Maintain up-to-date knowledge of industry trends and best practices
        
        Required Qualifications:
        - Bachelor's degree in relevant field or equivalent experience
        - {random.randint(2, 8)} years of experience in related role
        - Strong communication and interpersonal skills
        - Proficiency in relevant tools and technologies
        - Ability to work independently and as part of a team
        
        Preferred Qualifications:
        - Advanced degree in relevant field
        - Industry certifications
        - Experience with agile methodologies
        - Leadership or mentoring experience
        
        What We Offer:
        - Competitive salary range: ${random.randint(60, 150)}K - ${random.randint(80, 200)}K
        - Comprehensive benefits package
        - Professional development opportunities
        - Flexible work arrangements
        - Collaborative and inclusive work environment
        
        To apply, please submit your resume and cover letter through our careers portal.
        """
    
    def generate_policy_document(self) -> str:
        """Generate a policy document"""
        policies = [
            self._generate_remote_work_policy(),
            self._generate_expense_policy(),
            self._generate_pto_policy(),
            self._generate_security_policy()
        ]
        return random.choice(policies)
    
    def _generate_remote_work_policy(self) -> str:
        return f"""
        Remote Work Policy
        
        Effective Date: {fake.date_between(start_date='-1y', end_date='today')}
        
        Purpose:
        This policy establishes guidelines for remote work arrangements to ensure
        productivity, security, and effective communication while providing flexibility
        for our employees.
        
        Eligibility:
        Remote work arrangements are available to employees who:
        - Have been with the company for at least {random.randint(3, 12)} months
        - Demonstrate strong performance and self-management skills
        - Have roles that can be effectively performed remotely
        - Receive approval from their direct supervisor
        
        Guidelines:
        1. Work Schedule: Maintain regular business hours and be available for meetings
        2. Communication: Participate in daily check-ins and team meetings via video conference
        3. Productivity: Meet all performance standards and deadlines
        4. Equipment: Use company-provided equipment and maintain security protocols
        5. Workspace: Maintain a professional and distraction-free work environment
        
        Security Requirements:
        - Use VPN for all company network access
        - Secure physical workspace and equipment
        - Follow data protection and confidentiality guidelines
        - Report any security incidents immediately
        
        This policy is subject to review and may be modified based on business needs
        and employee feedback.
        """
    
    def _generate_expense_policy(self) -> str:
        return f"""
        Business Expense Reimbursement Policy
        
        Purpose:
        This policy outlines the procedures for submitting and approving business
        expense reimbursements to ensure appropriate use of company funds.
        
        Eligible Expenses:
        - Travel expenses (flights, hotels, ground transportation)
        - Business meals and entertainment (with business purpose)
        - Professional development and training
        - Office supplies and equipment
        - Client-related expenses
        
        Expense Limits:
        - Meals: ${random.randint(25, 75)} per person per day
        - Hotel accommodations: Up to ${random.randint(150, 300)} per night
        - Ground transportation: Reasonable and necessary costs
        - Professional development: Up to ${random.randint(2000, 5000)} annually
        
        Submission Requirements:
        - Submit expense reports within {random.randint(15, 30)} days of incurring expense
        - Provide original receipts for all expenses over ${random.randint(10, 25)}
        - Include business purpose and attendees for meal expenses
        - Obtain pre-approval for expenses over ${random.randint(500, 1000)}
        
        Approval Process:
        1. Employee submits expense report with supporting documentation
        2. Direct supervisor reviews and approves
        3. Finance team processes reimbursement
        4. Payment issued within {random.randint(5, 14)} business days
        
        Non-reimbursable expenses include personal items, excessive meal costs,
        entertainment without business purpose, and traffic violations.
        """
    
    def _generate_pto_policy(self) -> str:
        return f"""
        Paid Time Off (PTO) Policy
        
        Overview:
        Our PTO policy provides employees with flexible time off to rest, recharge,
        and attend to personal matters while maintaining business operations.
        
        PTO Accrual:
        - New employees: {random.randint(15, 20)} days annually
        - 2-5 years of service: {random.randint(20, 25)} days annually
        - 5+ years of service: {random.randint(25, 30)} days annually
        - PTO accrues monthly based on hours worked
        
        Usage Guidelines:
        - Minimum PTO request: 4 hours
        - Advance notice required: {random.randint(2, 4)} weeks for extended leave
        - Manager approval required for all PTO requests
        - PTO cannot be taken during blackout periods (year-end, major projects)
        
        Carryover Policy:
        - Maximum carryover: {random.randint(5, 10)} days to following year
        - Excess PTO above maximum will be forfeited
        - Use-it-or-lose-it policy encourages regular time off
        
        Holiday Schedule:
        In addition to PTO, the company observes {random.randint(10, 12)} paid holidays:
        - New Year's Day
        - Memorial Day
        - Independence Day
        - Labor Day
        - Thanksgiving (2 days)
        - Christmas Day
        - Additional floating holidays as announced
        
        Emergency Leave:
        In case of family emergencies or unexpected situations, employees may
        request emergency PTO with manager approval, even with short notice.
        """
    
    def _generate_security_policy(self) -> str:
        return f"""
        Information Security Policy
        
        Purpose:
        This policy establishes security standards to protect company information,
        systems, and assets from unauthorized access, disclosure, or damage.
        
        Password Requirements:
        - Minimum {random.randint(8, 12)} characters with complexity requirements
        - Include uppercase, lowercase, numbers, and special characters
        - Change passwords every {random.randint(60, 120)} days
        - No password reuse for last {random.randint(6, 12)} passwords
        - Use multi-factor authentication where available
        
        Data Classification:
        1. Public: Information that can be freely shared
        2. Internal: Information for internal use only
        3. Confidential: Sensitive information requiring protection
        4. Restricted: Highly sensitive information with limited access
        
        Access Controls:
        - Access granted based on job requirements and least privilege principle
        - Regular access reviews and updates
        - Immediate access revocation upon termination
        - Guest access requires approval and monitoring
        
        Incident Reporting:
        All security incidents must be reported immediately to the IT Security team:
        - Suspected malware or virus infections
        - Unauthorized access attempts
        - Lost or stolen devices
        - Suspicious emails or phishing attempts
        - Data breaches or potential breaches
        
        Compliance:
        All employees must complete annual security awareness training and
        acknowledge understanding of this policy. Violations may result in
        disciplinary action up to and including termination.
        """
    
    def generate_training_material(self) -> str:
        """Generate training material content"""
        topics = [
            "Leadership Development", "Communication Skills", "Project Management",
            "Technical Skills", "Customer Service", "Diversity and Inclusion",
            "Time Management", "Conflict Resolution", "Performance Management"
        ]
        
        topic = random.choice(topics)
        
        return f"""
        Training Module: {topic}
        
        Learning Objectives:
        By the end of this training, participants will be able to:
        - {fake.sentence()}
        - {fake.sentence()}
        - {fake.sentence()}
        - Apply learned concepts in real-world scenarios
        
        Module Content:
        
        Introduction:
        {topic} is a critical skill for professional success in today's workplace.
        This training module provides practical tools and techniques to enhance
        your capabilities in this area.
        
        Key Concepts:
        1. {fake.sentence()}
        2. {fake.sentence()}
        3. {fake.sentence()}
        4. {fake.sentence()}
        
        Best Practices:
        - {fake.sentence()}
        - {fake.sentence()}
        - {fake.sentence()}
        - Regular practice and application of learned skills
        - Seeking feedback and continuous improvement
        
        Case Studies:
        This section includes real-world examples and scenarios to help you
        understand how to apply these concepts in your daily work.
        
        Assessment:
        Complete the quiz and practical exercises to demonstrate your understanding
        of the material. A passing score of {random.randint(70, 85)}% is required.
        
        Resources:
        - Additional reading materials
        - Online resources and tools
        - Contact information for subject matter experts
        - Follow-up training opportunities
        """
    
    def generate_document(self) -> Dict[str, Any]:
        """Generate a complete document with metadata"""
        doc_type = random.choice(self.document_types)
        
        content_generators = {
            "employee_handbook": self.generate_employee_handbook_section,
            "job_description": self.generate_job_description,
            "policy_document": self.generate_policy_document,
            "training_material": self.generate_training_material,
            "performance_review": self._generate_performance_review,
            "company_announcement": self._generate_company_announcement,
            "benefits_guide": self._generate_benefits_guide,
            "code_of_conduct": self._generate_code_of_conduct,
            "safety_guidelines": self._generate_safety_guidelines,
            "onboarding_checklist": self._generate_onboarding_checklist
        }
        
        content = content_generators.get(doc_type, self.generate_employee_handbook_section)()
        
        return {
            "id": fake.uuid4(),
            "document_type": doc_type,
            "title": self._generate_title(doc_type),
            "content": content.strip(),
            "department": random.choice(self.departments),
            "created_date": fake.date_between(start_date='-2y', end_date='today').isoformat(),
            "author": fake.name(),
            "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}",
            "tags": self._generate_tags(doc_type),
            "word_count": len(content.split()),
            "metadata": {
                "classification": random.choice(["public", "internal", "confidential"]),
                "review_date": fake.date_between(start_date='today', end_date='+1y').isoformat(),
                "approver": fake.name(),
                "language": "en"
            }
        }
    
    def _generate_title(self, doc_type: str) -> str:
        """Generate appropriate title based on document type"""
        titles = {
            "employee_handbook": f"{fake.company()} Employee Handbook",
            "job_description": f"{random.choice(self.job_titles)} - Job Description",
            "policy_document": f"{random.choice(['Remote Work', 'Expense', 'PTO', 'Security'])} Policy",
            "training_material": f"{random.choice(['Leadership', 'Communication', 'Technical'])} Training",
            "performance_review": f"Performance Review - {fake.name()}",
            "company_announcement": f"Company Update: {fake.catch_phrase()}",
            "benefits_guide": "Employee Benefits Guide",
            "code_of_conduct": "Code of Conduct and Ethics",
            "safety_guidelines": "Workplace Safety Guidelines",
            "onboarding_checklist": "New Employee Onboarding Checklist"
        }
        return titles.get(doc_type, f"{doc_type.replace('_', ' ').title()}")
    
    def _generate_tags(self, doc_type: str) -> List[str]:
        """Generate relevant tags for the document"""
        base_tags = ["hr", "policy", "employee"]
        
        type_specific_tags = {
            "employee_handbook": ["handbook", "culture", "guidelines"],
            "job_description": ["hiring", "recruitment", "job"],
            "policy_document": ["policy", "procedures", "compliance"],
            "training_material": ["training", "development", "learning"],
            "performance_review": ["performance", "review", "evaluation"],
            "company_announcement": ["announcement", "news", "update"],
            "benefits_guide": ["benefits", "compensation", "wellness"],
            "code_of_conduct": ["conduct", "ethics", "behavior"],
            "safety_guidelines": ["safety", "health", "guidelines"],
            "onboarding_checklist": ["onboarding", "checklist", "new_hire"]
        }
        
        tags = base_tags + type_specific_tags.get(doc_type, [])
        return random.sample(tags, min(len(tags), random.randint(3, 6)))
    
    def _generate_performance_review(self) -> str:
        employee_name = fake.name()
        return f"""
        Performance Review: {employee_name}
        Review Period: {fake.date_between(start_date='-1y', end_date='-6m')} to {fake.date_between(start_date='-6m', end_date='today')}
        
        Overall Performance Rating: {random.choice(['Exceeds Expectations', 'Meets Expectations', 'Below Expectations'])}
        
        Key Accomplishments:
        - {fake.sentence()}
        - {fake.sentence()}
        - {fake.sentence()}
        
        Areas of Strength:
        - Strong technical skills and problem-solving abilities
        - Excellent communication and collaboration
        - Proactive approach to learning and development
        
        Areas for Improvement:
        - {fake.sentence()}
        - {fake.sentence()}
        
        Goals for Next Review Period:
        1. {fake.sentence()}
        2. {fake.sentence()}
        3. {fake.sentence()}
        
        Development Plan:
        - Attend relevant training sessions
        - Seek mentorship opportunities
        - Take on additional responsibilities
        
        Employee Comments:
        [Space for employee feedback and self-assessment]
        
        Manager: {fake.name()}
        Date: {fake.date_between(start_date='-1m', end_date='today')}
        """
    
    def _generate_company_announcement(self) -> str:
        return f"""
        Company Announcement: {fake.catch_phrase()}
        
        Dear Team,
        
        We are excited to share some important updates about our company's growth
        and future direction.
        
        {fake.paragraph(nb_sentences=3)}
        
        Key Highlights:
        - {fake.sentence()}
        - {fake.sentence()}
        - {fake.sentence()}
        
        What This Means for You:
        {fake.paragraph(nb_sentences=2)}
        
        Next Steps:
        We will be hosting a company-wide meeting on {fake.date_between(start_date='today', end_date='+1m')}
        to discuss these changes in detail and answer any questions you may have.
        
        Thank you for your continued dedication and hard work.
        
        Best regards,
        {fake.name()}
        CEO
        """
    
    def _generate_benefits_guide(self) -> str:
        return f"""
        Employee Benefits Guide
        
        Welcome to your comprehensive benefits package! We are committed to supporting
        your health, financial security, and work-life balance.
        
        Health Insurance:
        - Medical coverage with multiple plan options
        - Dental and vision insurance
        - Prescription drug coverage
        - Mental health and wellness programs
        
        Retirement Benefits:
        - 401(k) plan with company matching up to {random.randint(3, 6)}%
        - Vesting schedule: {random.randint(3, 5)} years
        - Investment options and financial planning resources
        
        Time Off Benefits:
        - Paid vacation: {random.randint(15, 25)} days annually
        - Sick leave: {random.randint(5, 10)} days annually
        - Personal days: {random.randint(2, 5)} days annually
        - Parental leave: Up to {random.randint(8, 16)} weeks
        
        Additional Benefits:
        - Life and disability insurance
        - Employee assistance program
        - Professional development budget
        - Flexible spending accounts
        - Commuter benefits
        
        Enrollment:
        Benefits enrollment occurs during your first 30 days of employment
        and during the annual open enrollment period.
        
        Questions?
        Contact HR at hr@company.com or visit the employee portal for more information.
        """
    
    def _generate_code_of_conduct(self) -> str:
        return f"""
        Code of Conduct and Ethics
        
        Our Commitment:
        We are committed to maintaining the highest standards of ethical conduct
        in all our business activities and relationships.
        
        Core Principles:
        1. Integrity: We act honestly and transparently in all situations
        2. Respect: We treat everyone with dignity and fairness
        3. Accountability: We take responsibility for our actions and decisions
        4. Excellence: We strive for quality in everything we do
        
        Professional Standards:
        - Maintain confidentiality of sensitive information
        - Avoid conflicts of interest
        - Use company resources responsibly
        - Comply with all applicable laws and regulations
        
        Workplace Behavior:
        - Foster an inclusive and respectful environment
        - Communicate professionally and constructively
        - Report unethical behavior or policy violations
        - Support colleagues and collaborate effectively
        
        Compliance:
        All employees are expected to read, understand, and comply with this
        code of conduct. Violations may result in disciplinary action.
        
        Reporting:
        If you witness or suspect violations of this code, please report them
        to your supervisor, HR, or through our anonymous reporting system.
        
        This code is reviewed annually and updated as needed to reflect our
        evolving values and business practices.
        """
    
    def _generate_safety_guidelines(self) -> str:
        return f"""
        Workplace Safety Guidelines
        
        Our Commitment to Safety:
        The safety and well-being of our employees is our top priority. These
        guidelines help ensure a safe and healthy work environment for everyone.
        
        General Safety Rules:
        - Report all accidents, injuries, and near-misses immediately
        - Keep work areas clean and organized
        - Use proper lifting techniques for heavy objects
        - Follow all posted safety signs and procedures
        
        Office Safety:
        - Ensure walkways are clear of obstacles
        - Use ergonomic workstation setups
        - Report any electrical hazards or equipment malfunctions
        - Know the location of emergency exits and procedures
        
        Emergency Procedures:
        - Fire: Evacuate immediately using designated routes
        - Medical Emergency: Call 911 and notify security
        - Severe Weather: Follow shelter-in-place procedures
        - Security Threat: Report to security and follow lockdown procedures
        
        Personal Protective Equipment:
        When required, employees must use appropriate PPE including:
        - Safety glasses in designated areas
        - Protective footwear in warehouse areas
        - Hearing protection in high-noise environments
        
        Training:
        All employees receive safety orientation and ongoing training relevant
        to their work environment and responsibilities.
        
        Reporting:
        Safety concerns should be reported immediately to your supervisor or
        the safety committee. We encourage proactive safety reporting.
        """
    
    def _generate_onboarding_checklist(self) -> str:
        return f"""
        New Employee Onboarding Checklist
        
        Welcome! This checklist will help ensure you have everything you need
        for a successful start with our company.
        
        Before Your First Day:
        □ Complete all required paperwork (I-9, W-4, benefits enrollment)
        □ Review employee handbook and company policies
        □ Set up direct deposit for payroll
        □ Submit emergency contact information
        
        First Day:
        □ Arrive at {fake.time()} for orientation
        □ Meet with HR for welcome session
        □ Receive employee ID badge and access cards
        □ Set up workstation and receive equipment
        □ Meet your manager and team members
        □ Review job description and initial goals
        
        First Week:
        □ Complete IT setup and system access
        □ Attend new employee orientation sessions
        □ Schedule meetings with key stakeholders
        □ Begin role-specific training
        □ Review performance expectations and goals
        
        First Month:
        □ Complete all required training modules
        □ Establish regular check-ins with manager
        □ Join relevant team meetings and projects
        □ Connect with mentor (if applicable)
        □ Provide feedback on onboarding experience
        
        Resources:
        - Employee portal: [URL]
        - HR contact: hr@company.com
        - IT support: it@company.com
        - Manager: [Name and contact]
        
        Questions?
        Don't hesitate to reach out to HR or your manager with any questions
        during your onboarding process.
        """
    
    def generate_batch(self, num_documents: int = 50) -> List[Dict[str, Any]]:
        """Generate a batch of synthetic documents"""
        return [self.generate_document() for _ in range(num_documents)]

if __name__ == "__main__":
    generator = HRDataGenerator()
    
    # Generate sample documents
    documents = generator.generate_batch(10)
    
    # Save to file
    with open('../data/sample_documents.json', 'w') as f:
        json.dump(documents, f, indent=2)
    
    print(f"Generated {len(documents)} sample documents")
    for doc in documents[:3]:
        print(f"- {doc['title']} ({doc['document_type']})")

