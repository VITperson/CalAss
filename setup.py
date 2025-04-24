from setuptools import setup, find_packages

setup(
    name="gpt-calendar-planner",
    version="0.1.0",
    packages=["gpt_calendar_planner"],
    install_requires=[
        "openai>=1.0",
        "caldav>=1.0",
        "icalendar>=5.0",
        "typer>=0.9.0",
        "python-dotenv>=1.0",
        "apscheduler>=3.10",
        "cryptography>=41.0",
        "pydantic>=2.0",
        "pydantic-settings>=2.0",
        "dateparser>=1.0",
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'mypy>=1.0',
            'black>=23.0',
            'pre-commit>=3.0',
            'flake8>=6.0',
            'isort>=5.0',
        ]
    },
    entry_points={
        "console_scripts": [
            "planner=gpt_calendar_planner.planner:app",
        ],
    },
) 