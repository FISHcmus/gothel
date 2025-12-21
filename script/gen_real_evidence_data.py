from sqlalchemy.orm import Session

from model.Base import get_db
from model.EvidenceProblem import EvidenceProblemDB
from script.reset import reset_single_table


def create_real_problems(session: Session) -> None:
    # Data with integer indices hardcoded directly
    problems_data = [
        {
            "reading_content": "The Great Pyramid of Giza is the oldest and largest of the three pyramids in the Giza pyramid complex bordering present-day Giza in Greater Cairo, Egypt. It is the oldest of the Seven Wonders of the Ancient World, and the only one to remain largely intact. It is estimated that the pyramid consists of approximately 2.3 million blocks of limestone and granite, some weighing as much as 80 tonnes.",
            "problem_statement": "How many blocks were used to build the Great Pyramid?",
            "options": [
                "Around 1 million blocks",
                "Approximately 2.3 million blocks",
                "Exactly 80 tonnes",
                "Less than 2 million"
            ],
            "correct_option": 1, # Index of "Approximately 2.3 million blocks"
            "evidence": "2.3 million blocks"
        },
        {
            "reading_content": "Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy that, through cellular respiration, can later be released to fuel the organism's activities. This chemical energy is stored in carbohydrate molecules, such as sugars and starches, which are synthesized from carbon dioxide and water.",
            "problem_statement": "What is the primary input converted into chemical energy in photosynthesis?",
            "options": [
                "Carbon dioxide",
                "Water",
                "Light energy",
                "Oxygen"
            ],
            "correct_option": 2, # Index of "Light energy"
            "evidence": "convert light energy into chemical energy"
        },
        {
            "reading_content": "Apollo 11 was the American spaceflight that first landed humans on the Moon. Commander Neil Armstrong and lunar module pilot Buzz Aldrin landed the Apollo Lunar Module Eagle on July 20, 1969, at 20:17 UTC, and Armstrong became the first person to step onto the Moon's surface six hours and 39 minutes later, on July 21 at 02:56 UTC.",
            "problem_statement": "Who was the first person to step onto the Moon?",
            "options": [
                "Buzz Aldrin",
                "Neil Armstrong",
                "Michael Collins",
                "Yuri Gagarin"
            ],
            "correct_option": 1, # Index of "Neil Armstrong"
            "evidence": "Armstrong became the first person to step onto the Moon's surface"
        },
        {
            "reading_content": "Honey bees are known for their construction of perennial colonial nests from wax, the large size of their colonies, and for their surplus production and storage of honey, distinguishing their hives as a prized foraging target of many animals, including honey badgers, bears and human hunter-gatherers.",
            "problem_statement": "What material do honey bees use to construct their nests?",
            "options": [
                "Mud",
                "Leaves",
                "Wax",
                "Wood"
            ],
            "correct_option": 2, # Index of "Wax"
            "evidence": "construction of perennial colonial nests from wax"
        },
        {
            "reading_content": "The Internet is a global system of interconnected computer networks that uses the Internet protocol suite (TCP/IP) to communicate between networks and devices. It is a network of networks that consists of private, public, academic, business, and government networks of local to global scope, linked by a broad array of electronic, wireless, and optical networking technologies.",
            "problem_statement": "Which protocol suite does the Internet use?",
            "options": [
                "UDP/IP",
                "TCP/IP",
                "HTTP/FTP",
                "OSI Model"
            ],
            "correct_option": 1, # Index of "TCP/IP"
            "evidence": "uses the Internet protocol suite (TCP/IP)"
        }
    ]

    for p_data in problems_data:
        exists = session.query(EvidenceProblemDB).filter(
            EvidenceProblemDB.problem_statement == p_data["problem_statement"]).first()

        if not exists:
            problem = EvidenceProblemDB(
                reading_content=p_data["reading_content"],
                problem_statement=p_data["problem_statement"],
                options=p_data["options"],
                correct_option=p_data["correct_option"],
                evidence=p_data["evidence"]
            )
            session.add(problem)
            print(f"Added problem: {p_data['problem_statement']}")
        else:
            print(f"Skipped duplicate: {p_data['problem_statement']}")

    session.commit()
    print("Done generating real evidence problems.")


if __name__ == "__main__":
    db_gen = get_db()
    db = next(db_gen)
    try:
        reset_single_table("evidence_problem_table")
        create_real_problems(db)
    finally:
        db_gen.close()
