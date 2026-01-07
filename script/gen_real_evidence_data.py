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
            "evidence": "light energy"
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
            "evidence": "Armstrong"
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
            "evidence": "wax"
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
            "evidence": "TCP/IP"
        },
        {
            "reading_content": "The water cycle, also known as the hydrological cycle, describes the continuous movement of water on, above and below the surface of the Earth. Water evaporates from the surface of the Earth, rises into the atmosphere, cools and condenses into clouds, and eventually returns to the surface as precipitation in the form of rain or snow. This cycle is crucial for maintaining life on Earth and regulating the planet's temperature.",
            "problem_statement": "What process converts liquid water into water vapor?",
            "options": [
                "Condensation",
                "Evaporation",
                "Precipitation",
                "Sublimation"
            ],
            "correct_option": 1, # Index of "Evaporation"
            "evidence": "evaporates"
        },
        {
            "reading_content": "Albert Einstein, one of the most influential physicists of the 20th century, developed the theory of relativity, which revolutionized our understanding of space, time, and gravity. His famous equation E=mc² demonstrates the equivalence of energy and mass, showing that a small amount of mass can be converted into a tremendous amount of energy. This discovery laid the theoretical foundation for nuclear energy and atomic weapons.",
            "problem_statement": "What famous equation did Einstein develop?",
            "options": [
                "F=ma",
                "E=mc²",
                "a²+b²=c²",
                "PV=nRT"
            ],
            "correct_option": 1, # Index of "E=mc²"
            "evidence": "E=mc²"
        },
        {
            "reading_content": "The Amazon Rainforest, often called the 'lungs of the Earth,' is the world's largest tropical rainforest, covering approximately 5.5 million square kilometers. It is home to an estimated 10% of all species on Earth, including over 40,000 plant species, 1,300 bird species, and 2.5 million different insects. The Amazon plays a crucial role in regulating the global climate and producing oxygen for the planet.",
            "problem_statement": "What percentage of Earth's species live in the Amazon?",
            "options": [
                "5%",
                "10%",
                "25%",
                "50%"
            ],
            "correct_option": 1, # Index of "10%"
            "evidence": "10%"
        },
        {
            "reading_content": "The Industrial Revolution, which began in Britain in the late 18th century, transformed society from agrarian to industrial. The steam engine, invented by James Watt, became the driving force behind this transformation, powering factories, trains, and ships. This invention revolutionized manufacturing and transportation, leading to unprecedented economic growth and urbanization, though it also created new social and environmental challenges.",
            "problem_statement": "What invention powered factories during the Industrial Revolution?",
            "options": [
                "Electric motor",
                "Steam engine",
                "Water wheel",
                "Windmill"
            ],
            "correct_option": 1, # Index of "Steam engine"
            "evidence": "steam engine"
        },
        {
            "reading_content": "In 1953, scientists James Watson and Francis Crick discovered the structure of DNA, the molecule that carries genetic information in all living organisms. They determined that DNA has a double helix structure, resembling a twisted ladder, with two strands coiling around each other. This groundbreaking discovery revolutionized biology and medicine, enabling scientists to understand how genetic information is stored, copied, and passed from generation to generation.",
            "problem_statement": "What shape is DNA's molecular structure?",
            "options": [
                "Single strand",
                "Double helix",
                "Triple helix",
                "Circular loop"
            ],
            "correct_option": 1, # Index of "Double helix"
            "evidence": "double helix"
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
