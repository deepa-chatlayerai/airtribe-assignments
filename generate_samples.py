"""Generate dummy resume files in ./resumes across TXT, DOCX, and PDF.

Run once to populate sample data:
    python generate_samples.py

Requires: python-docx (DOCX) and fpdf2 (PDF). TXT needs nothing.
"""

from __future__ import annotations

import os

import docx
from fpdf import FPDF
from fpdf.enums import XPos, YPos

RESUME_DIR = "resumes"

# (filename, format, resume dict)
RESUMES = [
    (
        "resume_john_doe",
        "pdf",
        {
            "name": "John Doe",
            "title": "Senior Backend Engineer",
            "email": "john.doe@example.com",
            "summary": "Backend engineer with 8 years building distributed systems.",
            "skills": ["Python", "Django", "PostgreSQL", "Redis", "AWS", "Docker"],
            "experience": [
                "Lead Engineer, Acme Corp (2019-present): scaled payments to 10k rps.",
                "Engineer, Beta Inc (2016-2019): built REST APIs in Python and Flask.",
            ],
            "education": "B.S. Computer Science, State University, 2016",
        },
    ),
    (
        "resume_jane_smith",
        "docx",
        {
            "name": "Jane Smith",
            "title": "Data Scientist",
            "email": "jane.smith@example.com",
            "summary": "Data scientist specializing in NLP and recommender systems.",
            "skills": ["Python", "PyTorch", "scikit-learn", "SQL", "Spark"],
            "experience": [
                "Data Scientist, DataWorks (2020-present): built churn models in Python.",
                "Analyst, Insight Co (2018-2020): A/B testing and dashboards.",
            ],
            "education": "M.S. Statistics, Tech Institute, 2018",
        },
    ),
    (
        "resume_raj_patel",
        "txt",
        {
            "name": "Raj Patel",
            "title": "Full Stack Developer",
            "email": "raj.patel@example.com",
            "summary": "Full stack developer comfortable across the JavaScript stack.",
            "skills": ["JavaScript", "TypeScript", "React", "Node.js", "MongoDB"],
            "experience": [
                "Full Stack Dev, WebScale (2021-present): React + Node microservices.",
                "Frontend Dev, Pixel Labs (2019-2021): built design-system components.",
            ],
            "education": "B.E. Information Technology, City College, 2019",
        },
    ),
    (
        "resume_maria_garcia",
        "txt",
        {
            "name": "Maria Garcia",
            "title": "Machine Learning Engineer",
            "email": "maria.garcia@example.com",
            "summary": "ML engineer deploying models to production at scale.",
            "skills": ["Python", "TensorFlow", "Kubernetes", "GCP", "Airflow"],
            "experience": [
                "ML Engineer, VisionAI (2020-present): real-time inference in Python.",
                "Software Engineer, CloudNine (2017-2020): data pipelines on GCP.",
            ],
            "education": "M.S. Computer Science, Mountain University, 2017",
        },
    ),
    (
        "resume_liam_oconnor",
        "txt",
        {
            "name": "Liam O'Connor",
            "title": "DevOps Engineer",
            "email": "liam.oconnor@example.com",
            "summary": "DevOps engineer focused on CI/CD and observability.",
            "skills": ["Terraform", "AWS", "Docker", "Kubernetes", "Python", "Go"],
            "experience": [
                "DevOps Engineer, ShipFast (2019-present): built GitOps pipelines.",
                "SysAdmin, HostCo (2016-2019): managed Linux fleets.",
            ],
            "education": "B.S. Computer Engineering, Harbor University, 2016",
        },
    ),
    (
        "resume_aisha_khan",
        "txt",
        {
            "name": "Aisha Khan",
            "title": "Product Manager",
            "email": "aisha.khan@example.com",
            "summary": "Technical PM bridging engineering and business teams.",
            "skills": ["Roadmapping", "SQL", "Figma", "Analytics", "A/B Testing"],
            "experience": [
                "Senior PM, GrowthLabs (2020-present): owned a $5M product line.",
                "PM, StartupXYZ (2018-2020): launched mobile app to 1M users.",
            ],
            "education": "MBA, Business School, 2018",
        },
    ),
    (
        "resume_chen_wei",
        "docx",
        {
            "name": "Chen Wei",
            "title": "Site Reliability Engineer",
            "email": "chen.wei@example.com",
            "summary": "SRE keeping high-traffic services reliable and fast.",
            "skills": ["Python", "Go", "Prometheus", "Grafana", "Kubernetes"],
            "experience": [
                "SRE, StreamHub (2019-present): cut incident MTTR by 40%.",
                "Backend Engineer, Nodal (2016-2019): Go services on Kubernetes.",
            ],
            "education": "B.S. Software Engineering, Capital University, 2016",
        },
    ),
    (
        "resume_sofia_rossi",
        "pdf",
        {
            "name": "Sofia Rossi",
            "title": "Frontend Engineer",
            "email": "sofia.rossi@example.com",
            "summary": "Frontend engineer passionate about accessibility and UX.",
            "skills": ["JavaScript", "React", "CSS", "TypeScript", "Accessibility"],
            "experience": [
                "Frontend Engineer, BrightUI (2020-present): led WCAG compliance.",
                "Web Developer, Studio7 (2018-2020): built marketing sites.",
            ],
            "education": "B.A. Design & Computing, Arts University, 2018",
        },
    ),
    (
        "resume_david_mueller",
        "txt",
        {
            "name": "David Mueller",
            "title": "Security Engineer",
            "email": "david.mueller@example.com",
            "summary": "Security engineer with a focus on application security.",
            "skills": ["Python", "Threat Modeling", "Burp Suite", "AWS", "Go"],
            "experience": [
                "Security Engineer, SafeGuard (2019-present): ran the AppSec program.",
                "Pentester, RedTeam Co (2017-2019): web and API assessments.",
            ],
            "education": "B.S. Cybersecurity, Fort University, 2017",
        },
    ),
    (
        "resume_emma_wilson",
        "txt",
        {
            "name": "Emma Wilson",
            "title": "Engineering Manager",
            "email": "emma.wilson@example.com",
            "summary": "Engineering manager who grew teams from 3 to 20.",
            "skills": ["Leadership", "Python", "System Design", "Hiring", "Mentoring"],
            "experience": [
                "Engineering Manager, ScaleUp (2018-present): led 4 squads.",
                "Tech Lead, BuildIt (2015-2018): Python backend architecture.",
            ],
            "education": "B.S. Computer Science, Lakeside University, 2015",
        },
    ),
]


def render_text(resume: dict) -> str:
    """Render a resume dict as plain text."""
    lines = [
        resume["name"],
        resume["title"],
        resume["email"],
        "",
        "SUMMARY",
        resume["summary"],
        "",
        "SKILLS",
        ", ".join(resume["skills"]),
        "",
        "EXPERIENCE",
    ]
    lines.extend(f"- {item}" for item in resume["experience"])
    lines += ["", "EDUCATION", resume["education"], ""]
    return "\n".join(lines)


def write_txt(path: str, resume: dict) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(render_text(resume))


def write_docx(path: str, resume: dict) -> None:
    document = docx.Document()
    document.add_heading(resume["name"], level=0)
    document.add_paragraph(resume["title"])
    document.add_paragraph(resume["email"])
    document.add_heading("Summary", level=1)
    document.add_paragraph(resume["summary"])
    document.add_heading("Skills", level=1)
    document.add_paragraph(", ".join(resume["skills"]))
    document.add_heading("Experience", level=1)
    for item in resume["experience"]:
        document.add_paragraph(item, style="List Bullet")
    document.add_heading("Education", level=1)
    document.add_paragraph(resume["education"])
    document.save(path)


def write_pdf(path: str, resume: dict) -> None:
    nl = {"new_x": XPos.LMARGIN, "new_y": YPos.NEXT}
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, resume["name"], **nl)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, resume["title"], **nl)
    pdf.cell(0, 8, resume["email"], **nl)
    pdf.ln(4)

    def section(title: str, body_lines: list[str]) -> None:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, title, **nl)
        pdf.set_font("Helvetica", "", 11)
        for line in body_lines:
            # latin-1 is fpdf's core-font encoding; strip unsupported glyphs.
            safe = line.encode("latin-1", "replace").decode("latin-1")
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.epw, 6, safe, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

    section("Summary", [resume["summary"]])
    section("Skills", [", ".join(resume["skills"])])
    section("Experience", [f"- {item}" for item in resume["experience"]])
    section("Education", [resume["education"]])
    pdf.output(path)


WRITERS = {"txt": write_txt, "docx": write_docx, "pdf": write_pdf}


def main() -> None:
    os.makedirs(RESUME_DIR, exist_ok=True)
    for stem, fmt, resume in RESUMES:
        path = os.path.join(RESUME_DIR, f"{stem}.{fmt}")
        WRITERS[fmt](path, resume)
        print(f"wrote {path}")
    print(f"\nGenerated {len(RESUMES)} resumes in ./{RESUME_DIR}")


if __name__ == "__main__":
    main()
